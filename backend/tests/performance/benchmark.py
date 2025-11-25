"""
Performance Benchmark Tests

Run with:
    python -m tests.performance.benchmark

Measures response times against the <2 second target.
"""

import asyncio
import statistics
import time
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any
from uuid import uuid4

import httpx

BASE_URL = "http://localhost:8000"
TARGET_RESPONSE_TIME = 2.0  # seconds


@dataclass
class BenchmarkResult:
    """Result of a benchmark test."""
    name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    min_time: float
    max_time: float
    avg_time: float
    median_time: float
    p95_time: float
    p99_time: float
    requests_per_second: float
    meets_target: bool


def generate_usage_data(months: int = 12) -> list[dict]:
    """Generate test usage data."""
    return [
        {
            "usage_date": (date.today() - timedelta(days=30 * i)).isoformat(),
            "kwh_usage": 1000 + (i * 50)
        }
        for i in range(months)
    ]


async def create_test_customer(client: httpx.AsyncClient) -> str | None:
    """Create a customer for testing."""
    response = await client.post(
        f"{BASE_URL}/api/v1/customers",
        json={
            "external_id": f"benchmark-{uuid4().hex[:8]}",
            "usage_data": generate_usage_data(12)
        }
    )
    if response.status_code == 200:
        return response.json()["id"]
    return None


async def benchmark_endpoint(
    client: httpx.AsyncClient,
    name: str,
    method: str,
    url: str,
    json_data: dict | None = None,
    iterations: int = 100
) -> BenchmarkResult:
    """Benchmark a single endpoint."""
    times: list[float] = []
    successful = 0
    failed = 0

    start_total = time.perf_counter()

    for _ in range(iterations):
        start = time.perf_counter()
        try:
            if method == "GET":
                response = await client.get(url)
            elif method == "POST":
                response = await client.post(url, json=json_data)
            elif method == "PUT":
                response = await client.put(url, json=json_data)
            else:
                raise ValueError(f"Unknown method: {method}")

            elapsed = time.perf_counter() - start
            times.append(elapsed)

            if response.status_code in [200, 201]:
                successful += 1
            else:
                failed += 1
        except Exception:
            failed += 1
            times.append(time.perf_counter() - start)

    total_time = time.perf_counter() - start_total

    # Calculate statistics
    sorted_times = sorted(times)
    p95_index = int(len(sorted_times) * 0.95)
    p99_index = int(len(sorted_times) * 0.99)

    return BenchmarkResult(
        name=name,
        total_requests=iterations,
        successful_requests=successful,
        failed_requests=failed,
        min_time=min(times),
        max_time=max(times),
        avg_time=statistics.mean(times),
        median_time=statistics.median(times),
        p95_time=sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1],
        p99_time=sorted_times[p99_index] if p99_index < len(sorted_times) else sorted_times[-1],
        requests_per_second=iterations / total_time,
        meets_target=statistics.mean(times) < TARGET_RESPONSE_TIME
    )


def print_result(result: BenchmarkResult) -> None:
    """Print benchmark result."""
    status = "✅ PASS" if result.meets_target else "❌ FAIL"

    print(f"\n{'=' * 60}")
    print(f"Benchmark: {result.name}")
    print(f"{'=' * 60}")
    print(f"Status: {status} (target: <{TARGET_RESPONSE_TIME}s)")
    print(f"Total Requests: {result.total_requests}")
    print(f"Successful: {result.successful_requests}")
    print(f"Failed: {result.failed_requests}")
    print(f"\nResponse Times:")
    print(f"  Min:    {result.min_time * 1000:.2f}ms")
    print(f"  Max:    {result.max_time * 1000:.2f}ms")
    print(f"  Avg:    {result.avg_time * 1000:.2f}ms")
    print(f"  Median: {result.median_time * 1000:.2f}ms")
    print(f"  P95:    {result.p95_time * 1000:.2f}ms")
    print(f"  P99:    {result.p99_time * 1000:.2f}ms")
    print(f"\nThroughput: {result.requests_per_second:.2f} req/s")


async def run_benchmarks() -> list[BenchmarkResult]:
    """Run all benchmarks."""
    results: list[BenchmarkResult] = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        print("\n🚀 Starting Performance Benchmarks")
        print("=" * 60)
        print(f"Target: All endpoints < {TARGET_RESPONSE_TIME}s average response time")
        print("=" * 60)

        # 1. Health Check (baseline)
        result = await benchmark_endpoint(
            client,
            "Health Check",
            "GET",
            f"{BASE_URL}/api/v1/health",
            iterations=200
        )
        print_result(result)
        results.append(result)

        # 2. Get Plans (cached)
        result = await benchmark_endpoint(
            client,
            "Get Plans (cached)",
            "GET",
            f"{BASE_URL}/api/v1/plans",
            iterations=100
        )
        print_result(result)
        results.append(result)

        # 3. Create Customer
        print("\n⏳ Creating test customers for benchmarks...")
        customer_ids: list[str] = []
        for _ in range(10):
            cid = await create_test_customer(client)
            if cid:
                customer_ids.append(cid)

        if not customer_ids:
            print("❌ Failed to create test customers")
            return results

        # 4. Get Customer
        result = await benchmark_endpoint(
            client,
            "Get Customer",
            "GET",
            f"{BASE_URL}/api/v1/customers/{customer_ids[0]}",
            iterations=100
        )
        print_result(result)
        results.append(result)

        # 5. Generate Recommendations (main target)
        preferences = {
            "cost_savings_weight": 0.4,
            "flexibility_weight": 0.2,
            "renewable_weight": 0.2,
            "supplier_rating_weight": 0.2
        }

        result = await benchmark_endpoint(
            client,
            "Generate Recommendations",
            "POST",
            f"{BASE_URL}/api/v1/recommendations",
            json_data={
                "customer_id": customer_ids[0],
                "preferences": preferences
            },
            iterations=50
        )
        print_result(result)
        results.append(result)

        # 6. Update Preferences
        result = await benchmark_endpoint(
            client,
            "Update Preferences",
            "PUT",
            f"{BASE_URL}/api/v1/preferences/{customer_ids[0]}",
            json_data=preferences,
            iterations=50
        )
        print_result(result)
        results.append(result)

        # 7. Concurrent Recommendations (stress test)
        print("\n⏳ Running concurrent recommendations stress test...")
        start = time.perf_counter()
        concurrent_tasks = [
            client.post(
                f"{BASE_URL}/api/v1/recommendations",
                json={"customer_id": cid, "preferences": preferences}
            )
            for cid in customer_ids
        ]
        responses = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
        concurrent_time = time.perf_counter() - start

        successful = sum(1 for r in responses if isinstance(r, httpx.Response) and r.status_code == 200)
        print(f"\n{'=' * 60}")
        print("Concurrent Recommendations (10 simultaneous)")
        print(f"{'=' * 60}")
        print(f"Successful: {successful}/10")
        print(f"Total Time: {concurrent_time * 1000:.2f}ms")
        print(f"Avg per request: {concurrent_time / 10 * 1000:.2f}ms")

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        passed = sum(1 for r in results if r.meets_target)
        total = len(results)
        print(f"Passed: {passed}/{total} benchmarks")

        if passed == total:
            print("✅ All benchmarks passed!")
        else:
            print("❌ Some benchmarks failed target")
            for r in results:
                if not r.meets_target:
                    print(f"   - {r.name}: {r.avg_time * 1000:.2f}ms (target: <{TARGET_RESPONSE_TIME * 1000}ms)")

    return results


if __name__ == "__main__":
    asyncio.run(run_benchmarks())
