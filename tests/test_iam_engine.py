"""Tests for IAM engine."""

import unittest
from datetime import datetime, timedelta

from risk_engine.models import User, UserRole, ClearanceLevel
from risk_engine.iam import Authenticator, Authorizer, AuditLogger


class TestAuthenticator(unittest.TestCase):
    """Test authentication service."""
    
    def setUp(self):
        self.authenticator = Authenticator()
        self.test_user = self.authenticator.credential_store.get_user("alice")
    
    def test_successful_authentication(self):
        """Valid credentials should authenticate."""
        session = self.authenticator.authenticate(
            username="alice",
            password="secure_password",
            ip_address="192.168.1.100"
        )
        
        self.assertIsNotNone(session)
        self.assertEqual(session.user_id, self.test_user.user_id)
        self.assertFalse(session.is_expired())
    
    def test_failed_authentication_wrong_password(self):
        """Wrong password should fail authentication."""
        session = self.authenticator.authenticate(
            username="alice",
            password="wrong_password",
            ip_address="192.168.1.100"
        )
        
        self.assertIsNone(session)
    
    def test_failed_authentication_user_not_found(self):
        """Non-existent user should fail authentication."""
        session = self.authenticator.authenticate(
            username="nonexistent",
            password="any_password",
            ip_address="192.168.1.100"
        )
        
        self.assertIsNone(session)
    
    def test_session_verification(self):
        """Valid session should be verifiable."""
        session = self.authenticator.authenticate(
            username="alice",
            password="secure_password",
            ip_address="192.168.1.100"
        )
        
        verified_user = self.authenticator.verify_session(session.session_id)
        self.assertIsNotNone(verified_user)
        self.assertEqual(verified_user.user_id, self.test_user.user_id)
    
    def test_session_revocation(self):
        """Revoked session should not be verifiable."""
        session = self.authenticator.authenticate(
            username="alice",
            password="secure_password",
            ip_address="192.168.1.100"
        )
        
        self.authenticator.revoke_session(session.session_id)
        
        verified_user = self.authenticator.verify_session(session.session_id)
        self.assertIsNone(verified_user)


class TestAuthorizer(unittest.TestCase):
    """Test authorization service."""
    
    def setUp(self):
        self.authorizer = Authorizer()
        self.admin_user = User(
            user_id="admin_001",
            username="admin",
            email="admin@example.com",
            roles={UserRole.ADMIN},
            clearance_level=ClearanceLevel.CONFIDENTIAL,
            mfa_enabled=True,
            last_login=datetime.utcnow(),
            creation_date=datetime.utcnow() - timedelta(days=30),
        )
        self.regular_user = User(
            user_id="user_001",
            username="alice",
            email="alice@example.com",
            roles={UserRole.USER},
            clearance_level=ClearanceLevel.INTERNAL,
            mfa_enabled=False,
            last_login=datetime.utcnow(),
            creation_date=datetime.utcnow() - timedelta(days=30),
        )
    
    def test_admin_access_allowed(self):
        """Admin should have access to admin resources."""
        authorized = self.authorizer.is_authorized(
            self.admin_user,
            "write",
            "admin_settings"
        )
        self.assertTrue(authorized)
    
    def test_user_denied_admin_access(self):
        """Regular user should not access admin resources."""
        authorized = self.authorizer.is_authorized(
            self.regular_user,
            "write",
            "admin_settings"
        )
        self.assertFalse(authorized)
    
    def test_clearance_level_check(self):
        """User without proper clearance should be denied."""
        authorized = self.authorizer.is_authorized(
            self.regular_user,
            "read",
            "secret_file"
        )
        self.assertFalse(authorized)


class TestAuditLogger(unittest.TestCase):
    """Test audit logging."""
    
    def setUp(self):
        self.audit_logger = AuditLogger()
        self.test_user_id = "user_001"
    
    def test_authentication_logged(self):
        """Authentication attempts should be logged."""
        self.audit_logger.log_authentication(
            user_id=self.test_user_id,
            success=True,
            source_ip="192.168.1.100"
        )
        
        trail = self.audit_logger.get_user_audit_trail(self.test_user_id)
        self.assertGreater(len(trail), 0)
        self.assertEqual(trail[-1].action, "authentication")
    
    def test_authorization_logged(self):
        """Authorization decisions should be logged."""
        self.audit_logger.log_authorization_decision(
            user_id=self.test_user_id,
            action="read",
            resource="file.txt",
            granted=True,
            reason="User has read permission"
        )
        
        trail = self.audit_logger.get_user_audit_trail(self.test_user_id)
        self.assertGreater(len(trail), 0)
        self.assertEqual(trail[-1].action_category, "authorization")
    
    def test_audit_trail_retrieval(self):
        """Audit trail should be retrievable for user."""
        # Log multiple events
        for i in range(5):
            self.audit_logger.log_authentication(
                user_id=self.test_user_id,
                success=True,
                source_ip="192.168.1.100"
            )
        
        trail = self.audit_logger.get_user_audit_trail(self.test_user_id)
        self.assertEqual(len(trail), 5)
    
    def test_compliance_report(self):
        """Compliance report should be generated."""
        self.audit_logger.log_authentication(
            user_id=self.test_user_id,
            success=True
        )
        
        report = self.audit_logger.export_compliance_report()
        self.assertIn("report_time", report)
        self.assertIn("total_entries", report)
        self.assertIn("summary", report)


if __name__ == "__main__":
    unittest.main()
