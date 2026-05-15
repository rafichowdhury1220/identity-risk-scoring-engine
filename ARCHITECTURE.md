# System Architecture Documentation

## Table of Contents

1. [Architectural Vision](#architectural-vision)
2. [Design Patterns](#design-patterns)
3. [Component Architecture](#component-architecture)
4. [Data Flow](#data-flow)
5. [Scalability & Performance](#scalability--performance)
6. [Failure Modes & Resilience](#failure-modes--resilience)

---

## Architectural Vision

The Identity Risk Scoring Engine follows a **layered, modular architecture** designed for:

- **Extensibility**: Add new risk factors without modifying core logic
- **Maintainability**: Clear separation of concerns across layers
- **Testability**: Each component can be tested in isolation
- **Scalability**: Stateless design enables horizontal scaling
- **Security**: Defense in depth with multiple validation layers

### Core Principles

1. **Dependency Injection**: Services are injected, not instantiated
2. **Interface Segregation**: Minimal, focused contracts
3. **Immutability**: Data models are immutable for thread safety
4. **Graceful Degradation**: System remains functional under failures

---

## Design Patterns

### 1. **Layered Architecture**

```
┌─────────────────────────────────────┐
│      Presentation / API Layer       │
├─────────────────────────────────────┤
│      IAM / Business Logic Layer      │
├─────────────────────────────────────┤
│      Data Access / Adapter Layer     │
├─────────────────────────────────────┤
│      External Services Layer         │
└─────────────────────────────────────┘
```

**Rationale**:

- Each layer has specific responsibility
- Changes in one layer don't cascade up
- Easy to swap implementations (databases, identity providers)

### 2. **Strategy Pattern (Risk Calculators)**

Different risk factors are calculated independently:

```python
class RiskCalculator:
    def __init__(self):
        self.strategies = [
            BehavioralRiskStrategy(),
            ComplianceRiskStrategy(),
            AnomalyRiskStrategy()
        ]

    def calculate(self, user):
        scores = [s.calculate(user) for s in self.strategies]
        return aggregate_scores(scores)
```

**Benefits**:

- Easy to add new risk factors
- Each factor tested independently
- Weights can be adjusted dynamically

### 3. **Adapter Pattern (Data Persistence & Identity Providers)**

```python
class DataStoreAdapter(ABC):
    @abstractmethod
    def save_audit_log(self, entry: AuditLogEntry) -> None: ...

    @abstractmethod
    def get_user_history(self, user_id: str) -> List[AccessRecord]: ...

# Implementations: PostgreSQL, MongoDB, S3
```

**Benefits**:

- Swap database implementations without code changes
- Support multiple identity providers (OAuth, SAML, LDAP)
- Easy testing with in-memory implementations

### 4. **Policy Pattern (Rule Engine)**

```python
@dataclass
class PolicyContext:
    user: User
    resource: Resource
    action: str
    environment: EnvironmentContext

class SecurityPolicy:
    rules: List[Rule]

    def evaluate(self, context: PolicyContext) -> PolicyDecision:
        # Evaluate rules in order
        # First deny wins, first allow with no denies grants access
```

**Benefits**:

- Declarative security policies
- Easy auditing of why access was granted/denied
- Dynamic policy updates without code deployment

### 5. **Observer Pattern (Audit Logging)**

```python
class AuthenticationEvent:
    observers: List[AuditObserver]

    def authenticate(self, credentials):
        user = self._verify(credentials)
        # Notify all observers
        self.notify_observers(AuthEventData(...))
        return user
```

**Benefits**:

- Decoupled logging from business logic
- Multiple audit sinks (database, SIEM, compliance)
- Asynchronous audit trail doesn't block authentication

---

## Component Architecture

### Layer 1: Models (Data)

```python
# Identity Model
@dataclass
class User:
    user_id: str
    username: str
    email: str
    roles: Set[UserRole]
    clearance_level: ClearanceLevel
    mfa_enabled: bool
    last_login: datetime
    creation_date: datetime

# Risk Model
@dataclass
class RiskScore:
    behavioral_score: float      # 0.0 - 1.0
    compliance_score: float      # 0.0 - 1.0
    anomaly_score: float        # 0.0 - 1.0
    total_score: float          # 0.0 - 1.0
    risk_factors: List[str]
    recommendation: AccessDecision
    timestamp: datetime

# Policy Model
@dataclass
class SecurityPolicy:
    policy_id: str
    name: str
    rules: List[Rule]
    version: str
    enabled: bool
    created_by: str
    last_modified: datetime
```

### Layer 2: Core Business Logic

#### Risk Calculator

```
RiskCalculator
├── BehavioralRiskStrategy
│   ├── Time-based analysis
│   ├── Geographical analysis
│   └── Access pattern comparison
├── ComplianceRiskStrategy
│   ├── Policy evaluation
│   ├── Certification checks
│   └── Credential validation
└── AnomalyRiskStrategy
    ├── Statistical outlier detection
    ├── Privilege analysis
    └── Session anomaly detection
```

**Decision Logic**:

```
if risk_score < 0.4:           → ALLOW
elif risk_score < 0.6:         → REQUIRE_MFA
elif risk_score < 0.8:         → REQUIRE_ADDITIONAL_AUTH
else:                          → DENY
```

#### Policy Engine

```
PolicyEngine
├── PolicyStore (load policies)
├── RuleEvaluator
│   ├── Condition evaluation
│   ├── Action execution
│   └── Audit logging
└── PolicyDecisionPoint
    ├── Combine multiple policies
    └── Determine final decision
```

### Layer 3: IAM (Identity & Access Management)

```
IAMEngine
├── Authenticator
│   ├── Credential verification
│   ├── MFA validation
│   └── Session management
├── Authorizer
│   ├── RBAC evaluation
│   ├── ABAC evaluation
│   └── Delegation handling
└── AuditLogger
    ├── Immutable audit trail
    ├── Compliance reporting
    └── Forensics support
```

### Layer 4: Adapters (External Integration)

```
AdapterLayer
├── IdentityProviderAdapter
│   ├── OAuth2 Implementation
│   ├── SAML Implementation
│   ├── LDAP Implementation
│   └── Custom Implementation
├── DataStoreAdapter
│   ├── PostgreSQL Implementation
│   ├── MongoDB Implementation
│   ├── In-Memory (Testing)
│   └── S3 (Audit Trail Archive)
└── ExternalServiceAdapter
    ├── MFA Provider (Twilio, Okta)
    ├── Threat Intelligence
    └── Compliance Service
```

---

## Data Flow

### Authentication Flow

```
User Request
    │
    ▼
┌─────────────────────────────┐
│  Credential Validation      │
│  - Username/Password check  │
│  - MFA validation           │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Create Session             │
│  - Generate session token   │
│  - Set expiration           │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Calculate Risk Score       │
│  - Behavioral analysis      │
│  - Compliance check         │
│  - Anomaly detection        │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Log Audit Event            │
│  - Who: user_id             │
│  - What: authentication     │
│  - When: timestamp          │
│  - Where: source_ip         │
│  - Result: success/failure  │
└────────┬────────────────────┘
         │
         ▼
    Return Session
```

### Access Control Flow

```
Access Request (with token)
    │
    ▼
┌─────────────────────────────┐
│  Validate Token             │
│  - Not expired              │
│  - Valid signature          │
│  - Not revoked              │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Extract User Context       │
│  - User roles               │
│  - User attributes          │
│  - Current permissions      │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Evaluate Policies          │
│  - RBAC rules               │
│  - ABAC conditions          │
│  - Contextual rules         │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Calculate Risk Score       │
│  - Request context analysis │
│  - Behavioral baseline      │
│  - Anomaly detection        │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Make Access Decision       │
│  - ALLOW / DENY / MFA_REQUIRED
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Log Audit Event            │
│  - Immutable record         │
│  - Decision rationale       │
└────────┬────────────────────┘
         │
         ▼
    Return Decision
```

---

## Scalability & Performance

### Horizontal Scaling Strategy

**Stateless Design**:

- Core engine holds no user state
- Session state stored in Redis/Memcached
- Audit logs in distributed database
- Configuration cached locally with TTL

```
Load Balancer
    │
    ├─→ Engine Node 1 ──┐
    ├─→ Engine Node 2 ──┤─→ Redis (Session Store)
    ├─→ Engine Node 3 ──┤→ PostgreSQL (Audit Logs)
    └─→ Engine Node N ──┘→ S3 (Archive)
```

### Performance Optimization

| Component         | Target | Strategy                               |
| ----------------- | ------ | -------------------------------------- |
| Risk Calculation  | <100ms | Parallel factor evaluation             |
| Policy Evaluation | <50ms  | Rule caching, short-circuit evaluation |
| Authentication    | <500ms | Async MFA, cached credential checks    |
| Audit Logging     | <1ms   | Async writes, batching                 |

### Caching Layers

```
Request
    ▼
1. Local In-Memory Cache (policy configs)
    │ Miss
    ▼
2. Distributed Cache (Redis)
    │ Miss
    ▼
3. Primary Store (PostgreSQL)
    │
    └→ Update all cache layers
```

---

## Failure Modes & Resilience

### Circuit Breaker Pattern

```python
@circuit_breaker(failure_threshold=5, timeout=60)
def call_identity_provider(credentials):
    # External call with automatic fallback
    pass
```

**Behavior**:

- **Closed**: Normal operation
- **Open**: Reject requests for timeout period (fast-fail)
- **Half-Open**: Allow test request to verify recovery

### Fallback Strategies

| Component         | Failure       | Strategy                      |
| ----------------- | ------------- | ----------------------------- |
| Identity Provider | Unavailable   | Cache credentials, warn user  |
| Audit Database    | Write failure | Queue to local disk, retry    |
| Cache             | Miss          | Query primary store           |
| Risk Calculator   | Exception     | Default to conservative score |

### Monitoring & Alerting

```
Metrics:
├── Authentication latency (p50, p95, p99)
├── Policy evaluation failures
├── Risk scoring anomalies
├── Audit log lag
└── Identity provider availability

Alerts (if):
├── Latency > 1000ms
├── Error rate > 1%
├── Database connection pool exhausted
└── Audit log lag > 5 minutes
```

---

## Technology Choices

| Layer         | Technology   | Rationale                                     |
| ------------- | ------------ | --------------------------------------------- |
| Language      | Python 3.11+ | Type hints, async support, rich ecosystem     |
| Web Framework | FastAPI      | Async, auto-validation, OpenAPI documentation |
| Database      | PostgreSQL   | ACID, audit trail, scalable                   |
| Cache         | Redis        | Sub-millisecond latency, distributed          |
| Testing       | pytest       | Comprehensive, plugin ecosystem               |
| Logging       | structlog    | Structured logs for SIEM integration          |
| Task Queue    | Celery       | Async audit logging, background tasks         |

---

## Future Enhancements

1. **Machine Learning Integration**
   - Unsupervised anomaly detection (Isolation Forest)
   - Behavioral clustering
   - Predictive risk modeling

2. **Real-time Visualization**
   - Dashboard for risk metrics
   - Access decision audit trail
   - Policy impact analysis

3. **Advanced Policy Language**
   - DSL for policy definition
   - Visual policy builder
   - Policy version control & rollback

4. **Multi-tenancy**
   - Tenant isolation
   - Custom risk models per tenant
   - Isolated audit trails

5. **Threat Intelligence Integration**
   - IP reputation scoring
   - Malware detection
   - Suspicious pattern correlation
