from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIClient

from backtests.engine import (
    PriceBar,
    _default_windows_for_frequency,
    _is_rebalance_day,
    _max_drawdown_pct,
    _strategy_mode,
)
from market.models import Asset, AssetPrice
from strategies.models import Strategy

User = get_user_model()


class BacktestApiTests(TestCase):
    def test_backtest_requires_own_or_public_strategy(self):
        owner = User.objects.create_user(username="owner", email="owner@example.com", password="password123")
        other = User.objects.create_user(username="other", email="other@example.com", password="password123")
        stock = Asset.objects.get(symbol="AAPL")
        private_strategy = Strategy.objects.create(owner=other, name="Private", config={}, is_public=False)
        public_strategy = Strategy.objects.create(owner=other, name="Public", config={}, is_public=True)

        client = APIClient()
        client.force_authenticate(owner)
        payload = {
            "strategy": private_strategy.id,
            "stock": stock.id,
            "start_date": "2025-01-02",
            "end_date": "2025-01-02",
            "initial_cash": "10000.00",
        }

        private_response = client.post("/backtests", payload, format="json")
        public_response = client.post(
            "/backtests",
            {**payload, "strategy": public_strategy.id},
            format="json",
        )

        self.assertEqual(private_response.status_code, 400)
        self.assertEqual(public_response.status_code, 201)

    def test_cannot_backtest_draft_strategy(self):
        owner = User.objects.create_user(username="owner2", email="owner2@example.com", password="password123")
        client = APIClient()
        client.force_authenticate(owner)

        # create a draft strategy owned by the user
        from strategies.models import Strategy

        s = Strategy.objects.create(owner=owner, name="Draft", config={}, source=Strategy.Source.AI, status=Strategy.Status.DRAFT)
        stock = Asset.objects.get(symbol="AAPL")
        payload = {
            "strategy": s.id,
            "stock": stock.id,
            "start_date": "2025-01-02",
            "end_date": "2025-01-02",
            "initial_cash": "10000.00",
        }
        resp = client.post("/backtests", payload, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_backtest_computes_buy_and_hold_results_from_stored_prices(self):
        owner = User.objects.create_user(username="runner", email="runner@example.com", password="password123")
        stock = Asset.objects.get(symbol="AAPL")
        strategy = Strategy.objects.create(
            owner=owner,
            name="Buy Hold",
            config={"mode": "buy_and_hold"},
            status=Strategy.Status.APPROVED,
        )
        self._create_price(stock, "2025-01-02", "100.00", "110.00")
        self._create_price(stock, "2025-01-03", "110.00", "120.00")

        client = APIClient()
        client.force_authenticate(owner)
        response = client.post(
            "/backtests",
            {
                "strategy": strategy.id,
                "stock": stock.id,
                "start_date": "2025-01-02",
                "end_date": "2025-01-03",
                "initial_cash": "10000.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "completed")
        self.assertEqual(response.data["metrics"]["final_equity"], 12000.0)
        self.assertEqual(response.data["metrics"]["total_return_pct"], 20.0)
        self.assertEqual(response.data["metrics"]["price_rows"], 2)
        self.assertEqual(response.data["trades"][0]["action"], "BUY")

    def test_backtest_records_failure_when_price_data_is_missing(self):
        owner = User.objects.create_user(username="nodata", email="nodata@example.com", password="password123")
        stock = Asset.objects.get(symbol="MSFT")
        strategy = Strategy.objects.create(
            owner=owner,
            name="No Data Strategy",
            config={"mode": "buy_and_hold"},
            status=Strategy.Status.APPROVED,
        )

        client = APIClient()
        client.force_authenticate(owner)
        response = client.post(
            "/backtests",
            {
                "strategy": strategy.id,
                "stock": stock.id,
                "start_date": "2025-01-02",
                "end_date": "2025-01-03",
                "initial_cash": "10000.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "failed")
        self.assertIn("requires at least two stored price rows", response.data["error_message"])

    def test_moving_average_backtest_records_trades(self):
        owner = User.objects.create_user(username="sma", email="sma@example.com", password="password123")
        stock = Asset.objects.get(symbol="NVDA")
        strategy = Strategy.objects.create(
            owner=owner,
            name="SMA Cross",
            config={"mode": "moving_average_crossover", "short_window": 2, "long_window": 3},
            status=Strategy.Status.APPROVED,
        )
        start = date(2025, 1, 2)
        closes = ["10", "10", "10", "12", "14", "16"]
        for offset, close in enumerate(closes):
            self._create_price(stock, start + timedelta(days=offset), close, close)

        client = APIClient()
        client.force_authenticate(owner)
        response = client.post(
            "/backtests",
            {
                "strategy": strategy.id,
                "stock": stock.id,
                "start_date": "2025-01-02",
                "end_date": "2025-01-07",
                "initial_cash": "10000.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "completed")
        self.assertEqual(response.data["metrics"]["mode"], "moving_average_crossover")
        self.assertGreaterEqual(response.data["metrics"]["trade_count"], 1)

    def test_generated_strategy_config_runs_active_trading_by_default(self):
        owner = User.objects.create_user(username="active", email="active@example.com", password="password123")
        stock = Asset.objects.get(symbol="TSLA")
        strategy = Strategy.objects.create(
            owner=owner,
            name="Active AI Strategy",
            config={
                "rebalance_frequency": "daily",
                "ranking_metric": "conviction",
                "portfolio_size": 1,
                "sizing": "equal_weight",
                "sector_cap_pct": 100,
                "exit_on_signal_flip": True,
                "min_conviction_score": 0.5,
                "short_window": 2,
                "long_window": 3,
            },
            status=Strategy.Status.APPROVED,
        )
        start = date(2025, 1, 2)
        closes = ["10", "10", "10", "12", "14", "10", "8", "7"]
        for offset, close in enumerate(closes):
            self._create_price(stock, start + timedelta(days=offset), close, close)

        client = APIClient()
        client.force_authenticate(owner)
        response = client.post(
            "/backtests",
            {
                "strategy": strategy.id,
                "stock": stock.id,
                "start_date": "2025-01-02",
                "end_date": "2025-01-09",
                "initial_cash": "10000.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "completed")
        self.assertEqual(response.data["metrics"]["mode"], "moving_average_crossover")
        self.assertEqual([trade["action"] for trade in response.data["trades"]], ["BUY", "SELL"])

    def _create_price(self, stock, point_date, open_price, close_price):
        return AssetPrice.objects.create(
            asset=stock,
            date=point_date,
            open=open_price,
            high=close_price,
            low=open_price,
            close=close_price,
            adjusted_close=close_price,
            volume=1000,
            source="test",
        )


class BacktestEngineTests(SimpleTestCase):
    def test_strategy_mode_defaults_to_moving_average(self):
        self.assertEqual(_strategy_mode({}), "moving_average_crossover")
        self.assertEqual(_strategy_mode({"signal_rule": "moving_average_crossover"}), "moving_average_crossover")
        self.assertEqual(_strategy_mode({"mode": "buy_and_hold"}), "buy_and_hold")
        self.assertEqual(_strategy_mode({"rebalance_frequency": "weekly"}), "moving_average_crossover")

    def test_default_windows_for_frequency(self):
        self.assertEqual(_default_windows_for_frequency("daily"), (5, 20))
        self.assertEqual(_default_windows_for_frequency("monthly"), (20, 60))
        self.assertEqual(_default_windows_for_frequency("quarterly"), (50, 100))
        self.assertEqual(_default_windows_for_frequency("weekly"), (10, 40))

    def test_is_rebalance_day(self):
        bars = [
            PriceBar(date=date(2025, 1, 6), open=Decimal("1"), close=Decimal("1")),
            PriceBar(date=date(2025, 1, 7), open=Decimal("1"), close=Decimal("1")),
            PriceBar(date=date(2025, 1, 13), open=Decimal("1"), close=Decimal("1")),
        ]
        self.assertFalse(_is_rebalance_day(bars, 0, "weekly"))
        self.assertFalse(_is_rebalance_day(bars, 1, "weekly"))
        self.assertTrue(_is_rebalance_day(bars, 2, "weekly"))
        self.assertTrue(_is_rebalance_day(bars, 1, "daily"))

    def test_max_drawdown_pct(self):
        drawdown = _max_drawdown_pct([Decimal("100"), Decimal("120"), Decimal("90")])
        self.assertEqual(drawdown, -25.0)
