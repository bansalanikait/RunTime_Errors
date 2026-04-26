"""Script to simulate attacker bot traffic against the honeypot."""

import sys
import time
import urllib.request
import urllib.error
import urllib.parse
from dataclasses import dataclass

BASE_URL = "http://localhost:8000"

@dataclass
class Scenario:
    name: str
    path: str
    method: str = "GET"
    data: dict = None
    headers: dict = None

def simulate_request(scenario: Scenario):
    print(f"[*] Running: {scenario.name} -> {scenario.method} {scenario.path}")
    encoded_path = urllib.parse.quote(scenario.path, safe='/?&=')
    url = f"{BASE_URL}{encoded_path}"
    
    headers = scenario.headers or {}
    data = None
    if scenario.data:
        data = urllib.parse.urlencode(scenario.data).encode('utf-8')
        
    req = urllib.request.Request(url, data=data, headers=headers, method=scenario.method)
    
    try:
        start = time.time()
        with urllib.request.urlopen(req) as response:
            status = response.status
            body = response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        status = e.code
        body = e.read().decode('utf-8')
    except urllib.error.URLError as e:
        print(f"[-] Connection failed: {e.reason}")
        return
        
    duration = time.time() - start
    print(f"    Status: {status} | Time: {duration:.2f}s")
    # print(f"    Response preview: {body[:100]}...")

def run_scenarios():
    scenarios = [
        Scenario("Recon: env file", "/.env"),
        Scenario("Recon: wp-login", "/wp-login.php"),
        Scenario("Recon: git config", "/.git/config"),
        Scenario("Exploit: SQLi in URL", "/search?q=' OR 1=1 --"),
        Scenario("Exploit: XSS in URL", "/product?id=<script>alert(1)</script>"),
        Scenario("Spider Trap: Admin Portal", "/hidden/admin-portal"),
        Scenario("Spider Trap: Robots bait", "/robots-bait"),
    ]
    
    # Add brute force scenario
    for i in range(5):
        scenarios.append(Scenario(
            f"Brute Force: Login attempt {i+1}", 
            "/login", 
            method="POST", 
            data={"username": "admin", "password": f"password{i}"}
        ))
        
    for s in scenarios:
        simulate_request(s)
        time.sleep(0.5)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1].rstrip("/")
    print(f"Starting bot simulation against {BASE_URL}...")
    run_scenarios()
    print("Simulation complete.")
