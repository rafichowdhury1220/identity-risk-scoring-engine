"""Example: Basic usage of Identity Risk Scoring Engine."""

from datetime import datetime, timedelta
from risk_engine.models import User, UserRole, ClearanceLevel
from risk_engine.core import RiskCalculator
from risk_engine.iam import Authenticator, Authorizer, AuditLogger
from risk_engine.core.policy_engine import PolicyEngine, create_zero_trust_policy, PolicyContext


def main():
    """Demonstrate basic IRSE functionality."""
    
    print("=" * 70)
    print("Identity Risk Scoring Engine - Basic Usage Example")
    print("=" * 70)
    
    # ==================== AUTHENTICATION ====================
    print("\n[1] AUTHENTICATION")
    print("-" * 70)
    
    authenticator = Authenticator()
    
    # Authenticate user
    session = authenticator.authenticate(
        username="alice",
        password="secure_password",
        ip_address="192.168.1.100"
    )
    
    if session:
        print(f"✓ Authentication successful")
        print(f"  Session ID: {session.session_id}")
        print(f"  User ID: {session.user_id}")
        print(f"  Expires: {session.expires_at}")
    
    # Failed authentication attempt
    failed_session = authenticator.authenticate(
        username="alice",
        password="wrong_password",
        ip_address="192.168.1.100"
    )
    print(f"✓ Failed authentication correctly rejected")
    
    # ==================== RISK SCORING ====================
    print("\n[2] RISK ASSESSMENT")
    print("-" * 70)
    
    # Get authenticated user
    user = authenticator.credential_store.get_user("alice")
    
    # Calculate risk
    risk_calculator = RiskCalculator()
    risk_score = risk_calculator.calculate_risk(user)
    
    print(f"Risk Assessment for user: {user.username}")
    print(f"  Behavioral Risk:  {risk_score.behavioral_score:.2%}")
    print(f"  Compliance Risk:  {risk_score.compliance_score:.2%}")
    print(f"  Anomaly Risk:     {risk_score.anomaly_score:.2%}")
    print(f"  Total Risk Score: {risk_score.total_score:.2%}")
    print(f"  Risk Level:       {risk_score.risk_level.value.upper()}")
    print(f"  Recommendation:   {risk_score.recommendation.value.upper()}")
    
    # Show top risk factors
    print(f"\n  Top Risk Factors:")
    for factor in risk_score.get_top_risk_factors(3):
        print(f"    - {factor.name}: {factor.score:.2%}")
        print(f"      {factor.description}")
    
    # ==================== AUTHORIZATION ====================
    print("\n[3] AUTHORIZATION")
    print("-" * 70)
    
    authorizer = Authorizer()
    
    # Check various access rights
    access_tests = [
        ("read", "user_profile"),
        ("write", "admin_settings"),
        ("delete", "confidential_data"),
    ]
    
    for action, resource in access_tests:
        authorized = authorizer.is_authorized(user, action, resource)
        status = "✓ GRANTED" if authorized else "✗ DENIED"
        print(f"{status} - {action.upper()} on {resource}")
    
    # ==================== POLICY ENGINE ====================
    print("\n[4] POLICY EVALUATION")
    print("-" * 70)
    
    # Create and apply zero-trust policy
    engine = PolicyEngine()
    zero_trust = create_zero_trust_policy()
    engine.add_policy(zero_trust)
    
    # Create policy context
    context = PolicyContext(
        user=user,
        action="access_resource",
        resource="admin_panel",
        source_ip="192.168.1.100",
        mfa_verified=False,
    )
    
    # Evaluate policy
    decision = engine.evaluate(context)
    print(f"Policy Decision: {decision.decision.value.upper()}")
    print(f"  Reason: {decision.reason}")
    print(f"  Applied Policies: {', '.join(decision.applied_policies)}")
    
    # ==================== AUDIT LOGGING ====================
    print("\n[5] AUDIT LOGGING & COMPLIANCE")
    print("-" * 70)
    
    audit_logger = AuditLogger()
    
    # Log authentication
    audit_logger.log_authentication(
        user_id=user.user_id,
        success=True,
        source_ip="192.168.1.100",
    )
    
    # Log authorization decision
    audit_logger.log_authorization_decision(
        user_id=user.user_id,
        action="read",
        resource="user_profile",
        granted=True,
        reason="User has USER role"
    )
    
    audit_logger.log_authorization_decision(
        user_id=user.user_id,
        action="write",
        resource="admin_settings",
        granted=True,
        reason="User has ADMIN role"
    )
    
    # Get audit trail
    trail = audit_logger.get_user_audit_trail(user.user_id)
    print(f"\nAudit Trail ({len(trail)} entries):")
    for entry in trail[-3:]:
        print(f"  - {entry.action}: {entry.resource} ({entry.status})")
    
    # Export compliance report
    report = audit_logger.export_compliance_report()
    print(f"\nCompliance Report:")
    print(f"  Total Events: {report['total_entries']}")
    print(f"  Successful: {report['summary']['success']}")
    print(f"  Failed: {report['summary']['failure']}")
    
    # ==================== SUMMARY ====================
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    print(f"""
The Identity Risk Scoring Engine demonstrates:

1. AUTHENTICATION: Secure user verification with session management
2. RISK SCORING: Multi-dimensional risk assessment (behavioral, compliance, anomaly)
3. AUTHORIZATION: Role-based and attribute-based access control
4. POLICY ENGINE: Declarative, flexible security policy evaluation
5. AUDIT LOGGING: Immutable audit trails for compliance (SOC 2, HIPAA, PCI-DSS)

Key Design Patterns:
- Strategy Pattern: Pluggable risk scoring strategies
- Policy Pattern: Declarative rule-based access control
- Observer Pattern: Event-driven audit logging
- Adapter Pattern: Swappable storage backends

This architecture enables:
✓ Scalability: Stateless design for horizontal scaling
✓ Flexibility: Pluggable components and strategies
✓ Security: Defense in depth with multiple validation layers
✓ Compliance: Comprehensive immutable audit trails
✓ Maintainability: Clear separation of concerns
    """)


if __name__ == "__main__":
    main()
