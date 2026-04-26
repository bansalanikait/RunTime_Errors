"""Fake honeypot endpoints that mimic real services and accept all input."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse
import json

router = APIRouter(tags=["honeypots"])


@router.get("/", include_in_schema=False)
async def homepage():
    """Fake homepage."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Welcome - DECEPTRA</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            p { color: #666; line-height: 1.6; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to DECEPTRA</h1>
            <p>Modular honeypot framework for attack detection and analysis.</p>
            <p>Version 1.0.0</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.get("/admin", include_in_schema=False)
async def admin_panel():
    """Fake admin login panel."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Dashboard - DECEPTRA</title>
        <style>
            body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
            .login-box { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); width: 300px; }
            h2 { text-align: center; color: #333; margin-top: 0; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; color: #555; font-size: 14px; }
            input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; font-size: 14px; }
            button { width: 100%; padding: 10px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; margin-top: 10px; }
            button:hover { background: #764ba2; }
            footer { text-align: center; color: #999; font-size: 12px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2>Admin Login</h2>
            <form method="POST" action="/login">
                <div class="form-group">
                    <label>Username</label>
                    <input type="text" name="username" required placeholder="admin">
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" required placeholder="••••••••">
                </div>
                <button type="submit">Sign In</button>
            </form>
            <footer>© 2026 DECEPTRA</footer>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.get("/login", include_in_schema=False)
async def login_page():
    """Fake login page (GET)."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>User Login - DECEPTRA</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
            .login-box { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); width: 350px; }
            h2 { text-align: center; color: #333; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; color: #555; }
            input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
            button { width: 100%; padding: 10px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; margin-top: 10px; }
            .checkbox-group { margin: 15px 0; }
            a { color: #667eea; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2>Login</h2>
            <form method="POST" action="/login">
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" name="email" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" required>
                </div>
                <div class="checkbox-group">
                    <input type="checkbox" name="remember" id="remember">
                    <label for="remember" style="display: inline;">Remember me</label>
                </div>
                <button type="submit">Login</button>
            </form>
            <p style="text-align: center; color: #666;"><a href="#">Forgot Password?</a></p>
            <p style="text-align: center; color: #666;">Don't have an account? <a href="#">Sign Up</a></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.post("/login", include_in_schema=False)
async def login_post(request: Request):
    """Fake login POST handler (always returns invalid credentials)."""
    return JSONResponse(status_code=401, content={
        "error": "Invalid credentials",
        "message": "Username or password is incorrect"
    })


@router.get("/.env", include_in_schema=False)
async def fake_env():
    """Fake leaked .env file."""
    env_content = """DATABASE_URL=postgresql://dbadmin:password123@localhost:5432/myapp
API_KEY=test_key_1234567890abcdef
AWS_ACCESS_KEY=AKIA2234567890ABCDEF
AWS_SECRET_ACCESS=abcdef1234567890+ABCDEFGHIJKLMNOP
THIRD_PARTY_TOKEN=token_1234567890
WEBHOOK_URL=https://example.com/webhooks/events
JWT_SECRET=jwt_super_secret_random_string
OPENAI_KEY=openai_key_1234567890abcdef
REDIS_URL=redis://localhost:6379/0
LOG_LEVEL=DEBUG
"""
    return PlainTextResponse(content=env_content)


@router.get("/api/v1/users", include_in_schema=False)
async def fake_users_list():
    """Fake user list API."""
    users = [
        {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com",
            "role": "administrator",
            "created_at": "2025-01-15T10:30:00Z",
            "last_login": "2026-04-26T09:00:00Z"
        },
        {
            "id": 2,
            "username": "jsmith",
            "email": "jsmith@example.com",
            "role": "user",
            "created_at": "2025-03-20T14:15:00Z",
            "last_login": "2026-04-25T15:45:00Z"
        },
        {
            "id": 3,
            "username": "mwilson",
            "email": "mwilson@example.com",
            "role": "user",
            "created_at": "2025-04-10T11:22:00Z",
            "last_login": "2026-04-24T08:30:00Z"
        }
    ]
    return JSONResponse(content={"users": users, "total": 3})


@router.get("/api/v1/users/{user_id}", include_in_schema=False)
async def fake_user_detail(user_id: int):
    """Fake single user API."""
    if user_id == 1:
        return JSONResponse(content={
            "id": 1,
            "username": "admin",
            "email": "admin@example.com",
            "role": "administrator",
            "phone": "+1-555-0100",
            "created_at": "2025-01-15T10:30:00Z",
            "last_login": "2026-04-26T09:00:00Z"
        })
    elif user_id == 2:
        return JSONResponse(content={
            "id": 2,
            "username": "jsmith",
            "email": "jsmith@example.com",
            "role": "user",
            "phone": "+1-555-0101",
            "created_at": "2025-03-20T14:15:00Z",
            "last_login": "2026-04-25T15:45:00Z"
        })
    else:
        return JSONResponse(status_code=404, content={"error": "User not found"})


@router.get("/debug/errors", include_in_schema=False)
async def fake_debug_errors():
    """Fake error/debug page."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Debug - Errors</title>
        <style>
            body { font-family: 'Courier New', monospace; background: #1e1e1e; color: #d4d4d4; margin: 0; padding: 20px; }
            .error-box { background: #252526; border: 1px solid #3e3e42; border-radius: 4px; padding: 15px; margin-bottom: 10px; }
            .error-title { color: #f48771; font-weight: bold; margin-bottom: 5px; }
            .error-trace { font-size: 12px; color: #ce9178; line-height: 1.4; }
            .file-path { color: #9cdcfe; }
        </style>
    </head>
    <body>
        <h1>Debug - Recent Errors</h1>
        <div class="error-box">
            <div class="error-title">DatabaseError: Connection timeout</div>
            <div class="error-trace">
                File "<span class="file-path">app/core/database.py</span>", line 42, in get_connection<br>
                &nbsp;&nbsp;conn = await engine.connect()<br>
                <br>
                sqlalchemy.exc.DatabaseError: (psycopg2.OperationalError) could not connect to server
            </div>
        </div>
        <div class="error-box">
            <div class="error-title">ConnectionError: Failed to reach API</div>
            <div class="error-trace">
                File "<span class="file-path">app/routes/api.py</span>", line 156, in fetch_external_data<br>
                &nbsp;&nbsp;response = await httpx.get(url, timeout=5)<br>
                <br>
                httpx.ConnectError: [Errno -2] Name or service not known
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.get("/config.php", include_in_schema=False)
async def fake_config_php():
    """Fake PHP config file."""
    config = """<?php
// Configuration File
define('DB_HOST', 'localhost');
define('DB_USER', 'app_user');
define('DB_PASSWORD', 'password_123_secure');
define('DB_NAME', 'application_db');
define('DB_PORT', '3306');

define('API_ENDPOINT', 'https://api.example.com');
define('API_TOKEN', 'token_1234567890');

define('ADMIN_EMAIL', 'admin@example.com');
define('SITE_URL', 'https://example.com');

// Debug mode
define('DEBUG', true);
?>"""
    return PlainTextResponse(content=config, media_type="text/plain")


@router.get("/robots.txt", include_in_schema=False)
async def fake_robots_txt():
    """Fake robots.txt file."""
    robots = """# robots.txt
User-agent: *
Disallow: /admin/
Disallow: /private/
Disallow: /temp/
Disallow: /*.php$
Disallow: /config/
Disallow: /uploads/temp/

User-agent: Googlebot
Disallow: /private/

Crawl-delay: 10
Request-rate: 1/10s

Sitemap: https://example.com/sitemap.xml
"""
    return PlainTextResponse(content=robots, media_type="text/plain")


@router.get("/.git/config", include_in_schema=False)
async def fake_git_config():
    """Fake .git/config file."""
    config = """[core]
	repositoryformatversion = 0
	filemode = false
	bare = false
	logallrefupdates = true
	ignorecase = true

[remote "origin"]
	url = https://github.com/example/repo.git
	fetch = +refs/heads/*:refs/remotes/origin/*

[branch "main"]
	remote = origin
	merge = refs/heads/main

[user]
	name = Developer
	email = dev@example.com
"""
    return PlainTextResponse(content=config, media_type="text/plain")


@router.get("/xmlrpc.php", include_in_schema=False)
async def fake_xmlrpc():
    """Fake WordPress XML-RPC endpoint."""
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<rsd version="100" xmlns="http://archipelago.phrasewise.com/rsd">
  <service>
    <engineName>WordPress</engineName>
    <engineLink>https://wordpress.org/</engineLink>
    <homePageLink>https://example.com</homePageLink>
    <apis>
      <api name="WordPress" blogID="1" preferred="true" apiLink="https://example.com/xmlrpc.php" />
      <api name="Movable Type" blogID="1" preferred="false" apiLink="https://example.com/xmlrpc.php" />
      <api name="Blogger" blogID="1" preferred="false" apiLink="https://example.com/xmlrpc.php" />
      <api name="MetaWeblog" blogID="1" preferred="false" apiLink="https://example.com/xmlrpc.php" />
    </apis>
  </service>
</rsd>
"""
    return PlainTextResponse(content=xml, media_type="application/xml")


@router.post("/api/login", include_in_schema=False)
async def fake_api_login():
    """Fake API-style login endpoint."""
    return JSONResponse(status_code=401, content={
        "status": "error",
        "code": 401,
        "message": "Unauthorized",
        "details": "Invalid API key or credentials"
    })


@router.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], include_in_schema=False)
async def catch_all_honeypot(request: Request, full_path: str):
    """Catch-all wildcard route for undefined endpoints."""
    path = f"/{full_path}"
    
    # Check against traps
    from app.decoys.spider_traps import get_all_traps
    from app.core.database import async_session_maker
    import re
    
    async with async_session_maker() as db:
        traps = await get_all_traps(db)
        is_trap = False
        for trap in traps:
            if path == trap.path_pattern or re.search(trap.path_pattern, path):
                is_trap = True
                break
                
        if is_trap:
            request.state.is_trap_hit = True
            
            # AI Hallucination layer
            from app.ai.generator import generate_fake_response
            from app.ai.schemas import SiteProfile
            import logging
            
            dummy_profile = SiteProfile(
                name="Corporate Admin Portal",
                theme="Enterprise Dashboard",
                stack_hints=["PHP", "React", "Nginx"],
                important_paths=["/admin", "/wp-login.php", "/.env"]
            )
            
            req_details = {
                "method": request.method,
                "path": path,
                "headers": dict(request.headers)
            }
            
            try:
                ai_html = await generate_fake_response("spider_trap_hit", req_details, dummy_profile)
                return HTMLResponse(content=ai_html, status_code=200)
            except Exception as e:
                logging.getLogger(__name__).error(f"AI trap generation failed: {e}")
                # Fallback to static 404
            
    return JSONResponse(status_code=404, content={
        "error": "Not Found", 
        "message": "The requested resource does not exist."
    })
