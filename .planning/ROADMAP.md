# DECEPTRA Project Roadmap

**Current Status:** Phase 3 (AI Integration & Decoy Generation) — In Planning

---

## Overview

DECEPTRA is a modular FastAPI honeypot framework for attack detection and analysis.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy, SQLite, Jinja2, vanilla JS/CSS

**Core Components:**
- 🍯 **Honeypot Endpoints** — Fake /admin, /login, /.env, etc. that log all requests
- 📊 **Dashboard API** — GET /api/attacks (list), GET /api/attacks/{id} (detail)
- 🤖 **AI Layer** — Site profiling, decoy generation, forensic analysis (Phase 3)
- 🎭 **Decoy Manager** — Registry and deployment of fake assets

---

## Phase 1: Core Honeypot Infrastructure ✅ COMPLETE

**Goal:** Basic honeypot endpoints and request logging to SQLite.

**Deliverables:**
- FastAPI app with request logging middleware
- Session + Request ORM models
- Honeypot endpoints (/admin, /login, /.env, etc.)
- Request logging to SQLite database
- GET /api/health, GET /api/attacks, GET /api/attacks/{session_id}

**Completion:** ✅ All endpoints working, database persistence confirmed

---

## Phase 2: Dashboard & Forensic UI ⏳ NEXT (After Phase 3)

**Goal:** Frontend dashboard for reviewing sessions and attack patterns.

**Requirements:**
- Dashboard template with session list
- Session detail view with request timeline
- Basic attack classification (scanner, crawler, bot, etc.)
- Export session data (JSON, CSV)

**Planned tasks:**
- [ ] Jinja2 dashboard templates
- [ ] Static CSS/JS for interactivity
- [ ] Session filtering and search
- [ ] Export endpoints (GET /api/export/session/{id})

---

## Phase 3: AI Integration & Decoy Generation 🚀 IN PLANNING

**Goal:** Intelligent decoy generation using LLM-assisted site profiling and forensic analysis.

**Responsibilities (per role spec):**
- Define AI schemas (SiteProfile, DecoyAssetDefinition, ForensicSummary)
- Implement site profiler (infer tech stack from signals)
- Implement decoy generator (LLM-assisted endpoint/file creation)
- Implement response writer (fake response bodies)
- Implement forensic analyzer (session summarization)

**Plans:**

### Plan 03-01: AI Schemas & LLM Client Foundation
**Wave:** 1 (parallel-ready)

Tasks:
1. Create Pydantic schemas (SiteProfile, DecoyAssetDefinition, ForensicSummary)
2. Create LLMClient wrapper for API calls
3. Update Settings to support LLM config (api_key, model, provider)

**Verification:** Schemas validate, LLMClient instantiates, no external calls yet.

### Plan 03-02: AI Functions (Site Profiler, Decoy Generator, Response Writer, Forensic Analyzer)
**Wave:** 2 (depends on 03-01)

Tasks:
1. `generate_site_profile()` — Accept raw signals, return SiteProfile
2. `generate_decoy_assets()` — Accept SiteProfile, return DecoyAssetDefinition[]
3. `generate_response_body()` — Accept decoy + request, return fake response
4. `summarize_session()` — Accept session + requests, return ForensicSummary

**All functions:** Pure, testable, graceful fallback if LLM unavailable

**Verification:** All functions callable, return correct types, have fallback logic.

### Plan 03-03: Backend Route Integration
**Wave:** 3 (depends on 03-02)

Tasks:
1. Add POST /api/decoys/generate endpoint (AI-assisted decoy creation)
2. Extend GET /api/attacks/{session_id} with optional forensic summary
3. Update API schemas (base.py) with new types
4. Integration tests

**Verification:** New endpoints return 200, save to DB, graceful fallback, API contracts frozen.

---

## Phase 4: Decoy Deployment & Testing (Planned for future)

**Goal:** Deploy generated decoys, test honeypot detection, measure false positive rate.

**Tentative requirements:**
- [ ] Deploy decoys to live endpoints (POST /api/decoys → activate)
- [ ] Track decoy hits (spider traps, cookie/header parsing)
- [ ] A/B test different decoy themes
- [ ] Measure attacker dwell time and data exfiltration attempts

---

## API Contracts (FROZEN)

All API responses are locked. Additions must be backward compatible.

### GET /api/attacks
```json
{
  "attacks": [
    {
      "id": "uuid",
      "ip_address": "string",
      "first_request_at": "datetime",
      "last_request_at": "datetime",
      "request_count": number,
      "is_automated": boolean,
      "tags": "string"
    }
  ],
  "total": number,
  "limit": number,
  "offset": number
}
```

### GET /api/attacks/{session_id}
```json
{
  "session": {
    "id": "uuid",
    "ip_address": "string",
    "request_count": number,
    ...
  },
  "requests": [
    {
      "id": "uuid",
      "method": "string",
      "path": "string",
      "response_status": number,
      ...
    }
  ],
  "forensics": null | {
    "headline": "string",
    "description": "string",
    "techniques": ["string"],
    "confidence": number,
    "recommendations": ["string"]
  }
}
```

---

## Project Rules

From Global.txt:

1. **No folder moves:** app/core/, app/routes/, app/decoys/, app/analyzer/, app/ai/ are fixed.
2. **No breaking API changes:** Response shapes locked; add optional fields only.
3. **Code standards:**
   - Consistent naming (snake_case functions, PascalCase classes)
   - Docstrings for public functions
   - At least one test per new feature
   - All code log its actions

4. **No unauthorized AI agents:** Use external LLM APIs, don't implement agents inside the app.

---

## Development Notes

### Running Locally

```bash
# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env: set LLM_API_KEY if integrating AI

# Run
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Test
pytest test_backend.py -v
```

### Key Files

- `.planning/phases/03-ai-integration/03-*.md` — Phase plans (executable)
- `.planning/phases/03-ai-integration/03-*-SUMMARY.md` — Execution results
- `app/ai/` — AI integration layer (schemas, LLM client, functions)
- `app/routes/` — FastAPI routers (honeypots, API)
- `app/core/` — Database, settings, models

---

## Next Steps

1. **Confirm Phase 3 Plan:** Review 03-01, 03-02, 03-03 plans above
2. **Set up LLM:** Configure LLM_API_KEY in .env (OpenAI, Anthropic, etc.)
3. **Execute Phase 3:**
   - Wave 1: 03-01 (schemas + LLM client)
   - Wave 2: 03-02 (AI functions)
   - Wave 3: 03-03 (route integration + tests)
4. **Plan Phase 2:** Dashboard UI (parallel with Phase 3 development)

---

**Last Updated:** 2026-04-26  
**Project Lead:** Role: AI Integration & Decoy Generation Engineer
