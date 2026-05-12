from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIClient

from strategies.ai_service import _candidate_chat_urls, generate_strategy_rules
from strategies.models import Strategy

User = get_user_model()


class StrategyApiTests(TestCase):
    def test_user_sees_own_and_public_strategies_only(self):
        owner = User.objects.create_user(username="owner", email="owner@example.com", password="password123")
        other = User.objects.create_user(username="other", email="other@example.com", password="password123")
        Strategy.objects.create(owner=owner, name="Private", config={}, is_public=False)
        Strategy.objects.create(owner=other, name="Public", config={}, is_public=True)
        Strategy.objects.create(owner=other, name="Other private", config={}, is_public=False)

        client = APIClient()
        client.force_authenticate(owner)
        response = client.get("/strategies")

        self.assertEqual(response.status_code, 200)
        self.assertEqual({item["name"] for item in response.data}, {"Private", "Public"})

    @patch("strategies.views.generate_strategy_rules")
    def test_generate_ai_creates_draft_and_stores_raw(self, mock_generate):
        user = User.objects.create_user(username="aiuser", email="ai@example.com", password="password123")
        client = APIClient()
        client.force_authenticate(user)

        mock_generate.return_value = {
            "parsed": {
                "name": "Mock AI",
                "description": "mock",
                "config": {
                    "rebalance_frequency": "weekly",
                    "ranking_metric": "conviction",
                    "portfolio_size": 3,
                    "sizing": "equal_weight",
                    "sector_cap_pct": 100,
                    "exit_on_signal_flip": True,
                    "min_conviction_score": 0.75,
                    "short_window": 5,
                    "long_window": 20,
                },
            },
            "raw": "RAW TEXT",
        }

        resp = client.post("/strategies/generate_ai", {"prompt": "make me a strategy"}, format="json")
        self.assertEqual(resp.status_code, 201)
        data = resp.data
        self.assertEqual(data["status"], "draft")
        s = Strategy.objects.get(id=data["id"])
        self.assertEqual(s.raw_llm_response, "RAW TEXT")
        self.assertEqual(s.source, Strategy.Source.AI)


class StrategyAiServiceTests(SimpleTestCase):
    @patch("strategies.ai_service.OLLAMA_BASE_URL", "http://localhost:11434")
    def test_candidate_chat_urls_includes_docker_fallback(self):
        self.assertEqual(
            _candidate_chat_urls(),
            ["http://localhost:11434/api/chat", "http://ollama:11434/api/chat"],
        )

    @patch("strategies.ai_service.httpx.Client")
    def test_generate_strategy_rules_parses_json_response(self, mock_client_factory):
        response_text = (
            "```json\n"
            "{\"name\": \"Mock\", \"description\": \"desc\", "
            "\"config\": {\"rebalance_frequency\": \"weekly\", "
            "\"ranking_metric\": \"conviction\", \"portfolio_size\": 3, "
            "\"sizing\": \"equal_weight\", \"sector_cap_pct\": 100, "
            "\"exit_on_signal_flip\": true, \"min_conviction_score\": 0.75}}\n"
            "```"
        )
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"message": {"content": response_text}}
        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_factory.return_value = mock_client

        result = generate_strategy_rules([{"role": "user", "content": "make a strategy"}])

        self.assertEqual(result["parsed"]["name"], "Mock")
        self.assertEqual(result["parsed"]["config"]["rebalance_frequency"], "weekly")
        self.assertEqual(result["raw"], response_text)
