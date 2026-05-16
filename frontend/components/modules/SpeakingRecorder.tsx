"use client";

import { useState, useRef } from "react";
import Button from "@/components/ui/Button";
import { getToken } from "@/lib/auth";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface SpeakingResult {
  transcription: string;
  pronunciation_score: number;
  fluency_score: number;
  feedback: string;
  phonetic_notes: string[];
  suggested_practice: string;
}

interface SpeakingRecorderProps {
  targetPhrase: string;
  level?: string;
  onComplete: (result: SpeakingResult) => void;
}

type RecordingState = "idle" | "recording" | "recorded" | "evaluating" | "done";

export default function SpeakingRecorder({
  targetPhrase,
  level = "B1",
  onComplete,
}: SpeakingRecorderProps) {
  const [state, setState] = useState<RecordingState>("idle");
  const [result, setResult] = useState<SpeakingResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [seconds, setSeconds] = useState(0);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const audioBlobRef = useRef<Blob | null>(null);

  async function startRecording() {
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        audioBlobRef.current = blob;
        setAudioUrl(URL.createObjectURL(blob));
        setState("recorded");
        stream.getTracks().forEach((t) => t.stop());
      };

      recorder.start(100);
      mediaRecorderRef.current = recorder;
      setState("recording");
      setSeconds(0);

      timerRef.current = setInterval(() => {
        setSeconds((s) => {
          if (s >= 30) {
            stopRecording();
            return s;
          }
          return s + 1;
        });
      }, 1000);
    } catch {
      setError("Microphone access denied. Please allow microphone access.");
    }
  }

  function stopRecording() {
    if (timerRef.current) clearInterval(timerRef.current);
    mediaRecorderRef.current?.stop();
  }

  async function submitRecording() {
    if (!audioBlobRef.current) return;
    setState("evaluating");
    setError(null);

    const formData = new FormData();
    formData.append("audio", audioBlobRef.current, "recording.webm");
    formData.append("target_phrase", targetPhrase);
    formData.append("level", level);

    try {
      const token = getToken();
      const response = await fetch(`${BASE_URL}/api/ai/speaking/evaluate`, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: formData,
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail ?? `HTTP ${response.status}`);
      }

      const data: SpeakingResult = await response.json();
      setResult(data);
      setState("done");
      onComplete(data);
    } catch (err: any) {
      setError(err.message ?? "Evaluation failed. Try again.");
      setState("recorded");
    }
  }

  function reset() {
    setState("idle");
    setResult(null);
    setError(null);
    setAudioUrl(null);
    setSeconds(0);
    audioBlobRef.current = null;
  }

  return (
    <div className="space-y-4">
      {/* Target phrase */}
      <div className="bg-background border-2 border-accent rounded-xl p-5 text-center">
        <p className="text-xs text-muted uppercase tracking-wider font-display mb-2">Read this aloud</p>
        <p className="text-foreground text-xl font-bold leading-relaxed">
          &ldquo;{targetPhrase}&rdquo;
        </p>
      </div>

      {/* Recording controls */}
      {state === "idle" && (
        <button
          onClick={startRecording}
          className="w-full py-4 rounded-xl bg-accent text-white font-display uppercase tracking-wider text-lg hover:bg-red-700 transition-colors flex items-center justify-center gap-3"
        >
          <span className="w-4 h-4 rounded-full bg-white animate-pulse" />
          Start Recording
        </button>
      )}

      {state === "recording" && (
        <div className="space-y-3">
          <div className="flex items-center justify-center gap-3 py-3">
            <span className="w-3 h-3 rounded-full bg-accent animate-ping" />
            <span className="font-display text-accent uppercase tracking-wider">
              Recording... {seconds}s
            </span>
          </div>
          {/* Waveform visual */}
          <div className="flex items-center justify-center gap-1 h-12">
            {Array.from({ length: 20 }).map((_, i) => (
              <div
                key={i}
                className="w-1 bg-accent rounded-full animate-pulse"
                style={{
                  height: `${20 + Math.random() * 24}px`,
                  animationDelay: `${i * 0.05}s`,
                  animationDuration: `${0.4 + Math.random() * 0.4}s`,
                }}
              />
            ))}
          </div>
          <button
            onClick={stopRecording}
            className="w-full py-3 rounded-xl border-2 border-accent text-accent font-display uppercase tracking-wider hover:bg-accent hover:text-white transition-colors"
          >
            Stop Recording
          </button>
        </div>
      )}

      {state === "recorded" && audioUrl && (
        <div className="space-y-3">
          <div className="bg-surface border border-border rounded-xl p-3">
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-2">Your recording</p>
            <audio src={audioUrl} controls className="w-full" />
          </div>
          {error && <p className="text-accent text-sm">{error}</p>}
          <div className="flex gap-2">
            <button
              onClick={reset}
              className="flex-1 py-3 rounded-xl border border-border text-muted font-display uppercase tracking-wider text-sm hover:text-foreground transition-colors"
            >
              Re-record
            </button>
            <button
              onClick={submitRecording}
              className="flex-1 py-3 rounded-xl bg-accent text-white font-display uppercase tracking-wider text-sm hover:bg-red-700 transition-colors"
            >
              Submit 🎤
            </button>
          </div>
        </div>
      )}

      {state === "evaluating" && (
        <div className="text-center py-6">
          <div className="animate-spin h-10 w-10 border-2 border-accent border-t-transparent rounded-full mx-auto mb-3" />
          <p className="text-muted font-display uppercase tracking-wider text-sm">
            Gemini is listening...
          </p>
        </div>
      )}

      {/* Results */}
      {state === "done" && result && (
        <div className="space-y-3">
          {/* Scores */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-surface border border-border rounded-xl p-4 text-center">
              <p className="text-xs text-muted uppercase tracking-wider font-display mb-1">Pronunciation</p>
              <p className={[
                "font-display text-4xl",
                result.pronunciation_score >= 80 ? "text-green-400" : result.pronunciation_score >= 60 ? "text-yellow-400" : "text-accent",
              ].join(" ")}>
                {result.pronunciation_score}
              </p>
            </div>
            <div className="bg-surface border border-border rounded-xl p-4 text-center">
              <p className="text-xs text-muted uppercase tracking-wider font-display mb-1">Fluency</p>
              <p className={[
                "font-display text-4xl",
                result.fluency_score >= 80 ? "text-green-400" : result.fluency_score >= 60 ? "text-yellow-400" : "text-accent",
              ].join(" ")}>
                {result.fluency_score}
              </p>
            </div>
          </div>

          {/* Transcription */}
          <div className="bg-surface border border-border rounded-xl p-3">
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-1">What Gemini heard</p>
            <p className="text-foreground text-sm italic">&ldquo;{result.transcription}&rdquo;</p>
          </div>

          {/* Feedback */}
          <div className="bg-surface border border-border rounded-xl p-4">
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-2">🤖 Phonetic Feedback</p>
            <p className="text-foreground text-sm leading-relaxed">{result.feedback}</p>
          </div>

          {/* Phonetic notes */}
          {result.phonetic_notes.length > 0 && (
            <div className="space-y-1">
              {result.phonetic_notes.map((note, i) => (
                <div key={i} className="flex gap-2 text-sm">
                  <span className="text-accent flex-shrink-0">•</span>
                  <span className="text-foreground">{note}</span>
                </div>
              ))}
            </div>
          )}

          {/* Practice tip */}
          <div className="bg-accent/10 border border-accent/30 rounded-xl p-3">
            <p className="text-xs text-accent uppercase tracking-wider font-display mb-1">Practice tip</p>
            <p className="text-foreground text-sm">{result.suggested_practice}</p>
          </div>

          <button
            onClick={reset}
            className="w-full py-3 rounded-xl border border-border text-muted font-display uppercase tracking-wider text-sm hover:text-foreground transition-colors"
          >
            Try Again
          </button>
        </div>
      )}
    </div>
  );
}
