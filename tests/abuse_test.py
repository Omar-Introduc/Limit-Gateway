import asyncio
import httpx
import os
import json
import time

# Configuration
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8001")
NUM_REQUESTS = 100
EVIDENCE_DIR = ".evidence"
REPORT_FILE = os.path.join(EVIDENCE_DIR, "abuse-test-report.json")


async def run_abuse_test():
    print(f"Starting abuse test against {GATEWAY_URL} with {NUM_REQUESTS} requests...")

    # Ensure evidence directory exists
    os.makedirs(EVIDENCE_DIR, exist_ok=True)

    results = {
        "total_requests": NUM_REQUESTS,
        "success_count": 0,
        "blocked_count": 0,
        "other_status_count": 0,
        "status_codes": {},
        "initial_metrics": {},
        "final_metrics": {},
    }

    async with httpx.AsyncClient(base_url=GATEWAY_URL, timeout=10.0) as client:
        # 1. Get Initial Metrics
        try:
            resp = await client.get("/metrics")
            if resp.status_code == 200:
                results["initial_metrics"] = resp.json()
                print(f"Initial Metrics: {results['initial_metrics']}")
            else:
                print(f"Failed to get initial metrics: {resp.status_code}")
        except Exception as e:
            print(f"Error fetching initial metrics: {e}")

        # 2. Send rapid requests
        start_time = time.time()
        # Create all tasks at once
        tasks = [client.get("/proxy/test") for _ in range(NUM_REQUESTS)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()

        results["duration_seconds"] = end_time - start_time
        print(
            f"Sent {NUM_REQUESTS} requests in {results['duration_seconds']:.2f} seconds"
        )

        # 3. Analyze responses
        for resp in responses:
            if isinstance(resp, Exception):
                print(f"Request failed: {resp}")
                continue

            code = resp.status_code
            results["status_codes"][code] = results["status_codes"].get(code, 0) + 1

            if code == 200:
                results["success_count"] += 1
            elif code == 429:
                results["blocked_count"] += 1
            else:
                results["other_status_count"] += 1

        # 4. Get Final Metrics
        try:
            resp = await client.get("/metrics")
            if resp.status_code == 200:
                results["final_metrics"] = resp.json()
                print(f"Final Metrics: {results['final_metrics']}")
            else:
                print(f"Failed to get final metrics: {resp.status_code}")
        except Exception as e:
            print(f"Error fetching final metrics: {e}")

    # 5. Generate Report
    with open(REPORT_FILE, "w") as f:
        json.dump(results, f, indent=4)

    print(f"Report generated at {REPORT_FILE}")
    print(
        f"Summary: Success={results['success_count']}, Blocked={results['blocked_count']}"
    )

    # Validation Logic for CI/Verification - Verify block happened if rate limit is low enough
    # Note: We rely on the user knowing the limit. If 100 requests in <1s don't trigger limit, something is wrong.
    if results["blocked_count"] > 0:
        print("SUCCESS: Rate limiting detected.")
    else:
        print("WARNING: No requests were blocked.")


if __name__ == "__main__":
    asyncio.run(run_abuse_test())
