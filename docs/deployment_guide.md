# Identity Risk Scoring Engine - Deployment & Operations Guide

## Local Development Setup

### Prerequisites

- Python 3.9+
- pip/conda
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/yourname/identity-risk-scoring-engine.git
cd identity-risk-scoring-engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e ".[dev]"
```

### Running Examples

```bash
# Basic usage example
python examples/basic_usage.py

# Advanced scenario
python examples/advanced_scenario.py
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# With coverage report
pytest tests/ --cov=src --cov-report=html

# Specific test module
pytest tests/test_risk_calculator.py -v
```

## Configuration

### Environment Variables

```bash
# Environment
ENVIRONMENT=development  # development, staging, production

# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=risk_engine
DB_PASSWORD=secure_password
DB_NAME=risk_engine

# Cache
CACHE_ENABLED=true
CACHE_URL=memory  # or redis://localhost:6379/0
CACHE_TTL=3600

# Security
JWT_SECRET_KEY=your-secret-key-change-in-prod
SESSION_TIMEOUT=30

# Audit
AUDIT_ENABLED=true
AUDIT_IMMUTABLE=true
SOC2_MODE=true
HIPAA_MODE=false
```

### Configuration File

Create `config.json`:

```json
{
  "environment": "production",
  "log_level": "INFO",
  "database": {
    "host": "db.example.com",
    "port": 5432,
    "username": "risk_engine",
    "password": "secure_password",
    "database": "risk_engine_prod"
  },
  "cache": {
    "enabled": true,
    "ttl_seconds": 3600,
    "backend_url": "redis://redis.example.com:6379/0"
  }
}
```

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY examples/ ./examples/

ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

CMD ["python", "-m", "uvicorn", "risk_engine.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: "3.8"

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: risk_engine
      POSTGRES_PASSWORD: secure_password
      POSTGRES_DB: risk_engine
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  risk-engine:
    build: .
    ports:
      - "8000:8000"
    environment:
      DB_HOST: postgres
      DB_USER: risk_engine
      DB_PASSWORD: secure_password
      DB_NAME: risk_engine
      CACHE_URL: redis://redis:6379/0
      ENVIRONMENT: production
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
```

Run with: `docker-compose up`

## Kubernetes Deployment

### Helm Chart Structure

```
helm-chart/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   └── rbac.yaml
```

### Deploy to Kubernetes

```bash
# Install
helm install risk-engine ./helm-chart --namespace security

# Upgrade
helm upgrade risk-engine ./helm-chart --namespace security

# Uninstall
helm uninstall risk-engine --namespace security
```

## Monitoring & Observability

### Logging

Structured logging using JSON format for SIEM integration:

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "INFO",
  "service": "risk_engine",
  "user_id": "user_001",
  "action": "authentication",
  "status": "success",
  "ip_address": "192.168.1.100",
  "risk_score": 0.35
}
```

### Metrics

Expose Prometheus metrics:

```
risk_engine_authentication_duration_seconds{user_id="user_001"} 0.045
risk_engine_authorization_decision_total{decision="allow"} 15432
risk_engine_risk_score_gauge{user_id="user_001"} 0.35
```

### Health Checks

```bash
# Health endpoint
curl http://localhost:8000/health

# Readiness check (dependencies OK)
curl http://localhost:8000/ready

# Liveness check (process alive)
curl http://localhost:8000/live
```

## Performance Tuning

### Database Optimization

```sql
-- Index for user lookups
CREATE INDEX idx_users_username ON users(username);

-- Index for audit queries
CREATE INDEX idx_audit_logs_user_timestamp
  ON audit_logs(actor_id, timestamp DESC);

-- Index for policy lookups
CREATE INDEX idx_policies_enabled ON policies(enabled)
  WHERE enabled = true;
```

### Caching Strategy

```python
# Cache configuration
cache_config = CacheConfig(
    ttl_seconds=3600,        # 1 hour
    max_entries=10000,       # Max cached policies
    backend_url="redis://redis:6379/0"
)
```

### Connection Pooling

```python
# Database pool tuning
db_config = DatabaseConfig(
    pool_size=20,           # Active connections
    max_overflow=40,        # Additional connections if needed
)
```

## Security Hardening

### TLS/SSL

All connections must use TLS 1.3:

```python
security_config = SecurityConfig(
    require_https=True,
    jwt_algorithm="HS256",
)
```

### Secrets Management

```bash
# Use environment variables (development)
export JWT_SECRET_KEY="$(openssl rand -hex 32)"

# Use K8s secrets (production)
kubectl create secret generic risk-engine-secrets \
  --from-literal=jwt-secret-key=$(openssl rand -hex 32)
```

### Rate Limiting

```python
# Implement rate limiting
from fastapi_limiter import FastAPILimiter

@app.get("/authenticate")
@limiter.limit("5/minute")
async def authenticate(username: str, password: str):
    # Max 5 auth attempts per minute per IP
    pass
```

## Backup & Disaster Recovery

### Backup Strategy

```bash
# Daily backup of audit logs
0 2 * * * pg_dump risk_engine > /backups/audit-$(date +%Y-%m-%d).sql

# Archive old logs to S3
30 3 * * 0 aws s3 sync /var/log/risk-engine s3://audit-archive/
```

### Recovery Procedures

1. **Database Failure**: Restore from latest backup, replay transaction logs
2. **Data Corruption**: Use point-in-time recovery with binary logs
3. **Complete Loss**: Deploy from backup, restore audit logs

## Compliance Verification

### Audit Compliance

```bash
# Generate SOC 2 compliance report
python -m risk_engine.compliance.soc2_report --output report.json

# Generate HIPAA report
python -m risk_engine.compliance.hipaa_report --output report.json

# Generate PCI-DSS report
python -m risk_engine.compliance.pci_dss_report --output report.json
```

### Audit Log Integrity

```python
# Verify audit log tamper-proof hash
def verify_audit_integrity():
    for entry in audit_store.get_all():
        computed_hash = entry.compute_hash()
        if computed_hash != entry.hash:
            raise TamperDetectionError(f"Log entry {entry.id} was modified")
```

## Troubleshooting

### Common Issues

**Issue**: High risk scores for all users

```bash
# Check configuration
python -c "from risk_engine.config import get_config; print(get_config().risk_scoring)"

# Verify risk calculator logic
pytest tests/test_risk_calculator.py -v
```

**Issue**: Audit logs not being written

```bash
# Check audit store connection
python -c "from risk_engine.iam import AuditLogger; AuditLogger().log_store.test_connection()"

# Verify audit is enabled
python -c "from risk_engine.config import get_config; print(get_config().audit.enabled)"
```

**Issue**: Sessions expiring unexpectedly

```bash
# Check session configuration
python -c "from risk_engine.config import get_config; print(get_config().security.session_timeout_minutes)"

# Verify clock synchronization between nodes
ntpq -p  # Check NTP sync
```

## Support & Escalation

- **Issues**: GitHub Issues
- **Security**: security@example.com
- **On-call**: PagerDuty integration enabled
