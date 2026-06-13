from django.contrib.auth import get_user_model
from django.test import TestCase

from conversations import debate_service
from conversations.models import DebateMessage, DebateSession, StockSignal
from market.models import Asset

User = get_user_model()


class DebateAgentEvalTests(TestCase):
  def test_judge_json_parser_accepts_fenced_json_and_normalizes_values(self):
    parsed = debate_service._parse_judge_json(
        """
        ```json
        {
          "action": "buy",
          "conviction": 1.7,
          "judge_reasoning": "Bull case is stronger after the rebuttals."
        }
        ```
        """
    )

    self.assertEqual(parsed["action"], "BUY")
    self.assertEqual(parsed["conviction"], 1.0)
    self.assertEqual(parsed["judge_reasoning"], "Bull case is stronger after the rebuttals.")

  def test_debate_flow_persists_agent_messages_and_stock_signal(self):
    user = User.objects.create_user(username="debateuser", email="debate@example.com", password="password123")
    asset = Asset.objects.get(symbol="AAPL")
    session = DebateSession.objects.create(
        user=user,
        stock=asset,
        topic="Bull vs Bear: AAPL",
    )
    responses = iter([
        "Bull thesis",
        "Bear thesis",
        "Bear rebuttal",
        "Bull rebuttal",
        '{"action": "HOLD", "conviction": 0.62, "judge_reasoning": "Balanced risks."}',
    ])

    original_call_llm = debate_service._call_llm
    debate_service._call_llm = lambda system_prompt, user_prompt: next(responses)
    try:
      signal = debate_service.run_debate(session, asset)
    finally:
      debate_service._call_llm = original_call_llm

    session.refresh_from_db()
    self.assertEqual(session.status, DebateSession.Status.COMPLETED)
    self.assertEqual(signal.action, StockSignal.Action.HOLD)
    self.assertEqual(float(signal.conviction), 0.62)
    self.assertEqual(signal.judge_reasoning, "Balanced risks.")
    self.assertEqual(DebateMessage.objects.filter(session=session).count(), 5)
    self.assertEqual(
        list(DebateMessage.objects.filter(session=session).values_list("agent_role", flat=True)),
        ["bullish", "bearish", "bearish", "bullish", "judge"],
    )
