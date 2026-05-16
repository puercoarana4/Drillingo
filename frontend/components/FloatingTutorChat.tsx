"use client";

import { useState, useRef, useEffect } from "react";
import { getToken } from "@/lib/auth";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface ChatMessage {
  role: "user" | "model";
  content: string;
}

const SUGGESTED_PROMPTS = [
  "What does 'merch it' mean?",
  "Correct this: 'He is not going to do that'",
  "Who is DD Osama?",
  "Explain double negation in AAVE",
  "How do I use 'finna'?",
];

export default function FloatingTutorChat() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [streamingText, setStreamingText] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [open]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingText]);

  async function sendMessage(text: string) {
    if (!text.trim() || streaming) return;

    const userMsg: ChatMessage = { role: "user", content: text };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput("");
    setStreaming(true);
    setStreamingText("");

    // Build history for API (exclude the message we just added)
    const history = messages.map((m) => ({ role: m.role, content: m.content }));

    try {
      const token = getToken();
      const response = await fetch(`${BASE_URL}/api/ai/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ message: text, history }),
      });

      if (!response.ok || !response.body) {
        throw new Error(`HTTP ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullText = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          try {
            const data = JSON.parse(line.slice(6));
            if (data.token) {
              fullText += data.token;
              setStreamingText(fullText);
            }
            if (data.done) {
              setMessages((prev) => [
                ...prev,
                { role: "model", content: data.full ?? fullText },
              ]);
              setStreamingText("");
            }
            if (data.error) {
              setMessages((prev) => [
                ...prev,
                { role: "model", content: "Something went wrong. Try again." },
              ]);
              setStreamingText("");
            }
          } catch {
            // ignore parse errors on partial chunks
          }
        }
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "model", content: "Can't reach the tutor right now. Check your connection." },
      ]);
      setStreamingText("");
    } finally {
      setStreaming(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  }

  return (
    <>
      {/* Floating button */}
      <button
        onClick={() => setOpen((o) => !o)}
        className={[
          "fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full shadow-lg",
          "flex items-center justify-center transition-all duration-200",
          open ? "bg-border rotate-45" : "bg-accent hover:bg-red-700",
        ].join(" ")}
        aria-label={open ? "Close tutor" : "Open Da Block Tutor"}
      >
        {open ? (
          <svg className="w-6 h-6 text-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <span className="text-2xl">🎤</span>
        )}
      </button>

      {/* Chat panel */}
      {open && (
        <div className="fixed bottom-24 right-6 z-50 w-80 sm:w-96 flex flex-col bg-surface border border-border rounded-2xl shadow-2xl overflow-hidden"
          style={{ maxHeight: "70vh" }}>
          {/* Header */}
          <div className="flex items-center gap-3 px-4 py-3 bg-background border-b border-border flex-shrink-0">
            <div className="w-8 h-8 rounded-full bg-accent flex items-center justify-center text-sm">🎤</div>
            <div>
              <p className="font-display text-sm uppercase tracking-wider text-foreground">Da Block Tutor</p>
              <p className="text-xs text-muted">Powered by Gemini</p>
            </div>
            <div className="ml-auto w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-0">
            {messages.length === 0 && (
              <div className="space-y-3">
                <p className="text-muted text-sm text-center">
                  Wassup. Ask me anything about Drill, AAVE, or your lessons.
                </p>
                <div className="space-y-2">
                  {SUGGESTED_PROMPTS.map((p) => (
                    <button
                      key={p}
                      onClick={() => sendMessage(p)}
                      className="w-full text-left px-3 py-2 rounded-lg bg-background border border-border text-muted text-xs hover:text-foreground hover:border-accent transition-colors"
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={[
                    "max-w-[85%] rounded-2xl px-3 py-2 text-sm leading-relaxed",
                    msg.role === "user"
                      ? "bg-accent text-white rounded-br-sm"
                      : "bg-background border border-border text-foreground rounded-bl-sm",
                  ].join(" ")}
                >
                  {msg.content}
                </div>
              </div>
            ))}

            {/* Streaming token */}
            {streamingText && (
              <div className="flex justify-start">
                <div className="max-w-[85%] rounded-2xl rounded-bl-sm px-3 py-2 text-sm leading-relaxed bg-background border border-border text-foreground">
                  {streamingText}
                  <span className="inline-block w-1 h-4 bg-accent ml-0.5 animate-pulse" />
                </div>
              </div>
            )}

            {streaming && !streamingText && (
              <div className="flex justify-start">
                <div className="bg-background border border-border rounded-2xl rounded-bl-sm px-4 py-3">
                  <div className="flex gap-1">
                    {[0, 1, 2].map((i) => (
                      <div
                        key={i}
                        className="w-2 h-2 rounded-full bg-muted animate-bounce"
                        style={{ animationDelay: `${i * 0.15}s` }}
                      />
                    ))}
                  </div>
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="flex items-center gap-2 px-3 py-3 border-t border-border flex-shrink-0">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={streaming}
              placeholder="Ask anything..."
              className="flex-1 bg-background border border-border rounded-xl px-3 py-2 text-sm text-foreground placeholder-muted focus:outline-none focus:border-accent transition-colors"
            />
            <button
              onClick={() => sendMessage(input)}
              disabled={!input.trim() || streaming}
              className="w-9 h-9 rounded-xl bg-accent text-white flex items-center justify-center hover:bg-red-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex-shrink-0"
              aria-label="Send"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </div>
      )}
    </>
  );
}
