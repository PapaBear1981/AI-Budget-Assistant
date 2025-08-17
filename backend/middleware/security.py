"""
Security Middleware for Request/Response Processing
Implements comprehensive security controls for all API requests
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time
import uuid
import logging

from ..core.security import get_audit_logger

security_logger = logging.getLogger("security_middleware")
audit_logger = get_audit_logger()

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID for tracking
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request for audit
        start_time = time.time()
        
        audit_logger.log_security_event(
            event_type="API_REQUEST",
            severity="INFO",
            details={
                "request_id": request_id,
                "method": request.method,
                "path": str(request.url.path),
                "client_ip": request.client.host,
                "user_agent": request.headers.get("user-agent", "unknown")
            }
        )
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["X-Request-ID"] = request_id
        
        # Log response for audit
        processing_time = time.time() - start_time
        
        audit_logger.log_security_event(
            event_type="API_RESPONSE",
            severity="INFO",
            details={
                "request_id": request_id,
                "status_code": response.status_code,
                "processing_time": round(processing_time, 3),
                "response_size": len(response.body) if hasattr(response, 'body') else 0
            }
        )
        
        return response

class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for request validation and security checks"""
    
    def __init__(self, app):
        super().__init__(app)
        self.max_request_size = 10 * 1024 * 1024  # 10MB
        self.blocked_user_agents = [
            "sqlmap", "nikto", "nmap", "masscan", "zap"
        ]
        self.suspicious_patterns = [
            "union select", "drop table", "insert into", "delete from",
            "<script", "javascript:", "eval(", "alert("
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            audit_logger.log_security_event(
                event_type="REQUEST_TOO_LARGE",
                severity="WARNING",
                details={
                    "content_length": content_length,
                    "max_allowed": self.max_request_size,
                    "client_ip": request.client.host
                }
            )
            return JSONResponse(
                status_code=413,
                content={"detail": "Request entity too large"}
            )
        
        # Check user agent
        user_agent = request.headers.get("user-agent", "").lower()
        for blocked_agent in self.blocked_user_agents:
            if blocked_agent in user_agent:
                audit_logger.log_security_event(
                    event_type="BLOCKED_USER_AGENT",
                    severity="WARNING",
                    details={
                        "user_agent": user_agent,
                        "client_ip": request.client.host
                    }
                )
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Forbidden"}
                )
        
        # Check for suspicious patterns in URL
        url_path = str(request.url.path).lower()
        for pattern in self.suspicious_patterns:
            if pattern in url_path:
                audit_logger.log_security_event(
                    event_type="SUSPICIOUS_REQUEST_PATTERN",
                    severity="WARNING",
                    details={
                        "pattern": pattern,
                        "path": url_path,
                        "client_ip": request.client.host
                    }
                )
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Bad request"}
                )
        
        # Validate required headers for API endpoints
        if request.url.path.startswith("/api/"):
            if request.method in ["POST", "PUT", "PATCH"]:
                content_type = request.headers.get("content-type", "")
                if not content_type.startswith("application/json"):
                    return JSONResponse(
                        status_code=415,
                        content={"detail": "Unsupported media type"}
                    )
        
        return await call_next(request)

class APIVersionMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce API versioning"""
    
    def __init__(self, app):
        super().__init__(app)
        self.supported_versions = ["v1"]
        self.current_version = "v1"
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check API version for API endpoints
        if request.url.path.startswith("/api/"):
            # Extract version from path
            path_parts = request.url.path.split("/")
            if len(path_parts) >= 3:
                version = path_parts[2]  # /api/v1/...
                if version not in self.supported_versions:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "detail": f"Unsupported API version: {version}",
                            "supported_versions": self.supported_versions
                        }
                    )
            
            # Add version info to response
            response = await call_next(request)
            response.headers["X-API-Version"] = self.current_version
            return response
        
        return await call_next(request)

class ComplianceLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for compliance and audit logging"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Log financial data access
        if self._is_financial_endpoint(request.url.path):
            audit_logger.log_security_event(
                event_type="FINANCIAL_DATA_ACCESS",
                severity="INFO",
                details={
                    "endpoint": request.url.path,
                    "method": request.method,
                    "client_ip": request.client.host,
                    "timestamp": time.time()
                }
            )
        
        # Log authentication events
        if request.url.path.startswith("/api/v1/auth/"):
            audit_logger.log_security_event(
                event_type="AUTH_ENDPOINT_ACCESS",
                severity="INFO",
                details={
                    "endpoint": request.url.path,
                    "method": request.method,
                    "client_ip": request.client.host
                }
            )
        
        response = await call_next(request)
        
        # Log failed requests for security monitoring
        if response.status_code >= 400:
            severity = "WARNING" if response.status_code < 500 else "ERROR"
            audit_logger.log_security_event(
                event_type="REQUEST_FAILED",
                severity=severity,
                details={
                    "status_code": response.status_code,
                    "endpoint": request.url.path,
                    "method": request.method,
                    "client_ip": request.client.host
                }
            )
        
        return response
    
    def _is_financial_endpoint(self, path: str) -> bool:
        """Check if endpoint handles financial data"""
        financial_endpoints = [
            "/api/v1/transactions",
            "/api/v1/budgets",
            "/api/v1/bills",
            "/api/v1/accounts"
        ]
        
        for endpoint in financial_endpoints:
            if path.startswith(endpoint):
                return True
        
        return False

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for secure error handling"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Log error for debugging (internal only)
            security_logger.error(f"Unhandled error: {str(e)}")
            
            # Log security event
            audit_logger.log_security_event(
                event_type="UNHANDLED_ERROR",
                severity="ERROR",
                details={
                    "error_type": type(e).__name__,
                    "endpoint": request.url.path,
                    "method": request.method,
                    "client_ip": request.client.host
                }
            )
            
            # Return generic error response (don't expose internal details)
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "request_id": getattr(request.state, 'request_id', 'unknown')
                }
            )
