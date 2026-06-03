import asyncio
import aiohttp
import time

URL = "http://127.0.0.1:8000/predict"
PAYLOAD = {"text": "This framework is great awesome excellent fast easy good love but terrible slow bad break fail"}
CONCURRENT_REQUESTS = 100 

async def send_request(session):
    try:
        async with session.post(URL, json=PAYLOAD) as response:
            await response.json()
    except Exception:
        pass

async def worker(session):
    
    while True:
        await send_request(session)

async def main():
    print("Starting CONTINUOUS stress test. Press Ctrl+C to stop...")
    connector = aiohttp.TCPConnector(limit=CONCURRENT_REQUESTS)
    async with aiohttp.ClientSession(connector=connector) as session:
        
        tasks = [worker(session) for _ in range(CONCURRENT_REQUESTS)]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStress test stopped by user.")