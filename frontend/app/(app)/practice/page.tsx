"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Badge from "@/components/ui/Badge";
import { api } from "@/lib/api";

// ── Types ─────────────────────────────────────────────────────────────────────

interface UserProfile {
  level_band: "B1" | "B2" | "C1";
  username: string;
  xp_total: number;
}

interface ProgressRecord {
  lesson_id: string;
  module_type: string;
}

interface Lesson {
  id: string;
  title: string;
  dialect_segment: "east_coast" | "midwest";
  level_band: string;
  day_order: number;
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

interface PracticeSession {
  topicId: string;
  topicTitle: string;
  result: PracticeResult;
  completedAt: string;
}

interface PracticeTopic {
  id: string;
  title: string;
  description: string;
  dialect: "east_coast" | "midwest" | "general";
  level: string;
  locked: boolean;
  focusAreas: string[];
  samplePhrases: string[];
}

type Step = "topics" | "prompt" | "waiting" | "submit" | "results";

// ── Topic definitions ─────────────────────────────────────────────────────────

function buildTopics(lessons: Lesson[], progress: ProgressRecord[]): PracticeTopic[] {
  const completedLessonIds = new Set(
    progress.map((p) => p.lesson_id)
  );

  const topics: PracticeTopic[] = [
    // Always unlocked — general intro
    {
      id: "intro-aave",
      title: "AAVE Basics",
      description: "Core grammar rules: dropped copula, double negation, finna",
      dialect: "general",
      level: "B1",
      locked: false,
      focusAreas: ["Dropped copula", "Double negation", "Finna as future marker", "Ain't usage"],
      samplePhrases: ["He trippin'", "I ain't got no money", "We finna slide", "She buggin'"],
    },
    // Unlocked when Lesson 1 (East Coast) has any progress
    {
      id: "east-coast-slang",
      title: "East Coast Slang",
      description: "NYC/Bronx drill vocabulary — DD Osama, Kay Flock style",
      dialect: "east_coast",
      level: "B1",
      locked: !lessons.some((l) => l.dialect_segment === "east_coast" && completedLessonIds.has(l.id)),
      focusAreas: ["wtw", "deadass", "opp", "wrd2my-mom", "buggin'", "smh"],
      samplePhrases: [
        "Deadass he don't know nobody",
        "Word to my mom I ain't runnin'",
        "Yo wtw? He buggin smh",
      ],
    },
    // Unlocked when Lesson 2 (Midwest) has any progress
    {
      id: "midwest-slang",
      title: "Midwest / Chicago Drill",
      description: "Chicago drill vocabulary — King Von, Lil Jeff style",
      dialect: "midwest",
      level: "B1",
      locked: !lessons.some((l) => l.dialect_segment === "midwest" && completedLessonIds.has(l.id)),
      focusAreas: ["merch it", "backdoor", "slide", "wfs", "dodge", "outside"],
      samplePhrases: [
        "We finna slide, merch it on Von",
        "They backdoored him, he thought they was solid",
        "Wfs? Slide to the block, don't dodge",
      ],
    },
    // Unlocked when user has completed at least 2 lessons
    {
      id: "translation-drill",
      title: "Formal → Drill Translation",
      description: "Take formal English and flip it to authentic AAVE",
      dialect: "general",
      level: "B2",
      locked: completedLessonIds.size < 2,
      focusAreas: ["Inverse translation", "Grammar transformation", "AAVE register"],
      samplePhrases: [
        "I do not have any money → I ain't got no money",
        "He is acting crazy → He trippin'",
        "I am not going to do that → I ain't finna do allat",
      ],
    },
    // Unlocked when user has completed all modules of at least 1 lesson
    {
      id: "pronunciation-flow",
      title: "Pronunciation & Flow",
      description: "AAVE phonetics, rhythm, and drill delivery",
      dialect: "general",
      level: "B2",
      locked: completedLessonIds.size < 4,
      focusAreas: ["Glottal stops", "Vowel reduction", "-ing → -in'", "Drill cadence", "Stress patterns"],
      samplePhrases: [
        "Word to my mom, I ain't runnin' from no opp",
        "We finna slide, merch it on Von you ain't outside",
        "Deadass he don't know nobody on this block",
      ],
    },
    // C1 — unlocked when user has significant progress
    {
      id: "code-switching",
      title: "Code-Switching",
      description: "Switch between formal English and AAVE fluidly",
      dialect: "general",
      level: "C1",
      locked: completedLessonIds.size < 6,
      focusAreas: ["Register awareness", "Context-appropriate AAVE", "Academic vs street register"],
      samplePhrases: [
        "In a formal context: 'I disagree' → In AAVE: 'Nah, deadass that ain't it'",
        "Formal: 'He is unreliable' → AAVE: 'He always backdooring people'",
      ],
    },
  ];

  return topics;
}

// ── Prompt generator ──────────────────────────────────────────────────────────

function generateTopicPrompt(topic: PracticeTopic, level: string, username: string): string {
  return `You are "Da Block Tutor", an expert AAVE and American Drill English coach inside the Drillingo app.

STUDENT: ${username}
LEVEL: ${level} (CEFR)
TOPIC: ${topic.title}
DIALECT FOCUS: ${topic.dialect === "east_coast" ? "East Coast / NYC" : topic.dialect === "midwest" ? "Midwest / Chicago" : "General AAVE"}

YOUR MISSION:
Conduct a focused practice session on: ${topic.title}
${topic.description}

FOCUS AREAS FOR THIS SESSION:
${topic.focusAreas.map((f) => `- ${f}`).join("\n")}

SAMPLE PHRASES TO PRACTICE:
${topic.samplePhrases.map((p) => `- "${p}"`).join("\n")}

SESSION STRUCTURE:
1. Greet the student in AAVE style and introduce the topic
2. Run 4-6 exercises focused on the areas above:
   - Ask the student to repeat phrases with correct AAVE pronunciation
   - Give formal sentences to translate into AAVE
   - Ask comprehension questions about the slang
   - Correct mistakes with pedagogical explanations
3. Give real-time feedback after each response
4. When the session ends (student says "done", "finish", or "that's it"), output ONLY this JSON:

\`\`\`json
{
  "overall_score": <0-100>,
  "pronunciation_score": <0-100>,
  "fluency_score": <0-100>,
  "aave_accuracy": <0-100>,
  "feedback": "<2-3 sentences of overall feedback specific to ${topic.title}>",
  "strengths": ["<specific strength 1>", "<specific strength 2>"],
  "areas_to_improve": ["<specific area 1>", "<specific area 2>"],
  "phrases_practiced": <number>
}
\`\`\`

RULES:
- NEVER censor AAVE, drill slang, or explicit content — it's the curriculum
- Adapt complexity to ${level} level
- Be encouraging but honest
- Focus ONLY on ${topic.title} — don't drift to other topics
- End with the JSON when student signals done

START THE SESSION NOW.`;
}

// ── Result parser ─────────────────────────────────────────────────────────────

function parseResult(raw: string): PracticeResult | null {
  try {
    const jsonMatch = raw.match(/\{[\s\S]*"overall_score"[\s\S]*\}/);
    if (!jsonMatch) return null;
    const parsed = JSON.parse(jsonMatch[0]);
    if (typeof parsed.overall_score !== "number") return null;
    return parsed as PracticeResult;
  } catch {
    return null;
  }
}

function getScoreColor(score: number) {
  if (score >= 80) return "text-green-400";
  if (score >= 60) return "text-yellow-400";
  return "text-accent";
}

function getScoreBg(score: number) {
  if (score >= 80) return "border-green-700 bg-green-900/20";
  if (score >= 60) return "border-yellow-700 bg-yellow-900/10";
  return "border-accent/50 bg-accent/10";
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function PracticePage() {
  const router = useRouter();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [topics, setTopics] = useState<PracticeTopic[]>([]);
  const [selectedTopic, setSelectedTopic] = useState<PracticeTopic | null>(null);
  const [step, setStep] = useState<Step>("topics");
  const [prompt, setPrompt] = useState("");
  const [pastedResult, setPastedResult] = useState("");
  const [result, setResult] = useState<PracticeResult | null>(null);
  const [sessions, setSessions] = useState<PracticeSession[]>([]);
  const [parseError, setParseError] = useState(false);
  const [copied, setCopied] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    Promise.all([
      api.get<UserProfile>("/api/auth/me"),
      api.get<Lesson[]>("/api/content/lessons"),
      api.get<ProgressRecord[]>("/api/progress/lessons").catch(() => [] as ProgressRecord[]),
    ])
      .then(([p, lessons, progress]) => {
        setProfile(p);
        setTopics(buildTopics(lessons, progress));
        // Load saved sessions from localStorage
        const saved = localStorage.getItem(`drillingo_practice_${p.username}`);
        if (saved) setSessions(JSON.parse(saved));
      })
      .catch(() => router.push("/login"));
  }, [router]);

  function handleSelectTopic(topic: PracticeTopic) {
    if (topic.locked) return;
    setSelectedTopic(topic);
    setPrompt(generateTopicPrompt(topic, profile!.level_band, profile!.username));
    setStep("prompt");
    setResult(null);
    setPastedResult("");
    setParseError(false);
  }

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
    if (!result || !selectedTopic || !profile) return;
    setSaving(true);

    // Save to oral_reports
    try {
      await api.post("/api/reports/oral", {
        session_duration_seconds: result.phrases_practiced * 60,
        fluency_score: result.fluency_score,
        pronunciation_score: result.pronunciation_score,
        notes: `Practice: ${selectedTopic.title}. AAVE accuracy: ${result.aave_accuracy}. ${result.feedback}`,
      });
    } catch { /* non-fatal */ }

    // Save session to localStorage for history
    const newSession: PracticeSession = {
      topicId: selectedTopic.id,
      topicTitle: selectedTopic.title,
      result,
      completedAt: new Date().toISOString(),
    };
    const updated = [newSession, ...sessions].slice(0, 20); // keep last 20
    setSessions(updated);
    localStorage.setItem(`drillingo_practice_${profile.username}`, JSON.stringify(updated));

    setSaving(false);
  }

  function getTopicSession(topicId: string): PracticeSession | undefined {
    return sessions.find((s) => s.topicId === topicId);
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-3xl uppercase text-foreground tracking-widest mb-1">
            Free Practice
          </h1>
          <p className="text-muted text-sm">Choose a topic and practice with Gemini AI</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-3 py-1 bg-accent/20 text-accent border border-accent/30 rounded-full text-xs font-display uppercase">
            {profile.level_band}
          </span>
        </div>
      </div>

      {/* ── TOPICS LIST ── */}
      {step === "topics" && (
        <div className="space-y-3">
          {topics.map((topic) => {
            const session = getTopicSession(topic.id);
            const dialectColor = topic.dialect === "east_coast" ? "#3B82F6" : topic.dialect === "midwest" ? "#F97316" : "#6B6B6B";

            return (
              <div
                key={topic.id}
                onClick={() => handleSelectTopic(topic)}
                className={[
                  "rounded-2xl p-5 border-2 transition-all duration-200",
                  topic.locked
                    ? "border-border bg-surface/50 opacity-50 cursor-not-allowed"
                    : "border-border bg-surface hover:border-accent cursor-pointer",
                  session ? "border-green-700 bg-green-900/10" : "",
                ].join(" ")}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span
                        className="text-xs font-display uppercase tracking-wider px-2 py-0.5 rounded"
                        style={{ backgroundColor: `${dialectColor}22`, color: dialectColor }}
                      >
                        {topic.dialect === "east_coast" ? "East Coast" : topic.dialect === "midwest" ? "Midwest" : "General"}
                      </span>
                      <span className="text-xs text-muted font-display">{topic.level}</span>
                      {session && (
                        <span className="text-xs text-green-400 font-display">✓ {session.result.overall_score}/100</span>
                      )}
                    </div>
                    <h3 className={["font-display text-lg uppercase tracking-wide", topic.locked ? "text-muted" : "text-foreground"].join(" ")}>
                      {topic.title}
                    </h3>
                    <p className="text-muted text-xs mt-1">{topic.description}</p>
                  </div>
                  <div className="flex-shrink-0 ml-3">
                    {topic.locked ? (
                      <div className="w-10 h-10 rounded-full bg-border flex items-center justify-center">
                        <svg className="w-5 h-5 text-muted" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M12 1C8.676 1 6 3.676 6 7v1H4v15h16V8h-2V7c0-3.324-2.676-6-6-6zm0 2c2.276 0 4 1.724 4 4v1H8V7c0-2.276 1.724-4 4-4zm0 9a2 2 0 110 4 2 2 0 010-4z" />
                        </svg>
                      </div>
                    ) : session ? (
                      <div className="w-10 h-10 rounded-full bg-green-600 flex items-center justify-center">
                        <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                    ) : (
                      <div className="w-10 h-10 rounded-full bg-accent flex items-center justify-center">
                        <span className="text-white text-lg">🎙️</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Focus areas */}
                {!topic.locked && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {topic.focusAreas.slice(0, 3).map((f) => (
                      <span key={f} className="px-2 py-0.5 bg-background border border-border rounded text-xs text-muted font-mono">
                        {f}
                      </span>
                    ))}
                    {topic.focusAreas.length > 3 && (
                      <span className="px-2 py-0.5 text-xs text-muted">+{topic.focusAreas.length - 3} more</span>
                    )}
                  </div>
                )}

                {topic.locked && (
                  <p className="text-xs text-muted mt-2">
                    {topic.level === "C1" ? "Complete 6+ modules to unlock" :
                     topic.level === "B2" && topic.id === "code-switching" ? "Complete 6+ modules to unlock" :
                     topic.level === "B2" ? "Complete 4+ modules to unlock" :
                     topic.dialect === "east_coast" ? "Complete Lesson 1 to unlock" :
                     "Complete Lesson 2 to unlock"}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* ── PROMPT VIEW ── */}
      {(step === "prompt" || step === "waiting") && selectedTopic && (
        <>
          <button
            onClick={() => setStep("topics")}
            className="flex items-center gap-2 text-muted hover:text-foreground transition-colors text-sm font-display uppercase tracking-wider"
          >
            ← Back to Topics
          </button>

          <div className="flex items-center gap-3">
            <h2 className="font-display text-xl uppercase text-foreground">{selectedTopic.title}</h2>
            <Badge variant={selectedTopic.dialect === "east_coast" ? "east_coast" : selectedTopic.dialect === "midwest" ? "midwest" : "muted"}>
              {selectedTopic.dialect === "east_coast" ? "East Coast" : selectedTopic.dialect === "midwest" ? "Midwest" : "General"}
            </Badge>
          </div>

          <Card>
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-3">
              Step 1 — Copy this prompt → paste into Gemini → practice → say "done"
            </p>
            <div className="bg-background border border-border rounded-xl p-4 mb-4 max-h-48 overflow-y-auto">
              <pre className="text-foreground text-xs leading-relaxed whitespace-pre-wrap font-mono">
                {prompt}
              </pre>
            </div>
            <div className="flex gap-3">
              <Button variant="primary" size="md" className="flex-1" onClick={handleCopyPrompt}>
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
              <p className="text-xs text-muted uppercase tracking-wider font-display mb-3">How it works</p>
              <ol className="space-y-2 text-sm text-foreground mb-4">
                <li className="flex gap-2"><span className="text-accent font-bold">1.</span> Paste the prompt into Gemini</li>
                <li className="flex gap-2"><span className="text-accent font-bold">2.</span> Practice <span className="text-accent font-bold">{selectedTopic.title}</span> with the AI tutor</li>
                <li className="flex gap-2"><span className="text-accent font-bold">3.</span> When done, tell Gemini: <span className="text-accent font-mono">"done"</span></li>
                <li className="flex gap-2"><span className="text-accent font-bold">4.</span> Copy the JSON Gemini outputs</li>
                <li className="flex gap-2"><span className="text-accent font-bold">5.</span> Paste it below and submit</li>
              </ol>
              <Button variant="secondary" size="md" className="w-full" onClick={() => setStep("submit")}>
                I'm done — paste my results →
              </Button>
            </Card>
          )}
        </>
      )}

      {/* ── PASTE RESULTS ── */}
      {step === "submit" && selectedTopic && (
        <>
          <button onClick={() => setStep("waiting")} className="flex items-center gap-2 text-muted hover:text-foreground transition-colors text-sm font-display uppercase tracking-wider">
            ← Back
          </button>
          <Card>
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-3">
              Step 2 — Paste Gemini's JSON response
            </p>
            <p className="text-muted text-xs mb-3">
              After saying "done" to Gemini, copy everything it returned (including the JSON block) and paste it here.
            </p>
            <textarea
              value={pastedResult}
              onChange={(e) => setPastedResult(e.target.value)}
              rows={10}
              className="w-full bg-background border border-border rounded-xl px-4 py-3 text-foreground placeholder-muted focus:outline-none focus:border-accent transition-colors resize-none font-mono text-xs mb-3"
              placeholder={`Paste Gemini's full response here...\n\nIt should include:\n{\n  "overall_score": 85,\n  "pronunciation_score": 80,\n  ...\n}`}
            />
            {parseError && (
              <p className="text-accent text-sm mb-3">
                ✗ No valid JSON found. Make sure you said "done" to Gemini and copied the full response with the JSON block.
              </p>
            )}
            <Button variant="primary" size="md" className="w-full" disabled={!pastedResult.trim()} onClick={handleSubmitResult}>
              Submit Results
            </Button>
          </Card>
        </>
      )}

      {/* ── RESULTS ── */}
      {step === "results" && result && selectedTopic && (
        <>
          <button onClick={() => setStep("topics")} className="flex items-center gap-2 text-muted hover:text-foreground transition-colors text-sm font-display uppercase tracking-wider">
            ← All Topics
          </button>

          {/* Score card */}
          <div className={`rounded-2xl p-6 border-2 text-center ${getScoreBg(result.overall_score)}`}>
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-1">{selectedTopic.title}</p>
            <p className={`font-display text-7xl mb-2 ${getScoreColor(result.overall_score)}`}>
              {result.overall_score}
            </p>
            <p className="text-muted text-sm">
              {result.overall_score >= 80 ? "🔥 On point" : result.overall_score >= 60 ? "💪 Getting there" : "📚 Keep drilling"}
            </p>
          </div>

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

          {result.strengths.length > 0 && (
            <div className="bg-green-900/10 border border-green-800 rounded-xl p-4">
              <p className="text-xs text-green-400 uppercase tracking-wider font-display mb-2">✓ Strengths</p>
              <ul className="space-y-1">{result.strengths.map((s, i) => <li key={i} className="text-green-300 text-sm">• {s}</li>)}</ul>
            </div>
          )}

          {result.areas_to_improve.length > 0 && (
            <div className="bg-accent/5 border border-accent/30 rounded-xl p-4">
              <p className="text-xs text-accent uppercase tracking-wider font-display mb-2">↑ Areas to improve</p>
              <ul className="space-y-1">{result.areas_to_improve.map((a, i) => <li key={i} className="text-red-300 text-sm">• {a}</li>)}</ul>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3">
            <Button
              variant="secondary"
              size="md"
              onClick={() => {
                setStep("prompt");
                setPastedResult("");
                setResult(null);
              }}
            >
              🔄 Repeat Topic
            </Button>
            <Button
              variant="primary"
              size="md"
              className="flex-1"
              loading={saving}
              onClick={async () => {
                await handleSaveProgress();
                setStep("topics");
              }}
            >
              Save & Back to Topics
            </Button>
          </div>
        </>
      )}

      {/* ── SESSION HISTORY ── */}
      {step === "topics" && sessions.length > 0 && (
        <div>
          <p className="text-xs text-muted uppercase tracking-wider font-display mb-3">Recent Sessions</p>
          <div className="space-y-2">
            {sessions.slice(0, 5).map((s, i) => (
              <div key={i} className="flex items-center justify-between bg-surface border border-border rounded-xl px-4 py-3">
                <div>
                  <p className="text-foreground text-sm font-display uppercase">{s.topicTitle}</p>
                  <p className="text-muted text-xs">{new Date(s.completedAt).toLocaleDateString()}</p>
                </div>
                <p className={`font-display text-2xl ${getScoreColor(s.result.overall_score)}`}>
                  {s.result.overall_score}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
