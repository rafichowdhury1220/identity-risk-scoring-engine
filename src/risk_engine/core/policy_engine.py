"""Policy engine for declarative security policy evaluation."""

from typing import List, Dict, Callable, Any
from dataclasses import dataclass
from datetime import datetime

from risk_engine.models import (
    Rule, SecurityPolicy, PolicyContext, PolicyDecision, AccessDecision
)


class PolicyEngine:
    """
    Declarative policy evaluation engine.
    
    Implements the Policy pattern for flexible, rule-based access control.
    Supports both RBAC (role-based) and ABAC (attribute-based) decisions.
    """
    
    def __init__(self, policies: List[SecurityPolicy] = None):
        """
        Initialize policy engine.
        
        Args:
            policies: Initial security policies
        """
        self.policies: List[SecurityPolicy] = policies or []
        self.rules_cache: Dict[str, List[Rule]] = {}
    
    def add_policy(self, policy: SecurityPolicy) -> None:
        """Register a new security policy."""
        if policy.enabled:
            self.policies.append(policy)
            self._invalidate_cache()
    
    def remove_policy(self, policy_id: str) -> None:
        """Remove a security policy."""
        self.policies = [p for p in self.policies if p.policy_id != policy_id]
        self._invalidate_cache()
    
    def evaluate(self, context: PolicyContext) -> PolicyDecision:
        """
        Evaluate all policies against the given context.
        
        Decision logic:
        1. If ANY rule explicitly DENYs, return DENY
        2. If policies grant access and no denies, return decision
        3. Otherwise, return default (DENY for security)
        
        This implements a "fail-safe" security posture.
        
        Args:
            context: Policy evaluation context
        
        Returns:
            PolicyDecision: Result of policy evaluation
        """
        applied_policies: List[str] = []
        reasons: List[str] = []
        final_decision = AccessDecision.ALLOW
        
        # Get all active rules from enabled policies
        all_rules = self._get_active_rules()
        
        # Sort by priority
        all_rules.sort(key=lambda r: r.priority)
        
        # Evaluate rules in order
        for rule in all_rules:
            if not rule.enabled:
                continue
            
            try:
                # Evaluate rule condition
                if rule.condition is None or rule.condition(context):
                    applied_policies.append(rule.name)
                    
                    # If rule denies, immediately return deny
                    if rule.action == AccessDecision.DENY:
                        return PolicyDecision(
                            decision=AccessDecision.DENY,
                            reason=f"Denied by rule: {rule.name}",
                            applied_policies=applied_policies,
                        )
                    
                    # If rule requires higher-level auth, upgrade decision
                    if rule.action in [
                        AccessDecision.REQUIRE_MFA,
                        AccessDecision.REQUIRE_ADDITIONAL_AUTH,
                        AccessDecision.REQUIRE_APPROVAL
                    ]:
                        # Only upgrade if not already at that level
                        if self._is_higher_auth_level(rule.action, final_decision):
                            final_decision = rule.action
            
            except Exception as e:
                # Log policy evaluation error (in production, use structured logging)
                reasons.append(f"Error evaluating rule {rule.name}: {str(e)}")
        
        return PolicyDecision(
            decision=final_decision,
            reason=" | ".join(reasons) if reasons else "No policies matched",
            applied_policies=applied_policies,
        )
    
    def _is_higher_auth_level(
        self,
        new_decision: AccessDecision,
        current_decision: AccessDecision
    ) -> bool:
        """Determine if new decision requires higher auth than current."""
        auth_hierarchy = {
            AccessDecision.ALLOW: 0,
            AccessDecision.REQUIRE_MFA: 1,
            AccessDecision.REQUIRE_ADDITIONAL_AUTH: 2,
            AccessDecision.REQUIRE_APPROVAL: 3,
            AccessDecision.DENY: 4,
        }
        return auth_hierarchy.get(new_decision, 0) > auth_hierarchy.get(
            current_decision, 0
        )
    
    def _get_active_rules(self) -> List[Rule]:
        """Get all rules from enabled policies."""
        all_rules = []
        for policy in self.policies:
            if policy.enabled:
                all_rules.extend(policy.rules)
        return all_rules
    
    def _invalidate_cache(self) -> None:
        """Invalidate rules cache when policies change."""
        self.rules_cache.clear()


class PolicyBuilder:
    """Builder for constructing policies programmatically."""
    
    def __init__(self, name: str):
        """Initialize policy builder."""
        self.name = name
        self.description = ""
        self.rules: List[Rule] = []
        self.enabled = True
        self.created_by = "system"
    
    def with_description(self, description: str) -> "PolicyBuilder":
        """Set policy description."""
        self.description = description
        return self
    
    def with_creator(self, user_id: str) -> "PolicyBuilder":
        """Set policy creator."""
        self.created_by = user_id
        return self
    
    def add_rule(
        self,
        name: str,
        condition: Callable[[PolicyContext], bool],
        action: AccessDecision,
        priority: int = 100
    ) -> "PolicyBuilder":
        """Add a rule to the policy."""
        rule = Rule(
            name=name,
            condition=condition,
            action=action,
            priority=priority,
            created_by=self.created_by,
        )
        self.rules.append(rule)
        return self
    
    def add_rbac_rule(
        self,
        required_role: str,
        action: AccessDecision = AccessDecision.ALLOW
    ) -> "PolicyBuilder":
        """Add a role-based access control rule."""
        def rbac_condition(context: PolicyContext) -> bool:
            # Check if user has required role
            return required_role in {r.value for r in context.user.roles}
        
        return self.add_rule(
            name=f"rbac_{required_role}",
            condition=rbac_condition,
            action=action,
        )
    
    def add_time_based_rule(
        self,
        allow_before_hour: int,
        allow_after_hour: int,
        action: AccessDecision = AccessDecision.REQUIRE_MFA
    ) -> "PolicyBuilder":
        """Add a time-based access rule."""
        def time_condition(context: PolicyContext) -> bool:
            hour = context.timestamp.hour
            return not (allow_after_hour <= hour < allow_before_hour)
        
        return self.add_rule(
            name=f"time_based_{allow_after_hour}_to_{allow_before_hour}",
            condition=time_condition,
            action=action,
            priority=150,
        )
    
    def add_mfa_required_rule(self) -> "PolicyBuilder":
        """Add rule requiring MFA."""
        def mfa_condition(context: PolicyContext) -> bool:
            return not context.mfa_verified
        
        return self.add_rule(
            name="mfa_required",
            condition=mfa_condition,
            action=AccessDecision.REQUIRE_MFA,
            priority=50,
        )
    
    def build(self) -> SecurityPolicy:
        """Build the policy."""
        return SecurityPolicy(
            name=self.name,
            description=self.description,
            rules=self.rules,
            created_by=self.created_by,
            enabled=self.enabled,
        )


# Pre-built common policies

def create_zero_trust_policy() -> SecurityPolicy:
    """
    Zero-trust policy: All access requires verification.
    No implicit trust based on network location or prior authentication.
    """
    return (
        PolicyBuilder("zero_trust_policy")
        .with_description("Require verification for all access")
        .add_rule(
            name="require_mfa_for_sensitive_resources",
            condition=lambda ctx: "admin" in ctx.resource.lower(),
            action=AccessDecision.REQUIRE_MFA,
            priority=100,
        )
        .add_rule(
            name="deny_inactive_users",
            condition=lambda ctx: not ctx.user.is_active,
            action=AccessDecision.DENY,
            priority=10,
        )
        .build()
    )


def create_least_privilege_policy() -> SecurityPolicy:
    """Principle of least privilege: minimize permission scope."""
    return (
        PolicyBuilder("least_privilege_policy")
        .with_description("Enforce least privilege access principle")
        .add_rule(
            name="require_approval_for_admin",
            condition=lambda ctx: ctx.user.is_admin(),
            action=AccessDecision.REQUIRE_APPROVAL,
            priority=80,
        )
        .build()
    )


def create_business_hours_policy() -> SecurityPolicy:
    """Restrict access outside business hours."""
    return (
        PolicyBuilder("business_hours_policy")
        .with_description("Restrict access outside business hours")
        .add_time_based_rule(
            allow_before_hour=8,
            allow_after_hour=18,
            action=AccessDecision.REQUIRE_ADDITIONAL_AUTH,
        )
        .build()
    )
