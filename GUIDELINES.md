# Collaboration Guidelines for DECEPTRA

This document outlines guidelines to minimize merge conflicts and coordinate efforts across Dev A, B, and C.

## 1. Branching and Rebasing
- **Feature Branches**: Always develop your features on separate, isolated branches (e.g., `feature/threat-signatures-devC`, `feature/ui-dashboard-devA`).
- **Rebase Frequently**: If another developer merges changes into `main` (or the primary integration branch), rebase your feature branch immediately to resolve conflicts locally before raising a PR.
  - `git fetch origin`
  - `git rebase origin/main`

## 2. Modifying Shared Database Models
- `app/core/models.py` is a highly contested file since both backend APIs and the analyzer rely on it.
- **Additive Changes**: Always prefer adding new tables (classes) or columns rather than renaming/deleting existing ones to prevent breaking other developers' code.
- **Merge Order**: If multiple PRs add database models simultaneously, the first PR to merge establishes the schema state. The subsequent PR authors MUST rebase, drop/recreate their local database, and ensure no table name or foreign key conflicts exist.

## 3. Modifying the Analyzer Core
- `app/analyzer/rules.py` is the critical path for request evaluation.
- Do not modify the existing hardcoded rules (`SQLI_PATTERN`, `XSS_PATTERN`, `RECON_PATHS`) as other components or baseline fallback systems rely on them.
- Introduce new features via configuration, cache extensions (like `_DYNAMIC_RULES`), or new helper functions instead of rewriting the fundamental `analyze_session` or `analyze_request` control flow.

## 4. Creating API Endpoints
- Keep feature-specific routes in their own dedicated files (e.g., `api_signatures.py`, `api_decoys.py`).
- Define feature-specific Pydantic schemas within your specific route file (or a dedicated `schemas/` module) rather than cluttering shared models, unless the schema is genuinely utilized globally.

## 5. UI Integration
- When building UI components that depend on unfinished backend APIs, mock the data in the frontend (e.g., hardcoded JSON responses).
- Once the backend is merged, the UI developer should update the frontend to consume the live endpoints.
