# API Reference

## Authentication Endpoints

### POST /authenticate

Authenticate user with credentials.

**Request**:

```json
{
  "username": "alice",
  "password": "secure_password",
  "ip_address": "192.168.1.100"
}
```

**Response (Success)**:

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user_001",
  "created_at": "2024-01-15T10:30:45Z",
  "expires_at": "2024-01-15T11:00:45Z",
  "mfa_verified": false
}
```

**Response (Failure)**:

```json
{
  "error": "Invalid credentials",
  "status": 401
}
```

**HTTP Status**:

- `200`: Authentication successful
- `401`: Invalid credentials
- `403`: Account disabled
- `429`: Too many failed attempts

---

### POST /verify-session

Verify session is still valid.

**Request**:

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (Valid)**:

```json
{
  "valid": true,
  "user": {
    "user_id": "user_001",
    "username": "alice",
    "roles": ["admin"],
    "clearance_level": "confidential"
  }
}
```

**HTTP Status**:

- `200`: Session valid
- `401`: Session expired/invalid

---

## Risk Assessment Endpoints

### POST /assess-risk

Calculate comprehensive risk score for a user.

**Request**:

```json
{
  "user_id": "user_001",
  "access_history": [
    {
      "timestamp": "2024-01-15T08:00:00Z",
      "ip": "192.168.1.100",
      "city": "San Francisco",
      "distance_from_last": 0
    }
  ],
  "access_patterns": {
    "concurrent_sessions": 1,
    "recent_failed_logins": 0
  }
}
```

**Response**:

```json
{
  "assessment_id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "user_001",
  "total_score": 0.35,
  "risk_level": "low",
  "behavioral_score": 0.25,
  "compliance_score": 0.3,
  "anomaly_score": 0.2,
  "recommendation": "allow",
  "risk_factors": [
    {
      "name": "off_hours_access",
      "category": "behavioral",
      "score": 0.15,
      "description": "Access attempted outside business hours",
      "recommendation": "Verify access is legitimate"
    }
  ],
  "timestamp": "2024-01-15T10:30:45Z"
}
```

**HTTP Status**:

- `200`: Assessment successful
- `400`: Invalid request
- `401`: Unauthorized
- `500`: Assessment error

---

## Authorization Endpoints

### POST /authorize

Check if user is authorized for specific action.

**Request**:

```json
{
  "user_id": "user_001",
  "action": "read",
  "resource": "customer_data",
  "context": {
    "source_ip": "192.168.1.100",
    "mfa_verified": true
  }
}
```

**Response**:

```json
{
  "authorized": true,
  "decision": "allow",
  "reason": "User has USER role with READ permission",
  "applied_policies": ["zero_trust_policy", "least_privilege_policy"],
  "audit_id": "audit_12345"
}
```

**HTTP Status**:

- `200`: Authorization check completed
- `403`: Authorization denied
- `401`: Unauthorized

---

## Policy Endpoints

### GET /policies

List all active policies.

**Response**:

```json
{
  "policies": [
    {
      "policy_id": "policy_001",
      "name": "zero_trust_policy",
      "description": "Require verification for all access",
      "enabled": true,
      "version": "1.0",
      "rules_count": 5,
      "created_at": "2024-01-01T00:00:00Z",
      "last_modified": "2024-01-15T10:00:00Z"
    }
  ]
}
```

---

### GET /policies/{policy_id}

Get detailed policy information.

**Response**:

```json
{
  "policy_id": "policy_001",
  "name": "zero_trust_policy",
  "description": "Require verification for all access",
  "rules": [
    {
      "rule_id": "rule_001",
      "name": "require_mfa_for_sensitive_resources",
      "priority": 100,
      "action": "require_mfa",
      "enabled": true
    }
  ],
  "version": "1.0",
  "enabled": true
}
```

---

## Audit Endpoints

### GET /audit/trail/{user_id}

Get audit trail for specific user.

**Query Parameters**:

- `limit`: Maximum entries (default: 100)
- `start_date`: Filter by start date (ISO-8601)
- `end_date`: Filter by end date (ISO-8601)

**Response**:

```json
{
  "user_id": "user_001",
  "entries": [
    {
      "entry_id": "audit_001",
      "timestamp": "2024-01-15T10:30:45Z",
      "action": "authentication",
      "action_category": "authentication",
      "resource": "auth_service",
      "status": "success",
      "source_ip": "192.168.1.100",
      "details": {
        "success": true
      }
    }
  ],
  "total": 150,
  "returned": 100
}
```

---

### POST /audit/export-report

Export compliance report.

**Request**:

```json
{
  "report_type": "soc2", // soc2, hipaa, pci_dss
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-31T23:59:59Z"
}
```

**Response**:

```json
{
  "report_id": "report_001",
  "report_type": "soc2",
  "period": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-31T23:59:59Z"
  },
  "summary": {
    "total_events": 15432,
    "successful_authentications": 15200,
    "failed_authentications": 232,
    "policy_violations": 5,
    "access_denials": 145
  },
  "url": "s3://audit-reports/report_001.pdf"
}
```

---

## Error Responses

### Standard Error Format

```json
{
  "error": {
    "code": "AUTH_FAILED",
    "message": "Invalid username or password",
    "details": {
      "username": "alice",
      "timestamp": "2024-01-15T10:30:45Z"
    }
  },
  "status": 401,
  "request_id": "req_12345"
}
```

### Common Error Codes

| Code                | HTTP | Description                     |
| ------------------- | ---- | ------------------------------- |
| AUTH_FAILED         | 401  | Authentication failed           |
| INVALID_SESSION     | 401  | Session invalid/expired         |
| UNAUTHORIZED        | 403  | User not authorized             |
| POLICY_VIOLATION    | 403  | Access denied by policy         |
| INVALID_REQUEST     | 400  | Invalid request parameters      |
| RESOURCE_NOT_FOUND  | 404  | Resource not found              |
| RATE_LIMITED        | 429  | Too many requests               |
| INTERNAL_ERROR      | 500  | Internal server error           |
| SERVICE_UNAVAILABLE | 503  | Service temporarily unavailable |

---

## Rate Limiting

**Limits**:

- Authentication: 10 requests per minute per IP
- Authorization: 1000 requests per minute per user
- General API: 5000 requests per hour per client

**Headers**:

```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 5
X-RateLimit-Reset: 1705330245
```

---

## Pagination

For endpoints returning lists:

**Query Parameters**:

- `offset`: Starting position (default: 0)
- `limit`: Number of items (default: 20, max: 100)

**Response**:

```json
{
  "items": [...],
  "pagination": {
    "offset": 0,
    "limit": 20,
    "total": 150,
    "has_more": true
  }
}
```

---

## Webhooks

### Risk Assessment Webhook

Triggered when risk score changes significantly.

**Event**:

```json
{
  "event_type": "risk_score_changed",
  "timestamp": "2024-01-15T10:30:45Z",
  "user_id": "user_001",
  "previous_score": 0.25,
  "current_score": 0.65,
  "risk_level_change": "low → medium",
  "reason": "Multiple failed login attempts detected"
}
```

### Authorization Denial Webhook

Triggered on access denial.

**Event**:

```json
{
  "event_type": "access_denied",
  "timestamp": "2024-01-15T10:30:45Z",
  "user_id": "user_001",
  "action": "read",
  "resource": "sensitive_data",
  "reason": "Policy violation: confidential_data_require_approval",
  "risk_score": 0.75
}
```

---

## Example Implementations

### Python Client

```python
from risk_engine import RiskEngineClient

client = RiskEngineClient(base_url="https://risk-api.example.com")

# Authenticate
session = client.authenticate(
    username="alice",
    password="secure_password",
    ip_address="192.168.1.100"
)

# Assess risk
risk = client.assess_risk(
    user_id=session.user_id,
    access_history=[...],
    access_patterns={...}
)

# Check authorization
authorized = client.authorize(
    user_id=session.user_id,
    action="read",
    resource="customer_data"
)
```

### cURL Examples

```bash
# Authenticate
curl -X POST https://risk-api.example.com/authenticate \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "secure_password",
    "ip_address": "192.168.1.100"
  }'

# Assess risk
curl -X POST https://risk-api.example.com/assess-risk \
  -H "Authorization: Bearer <session_id>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_001",
    "access_history": [...],
    "access_patterns": {...}
  }'
```

---

## Backwards Compatibility

API versions are indicated by the Accept header:

```
Accept: application/vnd.risk-engine.v1+json  # v1
Accept: application/vnd.risk-engine.v2+json  # v2
```

Current version: **v1**
