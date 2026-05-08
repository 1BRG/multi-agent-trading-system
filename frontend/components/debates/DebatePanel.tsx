"use client";

import type { StockSignal } from "../../types/debate";

interface DebatePanelProps {
  signal: StockSignal;
}

const ACTION_STYLES: Record<string, { bg: string; color: string; label: string }> = {
  BUY: { bg: "#ecfdf3", color: "#027a48", label: "BUY" },
  SELL: { bg: "#fff1f3", color: "#c9162b", label: "SELL" },
  HOLD: { bg: "#fffaeb", color: "#b54708", label: "HOLD" },
};

export function DebatePanel({ signal }: DebatePanelProps) {
  const style = ACTION_STYLES[signal.action] ?? ACTION_STYLES.HOLD;
  const pct = Math.round(signal.conviction * 100);

  return (
    <section className="debate-verdict-panel">
      <div className="debate-verdict-header">
        <div>
          <p className="eyebrow">Judge&apos;s Verdict</p>
          <div className="debate-verdict-action-row">
            <span
              className="debate-verdict-badge"
              style={{ background: style.bg, color: style.color }}
            >
              {style.label}
            </span>
            <span className="debate-verdict-ticker">{signal.ticker}</span>
          </div>
        </div>
        <div className="debate-conviction-ring">
          <svg viewBox="0 0 36 36" className="debate-conviction-svg">
            <path
              className="debate-conviction-bg"
              d="M18 2.0845
                a 15.9155 15.9155 0 0 1 0 31.831
                a 15.9155 15.9155 0 0 1 0 -31.831"
            />
            <path
              className="debate-conviction-fg"
              strokeDasharray={`${pct}, 100`}
              style={{ stroke: style.color }}
              d="M18 2.0845
                a 15.9155 15.9155 0 0 1 0 31.831
                a 15.9155 15.9155 0 0 1 0 -31.831"
            />
          </svg>
          <span className="debate-conviction-label">{pct}%</span>
        </div>
      </div>

      <div className="debate-verdict-reasoning">
        <p className="eyebrow">Reasoning</p>
        <p>{signal.judge_reasoning}</p>
      </div>
    </section>
  );
}
