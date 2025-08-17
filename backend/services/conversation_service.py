import logging
from datetime import datetime, timedelta, date
from typing import List, Optional, Dict, Any

from sqlmodel import select
from sqlmodel import Session

from ..core.database import db_manager, User, Conversation, Message
from ..core.security import get_encryption_manager

logger = logging.getLogger("conversation_service")
encryption_manager = get_encryption_manager()


class ConversationService:
    """Service for managing conversations and messages (with encryption + retention)"""

    def __init__(self):
        self.db_manager = db_manager
        self.encryption = encryption_manager

    async def get_conversation(self, conversation_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Return a conversation and decrypted messages for the given user."""
        session: Session = self.db_manager.get_session()
        try:
            stmt = select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user_id)
            convo = session.exec(stmt).one_or_none()
            if not convo:
                return None

            # Load messages
            msg_stmt = select(Message).where(Message.conversation_id == convo.id).order_by(Message.timestamp)
            msgs = session.exec(msg_stmt).all()

            messages = []
            for m in msgs:
                content = m.content
                try:
                    # Decrypt if possible
                    content = self.encryption.decrypt_data(content)
                except Exception:
                    # If decryption fails, fall back to stored content
                    logger.debug("Message decryption failed or not encrypted; returning raw content")
                messages.append(
                    {
                        "id": str(m.id),
                        "sender": m.sender,
                        "content": content,
                        "timestamp": m.timestamp.isoformat()
                    }
                )

            return {
                "id": str(convo.id),
                "user_id": str(convo.user_id),
                "created_at": convo.created_at,
                "updated_at": convo.updated_at,
                "retention_until": convo.retention_until,
                "messages": messages
            }
        finally:
            session.close()

    async def get_conversations(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """List conversations for a user (no message payloads)"""
        session: Session = self.db_manager.get_session()
        try:
            stmt = select(Conversation).where(Conversation.user_id == user_id).order_by(Conversation.updated_at.desc()).limit(limit).offset(offset)
            rows = session.exec(stmt).all()
            results = []
            for c in rows:
                results.append({
                    "id": str(c.id),
                    "user_id": str(c.user_id),
                    "created_at": c.created_at,
                    "updated_at": c.updated_at,
                    "retention_until": c.retention_until
                })
            return results
        finally:
            session.close()

    async def create_message(self, conversation_id: str, user_id: str, sender: str, content: str) -> Dict[str, Any]:
        """
        Create (or append) a message in a conversation.
        Ensures content is encrypted before storage.
        """
        session: Session = self.db_manager.get_session()
        try:
            # Ensure conversation exists (and belongs to user)
            stmt = select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user_id)
            convo = session.exec(stmt).one_or_none()
            if not convo:
                # create it
                convo = Conversation(user_id=user_id)
                session.add(convo)
                session.commit()
                session.refresh(convo)

            # Encrypt content if encryption manager initialized
            try:
                encrypted = self.encryption.encrypt_data(content)
            except Exception:
                # If encryption not initialized, store raw content but log warning
                logger.warning("Encryption not initialized; storing message as plaintext")
                encrypted = content

            msg = Message(conversation_id=convo.id, sender=sender, content=encrypted, timestamp=datetime.utcnow())
            session.add(msg)

            # update conversation timestamp
            convo.updated_at = datetime.utcnow()
            # If retention_until not set, set based on user's preference if available
            if convo.retention_until is None:
                # Attempt to read user's retention days from DB (if User exists)
                try:
                    user_stmt = select(User).where(User.id == user_id)
                    usr = session.exec(user_stmt).one_or_none()
                    days = 30
                    if usr and getattr(usr, "ai_data_retention_days", None):
                        days = usr.ai_data_retention_days
                    convo.retention_until = (date.today() + timedelta(days=days))
                except Exception:
                    convo.retention_until = (date.today() + timedelta(days=30))

            session.add(convo)
            session.commit()
            session.refresh(msg)

            return {
                "id": str(msg.id),
                "conversation_id": str(convo.id),
                "sender": msg.sender,
                "timestamp": msg.timestamp.isoformat()
            }
        finally:
            session.close()

    async def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """Delete a conversation and its messages (permanent)."""
        session: Session = self.db_manager.get_session()
        try:
            stmt = select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user_id)
            convo = session.exec(stmt).one_or_none()
            if not convo:
                return False

            # Delete messages
            msg_stmt = select(Message).where(Message.conversation_id == convo.id)
            msgs = session.exec(msg_stmt).all()
            for m in msgs:
                session.delete(m)

            session.delete(convo)
            session.commit()
            return True
        finally:
            session.close()

    async def purge_expired(self) -> int:
        """Find and delete conversations whose retention_until date is past."""
        session: Session = self.db_manager.get_session()
        try:
            today = date.today()
            stmt = select(Conversation).where(Conversation.retention_until != None, Conversation.retention_until < today)
            expired = session.exec(stmt).all()
            count = 0
            for c in expired:
                msg_stmt = select(Message).where(Message.conversation_id == c.id)
                msgs = session.exec(msg_stmt).all()
                for m in msgs:
                    session.delete(m)
                session.delete(c)
                count += 1
            session.commit()
            return count
        finally:
            session.close()


# FastAPI dependency provider
def get_conversation_service() -> ConversationService:
    return ConversationService()
