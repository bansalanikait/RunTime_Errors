import asyncio
import httpx
import json

async def test():
    print("--- RAW NATIVE OLLAMA TEST ---")
    client = httpx.AsyncClient(timeout=30.0)
    # Native endpoint
    url = 'http://localhost:11434/api/chat'
    payload = {
        'model': 'dolphin-llama3:latest',
        'messages': [{'role': 'user', 'content': 'Respond with JSON: {"test": "ok"}'}],
        'stream': False,
        'format': 'json'
    }
    try:
        print(f"Sending request to {url} with model dolphin-llama3:latest...")
        resp = await client.post(url, json=payload)
        print(f"Status: {resp.status_code}")
        print("Body:")
        print(resp.text)
    except Exception as e:
        print(f"Error: {e}")
    print("--- TEST END ---")

if __name__ == "__main__":
    asyncio.run(test())
