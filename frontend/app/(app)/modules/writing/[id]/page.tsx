"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import TranslationInput from "@/components/modules/TranslationInput";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import { api } from "@/lib/api";

// ── Types ─────────────────────────────────────────────────────────────────────

interface RubricCriterion {
  description: string;
  points: number;
  example: string;
}

interface WritingPayload {
  module_type: "writing";
  exercise_type: "inverse_translation";
  challenge_id: string;
  formal_input: string;
  formal_level: string;
  expected_drill_output: string;
  accepted_variants: string[];
  evaluation_rubric: Record<string, RubricCriterion>;
  grammar_explanation: string;
  cefr_target: string;
  xp_reward: number;
}

interface Lesson {
  id: string;
  title: string;
  dialect_segment: "east_coast" | "midwest";
  level_band: string;
  day_order: number;
  audio_url: string;
}

type Phase = "challenge" | "result" | "done";

// ── Component ─────────────────────────────────────────────────────────────────

export default function WritingModulePage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();

  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [payload, setPayload] = useState<WritingPayload | null>(null);
  const [phase, setPhase] = useState<Phase>("challenge");
  const [correct, setCorrect] = useState<boolean | null>(null);
  const [userAnswer, setUserAnswer] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [xpAwarded, setXpAwarded] = useState<number | null>(null);

  useEffect(() => {
    api.get<Lesson>(`/api/content/lessons/${id}`)
      .then((l) => {
        setLesson(l);
        if (l.audio_url.startsWith("{")) {
          setPayload(JSON.parse(l.audio_url) as WritingPayload);
        }
      })
      .catch(() => router.push("/login"))
      .finally(() => setLoading(false));
  }, [id, router]);

  function handleResult(isCorrect: boolean, answer: string) {
    setCorrect(isCorrect);
    setUserAnswer(answer);
    setPhase("result");
  }

  async function handleSaveProgress() {
    if (!lesson || submitting || correct === null) return;
    setSubmitting(true);
    const score = correct ? 100 : 40; // partial credit for attempting
    try {
      const result = await api.post<{ xp_awarded: number }>("/api/progress/lesson", {
        lesson_id: lesson.id,
        module_type: "writing",
        score,
      });
      setXpAwarded(result.xp_awarded);
    } catch {
      // non-fatal
    } finally {
      setSubmitting(false);
      setPhase("done");
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

  const rubricEntries = Object.entries(payload.evaluation_rubric);

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

      {/* Phase: CHALLENGE */}
      {phase === "challenge" && (
        <>
          {/* Rubric preview */}
          <Card>
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-3">
              Scoring Rubric
            </p>
            <div className="space-y-2">
              {rubricEntries.map(([key, criterion]) => (
                <div key={key} className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <p className="text-foreground text-sm">{criterion.description}</p>
                    <p className="text-muted text-xs mt-0.5 font-mono">{criterion.example}</p>
                  </div>
                  <span className="text-accent font-display text-sm flex-shrink-0">
                    +{criterion.points}pts
                  </span>
                </div>
              ))}
            </div>
          </Card>

          {/* Translation challenge */}
          <Card>
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-3">
              🎤 Spitting Bars — Translate to Drill
            </p>
            <TranslationInput
              formalPhrase={payload.formal_input}
              acceptedAnswers={payload.accepted_variants}
              explanation={payload.grammar_explanation}
              onResult={handleResult}
            />
          </Card>
        </>
      )}

      {/* Phase: RESULT */}
      {phase === "result" && correct !== null && (
        <>
          {/* Verdict */}
          <Card className="text-center">
            <p className="text-5xl mb-3">{correct ? "🔥" : "📚"}</p>
            <h2
              className={[
                "font-display text-3xl uppercase mb-2",
                correct ? "text-green-400" : "text-accent",
              ].join(" ")}
            >
              {correct ? "On Point" : "Keep Drilling"}
            </h2>
            <p className="text-muted text-sm">
              {correct
                ? "Your translation matches the drill structure."
                : "Your answer didn't match — check the breakdown below."}
            </p>
          </Card>

          {/* Reference answer */}
          <Card accent>
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-2">
              Reference Answer
            </p>
            <p className="text-foreground text-lg font-bold">
              &ldquo;{payload.expected_drill_output}&rdquo;
            </p>
            {payload.accepted_variants.length > 1 && (
              <div className="mt-3">
                <p className="text-xs text-muted uppercase tracking-wider font-display mb-1">
                  Also accepted
                </p>
                <ul className="space-y-1">
                  {payload.accepted_variants.slice(1).map((v, i) => (
                    <li key={i} className="text-muted text-sm italic">
                      &ldquo;{v}&rdquo;
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </Card>

          {/* Grammar explanation */}
          <Card>
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-3">
              Grammar Breakdown
            </p>
            <p className="text-foreground text-sm leading-relaxed">
              {payload.grammar_explanation}
            </p>
          </Card>

          {/* Rubric breakdown */}
          <Card>
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-3">
              Scoring Criteria
            </p>
            <div className="space-y-3">
              {rubricEntries.map(([key, criterion]) => (
                <div key={key} className="border-b border-border pb-3 last:border-0 last:pb-0">
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-foreground text-sm font-bold capitalize">
                      {key.replace(/_/g, " ")}
                    </p>
                    <span className="text-accent font-display text-sm">
                      {criterion.points} pts
                    </span>
                  </div>
                  <p className="text-muted text-xs">{criterion.description}</p>
                  <p className="text-muted text-xs font-mono mt-1">{criterion.example}</p>
                </div>
              ))}
            </div>
          </Card>

          <Button
            variant="primary"
            size="md"
            loading={submitting}
            onClick={handleSaveProgress}
            className="w-full"
          >
            Save Progress (+{correct ? payload.xp_reward : Math.round(payload.xp_reward * 0.4)} XP)
          </Button>
        </>
      )}

      {/* Phase: DONE */}
      {phase === "done" && (
        <Card className="text-center py-10">
          <p className="text-5xl mb-4">✍️</p>
          <h2 className="font-display text-3xl uppercase text-accent mb-2">
            Bars Submitted
          </h2>
          {xpAwarded !== null && (
            <p className="text-muted mb-6">+{xpAwarded} XP earned</p>
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
