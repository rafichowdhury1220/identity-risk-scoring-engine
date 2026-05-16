"""Unit tests for risk calculator."""

import unittest
from datetime import datetime, timedelta

from risk_engine.models import User, UserRole, ClearanceLevel, RiskLevel, AccessDecision
from risk_engine.core import (
    RiskCalculator,
    BehavioralRiskStrategy,
    ComplianceRiskStrategy,
    AnomalyRiskStrategy,
)
from risk_engine.config import Config, Environment, LogLevel, DatabaseConfig, CacheConfig, RiskScoringConfig, AuditConfig, SecurityConfig


class TestBehavioralRiskStrategy(unittest.TestCase):
    """Test behavioral risk assessment."""
    
    def setUp(self):
        self.strategy = BehavioralRiskStrategy()
    
    def test_new_account_risk(self):
        """New accounts should have higher risk."""
        new_user = User(
            user_id="new_001",
            username="newuser",
            email="new@example.com",
            roles={UserRole.USER},
            clearance_level=ClearanceLevel.PUBLIC,
            mfa_enabled=False,
            last_login=None,
            creation_date=datetime.utcnow() - timedelta(days=5),
        )
        
        score = self.strategy.calculate(new_user)
        self.assertGreater(score, 0.15)  # Should have risk from new account
    
    def test_established_account_risk(self):
        """Established accounts should have lower risk."""
        old_user = User(
            user_id="old_001",
            username="olduser",
            email="old@example.com",
            roles={UserRole.USER},
            clearance_level=ClearanceLevel.PUBLIC,
            mfa_enabled=False,
            last_login=datetime.utcnow() - timedelta(days=1),
            creation_date=datetime.utcnow() - timedelta(days=365),
        )
        
        score = self.strategy.calculate(old_user)
        self.assertLess(score, 0.15)


class TestComplianceRiskStrategy(unittest.TestCase):
    """Test compliance risk assessment."""
    
    def setUp(self):
        self.strategy = ComplianceRiskStrategy()
    
    def test_admin_without_mfa_risk(self):
        """Admins without MFA should have compliance risk."""
        admin_user = User(
            user_id="admin_001",
            username="admin",
            email="admin@example.com",
            roles={UserRole.ADMIN},
            clearance_level=ClearanceLevel.CONFIDENTIAL,
            mfa_enabled=False,
            last_login=datetime.utcnow(),
            creation_date=datetime.utcnow() - timedelta(days=30),
        )
        
        score = self.strategy.calculate(admin_user)
        self.assertGreater(score, 0.20)  # Should have significant compliance risk
    
    def test_admin_with_mfa_compliant(self):
        """Admins with MFA should be compliant."""
        admin_user = User(
            user_id="admin_001",
            username="admin",
            email="admin@example.com",
            roles={UserRole.ADMIN},
            clearance_level=ClearanceLevel.CONFIDENTIAL,
            mfa_enabled=True,
            last_login=datetime.utcnow(),
            creation_date=datetime.utcnow() - timedelta(days=30),
        )
        
        score = self.strategy.calculate(admin_user)
        self.assertLess(score, 0.15)


class TestAnomalyRiskStrategy(unittest.TestCase):
    """Test anomaly detection."""
    
    def setUp(self):
        self.strategy = AnomalyRiskStrategy()
    
    def test_excessive_concurrent_sessions(self):
        """Excessive concurrent sessions should be anomalous."""
        user = User(
            user_id="user_001",
            username="alice",
            email="alice@example.com",
            roles={UserRole.USER},
            clearance_level=ClearanceLevel.PUBLIC,
            mfa_enabled=False,
            last_login=datetime.utcnow(),
            creation_date=datetime.utcnow() - timedelta(days=30),
        )
        
        patterns = {"concurrent_sessions": 10}
        score = self.strategy.calculate(user, patterns)
        self.assertGreater(score, 0.15)
    
    def test_failed_login_attempts(self):
        """Multiple failed login attempts indicate anomaly."""
        user = User(
            user_id="user_001",
            username="alice",
            email="alice@example.com",
            roles={UserRole.USER},
            clearance_level=ClearanceLevel.PUBLIC,
            mfa_enabled=False,
            last_login=datetime.utcnow(),
            creation_date=datetime.utcnow() - timedelta(days=30),
        )
        
        patterns = {"recent_failed_logins": 5}
        score = self.strategy.calculate(user, patterns)
        self.assertGreater(score, 0.20)


class TestRiskCalculator(unittest.TestCase):
    """Test aggregate risk calculation."""
    
    def setUp(self):
        self.calculator = RiskCalculator()
        self.test_user = User(
            user_id="test_001",
            username="testuser",
            email="test@example.com",
            roles={UserRole.USER},
            clearance_level=ClearanceLevel.INTERNAL,
            mfa_enabled=True,
            last_login=datetime.utcnow() - timedelta(days=1),
            creation_date=datetime.utcnow() - timedelta(days=90),
        )
    
    def test_risk_score_range(self):
        """Risk score should be between 0 and 1."""
        risk = self.calculator.calculate_risk(self.test_user)
        self.assertGreaterEqual(risk.total_score, 0.0)
        self.assertLessEqual(risk.total_score, 1.0)
    
    def test_risk_level_classification(self):
        """Risk level should match total score."""
        risk = self.calculator.calculate_risk(self.test_user)
        
        if risk.total_score < 0.4:
            self.assertEqual(risk.risk_level, RiskLevel.LOW)
        elif risk.total_score < 0.6:
            self.assertEqual(risk.risk_level, RiskLevel.MEDIUM)
        elif risk.total_score < 0.8:
            self.assertEqual(risk.risk_level, RiskLevel.HIGH)
        else:
            self.assertEqual(risk.risk_level, RiskLevel.CRITICAL)
    
    def test_recommendation_matches_score(self):
        """Recommendation should match risk score."""
        risk = self.calculator.calculate_risk(self.test_user)
        
        if risk.total_score < 0.4:
            self.assertEqual(risk.recommendation, AccessDecision.ALLOW)
        elif risk.total_score < 0.6:
            self.assertEqual(risk.recommendation, AccessDecision.REQUIRE_MFA)


if __name__ == "__main__":
    unittest.main()
