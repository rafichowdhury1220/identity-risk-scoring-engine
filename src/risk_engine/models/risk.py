"""Risk assessment models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4


class RiskLevel(Enum):
    """Risk assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AccessDecision(Enum):
    """Access control decision."""
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_MFA = "require_mfa"
    REQUIRE_ADDITIONAL_AUTH = "require_additional_auth"
    REQUIRE_APPROVAL = "require_approval"


@dataclass(frozen=True)
class RiskFactor:
    """Individual risk contributing factor."""
    name: str
    category: str  # behavioral, compliance, anomaly
    score: float  # 0.0 - 1.0
    weight: float  # Importance multiplier
    description: str
    recommendation: str


@dataclass(frozen=True)
class RiskScore:
    """Comprehensive risk assessment result."""
    assessment_id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Individual scores
    behavioral_score: float = 0.0  # 0.0 - 1.0
    compliance_score: float = 0.0  # 0.0 - 1.0
    anomaly_score: float = 0.0     # 0.0 - 1.0
    
    # Aggregate score
    total_score: float = 0.0  # 0.0 - 1.0
    
    # Risk classification
    risk_level: RiskLevel = RiskLevel.LOW
    
    # Details
    risk_factors: List[RiskFactor] = field(default_factory=list)
    
    # Recommendation
    recommendation: AccessDecision = AccessDecision.ALLOW
    confidence: float = 0.95  # Confidence in assessment
    
    # Context
    assessment_context: Dict = field(default_factory=dict)
    
    def is_acceptable(self, threshold: float = 0.4) -> bool:
        """Determine if risk is below acceptable threshold."""
        return self.total_score < threshold
    
    def get_top_risk_factors(self, n: int = 3) -> List[RiskFactor]:
        """Get the most significant risk factors."""
        return sorted(self.risk_factors, key=lambda f: f.score * f.weight, reverse=True)[:n]
