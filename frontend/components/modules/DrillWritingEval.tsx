"use client";

import { useState } from "react";
import Button from "@/components/ui/Button";
import { api, ApiError } from "@/lib/api";

interface RubricCriterion {
  description: string;
  points: number;
  example: string;
}

interface DrillWritingEvalProps {
  formalInput: string;
  referenceAnswer: string;
  acceptedVariants: string[];
  rubric: Record<string, RubricCriterion>;
  grammarExplanation: string;
  xpReward: number;
  onComplete: (score: number) => void;
}

interface EvalResult {
  score: number;
  correct: boolean;
  feedback: string;
  grammar_hits: string[];
  grammar_misses: string[];
  suggested_improvement: string | null;
}

export default function DrillWritingEval({
  formalInput,
  referenceAnswer,
  acceptedVariants,
  rubric,
  grammarExplanation,
  xpReward,
  onComplete,
}: DrillWritingEvalProps) {
  const [answer, setAnswer] = useState("");
  const [result, setResult] = useState<EvalResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);

  async function handleSubmit() {
    if (!answer.trim() || loading) return;
    setLoading(true);
    setError(null);

    try {
      const eval_result = await api.post<EvalResult>("/api/ai/writing/evaluate", {
        formal_input: formalInput,
        student_answer: answer,
        reference_answer: referenceAnswer,
        accepted_variants: acceptedVariants,
      });
      setResult(eval_result);
      setSubmitted(true);
      onComplete(eval_result.score);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError("Gemini evaluation failed. Try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      {/* Formal input */}
      <div className="bg-background border border-border rounded-xl p-4">
        <p className="text-xs text-muted uppercase tracking-wider font-display mb-1">
          Formal English
        </p>
        <p className="text-foreground text-lg">&ldquo;{formalInput}&rdquo;</p>
      </div>

      {/* Rubric */}
      <div className="space-y-1">
        {Object.entries(rubric).map(([key, c]) => (
          <div key={key} className="flex items-start justify-between gap-3 text-xs">
            <div className="flex-1 min-w-0">
              <span className="text-muted">{c.description}</span>
              <span className="text-muted/60 font-mono ml-2">{c.example}</span>
            </div>
            <span className="text-accent font-display flex-shrink-0">+{c.points}pts</span>
          </div>
        ))}
      </div>

      {/* Text area */}
      {!submitted && (
        <>
          <div>
            <label className="block text-xs text-muted uppercase tracking-wider font-display mb-1">
              Say it in Drill
            </label>
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              rows={3}
              className="w-full bg-background border border-border rounded-xl px-4 py-3 text-foreground placeholder-muted focus:outline-none focus:border-accent transition-colors resize-none"
              placeholder="e.g. I ain't finna do allat..."
            />
          </div>

          {error && <p className="text-accent text-sm">{error}</p>}

          <Button
            onClick={handleSubmit}
            variant="primary"
            size="md"
            loading={loading}
            disabled={!answer.trim()}
            className="w-full"
          >
            {loading ? "Gemini is evaluating..." : "Spit It 🎤"}
          </Button>
        </>
      )}

      {/* Result */}
      {result && submitted && (
        <div className="space-y-3">
          {/* Score banner */}
          <div
            className={[
              "rounded-xl p-4 border text-center",
              result.correct
                ? "border-green-700 bg-green-900/20"
                : result.score >= 60
                ? "border-yellow-700 bg-yellow-900/10"
                : "border-accent/50 bg-accent/10",
            ].join(" ")}
          >
            <p
              className={[
                "font-display text-4xl mb-1",
                result.correct ? "text-green-400" : result.score >= 60 ? "text-yellow-400" : "text-accent",
              ].join(" ")}
            >
              {result.score}
            </p>
            <p className="font-display text-lg uppercase text-foreground">
              {result.correct ? "On Point 🔥" : result.score >= 60 ? "Almost There" : "Keep Drilling"}
            </p>
          </div>

          {/* Gemini feedback */}
          <div className="bg-surface border border-border rounded-xl p-4">
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-2">
              🤖 Tutor Feedback
            </p>
            <p className="text-foreground text-sm leading-relaxed">{result.feedback}</p>
          </div>

          {/* Grammar hits */}
          {result.grammar_hits.length > 0 && (
            <div className="bg-green-900/10 border border-green-800 rounded-xl p-3">
              <p className="text-xs text-green-400 uppercase tracking-wider font-display mb-2">✓ Used correctly</p>
              <ul className="space-y-1">
                {result.grammar_hits.map((h, i) => (
                  <li key={i} className="text-green-300 text-sm">• {h}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Grammar misses */}
          {result.grammar_misses.length > 0 && (
            <div className="bg-accent/5 border border-accent/30 rounded-xl p-3">
              <p className="text-xs text-accent uppercase tracking-wider font-display mb-2">✗ Needs work</p>
              <ul className="space-y-1">
                {result.grammar_misses.map((m, i) => (
                  <li key={i} className="text-red-300 text-sm">• {m}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Suggested improvement */}
          {result.suggested_improvement && (
            <div className="bg-surface border border-border rounded-xl p-3">
              <p className="text-xs text-muted uppercase tracking-wider font-display mb-1">Try this instead</p>
              <p className="text-foreground text-sm italic">&ldquo;{result.suggested_improvement}&rdquo;</p>
            </div>
          )}

          {/* Reference */}
          <div className="bg-surface border border-border rounded-xl p-3">
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-1">Reference</p>
            <p className="text-foreground text-sm font-bold">&ldquo;{referenceAnswer}&rdquo;</p>
            <p className="text-muted text-xs mt-2">{grammarExplanation}</p>
          </div>
        </div>
      )}
    </div>
  );
}
