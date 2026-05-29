import { useState, useRef, useEffect } from "react";
import Message from "./Message";
import PMAnnotation from "./PMAnnotation";

const SUGGESTED = [
  "Where is my order ORD-4521?",
  "Send me POD for ORD-4522",
  "How do I submit a tax exemption certificate?",
  "I got 8 cylinders but was billed for 10",
  "How do I add a new delivery location?",
];

function generateSessionId() {
  return "sess-" + Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
}

export default function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(generateSessionId);
  const [showAnnotation, setShowAnnotation] = useState(false);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage(text) {
    const msg = text.trim();
    if (!msg || loading) return;

    setMessages((prev) => [...prev, { role: "user", content: msg, id: Date.now() }]);
    setInput("");
    setLoading(true);
    setMessages((prev) => [...prev, { role: "typing", id: "typing" }]);

    try {
      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, message: msg }),
      });
      const data = await res.json();
      setMessages((prev) =>
        prev
          .filter((m) => m.id !== "typing")
          .concat({ role: "agent", data, id: Date.now() })
      );
    } catch {
      setMessages((prev) =>
        prev
          .filter((m) => m.id !== "typing")
          .concat({
            role: "agent",
            data: {
              reply: "",
              tier: "low",
              confidence_score: 0,
              intent: "error",
              sources: [],
              escalated: true,
              escalation_reason: "Service temporarily unavailable. Please try again shortly.",
              tool_used: null,
            },
            id: Date.now(),
          })
      );
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  }

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-white shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-blue-600 flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-900">AcmeCo Support</p>
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
              <span className="text-xs text-gray-500">AI Agent · Online</span>
            </div>
          </div>
        </div>
        <button
          onClick={() => setShowAnnotation(true)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-blue-50 text-blue-700 hover:bg-blue-100 transition-colors border border-blue-200"
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M12 2a10 10 0 100 20A10 10 0 0012 2z" />
          </svg>
          How this works
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full gap-6 py-8">
            <div className="text-center">
              <div className="w-16 h-16 rounded-full bg-blue-600 flex items-center justify-center mx-auto mb-3">
                <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <h2 className="text-lg font-semibold text-gray-900">How can I help you today?</h2>
              <p className="text-sm text-gray-500 mt-1">Ask about orders, deliveries, billing, or account setup.</p>
            </div>
            <div className="w-full max-w-sm space-y-2">
              {SUGGESTED.map((s) => (
                <button
                  key={s}
                  onClick={() => sendMessage(s)}
                  className="w-full text-left text-sm px-4 py-2.5 rounded-xl border border-gray-200 bg-white hover:border-blue-400 hover:bg-blue-50 transition-colors text-gray-700"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((msg) => (
          <Message key={msg.id} msg={msg} />
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="px-4 py-3 border-t border-gray-200 bg-white">
        <div className="flex gap-2">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your question..."
            rows={1}
            disabled={loading}
            className="flex-1 resize-none rounded-xl border border-gray-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 min-h-[42px] max-h-32"
            style={{ height: "42px", overflowY: "auto" }}
          />
          <button
            onClick={() => sendMessage(input)}
            disabled={!input.trim() || loading}
            className="flex-shrink-0 w-10 h-10 mt-0.5 rounded-xl bg-blue-600 text-white flex items-center justify-center hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
        <p className="text-xs text-gray-400 mt-1.5 text-center">
          AI-powered · Answers grounded in AcmeCo policy
        </p>
      </div>

      {showAnnotation && <PMAnnotation onClose={() => setShowAnnotation(false)} />}
    </div>
  );
}
