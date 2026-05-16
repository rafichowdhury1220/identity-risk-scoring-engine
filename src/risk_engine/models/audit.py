"""Audit logging models for compliance."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional
from uuid import uuid4


@dataclass(frozen=True)
class AuditLogEntry:
    """Immutable audit log entry for compliance."""
    entry_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Who
    actor_id: str = ""
    actor_type: str = "user"  # user, service, system
    
    # What
    action: str = ""
    action_category: str = ""  # authentication, authorization, data_access, config_change
    resource: str = ""
    
    # Result
    status: str = "success"  # success, failure
    error_message: Optional[str] = None
    
    # Context
    source_ip: str = ""
    user_agent: str = ""
    session_id: Optional[str] = None
    
    # Details (JSON for extensibility)
    details: Dict = field(default_factory=dict)
    
    # Integrity
    hash: Optional[str] = None  # For tamper detection
    
    def is_sensitive_action(self) -> bool:
        """Determine if this is a sensitive action requiring special handling."""
        sensitive_actions = {
            "authentication", "authorization_grant", "permission_change",
            "policy_modification", "user_creation", "user_deletion"
        }
        return self.action_category in sensitive_actions
