import asyncio
import os
import sys

# Add current directory to path so we can import app
sys.path.append(os.getcwd())

from app.ai.generator import summarize_session
from app.ai.schemas import ForensicSummary

async def diagnostic():
    print("--- FULL GENERATOR TEST ---")
    # Mock realistic session data (50 requests)
    requests_data = []
    for i in range(50):
        requests_data.append({
            "method": "GET" if i % 2 == 0 else "POST",
            "path": f"/api/test/{i}",
            "time": "2026-04-28 10:00:00"
        })
    
    session_data = [{
        "ip": "127.0.0.1",
        "tags": "recon, automated",
        "activity": requests_data
    }]
    
    try:
        print("Calling summarize_session...")
        summary = await summarize_session(session_data)
        print("Success! Response object:")
        if isinstance(summary, ForensicSummary):
            print(summary.model_dump_json(indent=2))
        else:
            print(summary)
    except Exception as e:
        print(f"FAILED: {e}")
    print("--- TEST END ---")

if __name__ == "__main__":
    asyncio.run(diagnostic())
