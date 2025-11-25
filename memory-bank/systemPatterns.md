# System Patterns: AI Energy Plan Recommendation Agent

**Organization:** Arbor  
**Project ID:** 85twgWvlJ3Z1g6dpiGy5_1762214728178

## Architecture Overview

### High-Level Architecture

```
Client Layer (Web/Mobile)
    ↓
API Gateway (Authentication, Rate Limiting)
    ↓
Application Layer
    ├── Recommendation Service
    ├── Data Processing Service
    └── Preference Management Service
    ↓
Data Layer
    ├── Customer Usage DB (TimescaleDB)
    ├── Supplier Catalog DB (PostgreSQL)
    ├── Preferences & Cache (Redis)
    └── Object Storage (Encrypted)
    ↓
External Services
    ├── Supplier APIs
    ├── Usage Data APIs
    └── Monitoring & Logging
```

## Core Components

### 1. Recommendation Service

**Purpose**: Core recommendation engine that generates personalized plan recommendations

**Responsibilities**:
- Analyze 12 months of usage data
- Calculate projected costs for each plan
- Compute annual savings
- Rank plans based on customer preferences
- Generate top 3 recommendations
- Create plain-language explanations
- Perform risk assessment

**Key Algorithms**:
- Usage pattern analysis (seasonal, peak detection)
- Cost projection engine
- Multi-criteria decision analysis (MCDA)
- Risk assessment and flagging

**Performance Target**: < 2 seconds per recommendation

**Design Patterns**:
- Strategy Pattern: Different recommendation strategies based on preferences
- Factory Pattern: Generate different explanation types
- Observer Pattern: Monitor recommendation quality

### 2. Data Processing Service

**Purpose**: Handle data ingestion, validation, and transformation

**Responsibilities**:
- Ingest customer usage data (12 months kWh)
- Process current plan details
- Import and update supplier plan catalog
- Data validation and sanitization
- Data anonymization for privacy
- Data transformation for analysis

**Design Patterns**:
- Pipeline Pattern: Data processing pipeline
- Validator Pattern: Data validation chain
- Adapter Pattern: Adapt different data sources

### 3. Preference Management Service

**Purpose**: Capture and apply customer preferences

**Responsibilities**:
- Store customer preferences
- Apply preference weights to recommendations
- Support multiple preference types:
  - Cost savings priority
  - Contract flexibility
  - Renewable energy percentage
  - Supplier ratings

**Design Patterns**:
- Strategy Pattern: Different weighting strategies
- Builder Pattern: Build preference profiles

## Data Flow Patterns

### Recommendation Generation Flow

```
1. Customer submits usage data + preferences
   ↓
2. Data Processing Service validates and stores
   ↓
3. Recommendation Service:
   a. Retrieves customer usage (12 months)
   b. Retrieves current plan details
   c. Retrieves supplier plan catalog
   d. Analyzes usage patterns
   e. Calculates costs for each plan
   f. Applies preference weights
   g. Ranks plans
   h. Selects top 3
   i. Generates explanations
   j. Performs risk assessment
   ↓
4. Returns recommendations to client
```

### Data Ingestion Flow

```
1. External API / Upload provides data
   ↓
2. Data Processing Service:
   a. Validates data format
   b. Sanitizes data
   c. Anonymizes customer identifiers
   d. Stores in appropriate database
   ↓
3. Triggers catalog update if supplier data
```

## Database Schema Patterns

### Customer Usage Database (TimescaleDB)

**Schema**: Time-series data for 12 months
- `date`: Timestamp
- `kwh_usage`: Decimal
- `customer_id`: UUID (anonymized)
- `created_at`: Timestamp
- `updated_at`: Timestamp

**Indexes**: 
- Primary: (customer_id, date)
- Time-series: date (for time-range queries)

### Supplier Plan Catalog Database (PostgreSQL)

**Schema**: Plan attributes and pricing
- `plan_id`: UUID
- `supplier_id`: UUID
- `supplier_name`: String
- `plan_name`: String
- `rate_structure`: JSON (variable/fixed/tiered)
- `rate_value`: Decimal
- `contract_length_months`: Integer
- `early_termination_fee`: Decimal
- `renewable_percentage`: Decimal
- `supplier_rating`: Decimal
- `plan_features`: JSON
- `effective_date`: Date
- `expiration_date`: Date
- `created_at`: Timestamp
- `updated_at`: Timestamp

**Indexes**:
- Primary: plan_id
- Supplier: supplier_id
- Active plans: (effective_date, expiration_date)

### Preferences & Cache (Redis)

**Structure**: Key-value store
- Key: `preferences:{customer_id}`
- Value: JSON object with preference weights
- TTL: 24 hours

## API Design Patterns

### RESTful API Structure

```
POST   /api/v1/customers/{customer_id}/usage
GET    /api/v1/customers/{customer_id}/usage
POST   /api/v1/customers/{customer_id}/preferences
GET    /api/v1/customers/{customer_id}/preferences
POST   /api/v1/customers/{customer_id}/recommendations
GET    /api/v1/customers/{customer_id}/recommendations/{recommendation_id}
GET    /api/v1/suppliers/plans
POST   /api/v1/suppliers/plans/import
```

### Response Patterns

**Success Response**:
```json
{
  "status": "success",
  "data": { ... },
  "metadata": {
    "timestamp": "2025-01-27T...",
    "request_id": "uuid"
  }
}
```

**Error Response**:
```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": { ... }
  },
  "metadata": {
    "timestamp": "2025-01-27T...",
    "request_id": "uuid"
  }
}
```

## Security Patterns

### Authentication & Authorization
- OAuth 2.0 / JWT tokens
- Role-based access control (RBAC)
- API key management for external services

### Data Security
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- Data anonymization for customer data
- Secure key management (AWS KMS / GCP KMS)

### Privacy Patterns
- GDPR compliance:
  - Right to access
  - Right to deletion
  - Data portability
  - Privacy by design

## Performance Patterns

### Caching Strategy
- Cache supplier plan catalog (updated periodically)
- Cache user preferences
- Cache computed recommendations (with TTL)
- CDN for static assets

### Database Optimization
- Indexed queries for time-series data
- Connection pooling
- Read replicas for scaling
- Query optimization and materialized views

### Async Processing
- Background jobs for data ingestion
- Queue-based processing for heavy computations
- WebSocket for real-time updates (if needed)

## Scalability Patterns

### Horizontal Scaling
- Stateless API services (scale horizontally)
- Database read replicas
- Load balancing across instances
- Auto-scaling based on metrics

### Vertical Scaling
- Optimize database performance
- Increase compute resources for recommendation engine

## Monitoring Patterns

### Metrics
- API response times
- Recommendation generation time
- Error rates
- Throughput (requests per second)
- Database query performance
- Cache hit rates

### Logging
- Structured logging (JSON format)
- Log aggregation and search
- Error tracking and alerting

---

*Last Updated: 2025-01-27*

