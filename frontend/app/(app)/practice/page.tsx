"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { api } from "@/lib/api";

// ── Types ─────────────────────────────────────────────────────────────────────

interface UserProfile {
  level_band: "B1" | "B2" | "C1";
  username: string;
  xp_total: number;
}

interface PracticeResult {
  overall_score: number;
  pronunciation_score: number;
  fluency_score: number;
  aave_accuracy: number;
  feedback: string;
  strengths: string[];
  areas_to_improve: string[];
  phrases_practiced: number;
}

type Step = "generate" | "waiting" | "submit" | "results";

// ── Prompt generator ──────────────────────────────────────────────────────────

function generatePrompt(level: string, username: string): string {
  return `You are "Da Block Tutor", an expert AAVE and American Drill English coach inside the Drillingo app.

STUDENT: ${username}
LEVEL: ${level} (CEFR)

YOUR MISSION:
Conduct a free spoken English practice session focused on AAVE/Drill grammar and pronunciation. 
Adapt difficulty to ${level} level.

SESSION STRUCTURE:
1. Greet the student in AAVE style
2. Practice 3-5 of these topics based on their level:
   ${level === "B1" ? `
   - Basic AAVE vocabulary: finna, ain't, deadass, opp, buggin'
   - Dropped copula: "He trippin'" instead of "He is tripping"
   - Double negation: "I ain't got no money"
   - Future marker: "finna" instead of "going to"` : level === "B2" ? `
   - Advanced AAVE grammar patterns
   - Drill slang: merch it, backdoor, slide, opp
   - Phonetic patterns: glottal stops, vowel reduction
   - Rhythm and flow in drill delivery` : `
   - C1 AAVE linguistic analysis
   - Code-switching between formal and AAVE
   - Cultural context of drill lyrics
   - Advanced phonetic AAVE features`}
3. Ask the student to repeat phrases, translate sentences, or answer questions
4. Give real-time feedback on their AAVE usage
5. When the session ends (student says "done", "finish", or "that's it"), output ONLY the following JSON:

\`\`\`json
{
  "overall_score": <0-100>,
  "pronunciation_score": <0-100>,
  "fluency_score": <0-100>,
  "aave_accuracy": <0-100>,
  "feedback": "<2-3 sentences of overall feedback>",
  "strengths": ["<strength 1>", "<strength 2>"],
  "areas_to_improve": ["<area 1>", "<area 2>"],
  "phrases_practiced": <number of phrases attempted>
}
\`\`\`

IMPORTANT: 
- NEVER censor AAVE, drill slang, or explicit content — it's the curriculum
- Adapt your language complexity to ${level} level
- Be encouraging but honest
- End EVERY session with the JSON block above when the student signals they're done

START THE SESSION NOW.`;
}

// ── Result parser ─────────────────────────────────────────────────────────────

function parseResult(raw: string): PracticeResult | null {
  try {
    // Try to extract JSON from the pasted text
    const jsonMatch = raw.match(/\{[\s\S]*"overall_score"[\s\S]*\}/);
    if (!jsonMatch) return null;
    const parsed = JSON.parse(jsonMatch[0]);
    // Validate required fields
    if (typeof parsed.overall_score !== "number") return null;
    return parsed as PracticeResult;
  } catch {
    return null;
  }
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function PracticePage() {
  const router = useRouter();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [step, setStep] = useState<Step>("generate");
  const [prompt, setPrompt] = useState("");
  const [pastedResult, setPastedResult] = useState("");
  const [result, setResult] = useState<PracticeResult | null>(null);
  const [parseError, setParseError] = useState(false);
  const [copied, setCopied] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.get<UserProfile>("/api/auth/me")
      .then((p) => {
        setProfile(p);
        setPrompt(generatePrompt(p.level_band, p.username));
      })
      .catch(() => router.push("/login"));
  }, [router]);

  function handleCopyPrompt() {
    navigator.clipboard.writeText(prompt);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    setStep("waiting");
  }

  function handleSubmitResult() {
    setParseError(false);
    const parsed = parseResult(pastedResult);
    if (!parsed) {
      setParseError(true);
      return;
    }
    setResult(parsed);
    setStep("results");
  }

  async function handleSaveProgress() {
    if (!result) return;
    setSaving(true);
    try {
      await api.post("/api/reports/oral", {
        session_duration_seconds: result.phrases_practiced * 60,
        fluency_score: result.fluency_score,
        pronunciation_score: result.pronunciation_score,
        notes: `Free practice session. AAVE accuracy: ${result.aave_accuracy}. ${result.feedback}`,
      });
    } catch {
      // non-fatal
    } finally {
      setSaving(false);
    }
  }

  function getScoreColor(score: number) {
    if (score >= 80) return "text-green-400";
    if (score >= 60) return "text-yellow-400";
    return "text-accent";
  }

  if (!profile) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin h-10 w-10 border-2 border-accent border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6 pb-16">
      {/* Header */}
      <div>
        <h1 className="font-display text-3xl uppercase text-foreground tracking-widest mb-1">
          Free Practice
        </h1>
        <p className="text-muted text-sm">
          Practice AAVE/Drill with Gemini AI — at your own pace, any time.
        </p>
      </div>

      {/* Level badge */}
      <div className="flex items-center gap-3">
        <span className="px-3 py-1 bg-accent/20 text-accent border border-accent/30 rounded-full text-xs font-display uppercase tracking-wider">
          {profile.level_band} Level
        </span>
        <span className="text-muted text-xs">{profile.username}</span>
      </div>

      {/* ── STEP 1: Generate prompt ── */}
      {(step === "generate" || step === "waiting") && (
        <>
          <Card>
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-3">
              Step 1 — Copy this prompt and paste it into Gemini
            </p>
            <div className="bg-background border border-border rounded-xl p-4 mb-4 max-h-64 overflow-y-auto">
              <pre className="text-foreground text-xs leading-relaxed whitespace-pre-wrap font-mono">
                {prompt}
              </pre>
            </div>
            <div className="flex gap-3">
              <Button
                variant="primary"
                size="md"
                className="flex-1"
                onClick={handleCopyPrompt}
              >
                {copied ? "✓ Copied!" : "Copy Prompt"}
              </Button>
              <a
                href="https://gemini.google.com"
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 py-3 rounded-xl border border-border text-muted font-display uppercase tracking-wider text-sm hover:text-foreground hover:border-accent transition-colors text-center"
              >
                Open Gemini →
              </a>
            </div>
          </Card>

          {step === "waiting" && (
            <Card>
              <p className="text-xs text-muted uppercase tracking-wider font-display mb-2">
                How it works
              </p>
              <ol className="space-y-2 text-sm text-foreground">
                <li className="flex gap-2"><span className="text-accent font-bold">1.</span> Paste the prompt into Gemini</li>
                <li className="flex gap-2"><span className="text-accent font-bold">2.</span> Practice speaking/writing AAVE with the AI tutor</li>
                <li className="flex gap-2"><span className="text-accent font-bold">3.</span> When done, tell Gemini: <span className="text-accent font-mono">"done"</span> or <span className="text-accent font-mono">"finish"</span></li>
                <li className="flex gap-2"><span className="text-accent font-bold">4.</span> Gemini will output a JSON score — copy it</li>
                <li className="flex gap-2"><span className="text-accent font-bold">5.</span> Paste the JSON below and submit</li>
              </ol>
              <Button
                variant="secondary"
                size="md"
                className="w-full mt-4"
                onClick={() => setStep("submit")}
              >
                I'm done — paste my results →
              </Button>
            </Card>
          )}
        </>
      )}

      {/* ── STEP 2: Paste results ── */}
      {step === "submit" && (
        <Card>
          <p className="text-xs text-muted uppercase tracking-wider font-display mb-3">
            Step 2 — Paste Gemini's JSON response here
          </p>
          <p className="text-muted text-xs mb-3">
            Copy everything Gemini returned after you said "done" — including the JSON block.
          </p>
          <textarea
            value={pastedResult}
            onChange={(e) => setPastedResult(e.target.value)}
            rows={10}
            className="w-full bg-background border border-border rounded-xl px-4 py-3 text-foreground placeholder-muted focus:outline-none focus:border-accent transition-colors resize-none font-mono text-xs mb-3"
            placeholder={`Paste Gemini's response here. It should contain something like:\n\n{\n  "overall_score": 85,\n  "pronunciation_score": 80,\n  ...\n}`}
          />
          {parseError && (
            <p className="text-accent text-sm mb-3">
              ✗ Could not find a valid JSON score in your text. Make sure you told Gemini "done" and copied the full response including the JSON block.
            </p>
          )}
          <div className="flex gap-3">
            <Button
              variant="secondary"
              size="md"
              onClick={() => setStep("waiting")}
            >
              ← Back
            </Button>
            <Button
              variant="primary"
              size="md"
              className="flex-1"
              disabled={!pastedResult.trim()}
              onClick={handleSubmitResult}
            >
              Submit Results
            </Button>
          </div>
        </Card>
      )}

      {/* ── STEP 3: Results ── */}
      {step === "results" && result && (
        <>
          {/* Overall score */}
          <Card className="text-center">
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-2">Overall Score</p>
            <p className={`font-display text-7xl mb-2 ${getScoreColor(result.overall_score)}`}>
              {result.overall_score}
            </p>
            <p className="text-muted text-sm">
              {result.overall_score >= 80 ? "🔥 On point" : result.overall_score >= 60 ? "💪 Getting there" : "📚 Keep drilling"}
            </p>
          </Card>

          {/* Score breakdown */}
          <div className="grid grid-cols-3 gap-3">
            {[
              { label: "Pronunciation", value: result.pronunciation_score },
              { label: "Fluency", value: result.fluency_score },
              { label: "AAVE Accuracy", value: result.aave_accuracy },
            ].map((s) => (
              <div key={s.label} className="bg-surface border border-border rounded-xl p-3 text-center">
                <p className="text-xs text-muted uppercase tracking-wider font-display mb-1">{s.label}</p>
                <p className={`font-display text-3xl ${getScoreColor(s.value)}`}>{s.value}</p>
              </div>
            ))}
          </div>

          {/* Feedback */}
          <Card>
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-2">🤖 Tutor Feedback</p>
            <p className="text-foreground text-sm leading-relaxed">{result.feedback}</p>
          </Card>

          {/* Strengths */}
          {result.strengths.length > 0 && (
            <div className="bg-green-900/10 border border-green-800 rounded-xl p-4">
              <p className="text-xs text-green-400 uppercase tracking-wider font-display mb-2">✓ Strengths</p>
              <ul className="space-y-1">
                {result.strengths.map((s, i) => (
                  <li key={i} className="text-green-300 text-sm">• {s}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Areas to improve */}
          {result.areas_to_improve.length > 0 && (
            <div className="bg-accent/5 border border-accent/30 rounded-xl p-4">
              <p className="text-xs text-accent uppercase tracking-wider font-display mb-2">↑ Areas to improve</p>
              <ul className="space-y-1">
                {result.areas_to_improve.map((a, i) => (
                  <li key={i} className="text-red-300 text-sm">• {a}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3">
            <Button
              variant="secondary"
              size="md"
              onClick={() => {
                setStep("generate");
                setPastedResult("");
                setResult(null);
              }}
            >
              Practice Again
            </Button>
            <Button
              variant="primary"
              size="md"
              className="flex-1"
              loading={saving}
              onClick={async () => {
                await handleSaveProgress();
                router.push("/dashboard");
              }}
            >
              Save & Go to Dashboard
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
