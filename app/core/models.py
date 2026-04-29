"""SQLAlchemy ORM models for honeypot data persistence."""

from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from uuid import uuid4

Base = declarative_base()


class Session(Base):
    """
    Represents a grouped attacker session (e.g., same IP within time window).
    
    Groups multiple HTTP requests from the same IP/user-agent combination.
    """
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    ip_address = Column(String(45), index=True, nullable=False)  # IPv4 or IPv6
    first_request_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_request_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_agent = Column(String(500), nullable=True)
    request_count = Column(Integer, default=0)
    is_automated = Column(Boolean, default=False)  # Heuristic: bot/scanner/crawler?
    tags = Column(String(200), nullable=True)  # Comma-separated: "scanner", "crawler", etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    requests = relationship(
        "Request",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<Session(ip={self.ip_address}, requests={self.request_count})>"


class Request(Base):
    """
    Represents a single HTTP request to any honeypot endpoint.
    
    Stores request details (method, path, headers, body, response) for analysis.
    """
    __tablename__ = "requests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id"), index=True, nullable=False)
    method = Column(String(10), nullable=False)  # GET, POST, PUT, DELETE, etc.
    path = Column(String(500), index=True, nullable=False)
    query_string = Column(String(1000), nullable=True)
    headers_json = Column(Text, nullable=True)  # JSON blob of headers (sanitized)
    body = Column(Text, nullable=True)  # Request body (truncated if >10KB)
    response_status = Column(Integer, nullable=False)
    response_body = Column(Text, nullable=True)  # Response body sent to attacker
    is_trap_hit = Column(Boolean, default=False)  # Was this a spider trap?
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    duration_ms = Column(Integer, nullable=True)  # Request processing time

    # Relationships
    session = relationship("Session", back_populates="requests")

    def __repr__(self):
        return f"<Request({self.method} {self.path} -> {self.response_status})>"


class Trap(Base):
    """
    Spider trap definitions: URLs that should never exist in legitimate traffic.
    
    When accessed, logged as a high-confidence attacker signal.
    """
    __tablename__ = "traps"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    path_pattern = Column(String(500), unique=True, nullable=False)
    description = Column(String(500), nullable=True)
    response_status = Column(Integer, default=404)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Trap({self.path_pattern})>"


class DecoyAsset(Base):
    """
    Metadata about decoy endpoints, templates, and their purpose.
    
    Used by honeypot routes to generate realistic responses.
    Can be created/updated by AI layer via POST /api/decoys.
    """
    __tablename__ = "decoy_assets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    asset_type = Column(String(50), nullable=False)  # "endpoint", "file", "credential", "api"
    name = Column(String(200), unique=True, index=True, nullable=False)
    path = Column(String(500), nullable=True)  # HTTP path (e.g., "/admin")
    description = Column(String(1000), nullable=True)  # What this decoy mimics
    mimics = Column(String(200), nullable=True)  # Target: "admin_panel", "env_file", "user_api"
    response_template = Column(Text, nullable=True)  # Jinja2 or plain text response
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<DecoyAsset(name={self.name}, type={self.asset_type})>"


class ThreatSignature(Base):
    """
    Dynamic threat signatures to detect malicious patterns in requests.
    Loaded at runtime by the analyzer.
    """
    __tablename__ = "threat_signatures"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(100), unique=True, index=True, nullable=False)
    pattern = Column(String(1000), nullable=False)  # regex pattern
    target = Column(String(50), nullable=False, default="payload")  # 'payload', 'path', 'header'
    threat_tag = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ThreatSignature(name={self.name}, target={self.target})>"
