from unittest.mock import Mock, patch
from django.test import SimpleTestCase, TestCase
from conversations.debate_service import _call_llm, _parse_judge_json, run_debate
from conversations.models import DebateMessage, DebateSession
from market.models import Asset
from django.contrib.auth import get_user_model

User = get_user_model()


class DebateServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.asset = Asset.objects.get(symbol="AAPL")
        self.session = DebateSession.objects.create(user=self.user, stock=self.asset, topic="AAPL")

    def test_parse_judge_json_valid(self):
        raw_json = '{"action": "BUY", "conviction": 0.85, "judge_reasoning": "Strong buy because of fundamentals."}'
        result = _parse_judge_json(raw_json)
        self.assertEqual(result["action"], "BUY")
        self.assertEqual(result["conviction"], 0.85)
        self.assertEqual(result["judge_reasoning"], "Strong buy because of fundamentals.")

    def test_parse_judge_json_markdown_wrapped(self):
        raw_json = '```json\n{"action": "SELL", "conviction": 0.9, "judge_reasoning": "Overvalued."}\n```'
        result = _parse_judge_json(raw_json)
        self.assertEqual(result["action"], "SELL")
        self.assertEqual(result["conviction"], 0.9)

    def test_parse_judge_json_malformed_fallback(self):
        # Some extra text around the JSON
        raw_json = 'Here is the verdict:\n{"action": "HOLD", "conviction": "0.5", "judge_reasoning": "Unclear future."}\nThank you.'
        result = _parse_judge_json(raw_json)
        self.assertEqual(result["action"], "HOLD")
        self.assertEqual(result["conviction"], 0.5)

    def test_parse_judge_json_invalid_action(self):
        raw_json = '{"action": "SHORT", "conviction": 0.8, "judge_reasoning": "Bad stock."}'
        result = _parse_judge_json(raw_json)
        self.assertEqual(result["action"], "HOLD")  # Should fallback to HOLD

    def test_parse_judge_json_clamps_conviction(self):
        raw_json = '{"action": "BUY", "conviction": 2.5, "judge_reasoning": "Too high."}'
        result = _parse_judge_json(raw_json)
        self.assertEqual(result["conviction"], 1.0)

    def test_parse_judge_json_no_json(self):
        raw_json = "I think it is a BUY but I forgot to output JSON."
        with self.assertRaises(ValueError):
            _parse_judge_json(raw_json)

    @patch("conversations.debate_service._call_llm")
    def test_run_debate_success(self, mock_call_llm):
        # Setup mock responses
        mock_call_llm.side_effect = [
            "Bull thesis here.",
            "Bear thesis here.",
            "Bear rebuttal here.",
            "Bull rebuttal here.",
            '{"action": "BUY", "conviction": 0.8, "judge_reasoning": "Bull wins."}',
        ]

        signal = run_debate(self.session, self.asset)

        self.assertEqual(mock_call_llm.call_count, 5)
        self.assertEqual(DebateMessage.objects.filter(session=self.session).count(), 5)

        self.session.refresh_from_db()
        self.assertEqual(self.session.status, DebateSession.Status.COMPLETED)

        self.assertEqual(signal.action, "BUY")
        self.assertEqual(signal.conviction, 0.80)
        self.assertEqual(signal.bull_thesis, "Bull thesis here.")

    @patch("conversations.debate_service._call_llm")
    def test_run_debate_failure(self, mock_call_llm):
        # Simulate LLM timeout or error on the first call
        mock_call_llm.side_effect = Exception("LLM connection error")

        with self.assertRaises(Exception):
            run_debate(self.session, self.asset)

        self.session.refresh_from_db()
        self.assertEqual(self.session.status, DebateSession.Status.FAILED)
        self.assertIn("Debate failed", self.session.summary)


class DebateLlmCallTests(SimpleTestCase):
    @patch("conversations.debate_service.httpx.Client")
    def test_call_llm_supports_response_format(self, mock_client_factory):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"response": "ok"}
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_factory.return_value = mock_client

        result = _call_llm("system", "prompt", response_format="json")

        self.assertEqual(result, "ok")
        _, kwargs = mock_client.post.call_args
        self.assertEqual(kwargs["json"]["format"], "json")
