# GDPR Compliance Documentation

## Overview

The Arbor Energy Plan Recommendation Agent is designed with privacy by design principles and complies with the General Data Protection Regulation (GDPR). This document outlines how we handle personal data and ensure compliance.

---

## Data Processing Summary

### Personal Data Collected

| Data Type | Purpose | Legal Basis | Retention |
|-----------|---------|-------------|-----------|
| External Customer ID | Customer identification | Legitimate interest | Until deletion request |
| Energy Usage Data | Recommendation generation | Consent/Contract | 2 years or until deletion |
| Preference Settings | Personalization | Consent | Until deletion request |
| IP Address | Rate limiting, security | Legitimate interest | 24 hours (logs only) |

### Data NOT Collected

- Names or email addresses
- Physical addresses
- Payment information
- Demographic data
- Device fingerprints

---

## GDPR Principles Compliance

### 1. Lawfulness, Fairness, and Transparency

**Implementation:**
- Clear privacy policy explaining data usage
- Consent obtained before data collection
- No hidden data processing

**Technical Measures:**
- All data collection is explicit via API
- No background tracking or analytics
- Usage data only processed for stated purpose

### 2. Purpose Limitation

**Implementation:**
- Data used solely for energy plan recommendations
- No secondary marketing or profiling
- No data sharing with third parties

**Technical Measures:**
```python
# Data is only used in recommendation generation
class RecommendationService:
    async def generate_recommendations(self, customer: Customer):
        # Usage data → Cost calculation → Recommendations
        # No other processing paths exist
```

### 3. Data Minimization

**Implementation:**
- Only essential data collected (usage kWh, preferences)
- No personally identifiable information required
- Anonymous external IDs supported

**Technical Measures:**
- Customer model contains minimal fields
- No optional "nice to have" data collection
- Preferences default to sensible values

### 4. Accuracy

**Implementation:**
- Users can update their data at any time
- Clear validation of input data
- No assumptions made about missing data

**Technical Measures:**
```python
# Validation ensures data accuracy
class UsageDataEntry(BaseModel):
    usage_date: date
    kwh_usage: Decimal = Field(ge=0)  # Must be non-negative
```

### 5. Storage Limitation

**Implementation:**
- Data retained only while needed
- Automatic deletion available
- No indefinite data retention

**Technical Measures:**
- Recommendations cached for 1 hour only
- Customer deletion removes all associated data
- Rate limit data expires in 24 hours

### 6. Integrity and Confidentiality

**Implementation:**
- Data encrypted in transit (HTTPS)
- Database access controls
- No plain-text sensitive data

**Technical Measures:**
- TLS 1.3 for all API communication
- PostgreSQL with authentication
- Redis with password protection

### 7. Accountability

**Implementation:**
- This documentation
- Audit logging capability
- Data processing records

---

## Data Subject Rights Implementation

### Right to Access (Article 15)

**Endpoint:** `GET /api/v1/customers/{customer_id}`

Returns all data held about a customer:
- Usage history
- Preferences
- Generated recommendations

### Right to Rectification (Article 16)

**Endpoints:**
- `PUT /api/v1/preferences/{customer_id}` - Update preferences
- `POST /api/v1/customers` - Submit corrected usage data

### Right to Erasure (Article 17)

**Endpoint:** `DELETE /api/v1/customers/{customer_id}`

Permanently deletes:
- Customer record
- All usage data (CASCADE)
- All preferences (CASCADE)
- Cached recommendations

**Implementation:**
```python
async def delete(self, customer_id: UUID) -> bool:
    customer = await self.get_by_id(customer_id)
    if not customer:
        return False
    await self.db.delete(customer)  # Cascades to related data
    await self.db.flush()
    return True
```

### Right to Restriction (Article 18)

**Implementation:**
- Customers can stop using the service
- No background processing occurs
- Data only processed on explicit API request

### Right to Data Portability (Article 20)

**Endpoint:** `GET /api/v1/customers/{customer_id}`

Returns data in JSON format suitable for transfer:
```json
{
  "id": "uuid",
  "external_id": "customer-reference",
  "usage_data": [
    {"usage_date": "2024-01-01", "kwh_usage": 950.00}
  ],
  "preferences": {
    "cost_savings_weight": 0.40
  }
}
```

### Right to Object (Article 21)

**Implementation:**
- Service is opt-in only
- No direct marketing
- No profiling beyond recommendation generation

---

## Data Anonymization

### Implementation

The `DataAnonymizer` class in `app/services/data_anonymizer.py` provides:

```python
class DataAnonymizer:
    def anonymize_customer_id(self, customer_id: str) -> str:
        """Hash customer ID for logging."""
        return hashlib.sha256(customer_id.encode()).hexdigest()[:16]

    def anonymize_usage_data(self, usage: list) -> dict:
        """Return statistical summary instead of raw data."""
        return {
            "total_kwh": sum(u.kwh_usage for u in usage),
            "months": len(usage),
            "anonymized": True
        }
```

### Usage in Logging

```python
logger.info(
    "Generated recommendations",
    customer_id=anonymizer.anonymize_customer_id(str(customer.id)),
    # Never logs raw customer ID
)
```

---

## Security Measures

### Technical Security

| Measure | Implementation |
|---------|----------------|
| Encryption in Transit | TLS 1.3 required |
| Rate Limiting | 60 req/min, 1000 req/hour |
| Input Validation | Pydantic schemas |
| SQL Injection Prevention | SQLAlchemy ORM |
| XSS Prevention | JSON API only |

### Organizational Security

- Code review required for all changes
- Dependency vulnerability scanning
- Regular security updates

---

## Data Processing Agreement (DPA) Requirements

When integrating with Arbor Energy Plan Agent, partners must:

1. **Purpose Limitation**: Only use the API for energy plan recommendations
2. **Data Security**: Protect customer data in their systems
3. **Breach Notification**: Notify Arbor within 72 hours of any breach
4. **Sub-processors**: Not share data with additional parties
5. **Deletion**: Delete customer data upon request

---

## Breach Response Plan

### Detection

- Monitoring for unusual API patterns
- Rate limit alerting
- Database access logging

### Response Steps

1. **Identify**: Determine scope and affected data
2. **Contain**: Revoke compromised credentials, block IPs
3. **Notify**: Inform supervisory authority within 72 hours
4. **Remediate**: Fix vulnerability, enhance monitoring
5. **Document**: Record incident and response

### Notification Template

```
Subject: Data Breach Notification - Arbor Energy Plan Agent

Date of Discovery: [DATE]
Nature of Breach: [DESCRIPTION]
Data Affected: [TYPES]
Customers Affected: [NUMBER]
Measures Taken: [ACTIONS]
Contact: privacy@arbor-energy.com
```

---

## Compliance Checklist

### Data Collection ✅
- [x] Only necessary data collected
- [x] Clear purpose for each data type
- [x] Consent mechanism available
- [x] No hidden data collection

### Data Storage ✅
- [x] Encrypted at rest (database)
- [x] Encrypted in transit (TLS)
- [x] Access controls implemented
- [x] Retention periods defined

### Data Subject Rights ✅
- [x] Access endpoint available
- [x] Deletion endpoint available
- [x] Data portability (JSON export)
- [x] Preference updates supported

### Security ✅
- [x] Input validation
- [x] Rate limiting
- [x] SQL injection prevention
- [x] Logging without PII

### Documentation ✅
- [x] Privacy policy
- [x] This compliance document
- [x] API documentation
- [x] Developer guide

---

## Contact

**Data Protection Inquiries:**
- Email: privacy@arbor-energy.com

**Technical Security Issues:**
- Email: security@arbor-energy.com

---

*Last Updated: 2025-01-27*
