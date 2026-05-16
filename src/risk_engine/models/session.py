"""User session models."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass(frozen=True)
class Session:
    """User session token."""
    session_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = None
    last_activity: datetime = field(default_factory=datetime.utcnow)
    ip_address: str = ""
    user_agent: str = ""
    mfa_verified: bool = False
    
    def is_valid(self) -> bool:
        """Check if session is still valid."""
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True
