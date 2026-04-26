# Phase 3: AI Integration & Decoy Generation — Planning Complete

**Date:** April 26, 2026  
**Role:** AI Integration & Decoy Generation Engineer  
**Status:** 3 executable phase plans created ✅

---

## What Just Happened

I've created a complete phase plan for implementing the AI Integration & Decoy Generation layer of DECEPTRA. This breaks down into **three executable plans** organized by dependencies and wave execution.

### Files Created

```
.planning/
├── ROADMAP.md                              # Project roadmap
└── phases/
    └── 03-ai-integration/
        ├── 03-01-PLAN.md                   # Schemas + LLM client
        ├── 03-02-PLAN.md                   # AI functions
        └── 03-03-PLAN.md                   # Backend integration
```

---

## The Three Plans

### **Plan 03-01: Schemas & LLM Foundation**
**Wave:** 1 (Parallel-ready — no dependencies)

**Deliverables:**
- ✅ Pydantic schemas: `SiteProfile`, `DecoyAssetDefinition`, `ForensicSummary`
- ✅ LLM client wrapper: `LLMClient` class + `get_llm_client()` factory
- ✅ Settings extended: `llm_api_key`, `llm_model`, `llm_provider`, `llm_temperature`
- ✅ Module: `app/ai/schemas.py` and `app/ai/llm_client.py`

**Effort:** ~2 hours (mostly boilerplate + Pydantic models)  
**Verification:** All imports work, schemas validate example data, no external API calls yet

**Run this first** — everything else depends on it.

---

### **Plan 03-02: AI Functions**
**Wave:** 2 (Depends on 03-01)

**Deliverables:**
- ✅ `generate_site_profile()` — Raw signals → SiteProfile
- ✅ `generate_decoy_assets()` — SiteProfile → DecoyAssetDefinition[]
- ✅ `generate_response_body()` — Decoy + request → Fake response body
- ✅ `summarize_session()` — Session requests → ForensicSummary
- ✅ Modules: `app/ai/site_profiler.py`, `app/ai/decoy_generator.py`, `app/ai/response_writer.py`, `app/ai/forensic_analyzer.py`

**Key Features:**
- Pure functions (input → output, no side effects)
- Graceful fallback if LLM unavailable (returns defaults)
- All validated against Pydantic schemas
- Logging at INFO/ERROR level

**Effort:** ~3-4 hours (prompt engineering + LLM integration)  
**Verification:** All functions callable, return correct types, graceful degradation tested

**After 03-01, run this** — the core AI logic.

---

### **Plan 03-03: Backend Integration**
**Wave:** 3 (Depends on 03-02)

**Deliverables:**
- ✅ POST /api/decoys/generate — AI-assisted decoy creation
- ✅ GET /api/attacks/{session_id}?include_forensics=true — Forensic summary optional
- ✅ Updated schemas in `app/core/base.py`
- ✅ Integration tests in `test_backend.py`

**Key Features:**
- Backward compatible (forensics field optional)
- Graceful fallback (endpoint still works if AI fails)
- Database integration (saves generated decoys)
- Frozen API contracts maintained

**Effort:** ~2 hours (routing + DB integration + tests)  
**Verification:** New endpoints return 200, save to DB, API contracts frozen, tests pass

**After 03-02, run this** — wire AI to the backend.

---

## Execution Roadmap

### **Prerequisites**
1. ✅ Backend core is working (honeypots, logging, DB persistence)
2. ✅ API contracts are frozen and documented
3. ⚠️ **LLM API key** must be configured in `.env` before 03-02 can use real LLM calls

### **Step 1: Wave 1 Execution** (03-01)
```bash
# Execute the tasks in .planning/phases/03-ai-integration/03-01-PLAN.md
# Expected: ~2 hours

# Create app/ai/ package with schemas and LLM client
# Verify: python -c "from app.ai import SiteProfile, DecoyAssetDefinition, ForensicSummary"
```

### **Step 2: Wave 2 Execution** (03-02)
```bash
# Execute the tasks in 03-02-PLAN.md (depends on 03-01 complete)
# Expected: ~3-4 hours

# Create app/ai/site_profiler.py, decoy_generator.py, response_writer.py, forensic_analyzer.py
# Verify: all functions importable, callable, graceful fallback works
```

### **Step 3: Wave 3 Execution** (03-03)
```bash
# Execute the tasks in 03-03-PLAN.md (depends on 03-02 complete)
# Expected: ~2 hours

# Add /api/decoys/generate and enhance /api/attacks/{id}
# Verify: new endpoints work, tests pass, API frozen
```

---

## Configuration (Before Starting)

### Add to `.env`:
```bash
# LLM Configuration
LLM_API_KEY=sk_your_key_here          # OpenAI, Anthropic, etc.
LLM_MODEL=gpt-4                       # Model identifier
LLM_PROVIDER=openai                   # Provider: openai, anthropic, custom
LLM_TEMPERATURE=0.7                   # 0.0 (deterministic) to 1.0 (creative)
```

If `LLM_API_KEY` is not set:
- Phase 03-01 & 03-02 still work (use fallback logic)
- Phase 03-03 endpoints work (forensics optional)
- AI features degrade gracefully but don't fail

---

## What the Plans Specify

Each plan includes:

1. **Objective** — What this plan accomplishes
2. **Must-Haves** — Observable truths, required artifacts, key links
3. **Tasks** — Specific, executable instructions
4. **Verification** — Automated tests/checks per task
5. **Threat Model** — STRIDE security analysis
6. **Success Criteria** — Measurable completion

All tasks are **`type: auto`** (fully autonomous — no human checkpoints).

---

## Risk & Assumptions

### Assumptions
- ✅ LLM API (OpenAI, Anthropic, etc.) available and responding
- ✅ No circular imports between app/ai/ and app/routes/
- ✅ All Pydantic validation catches malformed LLM responses
- ✅ Fallback logic handles LLM unavailability gracefully

### Risks & Mitigations
| Risk | Mitigation |
|------|-----------|
| LLM API rate limits | Implement backoff + fallback in LLMClient |
| LLM returns invalid JSON | Validate with Pydantic; retry with temperature reduction |
| LLM leaks sensitive data | Truncate request bodies before sending; document ToS |
| Decoy generation is too generic | Use detailed prompts + site profile context |

---

## Success Metrics

After all three phases complete:

- ✅ `app/ai/` module exists with 4 functions + 3 schemas
- ✅ POST /api/decoys/generate returns AI-generated decoys
- ✅ GET /api/attacks/{id}?include_forensics=true returns forensic summary
- ✅ All endpoints gracefully fallback if LLM unavailable
- ✅ API contracts remain frozen (no breaking changes)
- ✅ Integration tests pass
- ✅ No hardcoded secrets (env vars only)
- ✅ All code logged at INFO/ERROR level

---

## Next Actions

**For you:**

1. **Review the plans** — Read each `.planning/phases/03-ai-integration/03-*.md` file
2. **Confirm understanding** — Do the tasks match your role responsibilities?
3. **Set up LLM** — Add LLM_API_KEY to .env (or confirm fallback-only mode is acceptable)
4. **Execute Wave 1** — Start with 03-01-PLAN.md
5. **Create execution summaries** — After each wave, create `.planning/phases/03-ai-integration/03-*-SUMMARY.md` with results

---

## File Reference

| File | Purpose |
|------|---------|
| `.planning/ROADMAP.md` | Project overview + phase timeline |
| `.planning/phases/03-ai-integration/03-01-PLAN.md` | Executable plan: Schemas + LLM client |
| `.planning/phases/03-ai-integration/03-02-PLAN.md` | Executable plan: AI functions |
| `.planning/phases/03-ai-integration/03-03-PLAN.md` | Executable plan: Backend integration |
| `Global.txt` | Project rules + architecture |
| `API_CONTRACTS.md` | Frozen API response shapes |
| `app/ai/` | (To be created) AI integration module |

---

## Questions?

Each plan includes:
- Specific code snippets (copy-paste ready)
- Verification commands (test each task)
- Links to related files (@references)
- Threat model + mitigation strategies

All tasks are designed to be **self-contained and testable independently**.

---

**Planning Status:** ✅ COMPLETE  
**Execution Status:** ⏳ READY TO START (Wave 1: 03-01-PLAN.md)

Good luck! 🚀
