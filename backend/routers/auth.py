"""
Authentication API Endpoints
Implements secure user authentication with PIN/biometric support
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

from ..core.auth import (
    AuthService, 
    User, 
    get_auth_service, 
    get_current_user,
    check_rate_limit
)
from ..core.security import get_audit_logger

router = APIRouter()
security = HTTPBearer()
audit_logger = get_audit_logger()

# Request/Response Models
class LoginRequest(BaseModel):
    pin: str = Field(..., min_length=4, max_length=20, description="User PIN")
    device_id: Optional[str] = Field(None, description="Device identifier")
    biometric_token: Optional[str] = Field(None, description="Biometric authentication token")

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]

class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token")

class LogoutRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="Session ID to logout")

class CreateUserRequest(BaseModel):
    pin: str = Field(..., min_length=4, max_length=20, description="User PIN")
    device_id: Optional[str] = Field(None, description="Device identifier")
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict, description="User preferences")

class UserResponse(BaseModel):
    id: str
    device_id: Optional[str]
    preferences: Dict[str, Any]
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool

@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    login_request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
    _: bool = Depends(check_rate_limit)
):
    """
    Authenticate user with PIN and optional biometric token
    """
    try:
        # Get client IP for audit logging
        client_ip = request.client.host
        
        # Authenticate user
        user = auth_service.authenticate_user(
            pin=login_request.pin,
            device_id=login_request.device_id
        )
        
        if not user:
            audit_logger.log_authentication_event(
                user_id="unknown",
                event_type="LOGIN_FAILED",
                success=False,
                details={
                    "reason": "invalid_credentials",
                    "device_id": login_request.device_id,
                    "client_ip": client_ip
                }
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid PIN or device not recognized"
            )
        
        # Create session and tokens
        session_data = auth_service.create_user_session(
            user=user,
            device_id=login_request.device_id
        )
        
        # Prepare response
        user_data = {
            "id": user.id,
            "device_id": user.device_id,
            "preferences": user.preferences,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
        
        return LoginResponse(
            access_token=session_data["access_token"],
            refresh_token=session_data["refresh_token"],
            token_type=session_data["token_type"],
            expires_in=session_data["expires_in"],
            user=user_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        audit_logger.log_security_event(
            event_type="LOGIN_ERROR",
            severity="ERROR",
            details={"error": str(e), "client_ip": request.client.host}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )

@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
    request: Request,
    refresh_request: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
    _: bool = Depends(check_rate_limit)
):
    """
    Refresh access token using refresh token
    """
    try:
        # Verify refresh token
        payload = auth_service.auth_manager.verify_token(refresh_request.refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        user = auth_service.users.get(user_id)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new session
        session_data = auth_service.create_user_session(
            user=user,
            device_id=payload.get("device_id")
        )
        
        # Prepare response
        user_data = {
            "id": user.id,
            "device_id": user.device_id,
            "preferences": user.preferences,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
        
        audit_logger.log_authentication_event(
            user_id=user_id,
            event_type="TOKEN_REFRESHED",
            success=True,
            details={"client_ip": request.client.host}
        )
        
        return LoginResponse(
            access_token=session_data["access_token"],
            refresh_token=session_data["refresh_token"],
            token_type=session_data["token_type"],
            expires_in=session_data["expires_in"],
            user=user_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        audit_logger.log_security_event(
            event_type="TOKEN_REFRESH_ERROR",
            severity="ERROR",
            details={"error": str(e), "client_ip": request.client.host}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh service error"
        )

@router.post("/logout")
async def logout(
    request: Request,
    logout_request: LogoutRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Logout user and invalidate session
    """
    try:
        session_id = logout_request.session_id
        if session_id:
            auth_service.logout_user(session_id, current_user.id)
        
        audit_logger.log_authentication_event(
            user_id=current_user.id,
            event_type="LOGOUT",
            success=True,
            details={"client_ip": request.client.host, "session_id": session_id}
        )
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        audit_logger.log_security_event(
            event_type="LOGOUT_ERROR",
            severity="ERROR",
            details={"error": str(e), "user_id": current_user.id}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout service error"
        )

@router.post("/create-user", response_model=UserResponse)
async def create_user(
    request: Request,
    create_request: CreateUserRequest,
    auth_service: AuthService = Depends(get_auth_service),
    _: bool = Depends(check_rate_limit)
):
    """
    Create a new user account (MVP - single user)
    """
    try:
        # For MVP, only allow one user
        if auth_service.users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists. This MVP supports single user only."
            )
        
        # Create user
        user = auth_service.create_user(
            pin=create_request.pin,
            device_id=create_request.device_id,
            preferences=create_request.preferences
        )
        
        audit_logger.log_authentication_event(
            user_id=user.id,
            event_type="USER_CREATED",
            success=True,
            details={"client_ip": request.client.host, "device_id": create_request.device_id}
        )
        
        return UserResponse(
            id=user.id,
            device_id=user.device_id,
            preferences=user.preferences,
            created_at=user.created_at,
            last_login=user.last_login,
            is_active=user.is_active
        )
        
    except HTTPException:
        raise
    except Exception as e:
        audit_logger.log_security_event(
            event_type="USER_CREATION_ERROR",
            severity="ERROR",
            details={"error": str(e), "client_ip": request.client.host}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User creation service error"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information
    """
    return UserResponse(
        id=current_user.id,
        device_id=current_user.device_id,
        preferences=current_user.preferences,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
        is_active=current_user.is_active
    )

@router.get("/health")
async def auth_health_check():
    """
    Authentication service health check
    """
    return {
        "status": "healthy",
        "service": "authentication",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "PIN Authentication",
            "JWT Tokens",
            "Session Management",
            "Rate Limiting",
            "Security Audit Logging"
        ]
    }
