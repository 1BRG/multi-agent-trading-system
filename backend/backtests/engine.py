from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from math import sqrt
from statistics import mean, stdev
from typing import Any

from market.models import Asset, AssetPrice
from strategies.models import Strategy


@dataclass(frozen=True)
class PriceBar:
  date: date
  open: Decimal
  close: Decimal


def run_backtest(
    *,
    strategy: Strategy,
    stock: Asset,
    start_date: date,
    end_date: date,
    initial_cash: Decimal,
) -> dict[str, Any]:
  bars = [
      PriceBar(date=row.date, open=row.open, close=row.adjusted_close or row.close)
      for row in AssetPrice.objects.filter(
          asset=stock,
          date__gte=start_date,
          date__lte=end_date,
      ).order_by("date")
  ]

  if len(bars) < 2:
    raise ValueError("Backtest requires at least two stored price rows in the selected date range.")

  config = strategy.config or {}
  mode = _strategy_mode(config)

  if mode == "moving_average_crossover":
    return _run_moving_average_crossover(
        bars=bars,
        config=config,
        initial_cash=initial_cash,
        stock=stock,
        strategy=strategy,
    )

  return _run_buy_and_hold(
      bars=bars,
      config=config,
      initial_cash=initial_cash,
      stock=stock,
      strategy=strategy,
  )


def _strategy_mode(config: dict[str, Any]) -> str:
  raw_mode = (
      config.get("type")
      or config.get("mode")
      or config.get("entry_rule")
      or config.get("signal_rule")
      or "moving_average_crossover"
  )
  mode = str(raw_mode).strip().lower()
  if mode in {"sma_cross", "ma_cross", "moving_average", "moving_average_crossover"}:
    return "moving_average_crossover"
  if mode in {"buy_hold", "buy_and_hold", "hold"}:
    return "buy_and_hold"
  if "rebalance_frequency" in config:
    return "moving_average_crossover"
  return "buy_and_hold"


def _run_buy_and_hold(
    *,
    bars: list[PriceBar],
    config: dict[str, Any],
    initial_cash: Decimal,
    stock: Asset,
    strategy: Strategy,
) -> dict[str, Any]:
  first = bars[0]
  last = bars[-1]
  shares = initial_cash / first.open
  cash = Decimal("0")
  equity_curve = _mark_to_market_curve(bars, cash, shares)
  final_equity = shares * last.close
  trades = [
      _trade_payload(
          date=first.date,
          action="BUY",
          price=first.open,
          shares=shares,
          cash_after=cash,
          equity_after=shares * first.close,
          reason="Initial buy-and-hold entry",
      )
  ]

  return {
      "metrics": _metrics(
          equity_curve=equity_curve,
          initial_cash=initial_cash,
          final_equity=final_equity,
          bars=bars,
          trades=trades,
          strategy=strategy,
          stock=stock,
          mode="buy_and_hold",
          config=config,
      ),
      "equity_curve": equity_curve,
      "trades": trades,
  }


def _run_moving_average_crossover(
    *,
    bars: list[PriceBar],
    config: dict[str, Any],
    initial_cash: Decimal,
    stock: Asset,
    strategy: Strategy,
) -> dict[str, Any]:
  default_short_window, default_long_window = _default_windows_for_frequency(
      str(config.get("rebalance_frequency", "weekly"))
  )
  short_window = _positive_int(config.get("short_window") or config.get("fast_window"), default_short_window)
  long_window = _positive_int(config.get("long_window") or config.get("slow_window"), default_long_window)
  rebalance_frequency = str(config.get("rebalance_frequency", "weekly")).lower()
  exit_on_signal_flip = bool(config.get("exit_on_signal_flip", True))

  if short_window >= long_window:
    raise ValueError("Moving average strategy requires short_window to be less than long_window.")
  if len(bars) <= long_window:
    raise ValueError(
        f"Backtest requires more than {long_window} price rows for this moving average strategy."
    )

  cash = initial_cash
  shares = Decimal("0")
  trades: list[dict[str, Any]] = []
  equity_curve: list[dict[str, Any]] = []

  for index, bar in enumerate(bars):
    if index >= long_window and _is_rebalance_day(bars, index, rebalance_frequency):
      prior_closes = [candidate.close for candidate in bars[:index]]
      short_ma = _average_decimal(prior_closes[-short_window:])
      long_ma = _average_decimal(prior_closes[-long_window:])
      should_hold = short_ma > long_ma

      if should_hold and shares == 0:
        shares = cash / bar.open
        cash = Decimal("0")
        trades.append(
            _trade_payload(
                date=bar.date,
                action="BUY",
                price=bar.open,
                shares=shares,
                cash_after=cash,
                equity_after=shares * bar.close,
                reason=(
                    f"{rebalance_frequency.title()} rebalance: "
                    f"{short_window}-day average above {long_window}-day average"
                ),
            )
        )
      elif not should_hold and shares > 0 and exit_on_signal_flip:
        cash = shares * bar.open
        trades.append(
            _trade_payload(
                date=bar.date,
                action="SELL",
                price=bar.open,
                shares=shares,
                cash_after=cash,
                equity_after=cash,
                reason=(
                    f"{rebalance_frequency.title()} rebalance: "
                    f"{short_window}-day average below {long_window}-day average"
                ),
            )
        )
        shares = Decimal("0")

    equity_curve.append(_equity_point(bar.date, cash + shares * bar.close))

  final_equity = Decimal(str(equity_curve[-1]["equity"]))
  return {
      "metrics": _metrics(
          equity_curve=equity_curve,
          initial_cash=initial_cash,
          final_equity=final_equity,
          bars=bars,
          trades=trades,
          strategy=strategy,
          stock=stock,
          mode="moving_average_crossover",
          config={
              **config,
              "rebalance_frequency": rebalance_frequency,
              "short_window": short_window,
              "long_window": long_window,
          },
      ),
      "equity_curve": equity_curve,
      "trades": trades,
  }


def _metrics(
    *,
    equity_curve: list[dict[str, Any]],
    initial_cash: Decimal,
    final_equity: Decimal,
    bars: list[PriceBar],
    trades: list[dict[str, Any]],
    strategy: Strategy,
    stock: Asset,
    mode: str,
    config: dict[str, Any],
) -> dict[str, Any]:
  equity_values = [Decimal(str(point["equity"])) for point in equity_curve]
  returns = [
      float((equity_values[index] / equity_values[index - 1]) - Decimal("1"))
      for index in range(1, len(equity_values))
      if equity_values[index - 1] > 0
  ]
  total_return = (final_equity / initial_cash) - Decimal("1")
  years = max((bars[-1].date - bars[0].date).days / 365.25, 1 / 365.25)
  annualized_return = (float(final_equity / initial_cash) ** (1 / years)) - 1
  volatility = stdev(returns) * sqrt(252) if len(returns) > 1 else 0.0
  sharpe_ratio = (mean(returns) / stdev(returns)) * sqrt(252) if len(returns) > 1 and stdev(returns) else 0.0
  benchmark_return = (bars[-1].close / bars[0].open) - Decimal("1")

  return {
      "strategy_name": strategy.name,
      "symbol": stock.symbol,
      "mode": mode,
      "start_date": bars[0].date.isoformat(),
      "end_date": bars[-1].date.isoformat(),
      "initial_cash": _money(initial_cash),
      "final_equity": _money(final_equity),
      "total_return_pct": _pct(total_return),
      "annualized_return_pct": round(annualized_return * 100, 2),
      "benchmark_return_pct": _pct(benchmark_return),
      "max_drawdown_pct": _max_drawdown_pct(equity_values),
      "sharpe_ratio": round(sharpe_ratio, 3),
      "volatility_pct": round(volatility * 100, 2),
      "trade_count": len(trades),
      "win_rate_pct": _win_rate_pct(trades),
      "price_rows": len(bars),
      "config": config,
  }


def _mark_to_market_curve(
    bars: list[PriceBar],
    cash: Decimal,
    shares: Decimal,
) -> list[dict[str, Any]]:
  return [_equity_point(bar.date, cash + shares * bar.close) for bar in bars]


def _equity_point(point_date: date, equity: Decimal) -> dict[str, Any]:
  return {
      "date": point_date.isoformat(),
      "equity": _money(equity),
  }


def _trade_payload(
    *,
    date: date,
    action: str,
    price: Decimal,
    shares: Decimal,
    cash_after: Decimal,
    equity_after: Decimal,
    reason: str,
) -> dict[str, Any]:
  return {
      "date": date.isoformat(),
      "action": action,
      "price": _money(price),
      "shares": round(float(shares), 6),
      "cash_after": _money(cash_after),
      "equity_after": _money(equity_after),
      "reason": reason,
  }


def _max_drawdown_pct(equity_values: list[Decimal]) -> float:
  peak = equity_values[0]
  max_drawdown = Decimal("0")
  for equity in equity_values:
    peak = max(peak, equity)
    if peak > 0:
      max_drawdown = min(max_drawdown, (equity / peak) - Decimal("1"))
  return _pct(max_drawdown)


def _win_rate_pct(trades: list[dict[str, Any]]) -> float:
  round_trips = []
  entry = None
  for trade in trades:
    if trade["action"] == "BUY":
      entry = trade
    elif trade["action"] == "SELL" and entry:
      round_trips.append(float(trade["price"]) > float(entry["price"]))
      entry = None
  if not round_trips:
    return 0.0
  return round((sum(1 for item in round_trips if item) / len(round_trips)) * 100, 2)


def _average_decimal(values: list[Decimal]) -> Decimal:
  return sum(values, Decimal("0")) / Decimal(len(values))


def _positive_int(value: Any, fallback: int) -> int:
  try:
    parsed = int(value)
  except (TypeError, ValueError):
    return fallback
  return parsed if parsed > 0 else fallback


def _default_windows_for_frequency(rebalance_frequency: str) -> tuple[int, int]:
  frequency = rebalance_frequency.lower()
  if frequency == "daily":
    return 5, 20
  if frequency == "monthly":
    return 20, 60
  if frequency == "quarterly":
    return 50, 100
  return 10, 40


def _is_rebalance_day(bars: list[PriceBar], index: int, rebalance_frequency: str) -> bool:
  if index <= 0:
    return False

  current = bars[index].date
  previous = bars[index - 1].date
  frequency = rebalance_frequency.lower()

  if frequency == "daily":
    return True
  if frequency == "weekly":
    return current.isocalendar()[:2] != previous.isocalendar()[:2]
  if frequency == "monthly":
    return current.month != previous.month or current.year != previous.year
  if frequency == "quarterly":
    current_quarter = (current.month - 1) // 3
    previous_quarter = (previous.month - 1) // 3
    return current_quarter != previous_quarter or current.year != previous.year

  return True


def _money(value: Decimal) -> float:
  return round(float(value), 2)


def _pct(value: Decimal) -> float:
  return round(float(value * Decimal("100")), 2)
