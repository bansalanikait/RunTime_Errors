"""Pydantic schemas for request/response validation and documentation."""

from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, List


# ============================================================================
# SESSION & REQUEST SCHEMAS (Response DTOs)
# ============================================================================


class RequestInfoSchema(BaseModel):
    """
    Single HTTP request within a session.
    
    Returned by GET /api/attacks/{session_id}
    """
    id: UUID
    session_id: UUID
    method: str
    path: str
    query_string: Optional[str] = None
    headers_json: Optional[str] = None
    body: Optional[str] = None
    response_body: Optional[str] = None
    timestamp: datetime
    response_status: int
    duration_ms: Optional[int] = None
    is_trap_hit: bool = False

    class Config:
        from_attributes = True


class SessionSummarySchema(BaseModel):
    """
    Condensed session summary for listing.
    
    Returned by GET /api/attacks
    """
    id: UUID
    ip_address: str
    first_request_at: datetime
    last_request_at: datetime
    request_count: int = 0
    is_automated: bool = False
    tags: Optional[str] = None
    user_agent: Optional[str] = None

    class Config:
        from_attributes = True


class SessionDetailSchema(BaseModel):
    """
    Full session detail with request chain.
    
    Returned by GET /api/attacks/{session_id}
    """
    session: SessionSummarySchema
    requests: List[RequestInfoSchema]


# ============================================================================
# DECOY ASSET SCHEMAS (Request/Response)
# ============================================================================


class DecoyAssetCreateSchema(BaseModel):
    """
    Payload for creating/updating a decoy asset.
    
    Used by POST /api/decoys
    """
    asset_type: str = Field(..., description="Type: endpoint, file, credential, api")
    name: str = Field(..., description="Unique decoy name")
    path: Optional[str] = Field(None, description="HTTP path (e.g., /admin)")
    description: Optional[str] = Field(None, description="What this decoy mimics")
    mimics: Optional[str] = Field(None, description="Target: admin_panel, env_file, user_api")
    response_template: Optional[str] = Field(None, description="Response body template")
    is_active: bool = Field(True, description="Is this decoy active?")


class DecoyAssetSchema(DecoyAssetCreateSchema):
    """
    Complete decoy asset (with database fields).
    
    Returned by POST /api/decoys (creation response)
    """
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# API RESPONSE WRAPPERS (Frozen JSON contracts)
# ============================================================================


class AttacksListResponse(BaseModel):
    """
    GET /api/attacks response.
    
    FROZEN CONTRACT - Do not change response shape.
    """
    attacks: List[SessionSummarySchema]
    total: int = 0
    limit: int = 100
    offset: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "attacks": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "ip_address": "192.168.1.100",
                        "first_request_at": "2026-04-26T10:00:00",
                        "last_request_at": "2026-04-26T10:05:30",
                        "request_count": 5,
                        "is_automated": True,
                        "tags": "scanner,web-crawler",
                    }
                ],
                "total": 1,
                "limit": 100,
                "offset": 0,
            }
        }


class AttackDetailResponse(BaseModel):
    """
    GET /api/attacks/{session_id} response.
    
    FROZEN CONTRACT - Do not change response shape.
    """
    session: SessionSummarySchema
    requests: List[RequestInfoSchema]

    class Config:
        json_schema_extra = {
            "example": {
                "session": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "ip_address": "192.168.1.100",
                    "first_request_at": "2026-04-26T10:00:00",
                    "last_request_at": "2026-04-26T10:05:30",
                    "request_count": 2,
                    "is_automated": True,
                    "tags": "scanner",
                },
                "requests": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440001",
                        "session_id": "550e8400-e29b-41d4-a716-446655440000",
                        "method": "GET",
                        "path": "/admin",
                        "query_string": None,
                        "timestamp": "2026-04-26T10:00:01",
                        "response_status": 200,
                        "duration_ms": 15,
                        "is_trap_hit": False,
                    }
                ],
            }
        }


class DecoyAssetCreateResponse(BaseModel):
    """
    POST /api/decoys response.
    
    FROZEN CONTRACT - Do not change response shape.
    """
    id: UUID
    name: str
    asset_type: str
    path: Optional[str] = None
    is_active: bool

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "fake_admin_panel",
                "asset_type": "endpoint",
                "path": "/admin",
                "is_active": True,
            }
        }


class HealthCheckResponse(BaseModel):
    """
    GET /api/health response.
    
    FROZEN CONTRACT - Do not change response shape.
    """
    status: str = "ok"
    version: str = "1.0.0"

    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "version": "1.0.0",
            }
        }


class ErrorResponse(BaseModel):
    """
    Standard error response for all endpoints.
    
    FROZEN CONTRACT - Do not change response shape.
    """
    error: str
    details: Optional[str] = None
    status_code: int

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Not Found",
                "details": "Session 550e8400-e29b-41d4-a716-446655440000 not found",
                "status_code": 404,
            }
        }
