"""
Authentication and Authorization Module
Implements secure user authentication with PIN/biometric support
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from .security import (
    AuthenticationManager,
    SecurityAuditLogger,
    get_auth_manager,
    get_audit_logger,
    SecurityException
)
from sqlmodel import Session, select
from .database import db_manager, User as DBUser

# Security scheme for FastAPI
security_scheme = HTTPBearer()

class User:
    """Lightweight User wrapper for compatibility with existing code.
    When a database-backed user exists, we wrap DBUser into this structure.
    """
    def __init__(self, user_id: str, pin_hash: str, device_id: str = None,
                 preferences: Dict[str, Any] = None, is_active: bool = True):
        self.id = user_id
        self.pin_hash = pin_hash
        self.device_id = device_id
        self.preferences = preferences or {}
        self.created_at = datetime.utcnow()
        self.last_login = None
        self.is_active = is_active

def _dbuser_to_user(db_user: DBUser) -> User:
    return User(
        user_id=str(db_user.id),
        pin_hash=db_user.pin_hash,
        device_id=db_user.device_id,
        preferences=getattr(db_user, "preferences", {}) or {},
        is_active=getattr(db_user, "is_active", True)
    )

class AuthService:
    """Authentication service for user management (DB-backed)"""
    
    def __init__(self):
        self.auth_manager = get_auth_manager()
        self.audit_logger = get_audit_logger()
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_user(self, pin: str, device_id: str = None, 
                   preferences: Dict[str, Any] = None) -> User:
        """Create a new user with PIN authentication (persist to DB)"""
        session: Session = db_manager.get_session()
        try:
            pin_hash = self.auth_manager.hash_pin(pin)
            db_user = DBUser(pin_hash=pin_hash, device_id=device_id, preferences=preferences or {})
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            
            user = _dbuser_to_user(db_user)
            
            self.audit_logger.log_authentication_event(
                user_id=user.id,
                event_type="USER_CREATED",
                success=True,
                details={"device_id": device_id}
            )
            
            return user
            
        except Exception as e:
            self.audit_logger.log_security_event(
                event_type="USER_CREATION_FAILED",
                severity="ERROR",
                details={"error": str(e)}
            )
            raise SecurityException("User creation failed")
        finally:
            session.close()
    
    def authenticate_user(self, pin: str, device_id: str = None) -> Optional[User]:
        """Authenticate user with PIN (DB-backed)"""
        session: Session = db_manager.get_session()
        try:
            # If no users exist, create one (MVP)
            result = session.exec(select(DBUser))
            first = result.first()
            if not first:
                return self.create_user(pin=pin, device_id=device_id)
            
            db_user = first
            
            # Check account lockout
            if self.auth_manager.check_account_lockout(str(db_user.id)):
                self.audit_logger.log_authentication_event(
                    user_id=str(db_user.id),
                    event_type="LOGIN_BLOCKED",
                    success=False,
                    details={"reason": "account_locked", "device_id": device_id}
                )
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail="Account temporarily locked due to failed attempts"
                )
            
            # Verify PIN
            if not self.auth_manager.verify_pin(pin, db_user.pin_hash):
                self.auth_manager.record_failed_attempt(str(db_user.id))
                self.audit_logger.log_authentication_event(
                    user_id=str(db_user.id),
                    event_type="LOGIN_FAILED",
                    success=False,
                    details={"reason": "invalid_pin", "device_id": device_id}
                )
                return None
            
            # Successful authentication
            self.auth_manager.reset_failed_attempts(str(db_user.id))
            db_user.last_login = datetime.utcnow()
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            
            self.audit_logger.log_authentication_event(
                user_id=str(db_user.id),
                event_type="LOGIN_SUCCESS",
                success=True,
                details={"device_id": device_id}
            )
            
            return _dbuser_to_user(db_user)
        finally:
            session.close()
    
    def create_user_session(self, user: User, device_id: str = None) -> Dict[str, str]:
        """Create user session with JWT tokens"""
        try:
            # Create token payload
            token_data = {
                "sub": user.id,
                "device_id": device_id,
                "session_id": str(uuid.uuid4())
            }
            
            # Generate tokens
            access_token = self.auth_manager.create_access_token(token_data)
            refresh_token = self.auth_manager.create_refresh_token(token_data)
            
            # Store session
            session_id = token_data["session_id"]
            self.sessions[session_id] = {
                "user_id": user.id,
                "device_id": device_id,
                "created_at": datetime.utcnow(),
                "last_activity": datetime.utcnow()
            }
            
            self.audit_logger.log_authentication_event(
                user_id=user.id,
                event_type="SESSION_CREATED",
                success=True,
                details={"session_id": session_id, "device_id": device_id}
            )
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": 1800  # 30 minutes
            }
            
        except Exception as e:
            self.audit_logger.log_security_event(
                event_type="SESSION_CREATION_FAILED",
                severity="ERROR",
                details={"user_id": user.id, "error": str(e)}
            )
            raise SecurityException("Session creation failed")
    
    def get_user_from_token(self, token: str) -> Optional[User]:
        """Get user from JWT token"""
        try:
            payload = self.auth_manager.verify_token(token)
            if not payload:
                return None
            
            user_id = payload.get("sub")
            session_id = payload.get("session_id")
            
            # Check if session exists and is valid
            if session_id not in self.sessions:
                self.audit_logger.log_authentication_event(
                    user_id=user_id,
                    event_type="INVALID_SESSION",
                    success=False,
                    details={"session_id": session_id}
                )
                return None
            
            # Update session activity
            self.sessions[session_id]["last_activity"] = datetime.utcnow()
            
            # Get user from DB
            session = db_manager.get_session()
            try:
                db_user = session.exec(select(DBUser).where(DBUser.id == user_id)).one_or_none()
                if not db_user or not db_user.is_active:
                    return None
                return _dbuser_to_user(db_user)
            finally:
                session.close()
            
        except Exception as e:
            self.audit_logger.log_security_event(
                event_type="TOKEN_VERIFICATION_FAILED",
                severity="WARNING",
                details={"error": str(e)}
            )
            return None
    
    def logout_user(self, session_id: str, user_id: str) -> None:
        """Logout user and invalidate session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            
            self.audit_logger.log_authentication_event(
                user_id=user_id,
                event_type="LOGOUT",
                success=True,
                details={"session_id": session_id}
            )

# Global auth service instance
auth_service = AuthService()

def get_auth_service() -> AuthService:
    """Get global authentication service instance"""
    return auth_service

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    auth_svc: AuthService = Depends(get_auth_service)
) -> User:
    """FastAPI dependency to get current authenticated user"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        user = auth_svc.get_user_from_token(token)
        
        if user is None:
            raise credentials_exception
            
        return user
        
    except Exception:
        raise credentials_exception

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """FastAPI dependency to get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

# Rate limiting middleware
class RateLimitMiddleware:
    """Rate limiting middleware for API protection"""
    
    def __init__(self):
        self.requests: Dict[str, list] = {}
        self.max_requests = 100  # requests per minute
        self.window_size = 60  # seconds
    
    def is_rate_limited(self, client_ip: str) -> bool:
        """Check if client is rate limited"""
        now = datetime.utcnow().timestamp()
        
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Remove old requests outside the window
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < self.window_size
        ]
        
        # Check if limit exceeded
        if len(self.requests[client_ip]) >= self.max_requests:
            return True
        
        # Add current request
        self.requests[client_ip].append(now)
        return False

# Global rate limiter
rate_limiter = RateLimitMiddleware()

async def check_rate_limit(request: Request):
    """FastAPI dependency for rate limiting"""
    client_ip = request.client.host
    
    if rate_limiter.is_rate_limited(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    return True
