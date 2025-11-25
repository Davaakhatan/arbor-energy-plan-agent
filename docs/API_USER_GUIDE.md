# API User Guide

## Introduction

The Arbor Energy Plan Recommendation API helps you find the best energy plans based on customer usage patterns and preferences. This guide covers how to integrate with the API.

## Base URL

```
Production: https://api.arbor-energy.com/api/v1
Development: http://localhost:8000/api/v1
```

## Authentication

Currently, the API uses rate limiting per IP address. Future versions will include JWT authentication.

**Rate Limits:**
- 60 requests per minute
- 1000 requests per hour

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 58
```

---

## Quick Start

### Step 1: Create a Customer

Submit customer usage data to create a customer profile:

```bash
curl -X POST /api/v1/customers \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "your-customer-id",
    "usage_data": [
      {"usage_date": "2024-01-01", "kwh_usage": 950},
      {"usage_date": "2024-02-01", "kwh_usage": 920},
      {"usage_date": "2024-03-01", "kwh_usage": 880},
      {"usage_date": "2024-04-01", "kwh_usage": 820},
      {"usage_date": "2024-05-01", "kwh_usage": 900},
      {"usage_date": "2024-06-01", "kwh_usage": 1100},
      {"usage_date": "2024-07-01", "kwh_usage": 1350},
      {"usage_date": "2024-08-01", "kwh_usage": 1300},
      {"usage_date": "2024-09-01", "kwh_usage": 1050},
      {"usage_date": "2024-10-01", "kwh_usage": 900},
      {"usage_date": "2024-11-01", "kwh_usage": 880},
      {"usage_date": "2024-12-01", "kwh_usage": 920}
    ]
  }'
```

**Response:**
```json
{
  "id": "uuid",
  "external_id": "your-customer-id",
  "created_at": "2025-01-27T10:00:00Z"
}
```

### Step 2: Generate Recommendations

Request personalized plan recommendations:

```bash
curl -X POST /api/v1/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "uuid-from-step-1",
    "preferences": {
      "cost_savings_weight": 0.40,
      "flexibility_weight": 0.20,
      "renewable_weight": 0.25,
      "supplier_rating_weight": 0.15,
      "min_renewable_percentage": 25,
      "avoid_variable_rates": false
    }
  }'
```

---

## API Endpoints

### Customers

#### Create Customer
`POST /customers`

Creates a new customer with usage history.

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| external_id | string | Yes | Your unique customer identifier |
| usage_data | array | Yes | Array of monthly usage records |
| current_plan_id | uuid | No | ID of customer's current plan |
| contract_end_date | date | No | Current contract end date |
| early_termination_fee | decimal | No | ETF for current plan |

**Usage Data Entry:**
| Field | Type | Description |
|-------|------|-------------|
| usage_date | date | First day of the month (YYYY-MM-DD) |
| kwh_usage | decimal | Kilowatt-hours used that month |

**Note:** Minimum 6 months of data required; 12 months recommended for accurate recommendations.

#### Get Customer
`GET /customers/{customer_id}`

Retrieves customer details including usage history.

---

### Preferences

#### Update Preferences
`PUT /preferences/{customer_id}`

Updates customer preference weights.

**Request Body:**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| cost_savings_weight | decimal | 0.40 | Priority for lower costs (0-1) |
| flexibility_weight | decimal | 0.20 | Priority for shorter contracts (0-1) |
| renewable_weight | decimal | 0.20 | Priority for green energy (0-1) |
| supplier_rating_weight | decimal | 0.20 | Priority for supplier ratings (0-1) |
| min_renewable_percentage | integer | 0 | Minimum renewable % required (0-100) |
| max_contract_months | integer | null | Maximum contract length |
| avoid_variable_rates | boolean | false | Exclude variable rate plans |

**Note:** Weights should sum to 1.0. The API will normalize if they don't.

---

### Recommendations

#### Generate Recommendations
`POST /recommendations`

Generates top 3 plan recommendations.

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| customer_id | uuid | Yes | Customer ID |
| preferences | object | No | Override stored preferences |
| include_switching_analysis | boolean | No | Include ETF analysis (default: true) |

**Response Structure:**
```json
{
  "customer_id": "uuid",
  "recommendations": [
    {
      "rank": 1,
      "plan": { ... },
      "overall_score": 0.85,
      "cost_score": 0.90,
      "flexibility_score": 0.70,
      "renewable_score": 0.80,
      "rating_score": 0.85,
      "projected_annual_cost": 1440.00,
      "projected_annual_savings": 240.00,
      "switching_cost": 0.00,
      "net_first_year_savings": 240.00,
      "explanation": "This plan offers excellent value...",
      "risk_flags": [],
      "confidence_level": "high"
    }
  ],
  "usage_analysis": {
    "total_annual_kwh": 11970,
    "average_monthly_kwh": 997.50,
    "seasonal_pattern": "summer_peak",
    "consumption_tier": "medium",
    "insights": { ... }
  },
  "current_annual_cost": 1680.00,
  "best_savings": 240.00,
  "processing_time_ms": 145,
  "warnings": []
}
```

---

## Response Fields Explained

### Recommendation Object

| Field | Description |
|-------|-------------|
| rank | Position in recommendations (1-3) |
| overall_score | Weighted score combining all factors (0-1) |
| cost_score | How well plan scores on cost (0-1) |
| flexibility_score | Contract flexibility score (0-1) |
| renewable_score | Green energy percentage score (0-1) |
| rating_score | Supplier rating score (0-1) |
| projected_annual_cost | Estimated yearly cost based on usage |
| projected_annual_savings | Savings vs current plan (if known) |
| switching_cost | Early termination fee if applicable |
| net_first_year_savings | Savings minus switching cost |
| explanation | Human-readable recommendation reason |
| risk_flags | Array of potential concerns |
| confidence_level | "high", "medium", or "low" |

### Risk Flags

| Code | Severity | Description |
|------|----------|-------------|
| VARIABLE_RATE | medium | Rate may fluctuate with market |
| LONG_CONTRACT | low | Contract is 24+ months |
| HIGH_ETF | medium | Early termination fee is $200+ |
| INSUFFICIENT_DATA | low | Less than 12 months of usage data |

### Usage Analysis

| Field | Description |
|-------|-------------|
| seasonal_pattern | "summer_peak", "winter_peak", "dual_peak", "flat", "unknown" |
| consumption_tier | "low", "medium", "high", "very_high" |
| usage_trend | "increasing", "decreasing", "stable", "unknown" |
| insights | Personalized recommendations based on patterns |

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message here"
}
```

### Common HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad request (validation error) |
| 404 | Resource not found |
| 422 | Unprocessable entity |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

### Validation Errors

```json
{
  "detail": [
    {
      "loc": ["body", "usage_data"],
      "msg": "Minimum 6 months of usage data required",
      "type": "value_error"
    }
  ]
}
```

---

## Best Practices

### 1. Provide Complete Usage Data

More data = better recommendations. Always provide 12 months when available.

```json
{
  "usage_data": [
    // Include all 12 months for best accuracy
  ]
}
```

### 2. Include Current Plan Information

If the customer has an existing plan, include it for accurate savings calculations:

```json
{
  "external_id": "customer-123",
  "current_plan_id": "plan-uuid",
  "contract_end_date": "2025-06-01",
  "early_termination_fee": "150.00",
  "usage_data": [...]
}
```

### 3. Handle Rate Limiting

Check response headers and implement exponential backoff:

```python
import time

def make_request():
    response = requests.post(url, json=data)

    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 60))
        time.sleep(retry_after)
        return make_request()

    return response
```

### 4. Cache Recommendations

Recommendations are cached for 1 hour. Re-generate only when:
- Customer preferences change
- Usage data is updated
- Cache expires

### 5. Validate Input Client-Side

Check data before sending to reduce round trips:
- Usage dates should be valid past dates
- kWh values should be positive
- Preference weights should sum to ~1.0

---

## SDKs and Examples

### Python Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Create customer
customer = requests.post(f"{BASE_URL}/customers", json={
    "external_id": "customer-001",
    "usage_data": [
        {"usage_date": f"2024-{m:02d}-01", "kwh_usage": 900 + m * 20}
        for m in range(1, 13)
    ]
}).json()

# Generate recommendations
recommendations = requests.post(f"{BASE_URL}/recommendations", json={
    "customer_id": customer["id"],
    "preferences": {
        "cost_savings_weight": 0.5,
        "flexibility_weight": 0.2,
        "renewable_weight": 0.2,
        "supplier_rating_weight": 0.1
    }
}).json()

# Display top recommendation
top = recommendations["recommendations"][0]
print(f"Top Plan: {top['plan']['name']}")
print(f"Projected Cost: ${top['projected_annual_cost']}/year")
print(f"Savings: ${top['projected_annual_savings']}/year")
```

### JavaScript Example

```javascript
const BASE_URL = 'http://localhost:8000/api/v1';

async function getRecommendations(externalId, usageData) {
  // Create customer
  const customerRes = await fetch(`${BASE_URL}/customers`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      external_id: externalId,
      usage_data: usageData
    })
  });
  const customer = await customerRes.json();

  // Generate recommendations
  const recsRes = await fetch(`${BASE_URL}/recommendations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      customer_id: customer.id,
      preferences: {
        cost_savings_weight: 0.4,
        flexibility_weight: 0.2,
        renewable_weight: 0.25,
        supplier_rating_weight: 0.15
      }
    })
  });

  return recsRes.json();
}
```

---

## Support

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **OpenAPI Spec**: http://localhost:8000/openapi.json

---

*Last Updated: 2025-01-27*
