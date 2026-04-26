import asyncio
import os
from app.ai.generator import generate_site_profile

# 1. Set your environment variables for your local LLM or OpenAI

# --- OPTION A: For LM Studio ---
# Remove the '#' from the next 3 lines to use LM Studio
# os.environ["LLM_API_KEY"] = "lm-studio"
# os.environ["LLM_BASE_URL"] = "http://localhost:1234/v1"
# os.environ["LLM_MODEL_NAME"] = "local-model"

# --- OPTION B: For Ollama ---
# Remove the '#' from the next 3 lines to use Ollama
# os.environ["LLM_API_KEY"] = "ollama"
# os.environ["LLM_BASE_URL"] = "http://localhost:11434/v1" 
# os.environ["LLM_MODEL_NAME"] = "llama3" # Change to whichever model you downloaded

# --- OPTION C: For OpenAI ---
# os.environ["LLM_API_KEY"] = "sk-proj-your-real-openai-key-here"


async def run_test():
    raw_signals = """
    URL: https://target.local/login
    Page Title: Admin Portal Login
    Headers: Server: nginx/1.18.0, X-Powered-By: PHP/7.4
    Visible text: Welcome to the intranet portal. Please enter your credentials.
    """
    
    print("Testing generate_site_profile...")
    
    try:
        profile = await generate_site_profile(raw_signals)
        print("\n✅ Success! Validated Pydantic Model:")
        print(f"Name: {profile.name}")
        print(f"Theme: {profile.theme}")
        print(f"Stack Hints: {profile.stack_hints}")
        print(f"Important Paths: {profile.important_paths}")
    except Exception as e:
        print(f"\n❌ Error during LLM call: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())
