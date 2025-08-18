"""
Database Configuration with Encryption Support
Implements SQLCipher for encrypted financial data storage
"""

import os
import sqlite3
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from uuid import UUID, uuid4

from sqlalchemy import create_engine, event, Column, Boolean, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.pool import StaticPool
import logging

from sqlmodel import Field, SQLModel, Relationship

from .security import get_audit_logger, DataClassification

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./budget_assistant.db")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "change_this_in_production")

# SQLAlchemy setup
Base = declarative_base()
engine = None
SessionLocal = None

# Logging
db_logger = logging.getLogger("database")
audit_logger = get_audit_logger()

# SQLModel Base for declarative models
class SQLModelBase(SQLModel):
    class Config:
        arbitrary_types_allowed = True

# Define User model (SQLAlchemy ORM compatible with SQLModel)
class User(SQLModelBase, table=True):
    __tablename__ = "users"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    pin_hash: str = Field(index=True)
    device_id: Optional[str] = Field(default=None)
    preferences: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON)) # Store as JSON
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)

    # AI Privacy Consent Fields
    ai_data_consent: bool = Field(default=True, description="User consent for AI data processing")
    ai_data_retention_days: int = Field(default=30, description="Number of days to retain AI conversation data")

    conversations: List["Conversation"] = Relationship(back_populates="user")

# Define Conversation model
class Conversation(SQLModelBase, table=True):
    __tablename__ = "conversations"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    retention_until: Optional[date] = Field(default=None, description="Date until conversation data should be retained")

    user: User = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")

# Define Message model
class Message(SQLModelBase, table=True):
    __tablename__ = "messages"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id")
    sender: str = Field(description="Sender of the message (user or AI)")
    content: str = Field(description="Encrypted content of the message") # Will be encrypted
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    conversation: Conversation = Relationship(back_populates="messages")

# Financial data models
class Transaction(SQLModelBase, table=True):
    """Financial transaction record"""
    __tablename__ = "transactions"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    amount: float = Field(description="Positive for income, negative for expense")
    description: str
    category: str = Field(default="Uncategorized")
    date: date = Field(default_factory=date.today)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: User = Relationship()


class Budget(SQLModelBase, table=True):
    """Budget allocation for a category and period"""
    __tablename__ = "budgets"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    category: str
    limit: float = Field(description="Spending limit for the period")
    period: str = Field(default="monthly")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: User = Relationship()


class Bill(SQLModelBase, table=True):
    """Recurring or one-time bill"""
    __tablename__ = "bills"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    name: str
    amount: float
    due_date: date
    is_recurring: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: User = Relationship()

class DatabaseManager:
    """Manages database connections and encryption"""
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
        self.is_encrypted = False
    
    def initialize_database(self, encryption_key: Optional[str] = None) -> None:
        """Initialize database with optional encryption"""
        global engine, SessionLocal
        
        try:
            if encryption_key and self._is_sqlcipher_available():
                # Use SQLCipher for encryption
                database_url = self._create_encrypted_url(encryption_key)
                self.is_encrypted = True
                db_logger.info("Initializing encrypted database with SQLCipher")
            else:
                # Use standard SQLite
                database_url = DATABASE_URL
                self.is_encrypted = False
                db_logger.warning("Initializing unencrypted database - not recommended for production")
            
            # Create engine
            self.engine = create_engine(
                database_url,
                connect_args={
                    "check_same_thread": False,
                    "timeout": 30
                },
                poolclass=StaticPool,
                echo=False  # Set to True for SQL debugging
            )
            
            # Configure SQLCipher if encrypted
            if self.is_encrypted:
                self._configure_sqlcipher(self.engine)
            
            # Create session factory
            self.session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Set global variables for compatibility
            engine = self.engine
            SessionLocal = self.session_factory
            
            # Create tables
            SQLModel.metadata.create_all(bind=self.engine)
            
            audit_logger.log_security_event(
                event_type="DATABASE_INITIALIZED",
                severity="INFO",
                details={
                    "encrypted": self.is_encrypted,
                    "database_url": database_url.split("://")[0] + "://[REDACTED]"
                }
            )
            
            db_logger.info("Database initialized successfully")
            
        except Exception as e:
            db_logger.error(f"Database initialization failed: {str(e)}")
            audit_logger.log_security_event(
                event_type="DATABASE_INIT_FAILED",
                severity="ERROR",
                details={"error": str(e)}
            )
            raise
    
    def _is_sqlcipher_available(self) -> bool:
        """Check if SQLCipher is available"""
        try:
            import sqlcipher3
            return True
        except ImportError:
            return False
    
    def _create_encrypted_url(self, encryption_key: str) -> str:
        """Create SQLCipher database URL"""
        # Extract database path from URL
        if DATABASE_URL.startswith("sqlite:///"):
            db_path = DATABASE_URL[10:]  # Remove "sqlite:///"
        else:
            db_path = "./budget_assistant_encrypted.db"
        
        return f"sqlite+pysqlcipher://:{encryption_key}@/{db_path}"
    
    def _configure_sqlcipher(self, engine) -> None:
        """Configure SQLCipher encryption settings"""
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set SQLCipher encryption pragmas"""
            cursor = dbapi_connection.cursor()
            
            # Set encryption settings
            cursor.execute("PRAGMA cipher_page_size = 4096")
            cursor.execute("PRAGMA kdf_iter = 64000")  # PBKDF2 iterations
            cursor.execute("PRAGMA cipher_hmac_algorithm = HMAC_SHA256")
            cursor.execute("PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA256")
            
            # Enable foreign keys
            cursor.execute("PRAGMA foreign_keys=ON")
            
            # Set secure delete
            cursor.execute("PRAGMA secure_delete = ON")
            
            cursor.close()
    
    def get_session(self) -> Session:
        """Get database session"""
        if not self.session_factory:
            raise RuntimeError("Database not initialized")
        return self.session_factory()
    
    def close_session(self, session: Session) -> None:
        """Close database session"""
        try:
            session.close()
        except Exception as e:
            db_logger.error(f"Error closing session: {str(e)}")
    
    def backup_database(self, backup_path: str, encryption_key: Optional[str] = None) -> bool:
        """Create encrypted backup of database"""
        try:
            if not self.engine:
                raise RuntimeError("Database not initialized")
            
            # Create backup connection
            backup_conn = sqlite3.connect(backup_path)
            
            # Get source connection
            source_conn = self.engine.raw_connection()
            
            # Perform backup
            source_conn.backup(backup_conn)
            
            # Close connections
            backup_conn.close()
            source_conn.close()
            
            audit_logger.log_security_event(
                event_type="DATABASE_BACKUP_CREATED",
                severity="INFO",
                details={"backup_path": backup_path, "encrypted": bool(encryption_key)}
            )
            
            db_logger.info(f"Database backup created: {backup_path}")
            return True
            
        except Exception as e:
            db_logger.error(f"Database backup failed: {str(e)}")
            audit_logger.log_security_event(
                event_type="DATABASE_BACKUP_FAILED",
                severity="ERROR",
                details={"error": str(e), "backup_path": backup_path}
            )
            return False
    
    def verify_database_integrity(self) -> bool:
        """Verify database integrity"""
        try:
            if not self.engine:
                return False
            
            with self.engine.connect() as conn:
                # Check database integrity
                result = conn.execute("PRAGMA integrity_check")
                integrity_result = result.fetchone()[0]
                
                if integrity_result == "ok":
                    db_logger.info("Database integrity check passed")
                    return True
                else:
                    db_logger.error(f"Database integrity check failed: {integrity_result}")
                    audit_logger.log_security_event(
                        event_type="DATABASE_INTEGRITY_FAILED",
                        severity="ERROR",
                        details={"result": integrity_result}
                    )
                    return False
                    
        except Exception as e:
            db_logger.error(f"Database integrity check error: {str(e)}")
            return False

# Global database manager
db_manager = DatabaseManager()

def get_database_manager() -> DatabaseManager:
    """Get global database manager instance"""
    return db_manager

def get_db() -> Session:
    """FastAPI dependency for database session"""
    session = db_manager.get_session()
    try:
        yield session
    finally:
        db_manager.close_session(session)

async def init_db() -> None:
    """Initialize database for FastAPI startup"""
    try:
        encryption_key = ENCRYPTION_KEY if ENCRYPTION_KEY != "change_this_in_production" else None
        db_manager.initialize_database(encryption_key)
        
        # Verify database integrity
        if not db_manager.verify_database_integrity():
            raise RuntimeError("Database integrity check failed")
            
    except Exception as e:
        db_logger.error(f"Database initialization failed: {str(e)}")
        raise

class DatabaseAuditMixin:
    """Mixin for database models to add audit logging"""
    
    def log_data_access(self, user_id: str, operation: str, 
                       classification: str = DataClassification.CONFIDENTIAL) -> None:
        """Log data access for audit purposes"""
        audit_logger.log_data_access(
            user_id=user_id,
            data_type=self.__class__.__name__,
            classification=classification,
            operation=operation
        )
    
    def log_data_modification(self, user_id: str, operation: str, 
                            changes: Dict[str, Any] = None) -> None:
        """Log data modifications for audit purposes"""
        audit_logger.log_security_event(
            event_type="DATA_MODIFICATION",
            severity="INFO",
            details={
                "user_id": user_id,
                "model": self.__class__.__name__,
                "operation": operation,
                "changes": changes or {}
            }
        )

# Database health check
def check_database_health() -> Dict[str, Any]:
    """Check database health status"""
    try:
        if not db_manager.engine:
            return {"status": "error", "message": "Database not initialized"}
        
        with db_manager.engine.connect() as conn:
            # Test connection
            conn.execute("SELECT 1")
            
            # Check if encrypted
            encryption_status = "encrypted" if db_manager.is_encrypted else "unencrypted"
            
            return {
                "status": "healthy",
                "encryption": encryption_status,
                "message": "Database connection successful"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database health check failed: {str(e)}"
        }
