"""
Load Testing with Locust

Run with:
    locust -f tests/performance/locustfile.py --host=http://localhost:8000

Web UI: http://localhost:8089
"""

import random
import uuid
from datetime import date, timedelta

from locust import HttpUser, between, task


class ArborEnergyUser(HttpUser):
    """Simulates a typical user flow for the Arbor Energy Plan Agent."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    customer_id = None

    def on_start(self):
        """Called when a user starts - create a customer."""
        self.customer_id = self.create_customer()

    def generate_usage_data(self, months: int = 12) -> list[dict]:
        """Generate realistic usage data."""
        base_usage = random.uniform(800, 1500)
        usage_data = []

        for i in range(months):
            usage_date = date.today() - timedelta(days=30 * (months - i))
            # Add seasonal variation
            month = usage_date.month
            if month in [6, 7, 8]:  # Summer
                seasonal_factor = random.uniform(1.2, 1.5)
            elif month in [12, 1, 2]:  # Winter
                seasonal_factor = random.uniform(1.1, 1.3)
            else:
                seasonal_factor = random.uniform(0.9, 1.1)

            kwh = round(base_usage * seasonal_factor + random.uniform(-50, 50), 2)
            usage_data.append({
                "usage_date": usage_date.isoformat(),
                "kwh_usage": max(100, kwh)  # Ensure positive usage
            })

        return usage_data

    def create_customer(self) -> str | None:
        """Create a new customer with usage data."""
        external_id = f"load-test-{uuid.uuid4().hex[:8]}"
        usage_data = self.generate_usage_data(12)

        response = self.client.post(
            "/api/v1/customers",
            json={
                "external_id": external_id,
                "usage_data": usage_data
            },
            name="/api/v1/customers [POST]"
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("id")
        return None

    @task(5)
    def get_recommendations(self):
        """Get recommendations - most common operation."""
        if not self.customer_id:
            return

        preferences = {
            "cost_savings_weight": random.uniform(0.2, 0.5),
            "flexibility_weight": random.uniform(0.1, 0.3),
            "renewable_weight": random.uniform(0.1, 0.3),
            "supplier_rating_weight": random.uniform(0.1, 0.3)
        }

        # Normalize weights
        total = sum(preferences.values())
        preferences = {k: round(v / total, 2) for k, v in preferences.items()}

        self.client.post(
            "/api/v1/recommendations",
            json={
                "customer_id": self.customer_id,
                "preferences": preferences
            },
            name="/api/v1/recommendations [POST]"
        )

    @task(3)
    def get_customer(self):
        """Get customer details."""
        if not self.customer_id:
            return

        self.client.get(
            f"/api/v1/customers/{self.customer_id}",
            name="/api/v1/customers/{id} [GET]"
        )

    @task(2)
    def update_preferences(self):
        """Update customer preferences."""
        if not self.customer_id:
            return

        preferences = {
            "cost_savings_weight": random.uniform(0.2, 0.5),
            "flexibility_weight": random.uniform(0.1, 0.3),
            "renewable_weight": random.uniform(0.1, 0.3),
            "supplier_rating_weight": random.uniform(0.1, 0.3),
            "avoid_variable_rates": random.choice([True, False]),
            "min_renewable_percentage": random.randint(0, 50)
        }

        # Normalize weights
        total = (
            preferences["cost_savings_weight"] +
            preferences["flexibility_weight"] +
            preferences["renewable_weight"] +
            preferences["supplier_rating_weight"]
        )
        for key in ["cost_savings_weight", "flexibility_weight",
                    "renewable_weight", "supplier_rating_weight"]:
            preferences[key] = round(preferences[key] / total, 2)

        self.client.put(
            f"/api/v1/preferences/{self.customer_id}",
            json=preferences,
            name="/api/v1/preferences/{id} [PUT]"
        )

    @task(1)
    def health_check(self):
        """Check API health."""
        self.client.get("/api/v1/health", name="/api/v1/health [GET]")

    @task(1)
    def get_plans(self):
        """Get available plans."""
        self.client.get("/api/v1/plans", name="/api/v1/plans [GET]")


class HighLoadUser(HttpUser):
    """Simulates high-load scenarios focusing on recommendations."""

    wait_time = between(0.5, 1)  # Faster requests
    customer_id = None

    def on_start(self):
        """Create customer on start."""
        self.customer_id = self._create_customer()

    def _create_customer(self) -> str | None:
        """Create customer with minimal data."""
        response = self.client.post(
            "/api/v1/customers",
            json={
                "external_id": f"high-load-{uuid.uuid4().hex[:8]}",
                "usage_data": [
                    {"usage_date": (date.today() - timedelta(days=30 * i)).isoformat(),
                     "kwh_usage": random.uniform(800, 1200)}
                    for i in range(12)
                ]
            },
            name="/api/v1/customers [POST] (high-load)"
        )
        if response.status_code == 200:
            return response.json().get("id")
        return None

    @task
    def rapid_recommendations(self):
        """Rapid recommendation requests to test caching."""
        if not self.customer_id:
            return

        self.client.post(
            "/api/v1/recommendations",
            json={
                "customer_id": self.customer_id,
                "preferences": {
                    "cost_savings_weight": 0.4,
                    "flexibility_weight": 0.2,
                    "renewable_weight": 0.2,
                    "supplier_rating_weight": 0.2
                }
            },
            name="/api/v1/recommendations [POST] (high-load)"
        )


class SpikeTestUser(HttpUser):
    """Simulates traffic spikes."""

    wait_time = between(0.1, 0.3)  # Very fast requests

    @task
    def health_spike(self):
        """Spike health check requests."""
        self.client.get("/api/v1/health", name="/api/v1/health [SPIKE]")

    @task
    def plans_spike(self):
        """Spike plans requests."""
        self.client.get("/api/v1/plans", name="/api/v1/plans [SPIKE]")
