# DECEPTRA: Advanced Modular Honeypot Framework

DECEPTRA is an active defense web application designed to act as a highly attractive, vulnerable target for automated scanners, bots, and human attackers. It silently records all malicious behavior, applies deterministic threat analysis, and uses AI to generate dynamic traps.

---

## 📖 Complete System Manual

### 1. Initial Setup & Configuration
Before running the system, ensure your environment is configured properly.

1. **Activate your virtual environment:**
   ```bash
   myenv/Scripts/Activate
   ```
2. **Configure AI Settings:**
   Open the `.env` file in the root directory and define your LLM settings. You can use OpenAI or local models like Ollama.
   ```env
   # Example using local Ollama
   LLM_API_KEY=ollama
   LLM_BASE_URL=http://localhost:11434/v1
   LLM_MODEL_NAME=dolphin-llama3:latest
   ```

### 2. Running the Honeypot Server
To start the traps and begin listening for attacks, run the Uvicorn server.
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
* **What this does:** Starts the FastAPI application on port 8000. The `--reload` flag ensures that any changes you make to the Python code are instantly applied without needing to restart the server. The `RequestLoggingMiddleware` immediately begins intercepting all traffic.

### 3. Viewing the Dashboard (Visual Threat Intel)
You don't need to read raw JSON in the terminal! DECEPTRA includes a built-in UI.
1. Open your web browser.
2. Navigate to: `http://localhost:8000/dashboard/sessions`
* **Features:** 
  * The main table displays the Attacker IP, Timestamp, Tags, and the attacker's **User-Agent** (so you can spot scripts vs humans).
  * Clicking on an individual session opens the **Timeline View**.
  * Expanding a row in the timeline reveals the exact **Raw Headers** (yellow), **Request Payloads/Passwords** (red), and **Honeypot Responses** (blue).
  * Click the **Generate AI Summary ✨** button to automatically generate a full forensic report using your local LLM.

### 4. Running the Bot Simulator
To test your honeypot without waiting for a real hacker to find it, you can simulate an automated attack.
```bash
python tests/simulate_bot.py http://localhost:8000
```
* **What this does:** The script acts as an automated scanner. It probes for `.env` files, attempts SQL injections, tries Cross-Site Scripting (XSS), brute-forces the `/login` endpoint, and intentionally falls into hidden spider traps.

### 5. Manual Attack Simulation (The "Outside" Hack)
You can attack your own server manually from a separate terminal using `curl.exe` to see how DECEPTRA catches you:
* **Reconnaissance Probe:** `curl.exe http://localhost:8000/.env`
* **SQL Injection:** `curl.exe "http://localhost:8000/users?id=1' OR '1'='1"`
* **Brute Force Post:** `curl.exe -X POST http://localhost:8000/login -d "username=admin&password=SuperSecretPassword"`
* **Spider Trap:** `curl.exe http://localhost:8000/hidden/admin-portal`

### 6. Using the API Endpoints (Data Extraction)
If you want to pull the raw data out of DECEPTRA for a custom application (like `admin.html`) or a SIEM tool, use these endpoints:

* **List all Attacker Sessions:**
  ```bash
  curl http://localhost:8000/api/attacks
  ```
* **View Full Forensic Timeline of a Session:**
  *(Replace the UUID with one from the list above)*
  ```bash
  curl http://localhost:8000/api/attacks/cefba455-b21b-4ed2-9330-066c43c42309
  ```
* **Generate AI Forensic Summary:**
  ```bash
  curl http://localhost:8000/api/attacks/cefba455-b21b-4ed2-9330-066c43c42309/summary
  ```

### 6. Running the Unit Tests
If you modify the threat detection logic in `app/analyzer/rules.py`, you should always run the test suite to ensure the math and logic are still perfectly accurate.
```bash
python -m pytest tests/test_analyzer.py -v
```

---

## 🚀 Future Roadmap & Planned Changes

As DECEPTRA moves from a local testing environment to a production deployment, the following changes and enhancements are planned:

### 1. Database Migration (PostgreSQL)
* **Current State:** Uses SQLite asynchronously.
* **Planned:** Switch to PostgreSQL. The open internet generates thousands of malicious requests per hour. SQLite will eventually experience write-locks or file bloat. Migrating to PostgreSQL will ensure enterprise-grade stability under heavy bot attacks.

### 2. Active Tarpitting (Delay Mechanisms)
* **Current State:** The server responds as fast as possible to log the data.
* **Planned:** Create a `TarpitMiddleware`. If an IP address reaches a Risk Score of `> 80`, the server will begin intentionally delaying responses (e.g., waiting 5 to 30 seconds before replying). This forces attacker scripts to hang, wasting their computing resources and slowing down their scans.

### 3. Global Firewall Integration (Active Defense)
* **Current State:** DECEPTRA observes and records.
* **Planned:** Build a background cron job that routinely queries the `/api/attacks` endpoint. Any IP flagged as `automated_scanner` or with a high Risk Score will be automatically exported and pushed to the Cloudflare WAF or AWS Security Groups of your **real** production infrastructure, banning the hacker globally.

### 4. Advanced AI Hallucinations
* **Current State:** The AI generates static fake HTML pages when a spider trap is hit.
* **Planned:** Expand the AI module to generate interactive, stateful mock environments. For example, if an attacker attempts an SQL injection, the AI will generate a fake database schema and allow the attacker to successfully "extract" fake, hallucinated credit card numbers, trapping them in an elaborate deception loop.

### 5. Dynamic Threat Signatures
* **Current State:** Attack payloads (SQLi, XSS) are identified using hardcoded regex patterns in `app/analyzer/rules.py`.
* **Planned:** Move threat signatures to a database table. This will allow administrators to add new Regex rules or import standard Snort/Suricata rules dynamically via the dashboard without needing to edit the source code or restart the server.