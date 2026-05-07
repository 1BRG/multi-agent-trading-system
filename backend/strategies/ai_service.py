import json
import os
import re
import httpx

# You can set this in your .env later. Defaulting to local Ollama for now.
LLM_API_URL = "http://ollama:11434/api/generate"
LLM_MODEL = os.getenv("LLM_MODEL", "llama3")

SYSTEM_PROMPT = """You are an expert quantitative portfolio manager.
Your task is to translate the user's trading idea into a strict, deterministic ruleset.

You MUST output ONLY valid JSON matching this exact schema. Do not include markdown formatting, code blocks, or any explanations outside the JSON.

SCHEMA:
{
  "name": "String (A catchy name for the strategy)",
  "description": "String (A 1-2 sentence explanation of the logic)",
  "config": {
    "rebalance_frequency": "weekly",  // MUST be one of: "daily", "weekly", "monthly", "quarterly"
    "ranking_metric": "conviction",   // MUST be "conviction"
    "portfolio_size": 5,              // MUST be an integer between 1 and 500
    "sizing": "equal_weight",         // MUST be one of: "equal_weight", "conviction_weighted"
    "sector_cap_pct": 100,            // MUST be an integer between 1 and 100 (use 100 for no sector cap)
    "exit_on_signal_flip": true       // MUST be a boolean (true or false)
  }
}
"""

def generate_strategy_rules(user_prompt: str) -> dict:
    """
    Sends the user's prompt to the LLM and attempts to parse the strict JSON response.
    """
    payload = {
        "model": LLM_MODEL,
        "system": SYSTEM_PROMPT,
        "prompt": user_prompt,
        "stream": False
    }

    try:
        # We use a longer timeout because LLM generation can take a few seconds
        with httpx.Client(timeout=300.0) as client:
            response = client.post(LLM_API_URL, json=payload)
            response.raise_for_status()
            
            data = response.json()
            llm_response_text = data.get("response", "")

            # Cleanup: Sometimes LLMs ignore the "No Markdown" rule. 
            # We strip markdown formatting if it's there.
            cleaned_text = re.sub(r"```json\s*", "", llm_response_text)
            cleaned_text = re.sub(r"```\s*", "", cleaned_text).strip()

            # Parse the JSON
            strategy_dict = json.loads(cleaned_text)
            # Return both parsed strategy and raw text for auditing
            return {"parsed": strategy_dict, "raw": llm_response_text}

    except httpx.RequestError as e:
        raise ValueError(f"Failed to communicate with LLM API: {str(e)}")
    except json.JSONDecodeError:
        raise ValueError("The LLM failed to return valid JSON. Please try a different prompt.")

# --- MOCK FOR LOCAL DEVELOPMENT ---
# If you don't have Ollama running yet, you can comment out the real function above 
# and uncomment this mock to continue testing the API and UI immediately.

# def generate_strategy_rules(user_prompt: str) -> dict:
#     """Mock response for UI development without needing a running LLM."""
#     return {
#         "name": "AI Momentum Generator",
#         "description": f"A strategy based on: '{user_prompt}'. It buys top conviction stocks.",
#         "config": {
#             "rebalance_frequency": "weekly",
#             "ranking_metric": "conviction",
#             "portfolio_size": 5,
#             "sizing": "equal_weight",
#             "sector_cap_pct": 25,
#             "exit_on_signal_flip": True
#         }
#     }