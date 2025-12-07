import httpx
import asyncio
from gateway.app.main import app

# Use ASGITransport to test the app directly without a running server
async def _run_test_rate_limit():
    print("Starting Rate Limit Test...")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/metrics")
        print(f"Initial Metrics: {resp.json()}")

        print("Sending 15 requests (Limit is 10/min)...")
        for i in range(15):
            resp = await client.get("/proxy/test")
            print(f"Request {i+1}: Status {resp.status_code}")
            if resp.status_code == 429:
                print("Rate limit hit!")

        resp = await client.get("/metrics")
        print(f"Final Metrics: {resp.json()}")


def test_rate_limit():
    asyncio.run(_run_test_rate_limit())


if __name__ == "__main__":
    test_rate_limit()
