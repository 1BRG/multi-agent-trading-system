"""
Debate AI Service — orchestrates a 5-round Bull / Bear / Judge debate
over a single stock using the local Ollama LLM.

Flow:
  1. Bull opens   (round 1)
  2. Bear opens   (round 2)
  3. Bear rebuts  (round 3)
  4. Bull rebuts  (round 4)
  5. Judge decides (round 5)
"""

import json
import os
import re

import httpx

from conversations.models import DebateMessage, DebateSession, StockSignal
from market.models import Asset

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
LLM_API_URL = f"{OLLAMA_BASE_URL}/api/generate"
LLM_MODEL = os.getenv("LLM_MODEL", "llama3")

# ---------------------------------------------------------------------------
# System prompts for each agent
# ---------------------------------------------------------------------------

BULL_SYSTEM = """You are a senior equity analyst with a BULLISH outlook.
Your job is to present the strongest possible investment case for the stock.
Focus on: competitive advantages, growth catalysts, strong financials, market tailwinds, and management quality.
Be specific, use reasoning, and cite concrete factors. Keep your response to 2-3 paragraphs."""

BEAR_SYSTEM = """You are a senior equity analyst with a BEARISH outlook.
Your job is to present the strongest possible case AGAINST the stock.
Focus on: competitive threats, valuation concerns, slowing growth, regulatory risks, balance-sheet weaknesses, and macro headwinds.
Be specific, use reasoning, and cite concrete factors. Keep your response to 2-3 paragraphs."""

JUDGE_SYSTEM = """You are a senior portfolio manager acting as an impartial judge.
You have read a structured debate between a Bull analyst and a Bear analyst about a stock.
Your job is to weigh both arguments and render a final verdict.

You MUST output ONLY valid JSON matching this exact schema. Do not include markdown formatting, code blocks, or any explanations outside the JSON.

SCHEMA:
{
  "action": "BUY",
  "conviction": 0.78,
  "judge_reasoning": "One paragraph explaining your decision, referencing the strongest points from each side."
}

Rules:
- "action" MUST be one of: "BUY", "SELL", "HOLD"
- "conviction" MUST be a decimal between 0.00 and 1.00 representing confidence in the action
  (0.50 = low confidence, 0.75 = moderate, 0.90+ = very high)
- "judge_reasoning" MUST be a single paragraph string
"""


def _call_llm(system_prompt: str, user_prompt: str, response_format: str | None = None) -> str:
    """Send a prompt to the Ollama LLM and return the response text."""
    payload = {
        "model": LLM_MODEL,
        "system": system_prompt,
        "prompt": user_prompt,
        "stream": False,
    }
    if response_format:
        payload["format"] = response_format

    with httpx.Client(timeout=300.0) as client:
        response = client.post(LLM_API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()


def _save_message(
    session: DebateSession,
    agent_name: str,
    agent_role: str,
    round_number: int,
    content: str,
) -> DebateMessage:
    """Persist a debate message to the database."""
    return DebateMessage.objects.create(
        session=session,
        agent_name=agent_name,
        agent_role=agent_role,
        round_number=round_number,
        content=content,
    )


def _parse_judge_json(raw_text: str) -> dict:
    """Extract and parse the Judge's JSON verdict from raw LLM output."""
    # Strip markdown code fences if present
    cleaned = re.sub(r"```json\s*", "", raw_text)
    cleaned = re.sub(r"```\s*", "", cleaned).strip()

    try:
        result = json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback: try to find JSON object in the text
        match = re.search(r"\{[^{}]*\}", cleaned, re.DOTALL)
        if match:
            result = json.loads(match.group())
        else:
            raise ValueError("The Judge LLM failed to return valid JSON.")

    # Validate required fields
    action = str(result.get("action", "HOLD")).upper()
    if action not in ("BUY", "SELL", "HOLD"):
        action = "HOLD"

    conviction = result.get("conviction", 0.5)
    try:
        conviction = float(conviction)
        conviction = max(0.0, min(1.0, conviction))
    except (TypeError, ValueError):
        conviction = 0.5

    reasoning = result.get("judge_reasoning", "No reasoning provided.")

    return {
        "action": action,
        "conviction": round(conviction, 4),
        "judge_reasoning": str(reasoning),
    }


def run_debate(session: DebateSession, asset: Asset) -> StockSignal:
    """
    Execute the full 5-round debate for a given stock.

    Returns the created StockSignal with the Judge's verdict.
    """
    ticker = asset.symbol
    stock_name = asset.name

    session.status = DebateSession.Status.RUNNING
    session.save(update_fields=["status"])

    try:
        # ── Round 1: Bull opens ──────────────────────────────────────────
        bull_open_prompt = (
            f"Present your bullish investment thesis for {ticker} ({stock_name}). "
            f"Why should an investor BUY this stock right now?"
        )
        bull_open = _call_llm(BULL_SYSTEM, bull_open_prompt)
        _save_message(session, "Bull Analyst", "bullish", 1, bull_open)

        # ── Round 2: Bear opens ──────────────────────────────────────────
        bear_open_prompt = (
            f"The Bull analyst has presented the following case for {ticker} ({stock_name}):\n\n"
            f"{bull_open}\n\n"
            f"Now present your bearish counter-thesis. Why should an investor AVOID this stock?"
        )
        bear_open = _call_llm(BEAR_SYSTEM, bear_open_prompt)
        _save_message(session, "Bear Analyst", "bearish", 2, bear_open)

        # ── Round 3: Bear rebuts ─────────────────────────────────────────
        bear_rebuttal_prompt = (
            f"You previously argued against {ticker}. The Bull's opening was:\n\n"
            f"{bull_open}\n\n"
            f"Provide a focused rebuttal of the Bull's strongest points. "
            f"What are they getting wrong or overstating?"
        )
        bear_rebuttal = _call_llm(BEAR_SYSTEM, bear_rebuttal_prompt)
        _save_message(session, "Bear Analyst", "bearish", 3, bear_rebuttal)

        # ── Round 4: Bull rebuts ─────────────────────────────────────────
        bull_rebuttal_prompt = (
            f"You previously argued for {ticker}. The Bear's arguments were:\n\n"
            f"Bear Opening:\n{bear_open}\n\n"
            f"Bear Rebuttal:\n{bear_rebuttal}\n\n"
            f"Provide a focused rebuttal of the Bear's strongest points. "
            f"What are they getting wrong or overstating?"
        )
        bull_rebuttal = _call_llm(BULL_SYSTEM, bull_rebuttal_prompt)
        _save_message(session, "Bull Analyst", "bullish", 4, bull_rebuttal)

        # ── Round 5: Judge decides ───────────────────────────────────────
        judge_prompt = (
            f"Stock under review: {ticker} ({stock_name})\n\n"
            f"=== BULL OPENING ===\n{bull_open}\n\n"
            f"=== BEAR OPENING ===\n{bear_open}\n\n"
            f"=== BEAR REBUTTAL ===\n{bear_rebuttal}\n\n"
            f"=== BULL REBUTTAL ===\n{bull_rebuttal}\n\n"
            f"Based on the above debate, render your verdict as JSON."
        )
        judge_raw = _call_llm(JUDGE_SYSTEM, judge_prompt, response_format="json")
        verdict = _parse_judge_json(judge_raw)

        _save_message(session, "Judge", "judge", 5, judge_raw)

        # ── Create StockSignal ───────────────────────────────────────────
        signal = StockSignal.objects.create(
            user=session.user,
            asset=asset,
            debate_session=session,
            action=verdict["action"],
            conviction=verdict["conviction"],
            bull_thesis=bull_open,
            bear_thesis=bear_open,
            judge_reasoning=verdict["judge_reasoning"],
        )

        session.status = DebateSession.Status.COMPLETED
        session.summary = (
            f"Verdict: {verdict['action']} | "
            f"Conviction: {verdict['conviction']}"
        )
        session.save(update_fields=["status", "summary"])

        return signal

    except Exception as exc:
        session.status = DebateSession.Status.FAILED
        session.summary = f"Debate failed: {str(exc)[:500]}"
        session.save(update_fields=["status", "summary"])
        raise
