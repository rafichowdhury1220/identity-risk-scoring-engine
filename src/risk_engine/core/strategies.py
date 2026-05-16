"""Risk scoring strategies for multi-dimensional assessment."""

from datetime import datetime, timedelta
from typing import Dict, List

from risk_engine.config import get_config
from risk_engine.models import User


class BehavioralRiskStrategy:
    """Calculates risk based on user behavior patterns."""
    
    def calculate(self, user: User, access_history: List[Dict] = None) -> float:
        """
        Calculate behavioral risk score (0.0 - 1.0).
        
        Factors:
        - Time of access (off-hours = higher risk)
        - Geographic patterns (impossible travel = higher risk)
        - Access pattern deviation (unusual activity = higher risk)
        - Account age (newer accounts = higher risk)
        """
        if access_history is None:
            access_history = []
        
        score = 0.0
        
        # Off-hours access
        now = datetime.utcnow()
        config = get_config()
        if now.hour < config.risk_scoring.hours_of_operation_start or \
           now.hour >= config.risk_scoring.hours_of_operation_end:
            score += 0.15
        
        # Account age risk (new accounts are riskier)
        days_old = (now - user.creation_date).days
        if days_old < 30:
            score += 0.20
        elif days_old < 90:
            score += 0.10
        
        # Last login recency (inactive accounts are riskier)
        if user.last_login:
            days_since = (now - user.last_login).days
            if days_since > 90:
                score += 0.15
        else:
            score += 0.25  # Never logged in before
        
        # Geographic analysis (if multiple access records)
        if len(access_history) >= 2:
            score += self._calculate_geographic_risk(access_history)
        
        return min(score, 1.0)
    
    def _calculate_geographic_risk(self, access_history: List[Dict]) -> float:
        """Calculate risk based on impossible travel."""
        if len(access_history) < 2:
            return 0.0
        
        recent_accesses = sorted(
            access_history,
            key=lambda x: x.get("timestamp", datetime.utcnow()),
            reverse=True
        )[:2]
        
        if len(recent_accesses) < 2:
            return 0.0
        
        # Check if travel between locations is physically possible
        time_diff = (
            recent_accesses[0].get("timestamp", datetime.utcnow()) -
            recent_accesses[1].get("timestamp", datetime.utcnow())
        ).total_seconds() / 3600  # Hours
        
        if time_diff <= 0:
            return 0.0
        
        # Assume 900 km/hour max realistic speed (commercial flight)
        config = get_config()
        distance_km = recent_accesses[0].get("distance_from_last", 0)
        max_possible_km = config.risk_scoring.max_login_velocity_km_per_hour * time_diff
        
        if distance_km > max_possible_km:
            return 0.25  # Impossible travel detected
        
        return 0.0


class ComplianceRiskStrategy:
    """Calculates risk based on policy and compliance violations."""
    
    def calculate(self, user: User) -> float:
        """
        Calculate compliance risk score (0.0 - 1.0).
        
        Factors:
        - MFA enabled
        - Credential age
        - Role appropriateness
        - Policy violations
        """
        score = 0.0
        config = get_config()
        
        # MFA requirement for admins
        if user.is_admin() and not user.mfa_enabled:
            score += 0.30
        
        # Account status
        if not user.is_active:
            score += 0.40
        
        # Clearance level validation
        if user.clearance_level.value == "secret" and user.is_admin():
            # Admin with elevated clearance is generally OK
            score -= 0.05
        
        return min(max(score, 0.0), 1.0)


class AnomalyRiskStrategy:
    """Calculates risk based on statistical anomalies."""
    
    def calculate(self, user: User, access_patterns: Dict = None) -> float:
        """
        Calculate anomaly risk score (0.0 - 1.0).
        
        Factors:
        - Unusual privilege combinations
        - Statistical outliers
        - Concurrent session limits
        - Failed authentication attempts
        """
        if access_patterns is None:
            access_patterns = {}
        
        score = 0.0
        
        # Check concurrent sessions
        concurrent = access_patterns.get("concurrent_sessions", 1)
        config = get_config()
        if concurrent > config.risk_scoring.concurrent_session_limit:
            # Penalize for too many concurrent sessions
            excess = concurrent - config.risk_scoring.concurrent_session_limit
            score += min(excess * 0.05, 0.20)
        
        # Check failed login attempts
        recent_failures = access_patterns.get("recent_failed_logins", 0)
        if recent_failures > 0:
            score += min(recent_failures * 0.10, 0.25)
        
        # Unusual privilege combination
        if user.is_admin() and user.clearance_level.value == "public":
            score += 0.15
        
        return min(score, 1.0)
