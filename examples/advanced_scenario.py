"""Example: Advanced scenario with custom policies and risk models."""

from datetime import datetime, timedelta
from risk_engine.models import User, UserRole, ClearanceLevel, PolicyContext
from risk_engine.core import RiskCalculator
from risk_engine.iam import Authenticator, AuditLogger
from risk_engine.core.policy_engine import PolicyEngine, PolicyBuilder, AccessDecision


def main():
    """Demonstrate advanced IRSE capabilities."""
    
    print("=" * 70)
    print("Identity Risk Scoring Engine - Advanced Scenario")
    print("=" * 70)
    
    # Scenario: Sensitive data access request outside business hours
    print("\nSCENARIO: Sensitive Data Access Outside Business Hours")
    print("-" * 70)
    
    # Get test user
    authenticator = Authenticator()
    user = authenticator.credential_store.get_user("alice")
    
    # ==================== CUSTOM POLICY ====================
    print("\n[1] BUILDING CUSTOM SECURITY POLICY")
    print("-" * 70)
    
    # Create a custom policy for sensitive data protection
    custom_policy = (
        PolicyBuilder("sensitive_data_policy")
        .with_description("Enhanced protection for sensitive data access")
        .with_creator("security_admin")
        .add_rule(
            name="deny_inactive_users",
            condition=lambda ctx: not ctx.user.is_active,
            action=AccessDecision.DENY,
            priority=10,  # Highest priority
        )
        .add_rule(
            name="require_mfa_for_sensitive_data",
            condition=lambda ctx: "sensitive_" in ctx.resource,
            action=AccessDecision.REQUIRE_MFA,
            priority=50,
        )
        .add_rule(
            name="require_approval_for_admin_access",
            condition=lambda ctx: ctx.user.is_admin() and "database_" in ctx.resource,
            action=AccessDecision.REQUIRE_APPROVAL,
            priority=60,
        )
        .add_rule(
            name="time_based_access_control",
            condition=lambda ctx: ctx.timestamp.hour < 8 or ctx.timestamp.hour >= 18,
            action=AccessDecision.REQUIRE_ADDITIONAL_AUTH,
            priority=70,
        )
        .build()
    )
    
    print(f"✓ Created policy: {custom_policy.name}")
    print(f"  Rules: {len(custom_policy.rules)}")
    for rule in custom_policy.rules:
        print(f"    - {rule.name} (priority: {rule.priority})")
    
    # ==================== COMPLEX RISK SCENARIO ====================
    print("\n[2] COMPLEX RISK ASSESSMENT")
    print("-" * 70)
    
    # Simulate access patterns
    access_history = [
        {
            "timestamp": datetime.utcnow() - timedelta(hours=2),
            "ip": "192.168.1.100",
            "city": "San Francisco",
            "country": "USA",
            "distance_from_last": 0,
        },
        {
            "timestamp": datetime.utcnow() - timedelta(hours=1),
            "ip": "10.0.0.1",
            "city": "New York",
            "country": "USA",
            "distance_from_last": 4000,  # km
        },
    ]
    
    access_patterns = {
        "concurrent_sessions": 2,
        "recent_failed_logins": 1,
    }
    
    # Calculate comprehensive risk
    risk_calculator = RiskCalculator()
    risk_score = risk_calculator.calculate_risk(
        user=user,
        access_history=access_history,
        access_patterns=access_patterns,
    )
    
    print(f"\nRisk Assessment: {user.username}")
    print(f"  Total Risk: {risk_score.total_score:.2%} ({risk_score.risk_level.value})")
    print(f"\n  Dimension Breakdown:")
    print(f"    Behavioral:  {risk_score.behavioral_score:.2%} (weight: 40%)")
    print(f"    Compliance:  {risk_score.compliance_score:.2%} (weight: 35%)")
    print(f"    Anomaly:     {risk_score.anomaly_score:.2%} (weight: 25%)")
    
    print(f"\n  Recommendation: {risk_score.recommendation.value.upper()}")
    
    print(f"\n  Detailed Risk Factors:")
    for factor in risk_score.risk_factors:
        print(f"    ✓ {factor.name}")
        print(f"      Category: {factor.category}")
        print(f"      Score: {factor.score:.2%}")
        print(f"      Recommendation: {factor.recommendation}")
    
    # ==================== POLICY EVALUATION ====================
    print("\n[3] POLICY-DRIVEN DECISION MAKING")
    print("-" * 70)
    
    # Create policy engine with custom policy
    engine = PolicyEngine([custom_policy])
    
    # Test scenario 1: Evening access to sensitive data without MFA
    context1 = PolicyContext(
        user=user,
        action="read",
        resource="sensitive_customer_data",
        source_ip=access_history[-1]["ip"],
        timestamp=datetime(2024, 1, 15, 19, 30),  # 7:30 PM
        mfa_verified=False,
    )
    
    decision1 = engine.evaluate(context1)
    print(f"\nScenario 1: Sensitive data access at 7:30 PM without MFA")
    print(f"  Decision: {decision1.decision.value.upper()}")
    print(f"  Reason: {decision1.reason}")
    
    # Test scenario 2: Same access with MFA verified
    context2 = PolicyContext(
        user=user,
        action="read",
        resource="sensitive_customer_data",
        source_ip=access_history[-1]["ip"],
        timestamp=datetime(2024, 1, 15, 19, 30),
        mfa_verified=True,
    )
    
    decision2 = engine.evaluate(context2)
    print(f"\nScenario 2: Same access WITH MFA verified")
    print(f"  Decision: {decision2.decision.value.upper()}")
    print(f"  Reason: {decision2.reason}")
    
    # ==================== AUDIT TRAIL ====================
    print("\n[4] AUDIT & COMPLIANCE TRAIL")
    print("-" * 70)
    
    audit_logger = AuditLogger()
    
    # Log decision
    audit_logger.log_authorization_decision(
        user_id=user.user_id,
        action="read",
        resource="sensitive_customer_data",
        granted=decision2.decision == AccessDecision.ALLOW,
        reason=f"Risk: {risk_score.total_score:.2%} - Policy: {custom_policy.name}"
    )
    
    audit_logger.log_authorization_decision(
        user_id=user.user_id,
        action="read",
        resource="database_admin_access",
        granted=False,
        reason="Admin access requires approval (policy: sensitive_data_policy)"
    )
    
    # Display audit trail
    trail = audit_logger.get_user_audit_trail(user.user_id, limit=10)
    print(f"\nAudit Trail ({len(trail)} entries):")
    for entry in trail:
        status_symbol = "✓" if entry.status == "success" else "✗"
        print(f"  {status_symbol} [{entry.action_category}] {entry.action} on {entry.resource}")
        if entry.details.get("reason"):
            print(f"     → {entry.details['reason']}")
    
    # ==================== SUMMARY ====================
    print("\n" + "=" * 70)
    print("ADVANCED SCENARIO SUMMARY")
    print("=" * 70)
    
    print(f"""
This advanced example demonstrates:

1. CUSTOM POLICIES: Building domain-specific security rules
   - Priority-based rule ordering (fail-safe defaults)
   - Conditional policy evaluation
   - Time-based access control
   - MFA enforcement for sensitive resources

2. MULTI-DIMENSIONAL RISK: Analyzing access patterns
   - Behavioral anomalies (impossible travel, off-hours)
   - Compliance violations (missing MFA, inactive accounts)
   - Statistical anomalies (concurrent sessions, failed attempts)

3. CONTEXT-AWARE DECISIONS: Policies adapt to context
   - Time of day influences required authentication level
   - Resource sensitivity triggers MFA requirements
   - User role affects approval thresholds

4. COMPLIANCE AUDIT TRAIL: Every decision is logged
   - Tamper-proof audit entries
   - Decision rationale captured
   - Compliance reports generated

Key Benefits:

✓ ZERO TRUST: No implicit trust, all access verified
✓ DEFENSE IN DEPTH: Multiple validation layers
✓ AUDIT COMPLIANCE: Immutable audit trails for SOC 2 / HIPAA / PCI-DSS
✓ FLEXIBILITY: Policies adapt without code changes
✓ TRANSPARENCY: Decision rationale visible for forensics
    """)


if __name__ == "__main__":
    main()
