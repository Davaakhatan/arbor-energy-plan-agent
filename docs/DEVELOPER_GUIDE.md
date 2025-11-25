# Developer Onboarding Guide

## Overview

The Arbor Energy Plan Recommendation Agent is an AI-powered system that helps customers find the best energy plans based on their usage patterns and preferences. This guide will help you get started with development.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Local Development Setup](#local-development-setup)
4. [Backend Development](#backend-development)
5. [Frontend Development](#frontend-development)
6. [Testing](#testing)
7. [API Reference](#api-reference)
8. [Common Tasks](#common-tasks)

---

## Prerequisites

### Required Software

- **Docker & Docker Compose** - For running PostgreSQL and Redis
- **Python 3.11+** - Backend runtime
- **Node.js 20+** - Frontend runtime
- **pnpm** - Package manager for frontend

### Recommended Tools

- VS Code with Python and TypeScript extensions
- PostgreSQL client (pgAdmin, DBeaver, or CLI)
- Redis client (RedisInsight or CLI)

---

## Project Structure

```
arbor-energy-plan-agent/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/v1/         # API endpoints
│   │   ├── core/           # Config, database, logging
│   │   ├── middleware/     # Rate limiting, timing
│   │   ├── models/         # SQLAlchemy models
│   │   ├── repositories/   # Database access layer
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Business logic
│   ├── alembic/            # Database migrations
│   └── tests/              # Test suites
├── frontend/               # Next.js frontend
│   └── src/
│       ├── app/            # Next.js app router
│       ├── components/     # React components
│       ├── lib/            # API client, utilities
│       └── types/          # TypeScript types
├── docs/                   # Documentation
└── docker-compose.yml      # Development services
```

---

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Davaakhatan/arbor-energy-plan-agent.git
cd arbor-energy-plan-agent
```

### 2. Start Infrastructure Services

```bash
docker-compose up -d postgres redis
```

This starts:
- PostgreSQL on port 5432
- Redis on port 6379

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Run database migrations
alembic upgrade head

# Seed initial data
python -m app.scripts.seed_data

# Start the server
uvicorn app.main:app --reload --port 8000
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
pnpm install

# Set up environment
cp .env.example .env.local

# Start development server
pnpm dev
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Backend Development

### Technology Stack

- **FastAPI** - Web framework
- **SQLAlchemy 2.0** - ORM with async support
- **Pydantic** - Data validation
- **Redis** - Caching
- **Alembic** - Database migrations

### Key Services

#### RecommendationService (`app/services/recommendation.py`)
Main service that orchestrates the recommendation flow:
- Fetches customer data and preferences
- Retrieves cached plans
- Calculates costs using CostCalculator
- Scores plans using ScoringEngine (MCDA)
- Generates explanations and risk flags

#### CostCalculator (`app/services/cost_calculator.py`)
Calculates projected annual costs:
- Rate per kWh × usage
- Monthly fees × 12
- Handles different rate types (fixed, variable, time-of-use)

#### ScoringEngine (`app/services/scoring.py`)
Implements Multi-Criteria Decision Analysis:
- Normalizes scores across dimensions
- Applies preference weights
- Generates overall scores for ranking

#### UsageAnalyzer (`app/services/usage_analyzer.py`)
Analyzes customer usage patterns:
- Seasonal pattern detection (summer/winter peak)
- Usage trend analysis
- Consumption tier classification

### Creating a New Endpoint

1. Define the schema in `app/schemas/`
2. Add the route in `app/api/v1/`
3. Implement business logic in `app/services/`
4. Add tests in `tests/`

Example:
```python
# app/api/v1/endpoints/example.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

router = APIRouter()

@router.get("/example")
async def get_example(db: AsyncSession = Depends(get_db)):
    return {"message": "Hello"}
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

---

## Frontend Development

### Technology Stack

- **Next.js 15** - React framework with App Router
- **React 19** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **TanStack Query** - Data fetching
- **Zustand** - State management

### Key Components

#### UsageDataForm (`src/components/features/UsageDataForm.tsx`)
Handles monthly kWh input with CSV upload support.

#### PreferenceForm (`src/components/features/PreferenceForm.tsx`)
Preference weight sliders with real-time normalization.

#### RecommendationCard (`src/components/features/RecommendationCard.tsx`)
Displays individual plan recommendations with scores and explanations.

### Adding a New Component

1. Create component in `src/components/`
2. Use existing UI primitives from `src/components/ui/`
3. Follow accessibility guidelines (ARIA labels, keyboard navigation)

Example:
```tsx
// src/components/features/MyComponent.tsx
"use client";

import { Button } from "@/components/ui/Button";

interface MyComponentProps {
  title: string;
}

export function MyComponent({ title }: MyComponentProps) {
  return (
    <div role="region" aria-label={title}>
      <h2>{title}</h2>
      <Button>Action</Button>
    </div>
  );
}
```

### API Integration

Use the API client in `src/lib/api.ts`:

```typescript
import { customersApi, recommendationsApi } from "@/lib/api";

// Create customer
const customer = await customersApi.create(data);

// Generate recommendations
const recommendations = await recommendationsApi.generate(customerId, preferences);
```

---

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/unit/test_cost_calculator.py

# Run specific test
pytest tests/unit/test_cost_calculator.py::test_fixed_rate_calculation
```

### Frontend Tests

```bash
cd frontend

# Run all tests
pnpm test

# Run with watch mode
pnpm test:watch

# Run with coverage
pnpm test:coverage
```

### Test Categories

- **Unit Tests**: Individual functions and classes
- **Integration Tests**: API endpoints with database
- **E2E Tests**: Complete user flows
- **Security Tests**: Input validation, injection prevention
- **Accessibility Tests**: WCAG 2.1 compliance

---

## API Reference

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/customers` | Create customer with usage data |
| GET | `/api/v1/customers/{id}` | Get customer details |
| PUT | `/api/v1/preferences/{customer_id}` | Update preferences |
| POST | `/api/v1/recommendations` | Generate recommendations |
| GET | `/api/v1/health` | Health check |

### Example: Create Customer

```bash
curl -X POST http://localhost:8000/api/v1/customers \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "customer-001",
    "usage_data": [
      {"usage_date": "2024-01-01", "kwh_usage": 950},
      {"usage_date": "2024-02-01", "kwh_usage": 900}
    ]
  }'
```

### Example: Generate Recommendations

```bash
curl -X POST http://localhost:8000/api/v1/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "uuid-here",
    "preferences": {
      "cost_savings_weight": 0.4,
      "flexibility_weight": 0.2,
      "renewable_weight": 0.2,
      "supplier_rating_weight": 0.2
    }
  }'
```

---

## Common Tasks

### Adding a New Energy Plan Field

1. Update the model: `backend/app/models/plan.py`
2. Create migration: `alembic revision --autogenerate -m "add field"`
3. Update schema: `backend/app/schemas/plan.py`
4. Update frontend type: `frontend/src/types/index.ts`

### Modifying the Scoring Algorithm

1. Edit `backend/app/services/scoring.py`
2. Update tests in `backend/tests/unit/test_scoring.py`
3. Run tests to verify: `pytest tests/unit/test_scoring.py`

### Adding a New Preference Weight

1. Update preference model: `backend/app/models/preference.py`
2. Update scoring engine to use new weight
3. Update frontend slider in `PreferenceForm.tsx`
4. Update types in both backend and frontend

### Debugging Performance Issues

1. Check `X-Response-Time` header in API responses
2. Review logs for slow request warnings
3. Check Redis cache hit rates
4. Use `EXPLAIN ANALYZE` on slow queries

---

## Environment Variables

### Backend (.env)

```env
ENVIRONMENT=development
DEBUG=true
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=arbor
POSTGRES_PASSWORD=arbor_dev
POSTGRES_DB=arbor_energy
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Getting Help

- **Architecture**: See `docs/ARCHITECTURE.md`
- **Product Requirements**: See `docs/PRD.md`
- **Task Tracking**: See `docs/TASKS.md`
- **API Documentation**: http://localhost:8000/docs

---

*Last Updated: 2025-01-27*
