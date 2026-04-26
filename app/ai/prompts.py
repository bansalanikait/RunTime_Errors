from app.ai.schemas import SiteProfile

def build_site_profile_prompt(raw_signals: str) -> str:
    return f"""You are a cybersecurity intelligence analyst profiling a target application.
Given the following raw signals collected from the application (URL, page title, headers, visible sections, descriptions):
{raw_signals}

Analyze the signals and output a structured profile of the site, including its likely name, theme, technical stack hints, and important paths.
Respond ONLY with valid JSON matching the required schema.
"""

def build_decoy_assets_prompt(site_profile: SiteProfile) -> str:
    return f"""You are an expert in active defense and deception technologies.
We have profiled a target application with the following details:
- Name: {site_profile.name}
- Theme: {site_profile.theme}
- Stack Hints: {", ".join(site_profile.stack_hints)}
- Important Paths: {", ".join(site_profile.important_paths)}

Propose a set of highly realistic decoy assets (fake routes, fake pages, spider traps) that blend perfectly with this application to deceive automated scanners and human attackers.
Generate exactly 3 to 5 decoy asset definitions.
Respond ONLY with valid JSON matching the required schema.
"""

def build_fake_response_prompt(decoy_type: str, request_details: dict, site_profile: SiteProfile) -> str:
    req_str = str(request_details)
    return f"""You are a master at generating realistic mock responses for a deception system.
Target Application Profile:
- Theme: {site_profile.theme}
- Stack: {", ".join(site_profile.stack_hints)}

We need to generate the body (HTML or JSON) for a decoy of type: "{decoy_type}".
The attacker sent the following request:
{req_str}

Return ONLY the raw body content for the response. Do NOT use markdown code blocks like ```html. Return exactly what should be served over HTTP.
"""

def build_forensic_summary_prompt(session_data: list) -> str:
    session_str = str(session_data)
    return f"""You are a senior security analyst reviewing a session interacting with our deception system.
Below is the structured view of the session (list of requests + tags):
{session_str}

Produce a concise, security-analyst-style forensic summary.
Include a headline, a detailed narrative description, suspected tools/techniques, and mitigation recommendations.
Respond ONLY with valid JSON matching the required schema.
"""
