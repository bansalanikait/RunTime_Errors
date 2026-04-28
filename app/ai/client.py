import json
import httpx
from typing import Type, TypeVar, Optional, Any
from pydantic import BaseModel
from app.core.settings import settings

T = TypeVar("T", bound=BaseModel)

# Module level HTTP client for efficient reuse.
_client = httpx.AsyncClient(timeout=90.0)

async def call_llm(prompt: str, schema_class: Optional[Type[T]] = None) -> Any:
    """
    Calls an OpenAI-compatible LLM endpoint.
    If schema_class is provided, it validates and returns that Pydantic model.
    Otherwise, returns the raw text response.
    """
    api_key = settings.llm_api_key
    base_url = settings.effective_llm_base_url
    model_name = settings.llm_model_name

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    system_message = "You are a helpful assistant."
    if schema_class:
        # Build a simple {field: type} example instead of the full JSON Schema,
        # because small local models often parrot the raw schema back.
        schema = schema_class.model_json_schema()
        fields = schema.get("properties", {})
        example = {}
        for k, v in fields.items():
            ftype = v.get("type", "string")
            if ftype == "array":
                example[k] = ["example1", "example2"]
            else:
                example[k] = f"<{ftype}>"
        system_message += (
            f"\nYou must reply ONLY with a valid JSON object. "
            f"Do NOT return the schema definition. "
            f"Every array field must contain plain strings, NOT objects. "
            f"Return actual values in this exact shape:\n{json.dumps(example, indent=2)}"
        )

    # Native Ollama API endpoint
    endpoint = f"{base_url.replace('/v1', '')}/api/chat"
    
    print(f"[AI] Calling {model_name} at {endpoint}...")
    
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 500  # Limit response length to prevent infinite loops
        }
    }

    # Request JSON object if schema is provided
    if schema_class:
        payload["format"] = "json"

    try:
        response = await _client.post(endpoint, json=payload, headers=headers)
        print(f"[AI] Response received (status: {response.status_code})")
        
        if response.status_code == 404:
            # Helpful hint for Ollama users
            raise RuntimeError(f"LLM endpoint not found (404). If using Ollama, ensure it is running and the base URL includes '/v1' (e.g., http://localhost:11434/v1).")
        elif response.status_code == 401:
            raise RuntimeError(f"LLM authentication failed (401). Check your API key in .env.")
            
        response.raise_for_status()
        data = response.json()
        
        # Parse based on native Ollama format
        if "message" in data:
            content = data["message"]["content"]
        elif "choices" in data:
            content = data["choices"][0]["message"]["content"]
        else:
            raise ValueError(f"Unknown LLM response format: {data}")

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
            
    except httpx.ConnectError:
        raise RuntimeError(f"Could not connect to LLM at {base_url}. Is the service running?")
    except Exception as e:
        if "RuntimeError" in str(type(e)):
             raise e
        raise RuntimeError(f"LLM call failed: {str(e)}")
