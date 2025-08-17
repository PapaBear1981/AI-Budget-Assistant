"""
Security Architecture Foundation
Implements comprehensive security controls for financial data protection
Following PCI-DSS, GDPR, and CCPA compliance requirements
"""

import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from passlib.context import CryptContext
from jose import JWTError, jwt
import base64
import logging

# Configure security logging
security_logger = logging.getLogger("security")
security_logger.setLevel(logging.INFO)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
ENCRYPTION_KEY_SALT = os.getenv("SECURITY_SALT", "default_salt_change_in_production").encode()

class DataClassification:
    """Data classification levels for financial data protection"""
    PUBLIC = "public"           # Level 1: General budget categories
    INTERNAL = "internal"       # Level 2: Aggregated spending patterns
    CONFIDENTIAL = "confidential"  # Level 3: Account balances, transactions
    RESTRICTED = "restricted"   # Level 4: Auth credentials, encryption keys

class EncryptionManager:
    """Manages encryption/decryption for sensitive financial data"""
    
    def __init__(self):
        self._encryption_key = None
        self._fernet = None
    
    def initialize_encryption(self, user_pin: str) -> None:
        """Initialize encryption with user-derived key"""
        try:
            # Derive encryption key from user PIN using PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=ENCRYPTION_KEY_SALT,
                iterations=100000,  # NIST recommended minimum
            )
            key = base64.urlsafe_b64encode(kdf.derive(user_pin.encode()))
            self._encryption_key = key
            self._fernet = Fernet(key)
            
            security_logger.info("Encryption initialized successfully")
        except Exception as e:
            security_logger.error(f"Encryption initialization failed: {str(e)}")
            raise SecurityException("Failed to initialize encryption")
    
    def encrypt_data(self, data: str, classification: str = DataClassification.CONFIDENTIAL) -> str:
        """Encrypt sensitive data based on classification level"""
        if not self._fernet:
            raise SecurityException("Encryption not initialized")
        
        try:
            if classification in [DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED]:
                encrypted_data = self._fernet.encrypt(data.encode())
                security_logger.info(f"Data encrypted with classification: {classification}")
                return base64.urlsafe_b64encode(encrypted_data).decode()
            else:
                # Lower classification levels don't require encryption
                return data
        except Exception as e:
            security_logger.error(f"Encryption failed: {str(e)}")
            raise SecurityException("Data encryption failed")
    
    def decrypt_data(self, encrypted_data: str, classification: str = DataClassification.CONFIDENTIAL) -> str:
        """Decrypt sensitive data"""
        if not self._fernet:
            raise SecurityException("Encryption not initialized")
        
        try:
            if classification in [DataClassification.CONFIDENTIAL, DataClassification.RESTRICTED]:
                decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
                decrypted_data = self._fernet.decrypt(decoded_data)
                return decrypted_data.decode()
            else:
                return encrypted_data
        except Exception as e:
            security_logger.error(f"Decryption failed: {str(e)}")
            raise SecurityException("Data decryption failed")

class AuthenticationManager:
    """Manages user authentication with PIN/biometric support"""
    
    def __init__(self):
        self.failed_attempts: Dict[str, int] = {}
        self.lockout_times: Dict[str, datetime] = {}
    
    def hash_pin(self, pin: str) -> str:
        """Hash user PIN securely"""
        return pwd_context.hash(pin)
    
    def verify_pin(self, pin: str, hashed_pin: str) -> bool:
        """Verify user PIN against hash"""
        return pwd_context.verify(pin, hashed_pin)
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        security_logger.info(f"Access token created for user: {data.get('sub', 'unknown')}")
        return token
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        security_logger.info(f"Refresh token created for user: {data.get('sub', 'unknown')}")
        return token
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError as e:
            security_logger.warning(f"Token verification failed: {str(e)}")
            return None
    
    def check_account_lockout(self, user_id: str) -> bool:
        """Check if account is locked due to failed attempts"""
        if user_id in self.lockout_times:
            lockout_time = self.lockout_times[user_id]
            if datetime.utcnow() < lockout_time:
                return True
            else:
                # Lockout period expired
                del self.lockout_times[user_id]
                self.failed_attempts[user_id] = 0
        return False
    
    def record_failed_attempt(self, user_id: str) -> None:
        """Record failed authentication attempt"""
        self.failed_attempts[user_id] = self.failed_attempts.get(user_id, 0) + 1
        
        # Progressive lockout: 5 attempts = 5 min, 10 attempts = 30 min
        if self.failed_attempts[user_id] >= 10:
            self.lockout_times[user_id] = datetime.utcnow() + timedelta(minutes=30)
            security_logger.warning(f"Account locked for 30 minutes: {user_id}")
        elif self.failed_attempts[user_id] >= 5:
            self.lockout_times[user_id] = datetime.utcnow() + timedelta(minutes=5)
            security_logger.warning(f"Account locked for 5 minutes: {user_id}")
    
    def reset_failed_attempts(self, user_id: str) -> None:
        """Reset failed attempts after successful authentication"""
        if user_id in self.failed_attempts:
            del self.failed_attempts[user_id]
        if user_id in self.lockout_times:
            del self.lockout_times[user_id]

class SecurityAuditLogger:
    """Comprehensive security audit logging"""
    
    def __init__(self):
        self.audit_logger = logging.getLogger("security_audit")
        self.audit_logger.setLevel(logging.INFO)
        
        # Create audit log handler (ensure directory exists)
        audit_log_path = os.path.join(os.getcwd(), os.getenv("AUDIT_LOG_PATH", "logs/security_audit.log"))
        # Ensure the audit log directory exists to prevent FileHandler errors
        try:
            os.makedirs(os.path.dirname(audit_log_path), exist_ok=True)
        except Exception:
            # If directory creation fails, fall back to current working directory file
            audit_log_path = os.path.join(os.getcwd(), "logs", "security_audit.log")
            os.makedirs(os.path.dirname(audit_log_path), exist_ok=True)

        audit_handler = logging.FileHandler(audit_log_path)
        audit_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        audit_handler.setFormatter(audit_formatter)
        self.audit_logger.addHandler(audit_handler)
    
    def log_authentication_event(self, user_id: str, event_type: str, 
                                success: bool, details: Dict[str, Any] = None) -> None:
        """Log authentication events"""
        event_data = {
            "user_id": user_id,
            "event_type": event_type,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }
        
        level = logging.INFO if success else logging.WARNING
        self.audit_logger.log(level, f"AUTH_EVENT: {event_data}")
    
    def log_data_access(self, user_id: str, data_type: str, 
                       classification: str, operation: str) -> None:
        """Log data access events"""
        event_data = {
            "user_id": user_id,
            "data_type": data_type,
            "classification": classification,
            "operation": operation,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.audit_logger.info(f"DATA_ACCESS: {event_data}")
    
    def log_security_event(self, event_type: str, severity: str, 
                          details: Dict[str, Any]) -> None:
        """Log general security events"""
        event_data = {
            "event_type": event_type,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details
        }
        
        level = getattr(logging, severity.upper(), logging.INFO)
        self.audit_logger.log(level, f"SECURITY_EVENT: {event_data}")

class SecurityException(Exception):
    """Custom exception for security-related errors"""
    pass

# Global security instances
encryption_manager = EncryptionManager()
auth_manager = AuthenticationManager()
audit_logger = SecurityAuditLogger()

def get_encryption_manager() -> EncryptionManager:
    """Get global encryption manager instance"""
    return encryption_manager

def get_auth_manager() -> AuthenticationManager:
    """Get global authentication manager instance"""
    return auth_manager

def get_audit_logger() -> SecurityAuditLogger:
    """Get global security audit logger instance"""
    return audit_logger
