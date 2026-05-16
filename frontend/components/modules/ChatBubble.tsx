import React from "react";

type Sender = "self" | "other";

interface HighlightedTerm {
  term: string;
  /** Index of the term within the message text */
  index: number;
}

interface ChatBubbleProps {
  message: string;
  sender: Sender;
  /** Terms to highlight as interactive quiz targets */
  highlightedTerms?: HighlightedTerm[];
  /** Called when user clicks a highlighted term */
  onTermClick?: (term: string) => void;
  timestamp?: string;
}

export default function ChatBubble({
  message,
  sender,
  highlightedTerms = [],
  onTermClick,
  timestamp,
}: ChatBubbleProps) {
  const isSelf = sender === "self";

  // Render message with highlighted terms as interactive spans
  function renderMessage() {
    if (highlightedTerms.length === 0) {
      return <span>{message}</span>;
    }

    const termSet = new Set(highlightedTerms.map((t) => t.term.toLowerCase()));
    // Split message by highlighted terms (case-insensitive)
    const pattern = new RegExp(
      `(${highlightedTerms.map((t) => t.term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|")})`,
      "gi"
    );
    const parts = message.split(pattern);

    return (
      <>
        {parts.map((part, i) =>
          termSet.has(part.toLowerCase()) ? (
            <button
              key={i}
              onClick={() => onTermClick?.(part)}
              className="inline-block bg-accent/20 text-accent border-b-2 border-accent px-0.5 rounded-sm font-bold hover:bg-accent/30 transition-colors cursor-pointer focus:outline-none focus:ring-1 focus:ring-accent"
              aria-label={`Tap to define: ${part}`}
            >
              {part}
            </button>
          ) : (
            <span key={i}>{part}</span>
          )
        )}
      </>
    );
  }

  return (
    // Req 4.1: iMessage/DM style bubbles differentiated by sender
    <div className={`flex ${isSelf ? "justify-end" : "justify-start"} mb-3`}>
      <div
        className={[
          "max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed",
          isSelf
            ? "bg-accent text-white rounded-br-sm"
            : "bg-surface border border-border text-foreground rounded-bl-sm",
        ].join(" ")}
      >
        <p>{renderMessage()}</p>
        {timestamp && (
          <p className={`text-xs mt-1 ${isSelf ? "text-red-200" : "text-muted"}`}>
            {timestamp}
          </p>
        )}
      </div>
    </div>
  );
}
