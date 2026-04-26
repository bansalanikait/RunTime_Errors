from typing import List
from app.ai.schemas import SiteProfile, DecoyAssetDefinition, DecoyAssetList, ForensicSummary
from app.ai.prompts import (
    build_site_profile_prompt,
    build_decoy_assets_prompt,
    build_fake_response_prompt,
    build_forensic_summary_prompt
)
from app.ai.client import call_llm

async def generate_site_profile(raw_signals: str) -> SiteProfile:
    """
    Accepts pre-collected signals (URL, page title, headers, visible sections)
    and returns a validated SiteProfile Pydantic object.
    """
    prompt = build_site_profile_prompt(raw_signals)
    profile = await call_llm(prompt, schema_class=SiteProfile)
    return profile

async def generate_decoy_assets(site_profile: SiteProfile) -> List[DecoyAssetDefinition]:
    """
    Uses the site profile to ask the LLM to propose a set of decoy assets
    and returns a list of DecoyAssetDefinition objects.
    """
    prompt = build_decoy_assets_prompt(site_profile)
    asset_list = await call_llm(prompt, schema_class=DecoyAssetList)
    return asset_list.assets

async def generate_fake_response(decoy_type: str, request_details: dict, site_profile: SiteProfile) -> str:
    """
    Asks the LLM for a realistic fake body (HTML or JSON)
    based on the decoy endpoint type and request details.
    """
    prompt = build_fake_response_prompt(decoy_type, request_details, site_profile)
    # We want raw string here (HTML or JSON), so no schema_class
    raw_response = await call_llm(prompt)
    return raw_response

async def summarize_session(session_data: List[dict]) -> ForensicSummary:
    """
    Takes a structured view of the session (list of requests + tags)
    and returns a concise security-analyst-style summary.
    """
    prompt = build_forensic_summary_prompt(session_data)
    summary = await call_llm(prompt, schema_class=ForensicSummary)
    return summary
