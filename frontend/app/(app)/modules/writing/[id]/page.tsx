"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import TranslationInput from "@/components/modules/TranslationInput";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import { api } from "@/lib/api";

interface WritingExercise {
  lesson_id: string;
  title: string;
  dialect_segment: "east_coast" | "midwest";
  prompts: Array<{
    id: string;
    formal_phrase: string;
    accepted_answers: string[];
    explanation: string;
    grammar_structure: string;
  }>;
}

export default function WritingPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();

  const [exercise, setExercise] = useState<WritingExercise | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [results, setResults] = useState<boolean[]>([]);
  const [completed, setCompleted] = useState(false);
  const [xpEarned, setXpEarned] = useState(0);

  useEffect(() => {
    api.get<WritingExercise>(`/api/content/lessons/${id}`)
      .then((data) => setExercise(data as unknown as WritingExercise))
      .catch(() => router.push("/lessons"))
      .finally(() => setLoading(false));
  }, [id, router]);

  async function handleResult(correct: boolean) {
    const newResults = [...results, correct];
    setResults(newResults);

    const prompts = exercise?.prompts ?? [];
    if (currentIndex + 1 >= prompts.length) {
      // All prompts done — submit progress
      const score = Math.round((newResults.filter(Boolean).length / prompts.length) * 100);
      try {
        const res = await api.post<{ xp_awarded: number }>("/api/progress/lesson", {
          lesson_id: exercise?.lesson_id,
          module_type: "writing",
          score,
        });
        setXpEarned(res.xp_awarded);
      } catch {
        // continue
      }
      setCompleted(true);
    }
  }

  function handleNext() {
    setCurrentIndex((i) => i + 1);
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin h-8 w-8 border-2 border-accent border-t-transparent rounded-full" />
      </div>
    );
  }

  if (completed) {
    const score = Math.round((results.filter(Boolean).length / (exercise?.prompts.length ?? 1)) * 100);
    return (
      <Card accent className="max-w-lg mx-auto text-center">
        <p className="text-4xl mb-4">✍️</p>
        <h2 className="font-display text-3xl uppercase text-accent mb-2">Bars Written</h2>
        <p className="text-muted mb-4">
          Score: <span className="text-foreground font-bold">{score}%</span>
        </p>
        <p className="text-accent font-display text-xl mb-6">+{xpEarned} XP</p>
        <Button onClick={() => router.push("/lessons")} variant="primary">
          Back to Lessons
        </Button>
      </Card>
    );
  }

  const prompts = exercise?.prompts ?? [];
  const currentPrompt = prompts[currentIndex];
  const isAnswered = results.length > currentIndex;

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl uppercase text-foreground">
            Spitting Bars
          </h1>
          {exercise?.dialect_segment && (
            <Badge variant={exercise.dialect_segment} className="mt-1">
              {exercise.dialect_segment === "east_coast" ? "East Coast" : "Midwest"}
            </Badge>
          )}
        </div>
        <span className="text-muted text-sm">
          {currentIndex + 1}/{prompts.length}
        </span>
      </div>

      {currentPrompt && (
        <Card>
          <TranslationInput
            formalPhrase={currentPrompt.formal_phrase}
            acceptedAnswers={currentPrompt.accepted_answers}
            explanation={currentPrompt.explanation}
            onResult={handleResult}
          />
          {isAnswered && currentIndex + 1 < prompts.length && (
            <Button onClick={handleNext} variant="secondary" size="md" className="mt-4">
              Next Prompt →
            </Button>
          )}
        </Card>
      )}
    </div>
  );
}
