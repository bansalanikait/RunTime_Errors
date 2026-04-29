"""Rule-based analyzer for HTTP requests and sessions."""

import re

# Simple heuristic patterns
SQLI_PATTERN = re.compile(r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|OR 1=1)\b)|(--)", re.IGNORECASE)
XSS_PATTERN = re.compile(r"(<script>|javascript:|onerror=)", re.IGNORECASE)

# Dynamic rules cache
_DYNAMIC_RULES = {
    "payload": [],
    "path": [],
    "header": []
}

def load_signatures_from_db(signatures: list):
    """
    Reloads the dynamic rules cache from a list of ThreatSignature objects.
    """
    global _DYNAMIC_RULES
    new_rules = {"payload": [], "path": [], "header": []}
    
    for sig in signatures:
        if not getattr(sig, "is_active", True):
            continue
            
        try:
            pattern = re.compile(getattr(sig, "pattern", ""), re.IGNORECASE)
            target = getattr(sig, "target", "payload")
            tag = getattr(sig, "threat_tag", "dynamic_threat")
            
            if target in new_rules:
                new_rules[target].append((pattern, tag))
        except re.error:
            # Skip invalid regexes
            pass
            
    _DYNAMIC_RULES = new_rules

# Common recon paths
RECON_PATHS = {
    "/.env", "/wp-login.php", "/wp-admin", "/admin", "/phpinfo.php", 
    "/config.php", "/.git", "/.git/config"
}

def analyze_request(request_method: str, path: str, query_string: str, body: str) -> list[str]:
    """
    Analyzes a single request for known attack patterns.
    Returns a list of threat tags.
    """
    tags = []
    
    # Path analysis
    if path in RECON_PATHS or any(path.endswith(p) for p in [".php", ".env", ".git", ".bak"]):
        tags.append("recon_probe")
        
    # Payload analysis
    payload = f"{query_string or ''} {body or ''}"
    
    if SQLI_PATTERN.search(payload):
        tags.append("sqli_attempt")
        
    if XSS_PATTERN.search(payload):
        tags.append("xss_attempt")
        
    # Apply dynamic payload rules
    for pattern, tag in _DYNAMIC_RULES.get("payload", []):
        if pattern.search(payload):
            tags.append(tag)
            
    # Apply dynamic path rules
    for pattern, tag in _DYNAMIC_RULES.get("path", []):
        if pattern.search(path):
            tags.append(tag)
        
    return tags

def analyze_session(requests_list) -> tuple[float, list[str], bool]:
    """
    Analyzes a group of requests (a session).
    Returns (risk_score, session_tags, is_automated).
    
    requests_list is expected to be a list of Request model objects or dicts.
    """
    risk_score = 0.0
    session_tags = set()
    is_automated = False
    
    trap_hits = 0
    recon_hits = 0
    exploit_hits = 0
    
    for req in requests_list:
        # Determine attributes whether passed as dict or ORM object
        path = req.path if hasattr(req, 'path') else req.get('path', '')
        query = req.query_string if hasattr(req, 'query_string') else req.get('query_string', '')
        body = req.body if hasattr(req, 'body') else req.get('body', '')
        method = req.method if hasattr(req, 'method') else req.get('method', '')
        is_trap_hit = req.is_trap_hit if hasattr(req, 'is_trap_hit') else req.get('is_trap_hit', False)
        
        req_tags = analyze_request(method, path, query, body)
        session_tags.update(req_tags)
        
        if is_trap_hit:
            trap_hits += 1
            session_tags.add("spider_trap_hit")
            
        if "recon_probe" in req_tags:
            recon_hits += 1
            
        if "sqli_attempt" in req_tags or "xss_attempt" in req_tags:
            exploit_hits += 1
            
    # Calculate risk score
    risk_score += (trap_hits * 5.0)
    risk_score += (recon_hits * 2.0)
    risk_score += (exploit_hits * 10.0)
    
    # Frequency/Automation check (simple heuristic: >20 requests -> potentially automated)
    req_count = len(requests_list)
    if req_count > 20 or trap_hits > 1:
        is_automated = True
        session_tags.add("automated_scanner")
        
    # Cap risk score
    risk_score = min(risk_score, 100.0)
    
    return risk_score, list(session_tags), is_automated
