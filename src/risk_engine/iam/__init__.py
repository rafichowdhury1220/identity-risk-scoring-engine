"""IAM (Identity & Access Management) module."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import hashlib
import hmac

from risk_engine.models import User, UserRole, ClearanceLevel, Session, AuditLogEntry
from risk_engine.config import get_config


class Authenticator:
    """
    Authentication service for user identity verification.
    
    Demonstrates secure credential handling and session management.
    """
    
    def __init__(self, credential_store=None):
        """
        Initialize authenticator.
        
        Args:
            credential_store: Backend credential storage (injectable for testing)
        """
        self.credential_store = credential_store or InMemoryCredentialStore()
        self.config = get_config()
        self.sessions: Dict[str, Session] = {}
    
    def authenticate(
        self,
        username: str,
        password: str,
        ip_address: str = "127.0.0.1"
    ) -> Optional[Session]:
        """
        Authenticate user with credentials.
        
        Args:
            username: Username
            password: Password (will be hashed)
            ip_address: Source IP for audit logging
        
        Returns:
            Session if authentication successful, None otherwise
        """
        # Verify credentials
        user = self.credential_store.get_user(username)
        if not user:
            return None
        
        if not self._verify_password(password, user):
            return None
        
        # Check if account is active
        if not user.is_active:
            return None
        
        # Create session
        config = get_config()
        now = datetime.utcnow()
        session = Session(
            user_id=user.user_id,
            created_at=now,
            expires_at=now + timedelta(minutes=config.security.session_timeout_minutes),
            ip_address=ip_address,
        )
        
        # Store session
        self.sessions[session.session_id] = session
        
        return session
    
    def verify_session(self, session_id: str) -> Optional[User]:
        """
        Verify session is valid and return associated user.
        
        Args:
            session_id: Session identifier
        
        Returns:
            User if session valid, None otherwise
        """
        session = self.sessions.get(session_id)
        if not session or session.is_expired():
            return None
        
        # Update last activity
        self.sessions[session_id] = Session(
            session_id=session.session_id,
            user_id=session.user_id,
            created_at=session.created_at,
            expires_at=session.expires_at,
            last_activity=datetime.utcnow(),
            ip_address=session.ip_address,
            mfa_verified=session.mfa_verified,
        )
        
        return self.credential_store.get_user_by_id(session.user_id)
    
    def revoke_session(self, session_id: str) -> None:
        """Revoke a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def _verify_password(self, password: str, user: User) -> bool:
        """
        Verify password against stored hash.
        
        In production, use bcrypt or argon2 for password hashing.
        This is simplified for demonstration.
        """
        # In real system: use bcrypt.checkpw() or similar
        stored_hash = self.credential_store.get_password_hash(user.user_id)
        return stored_hash and self._hash_password(password) == stored_hash
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash password (simplified, use bcrypt in production)."""
        return hashlib.sha256(password.encode()).hexdigest()


class Authorizer:
    """
    Authorization service for access control decisions.
    
    Supports RBAC (role-based) and ABAC (attribute-based) control.
    """
    
    def __init__(self):
        """Initialize authorizer."""
        self.config = get_config()
    
    def is_authorized(
        self,
        user: User,
        action: str,
        resource: str
    ) -> bool:
        """
        Check if user is authorized for action on resource.
        
        Args:
            user: User attempting access
            action: Action (read, write, delete, etc.)
            resource: Resource being accessed
        
        Returns:
            True if authorized, False otherwise
        """
        # Check role-based access
        if not self._check_rbac(user, action, resource):
            return False
        
        # Check attribute-based access
        if not self._check_abac(user, action, resource):
            return False
        
        return True
    
    def _check_rbac(self, user: User, action: str, resource: str) -> bool:
        """Role-based access control."""
        # Super admin can do anything
        if user.has_role(UserRole.SUPER_ADMIN):
            return True
        
        # Admin can access most things (except super admin functions)
        if user.has_role(UserRole.ADMIN):
            return not resource.startswith("super_admin_")
        
        # Engineer can access their resources
        if user.has_role(UserRole.ENGINEER):
            return not (resource.startswith("admin_") or resource.startswith("super_admin_"))
        
        # User can access public and user resources
        return resource.startswith("public_") or resource.startswith("user_")
    
    def _check_abac(self, user: User, action: str, resource: str) -> bool:
        """Attribute-based access control."""
        # Clearance level check
        if "secret_" in resource:
            return user.clearance_level.value in ["secret", "top_secret"]
        
        if "confidential_" in resource:
            return user.clearance_level.value in ["confidential", "secret", "top_secret"]
        
        # Department check
        if resource.startswith("dept_"):
            dept = resource.split("_")[1]
            return user.department == dept
        
        return True


class AuditLogger:
    """
    Immutable audit logging for compliance and forensics.
    
    Stores all access decisions for compliance (SOC 2, HIPAA, PCI-DSS).
    """
    
    def __init__(self, log_store=None):
        """
        Initialize audit logger.
        
        Args:
            log_store: Backend log storage (injectable for testing)
        """
        self.log_store = log_store or InMemoryAuditStore()
        self.config = get_config()
    
    def log_authentication(
        self,
        user_id: str,
        success: bool,
        source_ip: str = "",
        reason: Optional[str] = None
    ) -> None:
        """Log authentication attempt."""
        if not self.config.audit.enabled:
            return
        
        entry = AuditLogEntry(
            actor_id=user_id,
            actor_type="user",
            action="authentication",
            action_category="authentication",
            resource="auth_service",
            status="success" if success else "failure",
            error_message=reason if not success else None,
            source_ip=source_ip,
            details={
                "success": success,
                "reason": reason,
            }
        )
        
        self.log_store.save(entry)
    
    def log_authorization_decision(
        self,
        user_id: str,
        action: str,
        resource: str,
        granted: bool,
        reason: Optional[str] = None
    ) -> None:
        """Log authorization decision."""
        if not self.config.audit.enabled:
            return
        
        entry = AuditLogEntry(
            actor_id=user_id,
            actor_type="user",
            action=action,
            action_category="authorization",
            resource=resource,
            status="success" if granted else "denied",
            error_message=reason if not granted else None,
            details={
                "action": action,
                "resource": resource,
                "granted": granted,
                "reason": reason,
            }
        )
        
        self.log_store.save(entry)
    
    def get_user_audit_trail(
        self,
        user_id: str,
        limit: int = 100
    ) -> List[AuditLogEntry]:
        """Get audit trail for specific user."""
        return self.log_store.get_user_entries(user_id, limit)
    
    def export_compliance_report(self) -> Dict:
        """Export audit data for compliance reporting."""
        return {
            "report_time": datetime.utcnow().isoformat(),
            "total_entries": self.log_store.count(),
            "summary": self.log_store.get_summary(),
        }


# Credential and audit storage implementations

class InMemoryCredentialStore:
    """In-memory credential storage for testing."""
    
    def __init__(self):
        """Initialize with test data."""
        self.users: Dict[str, User] = {}
        self.password_hashes: Dict[str, str] = {}
        self._load_test_data()
    
    def _load_test_data(self):
        """Load test users."""
        test_user = User(
            user_id="user_001",
            username="alice",
            email="alice@example.com",
            roles={UserRole.ADMIN},
            clearance_level=ClearanceLevel.CONFIDENTIAL,
            mfa_enabled=True,
            last_login=datetime.utcnow() - timedelta(days=1),
            creation_date=datetime.utcnow() - timedelta(days=30),
        )
        
        self.users["alice"] = test_user
        self.password_hashes["user_001"] = Authenticator._hash_password("secure_password")
    
    def get_user(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.users.get(username)
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        for user in self.users.values():
            if user.user_id == user_id:
                return user
        return None
    
    def get_password_hash(self, user_id: str) -> Optional[str]:
        """Get password hash for user."""
        return self.password_hashes.get(user_id)


class InMemoryAuditStore:
    """In-memory audit log storage for testing."""
    
    def __init__(self):
        """Initialize audit store."""
        self.entries: List[AuditLogEntry] = []
    
    def save(self, entry: AuditLogEntry) -> None:
        """Save audit entry."""
        self.entries.append(entry)
    
    def get_user_entries(
        self,
        user_id: str,
        limit: int = 100
    ) -> List[AuditLogEntry]:
        """Get entries for specific user."""
        return [
            e for e in self.entries if e.actor_id == user_id
        ][-limit:]
    
    def count(self) -> int:
        """Get total entry count."""
        return len(self.entries)
    
    def get_summary(self) -> Dict:
        """Get summary statistics."""
        success_count = sum(1 for e in self.entries if e.status == "success")
        failure_count = len(self.entries) - success_count
        
        return {
            "total": len(self.entries),
            "success": success_count,
            "failure": failure_count,
        }
