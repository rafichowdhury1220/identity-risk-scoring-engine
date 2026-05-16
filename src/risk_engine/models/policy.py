"""Policy and rule models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

from risk_engine.models.user import User
from risk_engine.models.risk import AccessDecision


@dataclass(frozen=True)
class Rule:
    """Policy rule definition."""
    rule_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    condition: Optional[Callable] = None  # Callable[[PolicyContext], bool]
    action: AccessDecision = AccessDecision.ALLOW
    priority: int = 100
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""


@dataclass(frozen=True)
class SecurityPolicy:
    """Security policy with multiple rules."""
    policy_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    rules: List[Rule] = field(default_factory=list)
    version: str = "1.0"
    enabled: bool = True
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_modified: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class PolicyContext:
    """Context for policy evaluation."""
    user: User
    action: str
    resource: str
    source_ip: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    mfa_verified: bool = False
    session_age_minutes: int = 0
    concurrent_sessions: int = 1
    
    # Custom attributes
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PolicyDecision:
    """Result of policy evaluation."""
    decision: AccessDecision = AccessDecision.ALLOW
    reason: str = ""
    applied_policies: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
