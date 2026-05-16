"""Risk Calculator - Main risk assessment engine."""

from typing import Dict, List

from risk_engine.config import get_config
from risk_engine.core.strategies import (
    BehavioralRiskStrategy,
    ComplianceRiskStrategy,
    AnomalyRiskStrategy,
)
from risk_engine.models import (
    User,
    RiskScore,
    RiskFactor,
    RiskLevel,
    AccessDecision,
)


class RiskCalculator:
    """
    Main risk calculation engine combining multiple risk strategies.
    
    Demonstrates the Strategy pattern for extensibility.
    Weighted aggregation allows tuning of risk factor importance.
    """
    
    def __init__(self):
        """Initialize risk calculator with default strategies."""
        self.config = get_config()
        self.behavioral_strategy = BehavioralRiskStrategy()
        self.compliance_strategy = ComplianceRiskStrategy()
        self.anomaly_strategy = AnomalyRiskStrategy()
    
    def calculate_risk(
        self,
        user: User,
        access_history: List[Dict] = None,
        access_patterns: Dict = None
    ) -> RiskScore:
        """
        Calculate comprehensive risk score for a user.
        
        Args:
            user: User to assess
            access_history: Historical access records
            access_patterns: Current behavioral patterns
        
        Returns:
            RiskScore: Comprehensive assessment with factors and recommendation
        """
        # Calculate individual risk dimensions
        behavioral_score = self.behavioral_strategy.calculate(user, access_history)
        compliance_score = self.compliance_strategy.calculate(user)
        anomaly_score = self.anomaly_strategy.calculate(user, access_patterns)
        
        # Aggregate with weights (must sum to 1.0)
        total_score = (
            behavioral_score * self.config.risk_scoring.behavioral_weight +
            compliance_score * self.config.risk_scoring.compliance_weight +
            anomaly_score * self.config.risk_scoring.anomaly_weight
        )
        
        # Determine risk level
        if total_score < self.config.risk_scoring.low_risk_threshold:
            risk_level = RiskLevel.LOW
        elif total_score < self.config.risk_scoring.medium_risk_threshold:
            risk_level = RiskLevel.MEDIUM
        elif total_score < self.config.risk_scoring.high_risk_threshold:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.CRITICAL
        
        # Determine access recommendation
        recommendation = self._get_recommendation(total_score)
        
        # Build risk factors for transparency
        risk_factors = self._build_risk_factors(
            user,
            behavioral_score,
            compliance_score,
            anomaly_score
        )
        
        return RiskScore(
            user_id=user.user_id,
            behavioral_score=behavioral_score,
            compliance_score=compliance_score,
            anomaly_score=anomaly_score,
            total_score=total_score,
            risk_level=risk_level,
            risk_factors=risk_factors,
            recommendation=recommendation,
            confidence=0.95,
        )
    
    def _get_recommendation(self, total_score: float) -> AccessDecision:
        """Get access recommendation based on risk score."""
        if total_score < self.config.risk_scoring.low_risk_threshold:
            return AccessDecision.ALLOW
        elif total_score < self.config.risk_scoring.medium_risk_threshold:
            return AccessDecision.REQUIRE_MFA
        elif total_score < self.config.risk_scoring.high_risk_threshold:
            return AccessDecision.REQUIRE_ADDITIONAL_AUTH
        else:
            return AccessDecision.DENY
    
    def _build_risk_factors(
        self,
        user: User,
        behavioral: float,
        compliance: float,
        anomaly: float
    ) -> List[RiskFactor]:
        """Build list of individual risk factors for transparency."""
        factors = []
        
        if behavioral > 0.1:
            factors.append(RiskFactor(
                name="off_hours_access",
                category="behavioral",
                score=behavioral,
                weight=self.config.risk_scoring.behavioral_weight,
                description="Access attempted outside business hours",
                recommendation="Verify access is legitimate"
            ))
        
        if compliance > 0.1:
            factors.append(RiskFactor(
                name="compliance_violation",
                category="compliance",
                score=compliance,
                weight=self.config.risk_scoring.compliance_weight,
                description="User not compliant with security policies",
                recommendation="Enable MFA or update account settings"
            ))
        
        if anomaly > 0.1:
            factors.append(RiskFactor(
                name="anomalous_pattern",
                category="anomaly",
                score=anomaly,
                weight=self.config.risk_scoring.anomaly_weight,
                description="Unusual access pattern detected",
                recommendation="Review recent access history"
            ))
        
        return factors
