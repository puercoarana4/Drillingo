"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import AudioPlayer from "@/components/modules/AudioPlayer";
import FillInBlank, { BlankSlot, BlankResult } from "@/components/modules/FillInBlank";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import { api } from "@/lib/api";

// ── Types ─────────────────────────────────────────────────────────────────────

interface BlankDef {
  position: number;
  correct_answers: string[];
  hint: string;
  distractor_options: string[];
}

interface ListeningPayload {
  module_type: "listening";
  exercise_type: "fill_in_the_blanks";
  artist: string;
  dialect_focus: string;
  audio_s3_url: string;
  original_bar: string;
  exercise_text: string;
  blanks: BlankDef[];
  full_translation: string;
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
  audio_url: string;
}

type Phase = "listen" | "exercise" | "results" | "done";

// ── Helpers ───────────────────────────────────────────────────────────────────

/**
 * Convert the seed's exercise_text format ("We ______ slide") into the
 * FillInBlank component's {{blank_id}} format.
 */
function buildTranscript(exerciseText: string, blanks: BlankDef[]): string {
  let transcript = exerciseText;
  let blankIndex = 0;
  transcript = transcript.replace(/______/g, () => {
    const id = `blank_${blankIndex++}`;
    return `{{${id}}}`;
  });
  return transcript;
}

function buildBlankSlots(blanks: BlankDef[]): BlankSlot[] {
  return blanks.map((b, i) => ({
    id: `blank_${i}`,
    position: b.position,
    correctAnswer: b.correct_answers[0],
    explanation: b.hint,
  }));
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function ListeningModulePage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();

  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [payload, setPayload] = useState<ListeningPayload | null>(null);
  const [phase, setPhase] = useState<Phase>("listen");
  const [results, setResults] = useState<BlankResult[]>([]);
  const [score, setScore] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [xpAwarded, setXpAwarded] = useState<number | null>(null);

  useEffect(() => {
    api.get<Lesson>(`/api/content/lessons/${id}`)
      .then((l) => {
        setLesson(l);
        if (l.audio_url.startsWith("{")) {
          setPayload(JSON.parse(l.audio_url) as ListeningPayload);
        }
      })
      .catch(() => router.push("/login"))
      .finally(() => setLoading(false));
  }, [id, router]);

  function handleExerciseComplete(finalScore: number, blankResults: BlankResult[]) {
    setScore(finalScore);
    setResults(blankResults);
    setPhase("results");
  }

  async function handleSaveProgress() {
    if (!lesson || submitting || score === null) return;
    setSubmitting(true);
    try {
      const result = await api.post<{ xp_awarded: number }>("/api/progress/lesson", {
        lesson_id: lesson.id,
        module_type: "listening",
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

  const transcript = buildTranscript(payload.exercise_text, payload.blanks);
  const blankSlots = buildBlankSlots(payload.blanks);

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

      {/* Phase: LISTEN */}
      {phase === "listen" && (
        <>
          <Card>
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-1">
              Artist
            </p>
            <p className="font-display text-2xl uppercase text-foreground mb-4">
              {payload.artist}
            </p>
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-1">
              Dialect
            </p>
            <p className="text-muted text-sm mb-4">{payload.dialect_focus}</p>

            {/* Audio player */}
            <AudioPlayer
              audioUrl={payload.audio_s3_url}
              title={`${payload.artist} — The Cypher`}
            />
          </Card>

          <Card>
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-2">
              The Bar
            </p>
            <p className="text-foreground text-lg italic">
              &ldquo;{payload.original_bar}&rdquo;
            </p>
          </Card>

          <Button
            variant="primary"
            size="md"
            onClick={() => setPhase("exercise")}
            className="w-full"
          >
            Start Fill-in-the-Blanks →
          </Button>
        </>
      )}

      {/* Phase: EXERCISE */}
      {phase === "exercise" && (
        <>
          <Card>
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-3">
              🎵 Fill in the blanks
            </p>
            <FillInBlank
              transcript={transcript}
              blanks={blankSlots}
              onComplete={handleExerciseComplete}
            />
          </Card>

          {/* Distractor hints */}
          <Card>
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-3">
              Word Bank
            </p>
            <div className="flex flex-wrap gap-2">
              {payload.blanks.flatMap((b) => b.distractor_options).map((opt, i) => (
                <span
                  key={i}
                  className="px-3 py-1 bg-background border border-border rounded-full text-sm text-muted font-display uppercase"
                >
                  {opt}
                </span>
              ))}
            </div>
          </Card>
        </>
      )}

      {/* Phase: RESULTS */}
      {phase === "results" && score !== null && (
        <>
          {/* Score */}
          <Card className="text-center">
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-2">
              Score
            </p>
            <p
              className={[
                "font-display text-6xl mb-2",
                score >= 80 ? "text-green-400" : score >= 50 ? "text-yellow-400" : "text-accent",
              ].join(" ")}
            >
              {score}
            </p>
            <p className="text-muted text-sm">out of 100</p>
          </Card>

          {/* Full translation */}
          <Card accent>
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-2">
              Full Translation
            </p>
            <p className="text-foreground leading-relaxed">{payload.full_translation}</p>
          </Card>

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
            onClick={handleSaveProgress}
            className="w-full"
          >
            Save Progress (+{payload.xp_reward} XP)
          </Button>
        </>
      )}

      {/* Phase: DONE */}
      {phase === "done" && (
        <Card className="text-center py-10">
          <p className="text-5xl mb-4">🎙️</p>
          <h2 className="font-display text-3xl uppercase text-accent mb-2">
            Cypher Complete
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
