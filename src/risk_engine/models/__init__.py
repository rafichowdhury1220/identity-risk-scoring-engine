"""
Data models for Identity Risk Scoring Engine.

Demonstrates immutable, well-typed data models following SOLID principles.
"""

# User models
from risk_engine.models.user import User, UserRole, ClearanceLevel, AccessRecord

# Risk models
from risk_engine.models.risk import RiskScore, RiskLevel, RiskFactor, AccessDecision

# Policy models
from risk_engine.models.policy import SecurityPolicy, PolicyContext, PolicyDecision, Rule

# Audit models
from risk_engine.models.audit import AuditLogEntry

# Session models
from risk_engine.models.session import Session

__all__ = [
    # User models
    "User",
    "UserRole",
    "ClearanceLevel",
    "AccessRecord",
    # Risk models
    "RiskScore",
    "RiskLevel",
    "RiskFactor",
    "AccessDecision",
    # Policy models
    "SecurityPolicy",
    "PolicyContext",
    "PolicyDecision",
    "Rule",
    # Audit models
    "AuditLogEntry",
    # Session models
    "Session",
]
    
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return not self.is_valid()
