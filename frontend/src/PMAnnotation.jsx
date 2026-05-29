import { useState, useEffect } from "react";

const ARCH_NOTES = [
  {
    title: "Why RAG + Tool Calling over a Rules Engine",
    body: "Rules engines break on edge cases and require constant maintenance. RAG lets the agent answer from living documentation — update the markdown file, the behaviour updates. Tool calling grounds order-specific answers in real data, not hallucinations.",
  },
  {
    title: "Confidence as a Dial, Not a Binary",
    body: "The 0.65/0.80 thresholds are env-configurable. If escalation rate exceeds 30%, widen the medium band. If you observe hallucinations, tighten. This mirrors how variance thresholds work in invoice automation — the right value is negotiated with the business, not hardcoded.",
  },
  {
    title: "The Escalation Log is the Product Feedback Loop",
    body: "Every low-confidence query is logged with its intent. These become KB gap candidates for the next sprint. The agent improves through use — escalation rate is the quality metric, not just a failure mode.",
  },
  {
    title: "POC → Production Delta",
    body: "Mock JSON → real OMS/ERP API. ChromaDB local → Pinecone with auto-sync. In-memory sessions → Redis with TTL. Stubbed escalation → Zendesk ticket creation. The architecture is production-shaped; the data sources are swappable.",
  },
];

function StatCard({ label, value, sub }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-3">
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      <p className="text-xs font-medium text-gray-600">{label}</p>
      {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
    </div>
  );
}

export default function PMAnnotation({ onClose }) {
  const [analytics, setAnalytics] = useState(null);
  const [activeNote, setActiveNote] = useState(0);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const res = await fetch("/analytics");
        const data = await res.json();
        setAnalytics(data);
      } catch {
        // backend not running
      }
    };
    fetchAnalytics();
    const id = setInterval(fetchAnalytics, 10000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="fixed inset-0 z-50 flex">
      <div className="flex-1 bg-black/40" onClick={onClose} />
      <div className="w-full max-w-md bg-white shadow-2xl flex flex-col overflow-hidden">
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-200 bg-gray-50">
          <div>
            <h2 className="text-base font-bold text-gray-900">How This Works</h2>
            <p className="text-xs text-gray-500">Architecture & PM decisions</p>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-gray-200 transition-colors">
            <svg className="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-5 space-y-6">
          {/* Live Stats */}
          {analytics && (
            <section>
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Live Stats</h3>
              <div className="grid grid-cols-2 gap-2">
                <StatCard label="Total Queries" value={analytics.total_queries} />
                <StatCard
                  label="Deflection Rate"
                  value={`${(analytics.deflection_rate * 100).toFixed(0)}%`}
                  sub="Target: >70%"
                />
                <StatCard
                  label="Avg Confidence"
                  value={`${(analytics.avg_confidence * 100).toFixed(0)}%`}
                />
                <StatCard label="Escalated" value={analytics.escalated} sub="Routed to human" />
              </div>
            </section>
          )}

          {/* Architecture */}
          <section>
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Architecture Flow</h3>
            <div className="space-y-1.5 text-xs">
              {[
                ["1", "Query → Intent Classification", "Gemini 2.0 Flash"],
                ["2", "RAG Retrieval", "ChromaDB · k=5 chunks"],
                ["3", "Tool Call (conditional)", "orders_lookup / pod_lookup"],
                ["4", "Confidence Gate", "mean(top-3 scores) → tier"],
                ["5", "Response Generation", "Grounded in KB + tool data"],
              ].map(([step, label, tech]) => (
                <div key={step} className="flex items-start gap-2.5">
                  <span className="w-5 h-5 rounded-full bg-blue-600 text-white text-[10px] font-bold flex items-center justify-center flex-shrink-0">
                    {step}
                  </span>
                  <div>
                    <span className="font-medium text-gray-800">{label}</span>
                    <span className="text-gray-400 ml-1">— {tech}</span>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* PM Notes */}
          <section>
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">PM Decisions</h3>
            <div className="flex gap-1.5 flex-wrap mb-3">
              {ARCH_NOTES.map((n, i) => (
                <button
                  key={i}
                  onClick={() => setActiveNote(i)}
                  className={`text-xs px-2.5 py-1 rounded-full font-medium transition-colors ${
                    activeNote === i
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                  }`}
                >
                  {i + 1}
                </button>
              ))}
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3.5">
              <p className="text-xs font-semibold text-blue-900 mb-1.5">{ARCH_NOTES[activeNote].title}</p>
              <p className="text-xs text-blue-800 leading-relaxed">{ARCH_NOTES[activeNote].body}</p>
            </div>
          </section>

          {/* Confidence Tiers */}
          <section>
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Confidence Tiers</h3>
            <div className="space-y-2">
              {[
                { tier: ">80%", label: "High", desc: "Direct answer + source citation", color: "green" },
                { tier: "65–80%", label: "Medium", desc: "Answer + verify disclaimer", color: "amber" },
                { tier: "<65%", label: "Low", desc: "Escalate to human", color: "red" },
              ].map((t) => (
                <div key={t.tier} className={`flex items-center gap-3 p-2.5 rounded-lg bg-${t.color}-50 border border-${t.color}-200`}>
                  <span className={`text-xs font-bold text-${t.color}-700 w-12`}>{t.tier}</span>
                  <div>
                    <span className={`text-xs font-semibold text-${t.color}-800`}>{t.label}</span>
                    <span className={`text-xs text-${t.color}-600 ml-1.5`}>— {t.desc}</span>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Stack */}
          <section>
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Stack</h3>
            <div className="grid grid-cols-2 gap-2 text-xs">
              {[
                ["LLM", "Gemini 2.0 Flash"],
                ["Embeddings", "text-embedding-004"],
                ["Vector DB", "ChromaDB"],
                ["Backend", "FastAPI + Python"],
                ["Frontend", "React 19 + Tailwind"],
                ["Deploy", "Render + Vercel"],
              ].map(([k, v]) => (
                <div key={k} className="bg-gray-50 rounded p-2">
                  <p className="text-gray-400 text-[10px] uppercase tracking-wider">{k}</p>
                  <p className="font-medium text-gray-800">{v}</p>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
