# DECEPTRA: Future Enhancements Roadmap

As DECEPTRA moves from a local testing environment to a production deployment, the following changes and enhancements are planned:

## 1. Database Migration (PostgreSQL)
- **Current State:** Uses SQLite asynchronously.
- **Planned:** Switch to PostgreSQL. The open internet generates thousands of malicious requests per hour. SQLite will eventually experience write-locks or file bloat. Migrating to PostgreSQL will ensure enterprise-grade stability under heavy bot attacks.

## 2. Active Tarpitting (Delay Mechanisms)
- **Current State:** The server responds as fast as possible to log the data.
- **Planned:** Create a `TarpitMiddleware`. If an IP address reaches a Risk Score of `> 80`, the server will begin intentionally delaying responses (e.g., waiting 5 to 30 seconds before replying). This forces attacker scripts to hang, wasting their computing resources and slowing down their scans.

## 3. Global Firewall Integration (Active Defense)
- **Current State:** DECEPTRA observes and records.
- **Planned:** Build a background cron job that routinely queries the `/api/attacks` endpoint. Any IP flagged as `automated_scanner` or with a high Risk Score will be automatically exported and pushed to the Cloudflare WAF or AWS Security Groups of your **real** production infrastructure, banning the hacker globally.

## 4. Advanced AI Hallucinations
- **Current State:** The AI generates static fake HTML pages when a spider trap is hit.
- **Planned:** Expand the AI module to generate interactive, stateful mock environments. For example, if an attacker attempts an SQL injection, the AI will generate a fake database schema and allow the attacker to successfully "extract" fake, hallucinated credit card numbers, trapping them in an elaborate deception loop.

## 5. Dynamic Threat Signatures
- **Current State:** Attack payloads (SQLi, XSS) are identified using hardcoded regex patterns in `app/analyzer/rules.py`.
- **Planned:** Move threat signatures to a database table. This will allow administrators to add new Regex rules or import standard Snort/Suricata rules dynamically via the dashboard without needing to edit the source code or restart the server.
