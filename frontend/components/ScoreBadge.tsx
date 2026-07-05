const STATUS = {
  good: { color: "#0ca30c", label: "매력적", icon: "▲" },
  warning: { color: "#c98500", label: "보통", icon: "●" },
  critical: { color: "#d03b3b", label: "비매력적", icon: "▼" },
} as const;

function bandFor(score: number): keyof typeof STATUS {
  if (score >= 65) return "good";
  if (score >= 35) return "warning";
  return "critical";
}

export default function ScoreBadge({ score }: { score: number }) {
  const band = STATUS[bandFor(score)];
  return (
    <div className="flex items-center gap-3">
      <span className="text-4xl font-semibold tabular-nums">{score.toFixed(1)}</span>
      <span
        className="flex items-center gap-1 rounded-full px-3 py-1 text-sm font-medium"
        style={{ color: band.color, backgroundColor: `${band.color}1a` }}
      >
        <span aria-hidden>{band.icon}</span>
        {band.label}
      </span>
    </div>
  );
}
