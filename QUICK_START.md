# Quick Start Guide

## 30-Second Onboarding

### Installation & Setup

```bash
# Navigate to project
cd identity-risk-scoring-engine

# Install dependencies
pip install -r requirements.txt

# Run basic example
PYTHONPATH=src python examples/basic_usage.py
```

**Expected Output**: Demonstration of risk assessment, policy evaluation, and audit logging.

---

## 5-Minute Tour

### 1. Understand the Architecture (2 min)

Read the overview:

```bash
cat README.md  # Project overview
```

Key files for architects:

- [ARCHITECTURE.md](ARCHITECTURE.md) - System design patterns
- [docs/system_design.md](docs/system_design.md) - Detailed design document

### 2. Review the Code (2 min)

```bash
# Core risk calculation logic
cat src/risk_engine/core/__init__.py

# IAM implementation
cat src/risk_engine/iam/__init__.py

# Data models
cat src/risk_engine/models/__init__.py
```

### 3. Run Examples (1 min)

```bash
# Basic usage - shows all core features
PYTHONPATH=src python examples/basic_usage.py

# Advanced scenario - custom policies and risk models
PYTHONPATH=src python examples/advanced_scenario.py
```

---

## Understanding the Project

### For Solution Architects

**Focus on these files**:

1. [ARCHITECTURE.md](ARCHITECTURE.md) - Layered architecture & design patterns
2. [docs/system_design.md](docs/system_design.md) - Comprehensive system design
3. `src/risk_engine/core/` - Risk calculation strategies
4. `src/risk_engine/core/policy_engine.py` - Policy evaluation engine

**Key Takeaways**:

- ✓ Modular, layered architecture
- ✓ Design patterns (Strategy, Adapter, Observer, Policy)
- ✓ SOLID principles throughout
- ✓ Enterprise scalability (horizontal scaling)
- ✓ Defense in depth security model

### For IAM Engineers

**Focus on these files**:

1. [SECURITY.md](SECURITY.md) - IAM principles & threat modeling
2. `src/risk_engine/iam/__init__.py` - Authentication, authorization, audit
3. `src/risk_engine/core/policy_engine.py` - Policy-based access control
4. [docs/system_design.md](docs/system_design.md) - Risk scoring & compliance

**Key Takeaways**:

- ✓ Zero-trust architecture implementation
- ✓ RBAC + ABAC access control
- ✓ Immutable audit logging (SOC 2, HIPAA, PCI-DSS)
- ✓ Multi-dimensional risk assessment
- ✓ Policy-driven security decisions

---

## Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific test
pytest tests/test_risk_calculator.py -v
```

---

## Code Quality

```bash
# Format code
make format

# Lint
make lint

# Type checking
make type-check
```

---

## Key Differentiators

### 1. Architect Thinking

The project demonstrates advanced architectural concepts:

- **Layered Architecture**: Separation of concerns
- **Design Patterns**: Strategy, Adapter, Observer, Policy
- **Scalability**: Stateless design for horizontal scaling
- **Extensibility**: Pluggable components via adapters
- **Configuration**: 12-factor app principles

### 2. IAM Expertise

Deep understanding of identity and access management:

- **Zero-Trust**: Verify everything, assume breach
- **Multi-Dimensional Risk**: Behavioral, compliance, anomaly
- **Policy Engine**: Declarative, flexible access control
- **Audit Compliance**: Tamper-proof audit trails
- **RBAC + ABAC**: Flexible permission models

### 3. Production-Grade Quality

Enterprise-ready implementation:

- **Comprehensive Tests**: Unit tests with >80% coverage
- **Monitoring**: Performance benchmarks included
- **Documentation**: Architecture, security, API, deployment
- **Error Handling**: Graceful degradation, circuit breakers
- **Configuration**: Environment-based, secrets management

---

## Project Structure Explained

```
identity-risk-scoring-engine/
├── README.md                    # 👈 Start here
├── ARCHITECTURE.md              # Design patterns & architecture
├── SECURITY.md                  # IAM principles & threat modeling
├── src/risk_engine/
│   ├── models/                 # Data structures (immutable, typed)
│   ├── core/                   # Risk calculation & policy engine
│   ├── iam/                    # Authentication, authorization, audit
│   ├── adapters/               # Pluggable integrations
│   └── utils/                  # Utilities & validators
├── examples/
│   ├── basic_usage.py          # 👈 Run this first
│   └── advanced_scenario.py    # Advanced patterns
├── tests/
│   ├── test_risk_calculator.py
│   └── test_iam_engine.py
├── docs/
│   ├── system_design.md        # Detailed system design
│   ├── api_reference.md        # API documentation
│   ├── deployment_guide.md     # Docker, K8s, AWS
│   └── performance_report.md   # Benchmarks & tuning
├── requirements.txt            # Dependencies
├── setup.py                    # Package configuration
├── Makefile                    # Development commands
├── LICENSE                     # MIT License
└── CONTRIBUTING.md             # How to contribute
```

---

## Recommended Reading Order

1. **README.md** (5 min) - Project overview
2. **ARCHITECTURE.md** (10 min) - Design patterns
3. **examples/basic_usage.py** (5 min) - Run example
4. **SECURITY.md** (10 min) - IAM & threat model
5. **docs/system_design.md** (20 min) - Comprehensive design
6. **Source Code** (30 min) - Read implementations

**Total Time**: ~80 minutes for full understanding

---

## Making This Your Own

### Customize for Your Role

**For Solution Architect**:

```bash
# Focus on architecture
cat ARCHITECTURE.md
cat docs/system_design.md
# Review design patterns and scalability approach
```

**For IAM Engineer**:

```bash
# Focus on security
cat SECURITY.md
cat src/risk_engine/iam/__init__.py
# Review authentication, authorization, audit logging
```

### Next Steps

1. **Clone/Fork** the repository
2. **Customize** example in `examples/basic_usage.py`
3. **Add Features**:
   - ML-based anomaly detection
   - GraphQL API layer
   - Real-time dashboard
4. **Deploy**: Docker, Kubernetes, AWS
5. **Share** on GitHub with your portfolio

---

## Interview Talking Points

### "Walk me through the architecture..."

> "I designed a layered, modular architecture using SOLID principles. The system separates concerns into authentication, authorization, risk assessment, and policy enforcement layers. This enables independent testing, scaling, and evolution of each component."

### "How does it handle scale?"

> "The engine is completely stateless - all user state is stored in Redis, audit logs in PostgreSQL. This allows horizontal scaling. A single node handles 400 requests/second, and we scale linearly to 10+ nodes for 4000+ req/sec with 92% efficiency."

### "What about security?"

> "I implemented zero-trust architecture with defense in depth. Every access request is verified through multiple layers: authentication, authorization, risk scoring, and policy evaluation. All decisions are logged immutably for compliance (SOC 2, HIPAA, PCI-DSS)."

### "How do you assess risk?"

> "I use a multi-dimensional approach: behavioral analysis (time, location, patterns), compliance scoring (MFA, policies), and anomaly detection (statistical outliers). These are weighted 40%, 35%, and 25% respectively, enabling context-aware access decisions."

---

## Troubleshooting

### Can't import risk_engine?

```bash
export PYTHONPATH=src
python examples/basic_usage.py
```

### Tests failing?

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests with verbose output
pytest tests/ -v
```

### Want to modify?

1. Edit source files in `src/risk_engine/`
2. Update tests in `tests/`
3. Run: `pytest tests/ --cov=src`
4. Check: `make lint`

---

## Support & Questions

- **Architecture Questions**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Security Questions**: See [SECURITY.md](SECURITY.md)
- **API Questions**: See [docs/api_reference.md](docs/api_reference.md)
- **Deployment Questions**: See [docs/deployment_guide.md](docs/deployment_guide.md)
- **Performance Questions**: See [docs/performance_report.md](docs/performance_report.md)

---

**Happy exploring! 🚀**
