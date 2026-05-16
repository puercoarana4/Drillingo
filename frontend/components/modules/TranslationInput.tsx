"use client";

import { useState } from "react";
import Button from "@/components/ui/Button";

interface TranslationInputProps {
  formalPhrase: string;
  acceptedAnswers: string[];
  explanation: string;
  onResult: (correct: boolean, userAnswer: string) => void;
}

/**
 * Normalise a string for comparison.
 */
const normalise = (s: string): string => {
  return s
    .toLowerCase()
    .trim()
    .replace(/[^\w\s']/g, "")
    .replace(/\s+/g, " ");
};

export default function TranslationInput({
  formalPhrase,
  acceptedAnswers,
  explanation,
  onResult,
}: TranslationInputProps) {
  const [value, setValue] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [correct, setCorrect] = useState<boolean | null>(null);

  const handleSubmit = () => {
    const norm = normalise(value);
    const isCorrect = acceptedAnswers.some((a) => normalise(a) === norm);
    setCorrect(isCorrect);
    setSubmitted(true);
    onResult(isCorrect, value);
  };

  return (
    <div className="space-y-4">
      {/* Formal phrase to translate */}
      <div className="bg-background border border-border rounded-xl p-4">
        <p className="text-xs text-muted uppercase tracking-wider font-display mb-1">
          Formal English
        </p>
        <p className="text-foreground text-lg">{"\""}{formalPhrase}{"\""}</p>
      </div>

      {/* Translation input */}
      <div>
        <label className="block text-xs text-muted uppercase tracking-wider font-display mb-1">
          Say it in Drill
        </label>
        <textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          disabled={submitted}
          rows={3}
          className="w-full bg-background border border-border rounded-xl px-4 py-3 text-foreground placeholder-muted focus:outline-none focus:border-accent transition-colors resize-none"
          placeholder="e.g. I ain't finna do allat"
        />
      </div>

      {!submitted ? (
        <Button
          onClick={handleSubmit}
          variant="primary"
          size="md"
          disabled={!value.trim()}
        >
          Spit It
        </Button>
      ) : (
        <div
          className={[
            "rounded-xl p-4 border",
            correct
              ? "border-green-700 bg-green-900/20"
              : "border-accent/50 bg-accent/10",
          ].join(" ")}
        >
          <p
            className={[
              "font-display text-lg uppercase mb-2",
              correct ? "text-green-400" : "text-accent",
            ].join(" ")}
          >
            {correct ? "✓ On point" : "✗ Not quite"}
          </p>
          {!correct && (
            <div className="text-sm space-y-1">
              <p className="text-muted">
                Reference:{" "}
                <span className="text-foreground font-bold">
                  {"\""}{acceptedAnswers[0]}{"\""}
                </span>
              </p>
              <p className="text-muted">{explanation}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
