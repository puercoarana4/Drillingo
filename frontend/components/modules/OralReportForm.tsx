"use client";

import { useState } from "react";
import Button from "@/components/ui/Button";
import { api, ApiError } from "@/lib/api";

interface OralReportFormProps {
  onSuccess?: (fluency: number, pronunciation: number) => void;
}

export default function OralReportForm({ onSuccess }: OralReportFormProps) {
  const [duration, setDuration] = useState(600);
  const [fluency, setFluency] = useState(50);
  const [pronunciation, setPronunciation] = useState(50);
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await api.post("/api/reports/oral", {
        session_duration_seconds: duration,
        fluency_score: fluency,
        pronunciation_score: pronunciation,
        notes: notes.trim() || undefined,
      });
      setSubmitted(true);
      onSuccess?.(fluency, pronunciation);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError("Failed to submit report. Try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  if (submitted) {
    return (
      <div className="text-center py-8">
        <p className="text-4xl mb-3">🎙️</p>
        <h3 className="font-display text-2xl uppercase text-accent mb-2">Report Synced</h3>
        <div className="flex justify-center gap-8 mt-4">
          <div>
            <p className="text-muted text-xs uppercase tracking-wider font-display">Fluency</p>
            <p className="text-foreground text-3xl font-display">{fluency}</p>
          </div>
          <div>
            <p className="text-muted text-xs uppercase tracking-wider font-display">Pronunciation</p>
            <p className="text-foreground text-3xl font-display">{pronunciation}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Session duration */}
      <div>
        <label className="block text-sm text-muted uppercase tracking-wider font-display mb-2">
          Session Duration (seconds)
        </label>
        <input
          type="number"
          min={1}
          value={duration}
          onChange={(e) => setDuration(parseInt(e.target.value) || 0)}
          className="w-full bg-background border border-border rounded px-4 py-3 text-foreground focus:outline-none focus:border-accent"
        />
      </div>

      {/* Fluency slider */}
      <div>
        <div className="flex justify-between mb-2">
          <label className="text-sm text-muted uppercase tracking-wider font-display">
            Fluency Score
          </label>
          <span className="text-accent font-display text-lg">{fluency}</span>
        </div>
        <input
          type="range"
          min={0}
          max={100}
          value={fluency}
          onChange={(e) => setFluency(parseInt(e.target.value))}
          className="w-full h-2 accent-accent cursor-pointer"
          aria-label="Fluency score"
        />
        <div className="flex justify-between text-xs text-muted mt-1">
          <span>0</span>
          <span>100</span>
        </div>
      </div>

      {/* Pronunciation slider */}
      <div>
        <div className="flex justify-between mb-2">
          <label className="text-sm text-muted uppercase tracking-wider font-display">
            Pronunciation Score
          </label>
          <span className="text-accent font-display text-lg">{pronunciation}</span>
        </div>
        <input
          type="range"
          min={0}
          max={100}
          value={pronunciation}
          onChange={(e) => setPronunciation(parseInt(e.target.value))}
          className="w-full h-2 accent-accent cursor-pointer"
          aria-label="Pronunciation score"
        />
        <div className="flex justify-between text-xs text-muted mt-1">
          <span>0</span>
          <span>100</span>
        </div>
      </div>

      {/* Notes (optional) */}
      <div>
        <label className="block text-sm text-muted uppercase tracking-wider font-display mb-2">
          Notes (optional)
        </label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={3}
          className="w-full bg-background border border-border rounded px-4 py-3 text-foreground placeholder-muted focus:outline-none focus:border-accent resize-none"
          placeholder="e.g. Practiced Kay Flock verse, worked on glottal stops..."
        />
      </div>

      {error && (
        <p role="alert" className="text-accent text-sm">
          {error}
        </p>
      )}

      <Button type="submit" variant="primary" size="md" loading={loading} className="w-full">
        Sync Report
      </Button>
    </form>
  );
}
