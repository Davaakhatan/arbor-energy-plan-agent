# Privacy Policy

**Effective Date:** January 27, 2025
**Last Updated:** January 27, 2025

---

## Introduction

Arbor Energy Plan Recommendation Agent ("we," "our," or "the Service") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, store, and protect your information when you use our energy plan recommendation service.

---

## Information We Collect

### Information You Provide

| Data Type | Description | Purpose |
|-----------|-------------|---------|
| External Customer ID | A reference identifier you assign | Links your data across sessions |
| Monthly Usage Data | Your electricity consumption in kWh | Generate accurate recommendations |
| Preference Settings | Your priorities (cost, flexibility, renewable, ratings) | Personalize recommendations |
| Current Plan Details | Your existing energy plan information | Calculate potential savings |

### Information Collected Automatically

| Data Type | Description | Retention |
|-----------|-------------|-----------|
| IP Address | Your network address | 24 hours (logs only) |
| Request Timestamps | When you access the service | 24 hours (logs only) |
| API Response Times | Performance metrics | Aggregated only |

### Information We Do NOT Collect

- Personal names or email addresses
- Physical home addresses
- Payment or banking information
- Social security or government IDs
- Demographic information (age, gender, income)
- Device fingerprints or tracking cookies
- Location data beyond IP address

---

## How We Use Your Information

### Primary Uses

1. **Generate Recommendations**: Your usage data and preferences are used to calculate and rank energy plans that best match your needs.

2. **Calculate Savings**: We compare your current plan costs against available alternatives to show potential savings.

3. **Improve Service**: Aggregated, anonymized usage patterns help us improve our recommendation algorithms.

### We Do NOT Use Your Data For

- Marketing or advertising
- Selling to third parties
- Building user profiles for other purposes
- Automated decision-making with legal effects

---

## Data Storage and Security

### Storage Location

All data is stored in secure cloud infrastructure within the United States/European Union.

### Security Measures

| Layer | Protection |
|-------|------------|
| Transport | TLS 1.3 encryption for all API communication |
| Database | Encrypted at rest with access controls |
| Application | Input validation, SQL injection prevention |
| Infrastructure | Rate limiting (60 req/min, 1000 req/hour) |

### Data Retention

| Data Type | Retention Period |
|-----------|------------------|
| Customer Usage Data | Until deletion requested or 2 years of inactivity |
| Preferences | Until deletion requested |
| Cached Recommendations | 1 hour |
| Access Logs | 24 hours |

---

## Your Rights

Under GDPR and similar privacy regulations, you have the following rights:

### Right to Access

Request a copy of all data we hold about you.

**How to exercise:** Call `GET /api/v1/customers/{your_id}`

### Right to Rectification

Correct inaccurate data or update your information.

**How to exercise:**
- Update preferences: `PUT /api/v1/preferences/{your_id}`
- Submit corrected usage: `POST /api/v1/customers`

### Right to Erasure ("Right to be Forgotten")

Request permanent deletion of all your data.

**How to exercise:** Call `DELETE /api/v1/customers/{your_id}`

This will delete:
- Your customer record
- All usage history
- All preference settings
- Any cached recommendations

### Right to Data Portability

Receive your data in a machine-readable format (JSON).

**How to exercise:** Call `GET /api/v1/customers/{your_id}`

### Right to Restrict Processing

You control when your data is processed. We only process data when you explicitly request recommendations.

### Right to Object

Since our service is opt-in and we don't perform marketing or profiling, you exercise this right by simply not using the service.

---

## Data Sharing

### Third-Party Sharing

We do NOT share your personal data with third parties for:
- Marketing purposes
- Data brokering
- Analytics services
- Social media platforms

### Service Providers

We may use service providers (cloud hosting, database services) who process data on our behalf. These providers:
- Are bound by data processing agreements
- Only access data necessary for their service
- Are prohibited from using data for other purposes

### Legal Requirements

We may disclose data if required by law, such as:
- Court orders
- Legal proceedings
- Government requests (with proper legal basis)

We will notify you of such requests unless legally prohibited.

---

## Cookies and Tracking

### Our Approach

The Arbor Energy Plan Recommendation Agent API does **not** use:
- Cookies
- Browser fingerprinting
- Tracking pixels
- Third-party analytics

### Frontend Application

If you use our web interface, we may use:
- Session storage (cleared when you close the browser)
- Local storage for your preferences (stays on your device)

No data from local/session storage is transmitted to our servers.

---

## Children's Privacy

Our service is not intended for children under 16 years of age. We do not knowingly collect data from children. If you believe a child has provided us data, please contact us for immediate deletion.

---

## International Data Transfers

If you access our service from outside our hosting region:
- Data transfers are protected by TLS encryption
- We comply with applicable data transfer regulations
- EU users: We use Standard Contractual Clauses where required

---

## Changes to This Policy

We may update this Privacy Policy periodically. Changes will be:
- Posted on this page with a new "Last Updated" date
- Communicated through our API changelog if significant
- Effective immediately upon posting

We encourage you to review this policy periodically.

---

## Data Protection Officer

For privacy-related inquiries:

**Email:** privacy@arbor-energy.com

**Response Time:** Within 30 days for formal requests

---

## Contact Us

### General Inquiries
Email: support@arbor-energy.com

### Privacy Concerns
Email: privacy@arbor-energy.com

### Security Issues
Email: security@arbor-energy.com

---

## Regulatory Compliance

This Privacy Policy is designed to comply with:

- **GDPR** (General Data Protection Regulation) - EU
- **CCPA** (California Consumer Privacy Act) - California, US
- **LGPD** (Lei Geral de Proteção de Dados) - Brazil

### CCPA-Specific Rights (California Residents)

California residents have additional rights:
- Right to know what data is collected
- Right to delete personal information
- Right to opt-out of data sales (we don't sell data)
- Right to non-discrimination for exercising rights

---

## Summary

| Topic | Our Practice |
|-------|--------------|
| Data Collected | Minimal (usage kWh, preferences only) |
| Data Sold | Never |
| Third-Party Marketing | None |
| Cookies/Tracking | None |
| Data Retention | Until you delete or 2 years inactive |
| Your Control | Full access, update, delete rights |
| Security | Encrypted, access-controlled, rate-limited |

---

*If you have any questions about this Privacy Policy, please contact us at privacy@arbor-energy.com*
