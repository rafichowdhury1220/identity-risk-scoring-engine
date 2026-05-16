"""User identity models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Set
from uuid import uuid4


class UserRole(Enum):
    """User roles in the system."""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    ENGINEER = "engineer"
    USER = "user"
    GUEST = "guest"


class ClearanceLevel(Enum):
    """Security clearance levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"
    TOP_SECRET = "top_secret"


@dataclass(frozen=True)
class User:
    """Immutable user identity model."""
    user_id: str
    username: str
    email: str
    roles: Set[UserRole]
    clearance_level: ClearanceLevel
    mfa_enabled: bool
    last_login: Optional[datetime]
    creation_date: datetime
    is_active: bool = True
    department: Optional[str] = None
    manager_id: Optional[str] = None
    
    def has_role(self, role: UserRole) -> bool:
        """Check if user has a specific role."""
        return role in self.roles
    
    def is_admin(self) -> bool:
        """Check if user has admin or higher role."""
        return self.has_role(UserRole.ADMIN) or self.has_role(UserRole.SUPER_ADMIN)
    
    def days_since_last_login(self) -> Optional[int]:
        """Calculate days since last login."""
        if not self.last_login:
            return None
        return (datetime.utcnow() - self.last_login).days


@dataclass(frozen=True)
class AccessRecord:
    """Immutable access attempt record."""
    record_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    action: str = ""
    resource: str = ""
    source_ip: str = ""
    user_agent: str = ""
    status: str = "unknown"  # success, denied, mfa_required
    reason: Optional[str] = None
    risk_score: float = 0.0
