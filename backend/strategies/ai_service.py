import json
import os
import re
import httpx

# You can set this in your .env later. Defaulting to local Ollama for now.
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3")


def _candidate_chat_urls() -> list[str]:
    base_urls = [OLLAMA_BASE_URL.rstrip("/")]
    if OLLAMA_BASE_URL in {"http://localhost:11434", "http://127.0.0.1:11434"}:
        base_urls.append("http://ollama:11434")
    elif OLLAMA_BASE_URL == "http://ollama:11434":
        base_urls.extend(["http://localhost:11434", "http://127.0.0.1:11434"])

    return [f"{base_url}/api/chat" for base_url in dict.fromkeys(base_urls)]

SYSTEM_PROMPT = """You are an expert quantitative portfolio manager.
Your task is to translate the user's trading idea into a strict, deterministic ruleset.

CRITICAL RULES FOR MODIFYING STRATEGIES:
If the user asks to modify, update, or change a strategy you previously generated:
1. Keep ALL other configuration variables exactly the same as your previous response.
2. ONLY change the specific fields the user requested.
3. You MUST update the "name" and "description" to accurately match the new numbers (e.g., Do not call it "Top 5" if the user changed the size to 8).

You MUST output ONLY valid JSON matching this exact schema. Do not include markdown formatting, code blocks, or any explanations outside the JSON.

SCHEMA:
{
  "name": "String (A catchy name for the strategy)",
  "description": "String (A 1-2 sentence explanation of the logic)",
  "config": {
    "signal_rule": "moving_average_crossover", // MUST be "moving_average_crossover"
    "short_window": 10,              // MUST be an integer between 2 and 252 and less than long_window
    "long_window": 40,               // MUST be an integer between 3 and 504 and greater than short_window
    "rebalance_frequency": "weekly",  // MUST be one of: "daily", "weekly", "monthly", "quarterly"
    "ranking_metric": "conviction",   // MUST be "conviction"
    "portfolio_size": 5,              // MUST be an integer between 1 and 500
    "sizing": "equal_weight",         // MUST be one of: "equal_weight", "conviction_weighted"
    "sector_cap_pct": 100,            // MUST be an integer between 1 and 100 (use 100 for no sector cap)
    "exit_on_signal_flip": true,      // MUST be a boolean (true or false)
    "min_conviction_score": 0.75      // MUST be a float between 0.0 and 1.0
  }
}
"""

def generate_strategy_rules(messages_history: list) -> dict:
    # Ensure the system prompt is always the first message
    payload_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages_history

    payload = {
        "model": LLM_MODEL,
        "messages": payload_messages,
        "stream": False
    }

    try:
        with httpx.Client(timeout=300.0) as client:
            last_connect_error = None
            response = None
            for api_url in _candidate_chat_urls():
                try:
                    response = client.post(api_url, json=payload)
                    break
                except httpx.ConnectError as exc:
                    last_connect_error = exc

            if response is None:
                attempted_urls = ", ".join(_candidate_chat_urls())
                raise ValueError(
                    f"Could not connect to Ollama. Tried: {attempted_urls}. "
                    "If the backend is running in Docker, set OLLAMA_BASE_URL=http://ollama:11434. "
                    "If it is running locally, start Ollama on localhost:11434."
                ) from last_connect_error

            response.raise_for_status()
            
            data = response.json()
            # /api/chat returns the text inside message.content
            llm_response_text = data.get("message", {}).get("content", "")

            # Clean and parse JSON
            cleaned_text = re.sub(r"```json\s*", "", llm_response_text)
            cleaned_text = re.sub(r"```\s*", "", cleaned_text).strip()

            strategy_dict = json.loads(cleaned_text)
            return {"parsed": strategy_dict, "raw": llm_response_text}
    except Exception as e:
        raise ValueError(f"LLM Error: {str(e)}")

# --- MOCK FOR LOCAL DEVELOPMENT ---
# If you don't have Ollama running yet, you can comment out the real function above 
# and uncomment this mock to continue testing the API and UI immediately.

# def generate_strategy_rules(user_prompt: str) -> dict:
#     """
#     Mock response to bypass Docker memory crashes.
#     This guarantees the backend responds instantly!
#     """
    
#     # We simulate a perfect JSON response that passes our Firewall
#     parsed_config = {
#         "name": "Aggressive Tech Portfolio",
#         "description": f"Strategy based on: '{user_prompt}'.",
#         "config": {
#             "rebalance_frequency": "daily",
#             "ranking_metric": "conviction",
#             "portfolio_size": 3,
#             "sizing": "conviction_weighted",
#             "sector_cap_pct": 100,
#             "exit_on_signal_flip": True
#         }
#     }
    
#     # Return both the parsed dictionary and the raw text for auditing
#     return {
#         "parsed": parsed_config, 
#         "raw": json.dumps(parsed_config, indent=2)
#     }
