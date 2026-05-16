"""Main package initialization."""

from risk_engine.models import (
    User,
    UserRole,
    ClearanceLevel,
    RiskScore,
    RiskLevel,
    AccessDecision,
    SecurityPolicy,
    Rule,
    PolicyContext,
    PolicyDecision,
    AuditLogEntry,
    Session,
)

from risk_engine.core import (
    RiskCalculator,
    BehavioralRiskStrategy,
    ComplianceRiskStrategy,
    AnomalyRiskStrategy,
)

from risk_engine.iam import (
    Authenticator,
    Authorizer,
    AuditLogger,
)

from risk_engine.config import (
    Config,
    Environment,
    LogLevel,
    get_config,
    set_config,
)

__version__ = "1.0.0"
__author__ = "Priya Arora"

__all__ = [
    # Models
    "User",
    "UserRole",
    "ClearanceLevel",
    "RiskScore",
    "RiskLevel",
    "AccessDecision",
    "SecurityPolicy",
    "Rule",
    "PolicyContext",
    "PolicyDecision",
    "AuditLogEntry",
    "Session",
    # Core
    "RiskCalculator",
    "BehavioralRiskStrategy",
    "ComplianceRiskStrategy",
    "AnomalyRiskStrategy",
    # IAM
    "Authenticator",
    "Authorizer",
    "AuditLogger",
    # Configuration
    "Config",
    "Environment",
    "LogLevel",
    "get_config",
    "set_config",
]
