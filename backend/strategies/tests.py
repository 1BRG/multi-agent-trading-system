from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

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

  def test_generate_ai_creates_draft_and_stores_raw(self):
    user = User.objects.create_user(username="aiuser", email="ai@example.com", password="password123")
    client = APIClient()
    client.force_authenticate(user)

    # Patch the ai_service to return a predictable response
    from strategies import ai_service

    def mock_generate(messages_history):
      self.assertEqual(messages_history[-1], {"role": "user", "content": "make me a strategy"})
      return {
          "parsed": {
              "name": "Mock AI",
              "description": "mock",
              "config": {
                  "signal_rule": "moving_average_crossover",
                  "short_window": 10,
                  "long_window": 40,
                  "rebalance_frequency": "weekly",
                  "ranking_metric": "conviction",
                  "portfolio_size": 3,
                  "sizing": "equal_weight",
                  "sector_cap_pct": 100,
                  "exit_on_signal_flip": True,
                  "min_conviction_score": 0.65,
              },
          },
          "raw": "RAW TEXT",
      }

    original = ai_service.generate_strategy_rules
    ai_service.generate_strategy_rules = mock_generate
    try:
      resp = client.post("/strategies/generate_ai", {"prompt": "make me a strategy"}, format="json")
      self.assertEqual(resp.status_code, 201)
      data = resp.data
      self.assertEqual(data["status"], "draft")
      # Fetch the strategy from DB and ensure raw_llm_response is stored
      from strategies.models import Strategy
      s = Strategy.objects.get(id=data["id"])
      self.assertEqual(s.raw_llm_response, "RAW TEXT")
    finally:
      ai_service.generate_strategy_rules = original
    
    
