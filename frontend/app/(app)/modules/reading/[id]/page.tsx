"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import ChatBubble from "@/components/modules/ChatBubble";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import { api } from "@/lib/api";

// ── Types ─────────────────────────────────────────────────────────────────────

interface BreakdownItem {
  abbr: string;
  meaning: string;
}

interface ReadingPayload {
  module_type: "reading";
  exercise_type: "street_text_decode";
  dialect_focus: string;
  raw_text: string;
  formal_translation: string;
  breakdown: BreakdownItem[];
  grammar_notes: string[];
  cefr_target: string;
  xp_reward: number;
}

interface Lesson {
  id: string;
  title: string;
  dialect_segment: "east_coast" | "midwest";
  level_band: string;
  day_order: number;
  audio_url: string; // JSON-encoded ReadingPayload for reading lessons
}

type Phase = "read" | "breakdown" | "done";

// ── Component ─────────────────────────────────────────────────────────────────

export default function ReadingModulePage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();

  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [payload, setPayload] = useState<ReadingPayload | null>(null);
  const [phase, setPhase] = useState<Phase>("read");
  const [revealedTerms, setRevealedTerms] = useState<Set<string>>(new Set());
  const [activeDefinition, setActiveDefinition] = useState<BreakdownItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [xpAwarded, setXpAwarded] = useState<number | null>(null);

  useEffect(() => {
    api.get<Lesson>(`/api/content/lessons/${id}`)
      .then((l) => {
        setLesson(l);
        // audio_url stores the JSON payload for non-audio lessons
        if (l.audio_url.startsWith("{")) {
          setPayload(JSON.parse(l.audio_url) as ReadingPayload);
        }
      })
      .catch(() => router.push("/login"))
      .finally(() => setLoading(false));
  }, [id, router]);

  async function handleComplete() {
    if (!lesson || submitting) return;
    setSubmitting(true);
    try {
      const result = await api.post<{ xp_awarded: number }>("/api/progress/lesson", {
        lesson_id: lesson.id,
        module_type: "reading",
        score: 100,
      });
      setXpAwarded(result.xp_awarded);
      setPhase("done");
    } catch {
      // non-fatal — still show done state
      setPhase("done");
    } finally {
      setSubmitting(false);
    }
  }

  function handleTermClick(term: string) {
    const item = payload?.breakdown.find(
      (b) => b.abbr.toLowerCase() === term.toLowerCase()
    );
    if (item) {
      setRevealedTerms((prev) => new Set(Array.from(prev).concat(term.toLowerCase())));
      setActiveDefinition(item);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin h-10 w-10 border-2 border-accent border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!lesson || !payload) {
    return (
      <div className="text-center py-16">
        <p className="text-muted">Lesson not found.</p>
        <Link href="/lessons" className="text-accent hover:underline mt-4 block">
          ← Back to Lessons
        </Link>
      </div>
    );
  }

  // Build highlighted terms from breakdown abbreviations
  const highlightedTerms = payload.breakdown.map((b) => ({
    term: b.abbr,
    index: 0,
  }));

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Link href="/lessons" className="text-muted hover:text-foreground transition-colors">
          ←
        </Link>
        <div className="flex-1 min-w-0">
          <h1 className="font-display text-xl uppercase text-foreground tracking-wider truncate">
            {lesson.title}
          </h1>
          <div className="flex gap-2 mt-1">
            <Badge variant={lesson.dialect_segment}>
              {lesson.dialect_segment === "east_coast" ? "East Coast" : "Midwest"}
            </Badge>
            <Badge variant="muted">{lesson.level_band}</Badge>
            <Badge variant="muted">{payload.cefr_target}</Badge>
          </div>
        </div>
      </div>

      {/* Phase: READ */}
      {phase === "read" && (
        <>
          <Card>
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-3">
              📱 Incoming DM — {payload.dialect_focus}
            </p>
            {/* Render as a chat bubble with tappable terms */}
            <ChatBubble
              message={payload.raw_text}
              sender="other"
              highlightedTerms={highlightedTerms}
              onTermClick={handleTermClick}
              timestamp="just now"
            />
            <p className="text-xs text-muted mt-3">
              Tap the <span className="text-accent font-bold">highlighted words</span> to decode them.
            </p>
          </Card>

          {/* Active definition popup */}
          {activeDefinition && (
            <Card accent>
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-display text-lg uppercase text-accent">
                    {activeDefinition.abbr}
                  </p>
                  <p className="text-foreground mt-1">{activeDefinition.meaning}</p>
                </div>
                <button
                  onClick={() => setActiveDefinition(null)}
                  className="text-muted hover:text-foreground ml-4 text-lg leading-none"
                  aria-label="Close definition"
                >
                  ×
                </button>
              </div>
            </Card>
          )}

          {/* Progress indicator */}
          <div className="flex items-center justify-between text-sm text-muted">
            <span>
              {revealedTerms.size} / {payload.breakdown.length} terms decoded
            </span>
            <Button
              variant="primary"
              size="md"
              onClick={() => setPhase("breakdown")}
            >
              See Full Breakdown →
            </Button>
          </div>
        </>
      )}

      {/* Phase: BREAKDOWN */}
      {phase === "breakdown" && (
        <>
          <Card>
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-3">
              Original Message
            </p>
            <p className="text-foreground font-mono text-sm bg-background rounded p-3">
              {payload.raw_text}
            </p>
          </Card>

          {/* Formal translation */}
          <Card accent>
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-2">
              Standard English Translation
            </p>
            <p className="text-foreground leading-relaxed">{payload.formal_translation}</p>
          </Card>

          {/* Term-by-term breakdown */}
          <div>
            <h2 className="font-display text-sm uppercase tracking-wider text-muted mb-3">
              Term Breakdown
            </h2>
            <div className="space-y-2">
              {payload.breakdown.map((item) => (
                <div
                  key={item.abbr}
                  className="flex items-start gap-3 bg-surface border border-border rounded-lg px-4 py-3"
                >
                  <span className="font-display text-accent uppercase text-sm w-28 flex-shrink-0">
                    {item.abbr}
                  </span>
                  <span className="text-foreground text-sm">{item.meaning}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Grammar notes */}
          {payload.grammar_notes.length > 0 && (
            <Card>
              <h2 className="font-display text-sm uppercase tracking-wider text-muted mb-3">
                Grammar Notes
              </h2>
              <ul className="space-y-2">
                {payload.grammar_notes.map((note, i) => (
                  <li key={i} className="flex gap-2 text-sm text-foreground">
                    <span className="text-accent flex-shrink-0">•</span>
                    <span>{note}</span>
                  </li>
                ))}
              </ul>
            </Card>
          )}

          <Button
            variant="primary"
            size="md"
            loading={submitting}
            onClick={handleComplete}
            className="w-full"
          >
            Complete Lesson (+{payload.xp_reward} XP)
          </Button>
        </>
      )}

      {/* Phase: DONE */}
      {phase === "done" && (
        <Card className="text-center py-10">
          <p className="text-5xl mb-4">🔥</p>
          <h2 className="font-display text-3xl uppercase text-accent mb-2">
            Lesson Complete
          </h2>
          {xpAwarded !== null && (
            <p className="text-muted mb-6">
              +{xpAwarded} XP earned
            </p>
          )}
          <div className="flex gap-3 justify-center">
            <Link href="/lessons">
              <Button variant="secondary" size="md">Back to Lessons</Button>
            </Link>
            <Link href="/dashboard">
              <Button variant="primary" size="md">Dashboard</Button>
            </Link>
          </div>
        </Card>
      )}
    </div>
  );
}
