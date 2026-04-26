import os
import json
import httpx
from typing import Type, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

# Module level HTTP client for efficient reuse.
_client = httpx.AsyncClient(timeout=30.0)

async def call_llm(prompt: str, schema_class: Optional[Type[T]] = None) -> Any:
    """
    Calls an OpenAI-compatible LLM endpoint.
    If schema_class is provided, it validates and returns that Pydantic model.
    Otherwise, returns the raw text response.
    """
    api_key = os.getenv("LLM_API_KEY", os.getenv("OPENAI_API_KEY", "local-key-fallback"))
    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    model_name = os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    system_message = "You are a helpful assistant."
    if schema_class:
        system_message += f"\nYou must reply with valid JSON conforming to this schema:\n{schema_class.model_json_schema()}"

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    # Request JSON object if schema is provided
    if schema_class:
        payload["response_format"] = {"type": "json_object"}

    try:
        response = await _client.post(f"{base_url}/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]

        if schema_class:
            try:
                parsed_json = json.loads(content)
                return schema_class(**parsed_json)
            except json.JSONDecodeError:
                # Basic fallback to extract JSON inside markdown block if LLM ignored response_format
                if "```json" in content:
                    extracted = content.split("```json")[1].split("```")[0].strip()
                    parsed_json = json.loads(extracted)
                    return schema_class(**parsed_json)
                raise ValueError(f"Failed to parse JSON from response: {content}")
        else:
            return content
            
    except Exception as e:
        raise RuntimeError(f"LLM call failed: {str(e)}")
