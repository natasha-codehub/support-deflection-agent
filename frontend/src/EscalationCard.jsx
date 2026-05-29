export default function EscalationCard({ reason, intent }) {
  return (
    <div className="rounded-xl border border-red-200 bg-red-50 p-4 space-y-3">
      <div className="flex items-start gap-3">
        <div className="mt-0.5 flex-shrink-0 w-8 h-8 rounded-full bg-red-100 flex items-center justify-center">
          <svg className="w-4 h-4 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M12 3a9 9 0 100 18A9 9 0 0012 3z" />
          </svg>
        </div>
        <div>
          <p className="text-sm font-semibold text-red-800">Connecting you with our support team</p>
          <p className="text-xs text-red-600 mt-0.5">{reason || "This query needs human assistance."}</p>
        </div>
      </div>
      <div className="flex flex-col sm:flex-row gap-2">
        <a
          href="mailto:support@acmeco.com?subject=Support Request"
          className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-red-600 text-white text-sm font-medium hover:bg-red-700 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          Email Support
        </a>
        <button
          onClick={() => alert("Ticket creation stubbed — integrate Zendesk/Freshdesk in production.")}
          className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg border border-red-300 text-red-700 text-sm font-medium hover:bg-red-100 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          Open a Ticket
        </button>
      </div>
    </div>
  );
}
