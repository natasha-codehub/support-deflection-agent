import ConfidenceBadge from "./ConfidenceBadge";
import EscalationCard from "./EscalationCard";

function SourceBadge({ source }) {
  const name = source.file.replace(/_/g, " ").replace(".md", "");
  return (
    <span className="inline-block text-xs bg-blue-50 text-blue-700 border border-blue-200 rounded px-2 py-0.5">
      {name}
    </span>
  );
}

export default function Message({ msg }) {
  if (msg.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[75%] bg-blue-600 text-white rounded-2xl rounded-tr-sm px-4 py-2.5 text-sm shadow-sm">
          {msg.content}
        </div>
      </div>
    );
  }

  if (msg.role === "agent") {
    const { tier, reply, sources, escalated, escalation_reason, confidence_score, intent } = msg.data;

    if (escalated) {
      return (
        <div className="flex justify-start gap-2">
          <div className="w-8 h-8 rounded-full bg-gray-200 flex-shrink-0 flex items-center justify-center text-xs font-bold text-gray-600">
            A
          </div>
          <div className="max-w-[80%] space-y-2">
            <EscalationCard reason={escalation_reason} intent={intent} />
          </div>
        </div>
      );
    }

    return (
      <div className="flex justify-start gap-2">
        <div className="w-8 h-8 rounded-full bg-blue-600 flex-shrink-0 flex items-center justify-center text-xs font-bold text-white">
          A
        </div>
        <div className="max-w-[80%] space-y-2">
          <div className={`rounded-2xl rounded-tl-sm px-4 py-3 text-sm shadow-sm whitespace-pre-wrap ${
            tier === "medium" ? "bg-amber-50 border border-amber-200" : "bg-white border border-gray-200"
          }`}>
            {reply}
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <ConfidenceBadge tier={tier} score={confidence_score} />
            {sources && sources.map((s, i) => <SourceBadge key={i} source={s} />)}
          </div>
        </div>
      </div>
    );
  }

  if (msg.role === "typing") {
    return (
      <div className="flex justify-start gap-2">
        <div className="w-8 h-8 rounded-full bg-blue-600 flex-shrink-0 flex items-center justify-center text-xs font-bold text-white">
          A
        </div>
        <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
          <div className="flex gap-1 items-center h-4">
            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
          </div>
        </div>
      </div>
    );
  }

  return null;
}
