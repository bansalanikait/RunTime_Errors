# API Contracts - FROZEN JSON Schemas

**IMPORTANT**: These schemas are LOCKED. Do not change response shapes without migration planning.

Frontend and backend can develop independently using these contracts as the interface.

---

## 1. GET /api/health

**Status**: ✅ PRODUCTION

**Purpose**: Health check endpoint. Always returns 200 OK.

**Response (200 OK):**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

**Example:**
```bash
curl http://localhost:8000/api/health
```

---

## 2. GET /api/attacks

**Status**: ✅ PRODUCTION

**Purpose**: List all honeypot sessions with pagination.

**Query Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| limit | integer | 100 | Max results per page |
| offset | integer | 0 | Pagination offset |

**Response (200 OK):**
```json
{
  "attacks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "ip_address": "192.168.1.100",
      "first_request_at": "2026-04-26T10:00:00",
      "last_request_at": "2026-04-26T10:05:30",
      "request_count": 5,
      "is_automated": true,
      "tags": "scanner,web-crawler"
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0
}
```

**Example:**
```bash
# Get first 50 sessions
curl "http://localhost:8000/api/attacks?limit=50&offset=0"

# Get next page
curl "http://localhost:8000/api/attacks?limit=50&offset=50"
```

---

## 3. GET /api/attacks/{session_id}

**Status**: ✅ PRODUCTION

**Purpose**: Get full request chain for a single session.

**Path Parameters:**
| Name | Type | Description |
|------|------|-------------|
| session_id | UUID | Session ID from /api/attacks |

**Response (200 OK):**
```json
{
  "session": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "ip_address": "192.168.1.100",
    "first_request_at": "2026-04-26T10:00:00",
    "last_request_at": "2026-04-26T10:05:30",
    "request_count": 5,
    "is_automated": true,
    "tags": "scanner,web-crawler"
  },
  "requests": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "method": "GET",
      "path": "/admin",
      "query_string": null,
      "timestamp": "2026-04-26T10:00:01",
      "response_status": 200,
      "duration_ms": 15,
      "is_trap_hit": false
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "method": "POST",
      "path": "/login",
      "query_string": null,
      "timestamp": "2026-04-26T10:00:05",
      "response_status": 401,
      "duration_ms": 8,
      "is_trap_hit": false
    }
  ]
}
```

**Response (404 Not Found):**
```json
{
  "error": "Not Found",
  "details": "Session 550e8400-e29b-41d4-a716-446655440000 not found",
  "status_code": 404
}
```

**Example:**
```bash
curl "http://localhost:8000/api/attacks/550e8400-e29b-41d4-a716-446655440000"
```

---

## 4. POST /api/decoys

**Status**: ✅ PRODUCTION

**Purpose**: Create or update a decoy asset.

**Request Body:**
```json
{
  "asset_type": "endpoint",
  "name": "fake_admin_panel",
  "path": "/admin",
  "description": "Fake admin login panel that captures credentials",
  "mimics": "admin_panel",
  "response_template": null,
  "is_active": true
}
```

**Request Body Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| asset_type | string | yes | Type: endpoint, file, credential, api |
| name | string | yes | Unique decoy name (used as key) |
| path | string | no | HTTP path (e.g., /admin) |
| description | string | no | What this decoy mimics |
| mimics | string | no | Target: admin_panel, env_file, user_api |
| response_template | string | no | Custom response body |
| is_active | boolean | no | Activate/deactivate (default true) |

**Response (200 OK - Created/Updated):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "fake_admin_panel",
  "asset_type": "endpoint",
  "path": "/admin",
  "is_active": true
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/decoys \
  -H "Content-Type: application/json" \
  -d '{
    "asset_type": "endpoint",
    "name": "fake_admin_panel",
    "path": "/admin",
    "description": "Admin login panel",
    "mimics": "admin_panel",
    "is_active": true
  }'
```

---

## 5. GET /api/decoys

**Status**: ✅ PRODUCTION

**Purpose**: List all decoy assets.

**Query Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| active_only | boolean | true | Only return active decoys |

**Response (200 OK):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "asset_type": "endpoint",
    "name": "fake_admin_panel",
    "path": "/admin",
    "description": "Fake admin login panel",
    "mimics": "admin_panel",
    "response_template": null,
    "is_active": true,
    "created_at": "2026-04-26T10:00:00",
    "updated_at": "2026-04-26T10:00:00"
  }
]
```

**Example:**
```bash
# Get only active decoys
curl "http://localhost:8000/api/decoys?active_only=true"

# Get all decoys (including inactive)
curl "http://localhost:8000/api/decoys?active_only=false"
```

---

## 6. GET /api/decoys/{decoy_id}

**Status**: ✅ PRODUCTION

**Purpose**: Get a single decoy asset by ID.

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "asset_type": "endpoint",
  "name": "fake_admin_panel",
  "path": "/admin",
  "description": "Fake admin login panel",
  "mimics": "admin_panel",
  "response_template": null,
  "is_active": true,
  "created_at": "2026-04-26T10:00:00",
  "updated_at": "2026-04-26T10:00:00"
}
```

**Response (404 Not Found):**
```json
{
  "error": "Not Found",
  "details": "Decoy 550e8400-e29b-41d4-a716-446655440000 not found",
  "status_code": 404
}
```

---

## Common Error Response Format

All errors follow this schema:

```json
{
  "error": "Error Type",
  "details": "Detailed error message",
  "status_code": 400
}
```

**Common Status Codes:**
| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (validation error) |
| 404 | Not found (resource doesn't exist) |
| 500 | Server error |

---

## Migration Guide

### If You Need to Change a Contract

1. **Do NOT modify existing fields** in documented responses
2. **Add new fields at the end** of objects with default values
3. **Never remove fields** that frontend/AI depends on
4. **Create versioned endpoints** (e.g., /api/v2/attacks) if major changes needed
5. **Update this document** and notify teams before deploying

### Example: Adding a Field
```json
// OLD (current)
{
  "id": "...",
  "ip_address": "..."
}

// NEW (with backward compatibility)
{
  "id": "...",
  "ip_address": "...",
  "geoip_country": null  // NEW: Add at end with null/default
}
```

---

## Frontend Integration Notes

- **Use UUIDs**: All IDs are strings (UUID format)
- **Pagination**: Always use limit/offset for large datasets
- **Timestamps**: ISO 8601 format (2026-04-26T10:00:00)
- **Error Handling**: Check status_code field in response
- **Null Fields**: Fields may be null; handle gracefully

---

## AI Layer Integration Notes

- **Create Decoys**: Use POST /api/decoys to register new decoy assets
- **Query Sessions**: Use GET /api/attacks for raw session data
- **Deep Analysis**: Use GET /api/attacks/{id} to get full request chain
- **Scoring**: Session data is raw; implement scoring in app/analyzer/

---

**Last Updated**: 2026-04-26  
**Status**: FROZEN - Production Ready
