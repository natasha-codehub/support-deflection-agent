export default function ConfidenceBadge({ tier, score }) {
  const config = {
    high: { label: "High Confidence", bg: "bg-green-100", text: "text-green-800", dot: "bg-green-500" },
    medium: { label: "Medium Confidence", bg: "bg-amber-100", text: "text-amber-800", dot: "bg-amber-500" },
    low: { label: "Low Confidence", bg: "bg-red-100", text: "text-red-800", dot: "bg-red-500" },
  };
  const c = config[tier] || config.low;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${c.bg} ${c.text}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${c.dot}`} />
      {c.label}
      {score != null && <span className="opacity-60">· {(score * 100).toFixed(0)}%</span>}
    </span>
  );
}
