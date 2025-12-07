import httpx
import asyncio
import pytest

GATEWAY_URL = "http://localhost:8001"

def test_rate_limit():
    asyncio.run(_run_test_rate_limit())

async def _run_test_rate_limit():
    print("Starting Rate Limit Test...")

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{GATEWAY_URL}/metrics")
        print(f"Initial Metrics: {resp.json()}")

        print("Sending 15 requests (Limit is 10/min)...")
        for i in range(15):
            resp = await client.get(f"{GATEWAY_URL}/proxy/test")
            print(f"Request {i+1}: Status {resp.status_code}")
            if resp.status_code == 429:
                print("Rate limit hit!")

        resp = await client.get(f"{GATEWAY_URL}/metrics")
        print(f"Final Metrics: {resp.json()}")


if __name__ == "__main__":
    test_rate_limit()
