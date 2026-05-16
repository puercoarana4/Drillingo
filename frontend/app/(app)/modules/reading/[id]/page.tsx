"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import ChatBubble from "@/components/modules/ChatBubble";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import { api, ApiError } from "@/lib/api";

interface Message {
  id: string;
  text: string;
  sender: "self" | "other";
  terms: Array<{ term: string; definition: string; example: string }>;
}

interface ReadingExercise {
  lesson_id: string;
  title: string;
  dialect_segment: "east_coast" | "midwest";
  messages: Message[];
}

interface TermState {
  term: string;
  definition: string;
  example: string;
  answered: boolean;
  correct: boolean | null;
}

export default function ReadingPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();

  const [exercise, setExercise] = useState<ReadingExercise | null>(null);
  const [activeTerm, setActiveTerm] = useState<TermState | null>(null);
  const [userAnswer, setUserAnswer] = useState("");
  const [score, setScore] = useState(0);
  const [totalTerms, setTotalTerms] = useState(0);
  const [answeredTerms, setAnsweredTerms] = useState<Set<string>>(new Set());
  const [completed, setCompleted] = useState(false);
  const [xpEarned, setXpEarned] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    api.get<ReadingExercise>(`/api/content/lessons/${id}`)
      .then((data) => {
        setExercise(data as unknown as ReadingExercise);
        const terms = (data as unknown as ReadingExercise).messages?.flatMap((m) => m.terms) ?? [];
        setTotalTerms(terms.length);
      })
      .catch(() => router.push("/lessons"))
      .finally(() => setLoading(false));
  }, [id, router]);

  function handleTermClick(term: string) {
    if (answeredTerms.has(term.toLowerCase())) return;
    const allTerms = exercise?.messages.flatMap((m) => m.terms) ?? [];
    const found = allTerms.find((t) => t.term.toLowerCase() === term.toLowerCase());
    if (!found) return;
    setActiveTerm({ ...found, answered: false, correct: null });
    setUserAnswer("");
  }

  async function handleAnswerSubmit() {
    if (!activeTerm || !exercise) return;
    const isCorrect =
      userAnswer.trim().toLowerCase() === activeTerm.definition.toLowerCase();

    setActiveTerm((prev) => prev ? { ...prev, answered: true, correct: isCorrect } : null);

    const newAnswered = new Set(answeredTerms);
    newAnswered.add(activeTerm.term.toLowerCase());
    setAnsweredTerms(newAnswered);

    if (isCorrect) setScore((s) => s + 1);

    // If all terms answered, complete the module
    if (newAnswered.size >= totalTerms) {
      setSubmitting(true);
      try {
        const finalScore = Math.round(((score + (isCorrect ? 1 : 0)) / totalTerms) * 100);
        const res = await api.post<{ xp_awarded: number }>("/api/progress/lesson", {
          lesson_id: exercise.lesson_id,
          module_type: "reading",
          score: finalScore,
        });
        setXpEarned(res.xp_awarded);
        setCompleted(true);
      } catch {
        setCompleted(true);
      } finally {
        setSubmitting(false);
      }
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin h-8 w-8 border-2 border-accent border-t-transparent rounded-full" />
      </div>
    );
  }

  if (completed) {
    const finalScore = Math.round((score / totalTerms) * 100);
    return (
      <Card accent className="max-w-lg mx-auto text-center">
        <p className="text-4xl mb-4">🔥</p>
        <h2 className="font-display text-3xl uppercase text-accent mb-2">Done</h2>
        <p className="text-muted mb-4">
          Score: <span className="text-foreground font-bold">{finalScore}%</span>
        </p>
        <p className="text-accent font-display text-xl mb-6">+{xpEarned} XP</p>
        <Button onClick={() => router.push("/lessons")} variant="primary">
          Back to Lessons
        </Button>
      </Card>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl uppercase text-foreground">
            {exercise?.title ?? "Street Texts"}
          </h1>
          {exercise?.dialect_segment && (
            <Badge variant={exercise.dialect_segment} className="mt-1">
              {exercise.dialect_segment === "east_coast" ? "East Coast" : "Midwest"}
            </Badge>
          )}
        </div>
        <span className="text-muted text-sm">
          {answeredTerms.size}/{totalTerms} terms
        </span>
      </div>

      {/* Chat interface (Req 4.1) */}
      <Card className="mb-4 min-h-[400px] overflow-y-auto">
        {exercise?.messages.map((msg) => (
          <ChatBubble
            key={msg.id}
            message={msg.text}
            sender={msg.sender}
            highlightedTerms={msg.terms.map((t, i) => ({ term: t.term, index: i }))}
            onTermClick={handleTermClick}
          />
        ))}
      </Card>

      {/* Term quiz panel */}
      {activeTerm && (
        <Card accent className="mb-4">
          {!activeTerm.answered ? (
            <>
              <p className="text-muted text-sm mb-2 uppercase tracking-wider font-display">
                What does <span className="text-accent">&quot;{activeTerm.term}&quot;</span> mean?
              </p>
              <input
                type="text"
                value={userAnswer}
                onChange={(e) => setUserAnswer(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleAnswerSubmit()}
                className="w-full bg-background border border-border rounded px-4 py-3 text-foreground focus:outline-none focus:border-accent mb-3"
                placeholder="Type the meaning..."
                autoFocus
              />
              <Button onClick={handleAnswerSubmit} variant="primary" size="md" loading={submitting}>
                Submit
              </Button>
            </>
          ) : (
            <>
              <p className={`font-display text-lg uppercase mb-2 ${activeTerm.correct ? "text-green-400" : "text-accent"}`}>
                {activeTerm.correct ? "✓ Correct" : "✗ Wrong"}
              </p>
              {/* Req 4.4: show definition and example on wrong answer */}
              {!activeTerm.correct && (
                <div className="text-sm text-muted space-y-1">
                  <p><span className="text-foreground font-bold">{activeTerm.term}</span>: {activeTerm.definition}</p>
                  <p className="italic">&quot;{activeTerm.example}&quot;</p>
                </div>
              )}
              <Button
                onClick={() => setActiveTerm(null)}
                variant="secondary"
                size="sm"
                className="mt-3"
              >
                Continue
              </Button>
            </>
          )}
        </Card>
      )}

      {!activeTerm && totalTerms > 0 && (
        <p className="text-center text-muted text-sm">
          Tap a <span className="text-accent">highlighted word</span> to test yourself
        </p>
      )}
    </div>
  );
}
