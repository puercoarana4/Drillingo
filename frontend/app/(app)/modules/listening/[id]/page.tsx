"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import AudioPlayer from "@/components/modules/AudioPlayer";
import FillInBlank, { BlankResult } from "@/components/modules/FillInBlank";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import { api } from "@/lib/api";

interface ListeningExercise {
  lesson_id: string;
  title: string;
  dialect_segment: "east_coast" | "midwest";
  audio_url: string;
  transcript: string;
  blanks: Array<{
    id: string;
    position: number;
    correctAnswer: string;
    explanation: string;
  }>;
  semantic_question?: {
    question: string;
    answer: string;
  };
}

export default function ListeningPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();

  const [exercise, setExercise] = useState<ListeningExercise | null>(null);
  const [loading, setLoading] = useState(true);
  const [fillScore, setFillScore] = useState<number | null>(null);
  const [semanticAnswer, setSemanticAnswer] = useState("");
  const [semanticSubmitted, setSemanticSubmitted] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [xpEarned, setXpEarned] = useState(0);

  useEffect(() => {
    api.get<ListeningExercise>(`/api/content/lessons/${id}`)
      .then((data) => setExercise(data as unknown as ListeningExercise))
      .catch(() => router.push("/lessons"))
      .finally(() => setLoading(false));
  }, [id, router]);

  async function handleFillComplete(score: number, _results: BlankResult[]) {
    setFillScore(score);
    if (!exercise?.semantic_question) {
      await submitProgress(score);
    }
  }

  async function handleSemanticSubmit() {
    setSemanticSubmitted(true);
    const finalScore = fillScore ?? 0;
    await submitProgress(finalScore);
  }

  async function submitProgress(score: number) {
    if (!exercise) return;
    try {
      const res = await api.post<{ xp_awarded: number }>("/api/progress/lesson", {
        lesson_id: exercise.lesson_id,
        module_type: "listening",
        score,
      });
      setXpEarned(res.xp_awarded);
    } catch {
      // continue even if progress fails
    }
    setCompleted(true);
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin h-8 w-8 border-2 border-accent border-t-transparent rounded-full" />
      </div>
    );
  }

  if (completed) {
    return (
      <Card accent className="max-w-lg mx-auto text-center">
        <p className="text-4xl mb-4">🎤</p>
        <h2 className="font-display text-3xl uppercase text-accent mb-2">Bars Decoded</h2>
        <p className="text-muted mb-4">
          Score: <span className="text-foreground font-bold">{fillScore}%</span>
        </p>
        <p className="text-accent font-display text-xl mb-6">+{xpEarned} XP</p>
        <Button onClick={() => router.push("/lessons")} variant="primary">
          Back to Lessons
        </Button>
      </Card>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl uppercase text-foreground">
            {exercise?.title ?? "The Cypher"}
          </h1>
          {exercise?.dialect_segment && (
            <Badge variant={exercise.dialect_segment} className="mt-1">
              {exercise.dialect_segment === "east_coast" ? "East Coast" : "Midwest"}
            </Badge>
          )}
        </div>
      </div>

      {/* Audio player — streams directly from S3 (Req 5.7, 5.8) */}
      {exercise?.audio_url && (
        <AudioPlayer audioUrl={exercise.audio_url} title={exercise.title} />
      )}

      {/* Fill in the blanks (Req 5.2) */}
      {exercise && fillScore === null && (
        <Card>
          <h2 className="font-display text-lg uppercase text-muted mb-4">
            Complete the Bars
          </h2>
          <FillInBlank
            transcript={exercise.transcript}
            blanks={exercise.blanks}
            onComplete={handleFillComplete}
          />
        </Card>
      )}

      {/* Semantic question (Req 5.5) */}
      {fillScore !== null && exercise?.semantic_question && !semanticSubmitted && (
        <Card accent>
          <h2 className="font-display text-lg uppercase text-muted mb-3">
            What&apos;s the Double Meaning?
          </h2>
          <p className="text-foreground mb-4">{exercise.semantic_question.question}</p>
          <textarea
            value={semanticAnswer}
            onChange={(e) => setSemanticAnswer(e.target.value)}
            className="w-full bg-background border border-border rounded px-4 py-3 text-foreground focus:outline-none focus:border-accent mb-3 resize-none"
            rows={3}
            placeholder="Explain the meaning..."
          />
          <Button onClick={handleSemanticSubmit} variant="primary" size="md">
            Submit
          </Button>
        </Card>
      )}
    </div>
  );
}
