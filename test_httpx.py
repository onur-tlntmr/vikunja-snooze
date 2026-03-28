import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        headers = {
            "Title": "🔔 Vikunja: test".encode("utf-8"),
            "Actions": "http, ✅ Complete, http://localhost/complete".encode("utf-8")
        }
        print("Sending request to port 8081...")
        try:
            await client.post("http://127.0.0.1:8081", headers=headers, content=b"body")
        except Exception as e:
            print(f"Exception: {e}")

asyncio.run(main())
