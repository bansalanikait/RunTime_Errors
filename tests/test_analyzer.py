"""Tests for the rule-based request analyzer."""

import pytest
from app.analyzer.rules import analyze_request, analyze_session

class MockRequest:
    def __init__(self, method="GET", path="/", query_string="", body="", is_trap_hit=False):
        self.method = method
        self.path = path
        self.query_string = query_string
        self.body = body
        self.is_trap_hit = is_trap_hit

def test_analyze_request_recon():
    tags = analyze_request("GET", "/.env", "", "")
    assert "recon_probe" in tags

def test_analyze_request_sqli():
    tags = analyze_request("GET", "/search", "q=' OR 1=1 --", "")
    assert "sqli_attempt" in tags
    assert "recon_probe" not in tags

def test_analyze_request_xss():
    tags = analyze_request("POST", "/comment", "", "text=<script>alert('xss')</script>")
    assert "xss_attempt" in tags

def test_analyze_request_multiple():
    tags = analyze_request("GET", "/.env", "q=' OR 1=1", "")
    assert "recon_probe" in tags
    assert "sqli_attempt" in tags

def test_analyze_session():
    requests = [
        MockRequest(path="/"),
        MockRequest(path="/about"),
        MockRequest(path="/.env"),
        MockRequest(path="/search", query_string="q=UNION SELECT"),
        MockRequest(path="/hidden-trap", is_trap_hit=True),
    ]
    
    risk_score, tags, is_automated = analyze_session(requests)
    
    assert "recon_probe" in tags 
    assert "sqli_attempt" in tags
    assert "spider_trap_hit" in tags
    
    # risk score calculation:
    # 1 trap hit * 5.0 = 5.0
    # 1 recon hit * 2.0 = 2.0
    # 1 sqli hit * 10.0 = 10.0
    # Total = 17.0
    assert risk_score == 17.0
    assert is_automated == False

def test_analyze_session_automated_by_frequency():
    requests = [MockRequest(path="/")] * 21
    
    risk_score, tags, is_automated = analyze_session(requests)
    assert is_automated == True
    assert "automated_scanner" in tags

def test_analyze_session_automated_by_traps():
    requests = [
        MockRequest(path="/trap1", is_trap_hit=True),
        MockRequest(path="/trap2", is_trap_hit=True)
    ]
    
    risk_score, tags, is_automated = analyze_session(requests)
    assert is_automated == True
    assert "spider_trap_hit" in tags
    assert "automated_scanner" in tags
    assert risk_score == 10.0
