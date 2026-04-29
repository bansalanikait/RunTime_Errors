# DECEPTRA: Full System Architecture & Results

This document serves as the complete technical blueprint for the DECEPTRA Honeypot framework, detailing the exact technology stack, the functional architecture of every feature, and the real-world results achieved during development.

---

## 1. The Full Tech Stack

DECEPTRA is built entirely on modern, asynchronous, and AI-ready technologies to ensure maximum performance and flexibility.

* **Core Backend Framework**: **FastAPI (Python)**. Chosen for its extreme speed, native `async/await` support, and automatic API documentation.
* **Database & ORM**: **SQLite + SQLAlchemy (async)**. Stores thousands of malicious requests efficiently while allowing complex relational queries between IP Sessions and HTTP Requests.
* **Frontend Dashboard**: **Jinja2, HTML5, Vanilla JS, CSS**. A lightweight, dependency-free dashboard. No heavy React/Vue builds are required, ensuring the honeypot remains stealthy and easy to deploy.
* **AI / Intelligence Layer**: **Ollama (dolphin-llama3)**. Local, uncensored LLM integration that processes attack data without sending sensitive forensic logs to the cloud (like OpenAI).
* **Data Validation**: **Pydantic**. Strictly enforces the data structures coming *into* the API and the JSON data coming *out* of the AI, preventing hallucinations from breaking the dashboard.

---

## 2. Core Features: How It Works

DECEPTRA is not a firewall that blocks traffic; it is an active defense system that gathers intelligence.

### A. The Request Logging Middleware (The Interceptor)
* **How it works:** Before an attacker's HTTP request even touches the routing logic of the server, the `RequestLoggingMiddleware` intercepts it. 
* **What it does:** It logs the IP Address, Timestamp, Method, Path, User-Agent, Raw Headers, and the Request Body (Payload). If the IP is new, it creates a new `Session`. If the IP is known, it appends the request to their timeline.

### B. The Threat Analyzer Engine (Deterministic Tagging)
* **How it works:** Once the middleware intercepts the request, the Analyzer scans the data against known threat signatures using Regex.
* **What it does:** If an attacker types `' OR 1=1` into a URL, the Analyzer instantly tags the session with `sqli_attempt`. If they ask for `/.env`, they are tagged with `recon_probe`. This allows admins to filter hackers by "crime" on the dashboard.

### C. Dynamic Decoys & Spider Traps (The Honeypot)
* **How it works:** DECEPTRA hosts fake endpoints (like `/login` or `/hidden/admin-portal`).
* **What it does:** Normal users cannot see these links. Automated hacking bots and web scrapers find them by brute force. When a bot clicks a spider trap, DECEPTRA logs a high-confidence `spider_trap_hit` tag. When they attempt to guess a password on `/login`, DECEPTRA returns a fake `401 Unauthorized` but secretly records their password guess in the database.

### D. The Visual Dashboard (The Command Center)
* **How it works:** Instead of reading terminal logs, the admin navigates to `/dashboard`.
* **What it does:** The Javascript fetches data from the backend APIs and constructs a beautiful UI. It shows a list of all attackers, their IP addresses, their User-Agents, and their tags. Clicking an attacker expands a full timeline of every click they made, revealing their hidden HTTP headers and the exact payloads (passwords) they injected.

### E. AI Forensic Summarization (The Brain)
* **How it works:** The admin clicks the "Generate AI Summary" button on the dashboard.
* **What it does:** The backend queries the database for the attacker's last 50 requests. It strips out heavy metadata to optimize the payload size, packages it into a strict prompt, and sends it to the local Ollama LLM. The AI analyzes the attack timeline, identifies the hacker's goals, and returns a strict JSON object containing a Headline, Description, Techniques, and Security Recommendations, which is instantly rendered on the screen.

---

## 3. Real Results Achieved

During the final phase of development and integration, the following real-world results and engineering hurdles were successfully resolved:

1. **Defeated the Windows "Frozen Server" Deadlock:** 
   * **Result:** Resolved an issue where Windows PowerShell's "QuickEdit Mode" and ghost `uvicorn` processes were locking the SQLite database and freezing the server for up to 20 minutes. The server now processes requests and AI calls in under 10 seconds.
2. **Eliminated LLM Context Overflow:**
   * **Result:** Initially, sending hundreds of raw request logs to the local LLM caused memory overflows and infinite generation loops. By implementing a sliding window (truncating to the 50 most recent requests) and stripping non-essential data, the AI now returns hyper-accurate summaries instantly.
3. **Strict AI JSON Enforcement:**
   * **Result:** Fixed an issue where the LLM's conversational text (e.g., "Here is your report:") was crashing the dashboard. Pydantic schemas and strict JSON formatting flags now guarantee the AI only outputs machine-readable data.
4. **100% Forensic Data Visibility:**
   * **Result:** Successfully modified the API schemas and frontend JavaScript to expose critical hidden data. Admins can now visually read the attacker's `User-Agent`, `Raw Headers`, and `Request Body` directly in the UI timeline without querying the database manually.
