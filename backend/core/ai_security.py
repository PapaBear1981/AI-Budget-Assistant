"""
AI Security Controls and Privacy Protection
Implements comprehensive security for AI interactions with financial data
"""

import re
import hashlib
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging

from .security import get_audit_logger, DataClassification
from .database import db_manager, User as DBUser
from sqlmodel import Session, select

# AI security logging
ai_security_logger = logging.getLogger("ai_security")
audit_logger = get_audit_logger()

class AISecurityFilter:
    """Security layer for AI interactions with financial data"""
    
    def __init__(self):
        self.sensitive_patterns = self._load_sensitive_patterns()
        self.prompt_injection_patterns = self._load_injection_patterns()
        self.max_input_length = 10000  # Maximum input length
        self.max_output_length = 50000  # Maximum output length
    
    def _load_sensitive_patterns(self) -> List[re.Pattern]:
        """Load patterns for detecting sensitive financial data"""
        patterns = [
            # Account numbers (various formats)
            re.compile(r'\b\d{8,17}\b'),
            # SSN patterns
            re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            re.compile(r'\b\d{9}\b'),
            # Credit card patterns
            re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
            # Routing numbers
            re.compile(r'\b\d{9}\b'),
            # Phone numbers
            re.compile(r'\b\d{3}-\d{3}-\d{4}\b'),
            re.compile(r'\(\d{3}\)\s?\d{3}-\d{4}'),
            # Email addresses
            re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            # Addresses (basic pattern)
            re.compile(r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln)\b', re.IGNORECASE),
        ]
        return patterns
    
    def _load_injection_patterns(self) -> List[re.Pattern]:
        """Load patterns for detecting prompt injection attempts"""
        patterns = [
            # Direct instruction attempts
            re.compile(r'ignore\s+(?:previous|all|above|prior)\s+instructions?', re.IGNORECASE),
            re.compile(r'forget\s+(?:everything|all|previous)', re.IGNORECASE),
            re.compile(r'new\s+instructions?:', re.IGNORECASE),
            re.compile(r'system\s*:', re.IGNORECASE),
            re.compile(r'assistant\s*:', re.IGNORECASE),
            
            # Role manipulation
            re.compile(r'you\s+are\s+now', re.IGNORECASE),
            re.compile(r'act\s+as\s+(?:if|a)', re.IGNORECASE),
            re.compile(r'pretend\s+(?:to\s+be|you\s+are)', re.IGNORECASE),
            
            # Data extraction attempts
            re.compile(r'show\s+me\s+(?:all|your|the)\s+(?:data|information|records)', re.IGNORECASE),
            re.compile(r'list\s+(?:all|every)\s+(?:users?|accounts?|transactions?)', re.IGNORECASE),
            re.compile(r'export\s+(?:all|everything)', re.IGNORECASE),
            
            # System manipulation
            re.compile(r'execute\s+(?:command|code|script)', re.IGNORECASE),
            re.compile(r'run\s+(?:command|code|script)', re.IGNORECASE),
            re.compile(r'eval\s*\(', re.IGNORECASE),
        ]
        return patterns
    
    async def sanitize_input(self, user_input: str, user_id: str) -> Tuple[str, List[str]]:
        """Sanitize user input before AI processing"""
        warnings = []
        
        try:
            # Check input length
            if len(user_input) > self.max_input_length:
                user_input = user_input[:self.max_input_length]
                warnings.append("Input truncated due to length limit")
            
            # Check for prompt injection attempts
            injection_detected = False
            for pattern in self.prompt_injection_patterns:
                if pattern.search(user_input):
                    injection_detected = True
                    break
            
            if injection_detected:
                audit_logger.log_security_event(
                    event_type="PROMPT_INJECTION_DETECTED",
                    severity="WARNING",
                    details={
                        "user_id": user_id,
                        "input_preview": user_input[:100] + "..." if len(user_input) > 100 else user_input
                    }
                )
                warnings.append("Potential prompt injection detected")
                # For security, we'll sanitize the input
                user_input = self._sanitize_injection_attempt(user_input)
            
            # Mask sensitive data
            sanitized_input, masked_count = self._mask_sensitive_data(user_input)
            if masked_count > 0:
                warnings.append(f"Masked {masked_count} sensitive data patterns")
                
                audit_logger.log_security_event(
                    event_type="SENSITIVE_DATA_MASKED",
                    severity="INFO",
                    details={
                        "user_id": user_id,
                        "masked_patterns": masked_count
                    }
                )
            
            ai_security_logger.info(f"Input sanitized for user {user_id}: {len(warnings)} warnings")
            return sanitized_input, warnings
            
        except Exception as e:
            ai_security_logger.error(f"Input sanitization failed: {str(e)}")
            audit_logger.log_security_event(
                event_type="INPUT_SANITIZATION_FAILED",
                severity="ERROR",
                details={"user_id": user_id, "error": str(e)}
            )
            raise SecurityException("Input sanitization failed")
    
    def _sanitize_injection_attempt(self, text: str) -> str:
        """Sanitize potential prompt injection attempts"""
        # Replace injection patterns with safe alternatives
        for pattern in self.prompt_injection_patterns:
            text = pattern.sub("[FILTERED]", text)
        
        return text
    
    def _mask_sensitive_data(self, text: str) -> Tuple[str, int]:
        """Mask sensitive data patterns in text"""
        masked_count = 0
        
        for pattern in self.sensitive_patterns:
            matches = pattern.findall(text)
            if matches:
                masked_count += len(matches)
                text = pattern.sub("[REDACTED]", text)
        
        return text, masked_count
    
    async def filter_output(self, ai_response: str, user_id: str) -> Tuple[str, List[str]]:
        """Filter AI response for data leakage and inappropriate content"""
        warnings = []
        
        try:
            # Check output length
            if len(ai_response) > self.max_output_length:
                ai_response = ai_response[:self.max_output_length] + "\n[Response truncated]"
                warnings.append("Response truncated due to length limit")
            
            # Check for sensitive data leakage
            filtered_response, leaked_count = self._mask_sensitive_data(ai_response)
            if leaked_count > 0:
                warnings.append(f"Filtered {leaked_count} sensitive data leaks")
                
                audit_logger.log_security_event(
                    event_type="DATA_LEAKAGE_PREVENTED",
                    severity="WARNING",
                    details={
                        "user_id": user_id,
                        "leaked_patterns": leaked_count
                    }
                )
            
            # Check for inappropriate financial advice
            if self._contains_inappropriate_advice(filtered_response):
                warnings.append("Response contains disclaimer about financial advice")
                filtered_response += "\n\n⚠️ This is for informational purposes only and should not be considered professional financial advice."
            
            ai_security_logger.info(f"Output filtered for user {user_id}: {len(warnings)} warnings")
            return filtered_response, warnings
            
        except Exception as e:
            ai_security_logger.error(f"Output filtering failed: {str(e)}")
            audit_logger.log_security_event(
                event_type="OUTPUT_FILTERING_FAILED",
                severity="ERROR",
                details={"user_id": user_id, "error": str(e)}
            )
            raise SecurityException("Output filtering failed")
    
    def _contains_inappropriate_advice(self, text: str) -> bool:
        """Check if response contains financial advice that needs disclaimers"""
        advice_patterns = [
            re.compile(r'you\s+should\s+(?:invest|buy|sell)', re.IGNORECASE),
            re.compile(r'i\s+recommend\s+(?:investing|buying|selling)', re.IGNORECASE),
            re.compile(r'guaranteed\s+(?:returns?|profit)', re.IGNORECASE),
            re.compile(r'risk-free\s+investment', re.IGNORECASE),
        ]
        
        for pattern in advice_patterns:
            if pattern.search(text):
                return True
        
        return False

class PrivacyManager:
    """Manages privacy-preserving AI processing"""
    
    def __init__(self):
        self.local_processing_threshold = 0.8  # Sensitivity threshold for local processing
        self.anonymization_enabled = True
    
    async def should_use_local_processing(self, user_input: str, context: Dict[str, Any], user_id: Optional[str] = None) -> bool:
        """Determine if query should be processed locally for privacy

        Logic:
        - If a user_id is provided and the user explicitly opts out of cloud AI processing
          (ai_data_consent == False), force local processing.
        - Otherwise compute sensitivity score and compare with threshold.
        """
        try:
            # Check user consent (if available)
            if user_id:
                try:
                    session: Session = db_manager.get_session()
                    db_user = session.exec(select(DBUser).where(DBUser.id == user_id)).one_or_none()
                    session.close()
                    if db_user is not None:
                        consent = getattr(db_user, "ai_data_consent", True)
                        if consent is False:
                            audit_logger.log_security_event(
                                event_type="LOCAL_PROCESSING_FORCED_BY_CONSENT",
                                severity="INFO",
                                details={"user_id": user_id}
                            )
                            return True
                except Exception as e:
                    ai_security_logger.debug(f"Unable to read user consent from DB: {e}")
            
            # Calculate sensitivity score
            sensitivity_score = self._calculate_sensitivity_score(user_input, context)
            
            # Use local processing for highly sensitive queries
            use_local = sensitivity_score >= self.local_processing_threshold
            
            if use_local:
                audit_logger.log_security_event(
                    event_type="LOCAL_PROCESSING_SELECTED",
                    severity="INFO",
                    details={
                        "sensitivity_score": sensitivity_score,
                        "threshold": self.local_processing_threshold
                    }
                )
            
            return use_local
            
        except Exception as e:
            ai_security_logger.error(f"Local processing decision failed: {str(e)}")
            # Default to local processing for safety
            return True
    
    def _calculate_sensitivity_score(self, user_input: str, context: Dict[str, Any]) -> float:
        """Calculate sensitivity score for privacy decision"""
        score = 0.0
        
        # Check for sensitive keywords
        sensitive_keywords = [
            'account', 'balance', 'income', 'salary', 'debt', 'loan',
            'credit', 'ssn', 'social security', 'tax', 'investment'
        ]
        
        input_lower = user_input.lower()
        for keyword in sensitive_keywords:
            if keyword in input_lower:
                score += 0.2
        
        # Check context for sensitive data
        if context:
            if 'transaction_data' in context:
                score += 0.3
            if 'account_info' in context:
                score += 0.4
            if 'personal_info' in context:
                score += 0.5
        
        return min(score, 1.0)  # Cap at 1.0
    
    async def anonymize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize context data for cloud processing"""
        if not self.anonymization_enabled:
            return context
        
        try:
            anonymized_context = {}
            
            for key, value in context.items():
                if key in ['user_id', 'account_id', 'transaction_id']:
                    # Hash identifiers
                    anonymized_context[key] = self._hash_identifier(str(value))
                elif key == 'transaction_data':
                    # Anonymize transaction data
                    anonymized_context[key] = self._anonymize_transactions(value)
                elif key == 'personal_info':
                    # Skip personal info entirely
                    continue
                else:
                    # Keep other context as-is
                    anonymized_context[key] = value
            
            audit_logger.log_security_event(
                event_type="CONTEXT_ANONYMIZED",
                severity="INFO",
                details={"original_keys": list(context.keys()), "anonymized_keys": list(anonymized_context.keys())}
            )
            
            return anonymized_context
            
        except Exception as e:
            ai_security_logger.error(f"Context anonymization failed: {str(e)}")
            # Return empty context for safety
            return {}
    
    def _hash_identifier(self, identifier: str) -> str:
        """Hash identifier for anonymization"""
        return hashlib.sha256(identifier.encode()).hexdigest()[:16]
    
    def _anonymize_transactions(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Anonymize transaction data"""
        anonymized = []
        
        for transaction in transactions:
            anon_transaction = {
                'amount': transaction.get('amount'),
                'category': transaction.get('category'),
                'date': transaction.get('date'),
                'type': transaction.get('type')
            }
            # Remove description and other identifying info
            anonymized.append(anon_transaction)
        
        return anonymized

class SecurityException(Exception):
    """Custom exception for AI security-related errors"""
    pass

# Global instances
ai_security_filter = AISecurityFilter()
privacy_manager = PrivacyManager()

def get_ai_security_filter() -> AISecurityFilter:
    """Get global AI security filter instance"""
    return ai_security_filter

def get_privacy_manager() -> PrivacyManager:
    """Get global privacy manager instance"""
    return privacy_manager
