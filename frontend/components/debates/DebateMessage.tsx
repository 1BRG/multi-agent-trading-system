"use client";

import type { DebateMessage as DebateMessageType } from "../../types/debate";

interface DebateMessageProps {
  message: DebateMessageType;
}

const ROLE_CONFIG: Record<string, { label: string; className: string }> = {
  bullish: { label: "🐂 Bull Analyst", className: "debate-msg-bull" },
  bearish: { label: "🐻 Bear Analyst", className: "debate-msg-bear" },
  judge: { label: "⚖️ Judge", className: "debate-msg-judge" },
};

const ROUND_LABELS: Record<number, string> = {
  1: "Opening Argument",
  2: "Opening Argument",
  3: "Rebuttal",
  4: "Rebuttal",
  5: "Final Verdict",
};

export function DebateMessage({ message }: DebateMessageProps) {
  const config = ROLE_CONFIG[message.agent_role] ?? {
    label: message.agent_name,
    className: "",
  };

  const roundLabel = ROUND_LABELS[message.round_number] ?? `Round ${message.round_number}`;

  return (
    <article className={`debate-message ${config.className}`}>
      <div className="debate-msg-header">
        <strong>{config.label}</strong>
        <span className="debate-msg-round">{roundLabel}</span>
      </div>
      <div className="debate-msg-content">
        {message.content.split("\n").map((paragraph, i) =>
          paragraph.trim() ? <p key={i}>{paragraph}</p> : null
        )}
      </div>
    </article>
  );
}
