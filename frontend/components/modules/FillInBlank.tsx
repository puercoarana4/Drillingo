"use client";

import { useState } from "react";
import Button from "@/components/ui/Button";

export interface BlankSlot {
  id: string;
  /** Position index in the transcript where the blank appears */
  position: number;
  correctAnswer: string;
  explanation: string;
}

interface FillInBlankProps {
  /** Transcript text with blanks marked as {{blank_id}} */
  transcript: string;
  blanks: BlankSlot[];
  onComplete: (score: number, results: BlankResult[]) => void;
}

export interface BlankResult {
  blankId: string;
  userAnswer: string;
  correctAnswer: string;
  correct: boolean;
  explanation: string;
}

export default function FillInBlank({ transcript, blanks, onComplete }: FillInBlankProps) {
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [submitted, setSubmitted] = useState(false);
  const [results, setResults] = useState<BlankResult[]>([]);

  function handleChange(blankId: string, value: string) {
    setAnswers((prev) => ({ ...prev, [blankId]: value }));
  }

  function handleSubmit() {
    const evaluated: BlankResult[] = blanks.map((blank) => {
      const userAnswer = (answers[blank.id] ?? "").trim().toLowerCase();
      const correct = userAnswer === blank.correctAnswer.toLowerCase();
      return {
        blankId: blank.id,
        userAnswer: answers[blank.id] ?? "",
        correctAnswer: blank.correctAnswer,
        correct,
        explanation: blank.explanation,
      };
    });

    setResults(evaluated);
    setSubmitted(true);

    const correctCount = evaluated.filter((r) => r.correct).length;
    const score = Math.round((correctCount / blanks.length) * 100);
    onComplete(score, evaluated);
  }

  // Render transcript with input fields replacing {{blank_id}} placeholders
  function renderTranscript() {
    const parts = transcript.split(/(\{\{[^}]+\}\})/g);
    return parts.map((part, i) => {
      const match = part.match(/^\{\{(.+)\}\}$/);
      if (!match) return <span key={i}>{part}</span>;

      const blankId = match[1];
      const result = results.find((r) => r.blankId === blankId);

      if (submitted && result) {
        return (
          <span key={i} className="inline-block mx-1">
            <span
              className={[
                "inline-block px-2 py-0.5 rounded font-bold text-sm",
                result.correct
                  ? "bg-green-900 text-green-300"
                  : "bg-red-900 text-red-300 line-through",
              ].join(" ")}
            >
              {result.userAnswer || "_____"}
            </span>
            {!result.correct && (
              <span className="ml-1 text-green-400 font-bold text-sm">
                {result.correctAnswer}
              </span>
            )}
          </span>
        );
      }

      return (
        <input
          key={i}
          type="text"
          value={answers[blankId] ?? ""}
          onChange={(e) => handleChange(blankId, e.target.value)}
          disabled={submitted}
          className="inline-block mx-1 w-28 bg-background border-b-2 border-accent text-foreground text-center text-sm px-1 py-0.5 focus:outline-none focus:border-red-400"
          aria-label={`Fill in blank ${blankId}`}
          placeholder="___"
        />
      );
    });
  }

  return (
    <div>
      {/* Transcript with blanks (Req 5.2) */}
      <div className="bg-surface border border-border rounded-xl p-5 text-foreground leading-loose text-base mb-4">
        {renderTranscript()}
      </div>

      {/* Explanations after submission (Req 5.4) */}
      {submitted && results.some((r) => !r.correct) && (
        <div className="space-y-2 mb-4">
          {results
            .filter((r) => !r.correct)
            .map((r) => (
              <div key={r.blankId} className="bg-surface border border-accent/30 rounded-lg p-3 text-sm">
                <p className="text-accent font-bold mb-1">
                  Correct: <span className="text-foreground">{r.correctAnswer}</span>
                </p>
                <p className="text-muted">{r.explanation}</p>
              </div>
            ))}
        </div>
      )}

      {!submitted && (
        <Button
          onClick={handleSubmit}
          variant="primary"
          size="md"
          disabled={blanks.some((b) => !answers[b.id]?.trim())}
        >
          Check Answers
        </Button>
      )}
    </div>
  );
}
