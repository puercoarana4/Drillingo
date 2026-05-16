"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import ChatBubble from "@/components/modules/ChatBubble";
import DrillYoutubePlayer from "@/components/modules/DrillYoutubePlayer";
import FillInBlank, { BlankSlot, BlankResult } from "@/components/modules/FillInBlank";
import DrillWritingEval from "@/components/modules/DrillWritingEval";
import SpeakingRecorder from "@/components/modules/SpeakingRecorder";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import { api } from "@/lib/api";

// ── Types ─────────────────────────────────────────────────────────────────────

type ModuleType = "reading" | "listening" | "writing";

interface Lesson {
  id: string;
  title: string;
  dialect_segment: "east_coast" | "midwest";
  level_band: string;
  day_order: number;
  audio_url: string;
}

interface BreakdownItem { abbr: string; meaning: string; }

interface ReadingPayload {
  module_type: "reading";
  raw_text: string;
  formal_translation: string;
  breakdown: BreakdownItem[];
  grammar_notes: string[];
  dialect_focus: string;
  cefr_target: string;
  xp_reward: number;
}

interface BlankDef {
  position: number;
  correct_answers: string[];
  hint: string;
  distractor_options: string[];
}

interface ListeningPayload {
  module_type: "listening";
  artist: string;
  dialect_focus: string;
  // Can be a YouTube video ID (11 chars) or an S3 URL
  audio_s3_url: string;
  youtube_video_id?: string;
  original_bar: string;
  exercise_text: string;
  blanks: BlankDef[];
  full_translation: string;
  grammar_notes: string[];
  cefr_target: string;
  xp_reward: number;
}

interface WritingPayload {
  module_type: "writing";
  formal_input: string;
  expected_drill_output: string;
  accepted_variants: string[];
  evaluation_rubric: Record<string, { description: string; points: number; example: string }>;
  grammar_explanation: string;
  cefr_target: string;
  xp_reward: number;
}

type Payload = ReadingPayload | ListeningPayload | WritingPayload;

const MODULE_ORDER: ModuleType[] = ["reading", "listening", "writing"];

// ── Helpers ───────────────────────────────────────────────────────────────────

function buildTranscript(exerciseText: string): string {
  let i = 0;
  return exerciseText.replace(/______/g, () => `{{blank_${i++}}}`);
}

function buildBlankSlots(blanks: BlankDef[]): BlankSlot[] {
  return blanks.map((b, i) => ({
    id: `blank_${i}`,
    position: b.position,
    correctAnswer: b.correct_answers[0],
    explanation: b.hint,
  }));
}

/** Extract YouTube video ID from a URL or return the string if it's already an ID */
function extractYouTubeId(urlOrId: string): string | null {
  if (!urlOrId) return null;
  // Already an 11-char ID
  if (/^[a-zA-Z0-9_-]{11}$/.test(urlOrId)) return urlOrId;
  // youtu.be/ID
  const short = urlOrId.match(/youtu\.be\/([a-zA-Z0-9_-]{11})/);
  if (short) return short[1];
  // youtube.com/watch?v=ID
  const long = urlOrId.match(/[?&]v=([a-zA-Z0-9_-]{11})/);
  if (long) return long[1];
  return null;
}

// ── Celebration overlay ───────────────────────────────────────────────────────

function CelebrationOverlay({
  xp, isLastModule, nextModule, onContinue,
}: {
  xp: number;
  isLastModule: boolean;
  nextModule: ModuleType | null;
  onContinue: () => void;
}) {
  return (
    <div className="fixed inset-0 bg-background/90 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-surface border-2 border-accent rounded-2xl p-8 max-w-sm w-full text-center">
        <div className="text-6xl mb-4">{isLastModule ? "🏆" : "🔥"}</div>
        <h2 className="font-display text-3xl uppercase text-accent mb-2">
          {isLastModule ? "Lesson Complete!" : "Module Done!"}
        </h2>
        <p className="text-foreground text-lg font-display mb-1">+{xp} XP</p>
        <p className="text-muted text-sm mb-6">
          {isLastModule ? "You unlocked the next lesson." : `Next up: ${nextModule?.toUpperCase()}`}
        </p>
        {isLastModule ? (
          <Link href="/learn">
            <Button variant="primary" size="md" className="w-full">Back to Path →</Button>
          </Link>
        ) : (
          <Button variant="primary" size="md" className="w-full" onClick={onContinue}>
            Continue to {nextModule?.toUpperCase()} →
          </Button>
        )}
      </div>
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function GuidedModulePage() {
  const { lessonId, module: moduleParam } = useParams<{ lessonId: string; module: string }>();
  const router = useRouter();
  const currentModule = moduleParam as ModuleType;

  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [payload, setPayload] = useState<Payload | null>(null);
  const [loading, setLoading] = useState(true);
  const [xpAwarded, setXpAwarded] = useState<number>(0);
  const [showCelebration, setShowCelebration] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Reading state
  const [revealedTerms, setRevealedTerms] = useState<string[]>([]);
  const [activeDefinition, setActiveDefinition] = useState<BreakdownItem | null>(null);
  const [readingPhase, setReadingPhase] = useState<"read" | "breakdown">("read");

  // Listening state
  const [videoStarted, setVideoStarted] = useState(false);

  useEffect(() => {
    setLoading(true);
    setShowCelebration(false);
    setReadingPhase("read");
    setRevealedTerms([]);
    setActiveDefinition(null);
    setVideoStarted(false);

    api.get<Lesson>(`/api/content/lessons/${lessonId}`)
      .then((l) => {
        setLesson(l);
        if (l.audio_url.startsWith("{")) {
          setPayload(JSON.parse(l.audio_url) as Payload);
        }
      })
      .catch(() => router.push("/login"))
      .finally(() => setLoading(false));
  }, [lessonId, currentModule, router]);

  const currentModuleIndex = MODULE_ORDER.indexOf(currentModule);
  const isLastModule = currentModuleIndex === MODULE_ORDER.length - 1;
  const nextModule = isLastModule ? null : MODULE_ORDER[currentModuleIndex + 1];
  const progressPct = ((currentModuleIndex + 1) / MODULE_ORDER.length) * 100;

  async function saveProgress(finalScore: number) {
    if (!lesson || submitting) return;
    setSubmitting(true);
    try {
      const result = await api.post<{ xp_awarded: number }>("/api/progress/lesson", {
        lesson_id: lesson.id,
        module_type: currentModule,
        score: finalScore,
      });
      setXpAwarded(result.xp_awarded);
    } catch {
      setXpAwarded(0);
    } finally {
      setSubmitting(false);
      setShowCelebration(true);
    }
  }

  function handleContinueToNext() {
    setShowCelebration(false);
    if (nextModule) router.push(`/learn/${lessonId}/${nextModule}`);
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin h-10 w-10 border-2 border-accent border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!lesson || !payload) {
    return (
      <div className="text-center py-16">
        <p className="text-muted">Lesson not found.</p>
        <Link href="/learn" className="text-accent hover:underline mt-4 block">← Back to Path</Link>
      </div>
    );
  }

  return (
    <>
      {showCelebration && (
        <CelebrationOverlay
          xp={xpAwarded}
          isLastModule={isLastModule}
          nextModule={nextModule}
          onContinue={handleContinueToNext}
        />
      )}

      <div className="max-w-2xl mx-auto space-y-5">
        {/* Top bar */}
        <div className="flex items-center gap-4">
          <Link href="/learn" className="text-muted hover:text-foreground transition-colors text-xl">✕</Link>
          <div className="flex-1 h-3 bg-border rounded-full overflow-hidden">
            <div className="h-full bg-accent rounded-full transition-all duration-500" style={{ width: `${progressPct}%` }} />
          </div>
          <span className="text-muted text-xs font-display uppercase">{currentModuleIndex + 1}/{MODULE_ORDER.length}</span>
        </div>

        {/* Module tabs */}
        <div className="flex gap-2">
          {MODULE_ORDER.map((mod, i) => (
            <div key={mod} className={[
              "flex-1 py-2 rounded-lg text-center text-xs font-display uppercase tracking-wider",
              mod === currentModule ? "bg-accent text-white"
                : i < currentModuleIndex ? "bg-green-900/40 text-green-400"
                : "bg-border text-muted",
            ].join(" ")}>
              {i < currentModuleIndex ? "✓ " : ""}{mod}
            </div>
          ))}
        </div>

        {/* Lesson header */}
        <div>
          <div className="flex gap-2 mb-1">
            <Badge variant={lesson.dialect_segment}>
              {lesson.dialect_segment === "east_coast" ? "East Coast" : "Midwest"}
            </Badge>
            <Badge variant="muted">{lesson.level_band}</Badge>
          </div>
          <h1 className="font-display text-lg uppercase text-foreground tracking-wide">{lesson.title}</h1>
        </div>

        {/* ── READING ── */}
        {currentModule === "reading" && payload.module_type === "reading" && (
          <>
            {readingPhase === "read" && (
              <>
                <Card>
                  <p className="text-xs text-muted uppercase tracking-wider font-display mb-3">
                    📱 Incoming DM — {payload.dialect_focus}
                  </p>
                  <ChatBubble
                    message={payload.raw_text}
                    sender="other"
                    highlightedTerms={payload.breakdown.map((b) => ({ term: b.abbr, index: 0 }))}
                    onTermClick={(term) => {
                      const item = payload.breakdown.find((b) => b.abbr.toLowerCase() === term.toLowerCase());
                      if (item) {
                        setRevealedTerms((prev) => prev.includes(term.toLowerCase()) ? prev : [...prev, term.toLowerCase()]);
                        setActiveDefinition(item);
                      }
                    }}
                    timestamp="just now"
                  />
                  <p className="text-xs text-muted mt-3">
                    Tap <span className="text-accent font-bold">highlighted words</span> to decode them.
                  </p>
                </Card>
                {activeDefinition && (
                  <Card accent>
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-display text-lg uppercase text-accent">{activeDefinition.abbr}</p>
                        <p className="text-foreground mt-1">{activeDefinition.meaning}</p>
                      </div>
                      <button onClick={() => setActiveDefinition(null)} className="text-muted hover:text-foreground ml-4 text-xl">×</button>
                    </div>
                  </Card>
                )}
                <div className="flex items-center justify-between text-sm text-muted">
                  <span>{revealedTerms.length}/{payload.breakdown.length} decoded</span>
                  <Button variant="primary" size="md" onClick={() => setReadingPhase("breakdown")}>See Breakdown →</Button>
                </div>
              </>
            )}

            {readingPhase === "breakdown" && (
              <>
                <Card accent>
                  <p className="text-xs text-muted uppercase tracking-wider font-display mb-2">Translation</p>
                  <p className="text-foreground leading-relaxed">{payload.formal_translation}</p>
                </Card>
                <div className="space-y-2">
                  {payload.breakdown.map((item) => (
                    <div key={item.abbr} className="flex items-start gap-3 bg-surface border border-border rounded-lg px-4 py-3">
                      <span className="font-display text-accent uppercase text-sm w-28 flex-shrink-0">{item.abbr}</span>
                      <span className="text-foreground text-sm">{item.meaning}</span>
                    </div>
                  ))}
                </div>
                {payload.grammar_notes.length > 0 && (
                  <Card>
                    <p className="text-xs text-muted uppercase tracking-wider font-display mb-3">Grammar Notes</p>
                    <ul className="space-y-2">
                      {payload.grammar_notes.map((note, i) => (
                        <li key={i} className="flex gap-2 text-sm text-foreground">
                          <span className="text-accent flex-shrink-0">•</span>
                          <span>{note}</span>
                        </li>
                      ))}
                    </ul>
                  </Card>
                )}
                <Button variant="primary" size="md" className="w-full" loading={submitting} onClick={() => saveProgress(100)}>
                  Complete Reading (+{payload.xp_reward} XP)
                </Button>
              </>
            )}
          </>
        )}

        {/* ── LISTENING — YouTube Drill Cypher ── */}
        {currentModule === "listening" && payload.module_type === "listening" && (() => {
          const ytId = payload.youtube_video_id ?? extractYouTubeId(payload.audio_s3_url);
          return (
            <>
              <Card>
                <p className="text-xs text-muted uppercase tracking-wider font-display mb-1">Artist</p>
                <p className="font-display text-2xl uppercase text-foreground mb-3">{payload.artist}</p>
                {ytId ? (
                  <>
                    <DrillYoutubePlayer
                      videoId={ytId}
                      title={`${payload.artist} — The Cypher`}
                      onFirstPlay={() => setVideoStarted(true)}
                    />
                    {!videoStarted && (
                      <p className="text-xs text-muted mt-2 text-center">
                        ▶ Play the video, then fill in the blanks below
                      </p>
                    )}
                  </>
                ) : (
                  <div className="bg-background border border-border rounded-xl p-4 text-center">
                    <p className="text-muted text-sm">Audio: <span className="text-accent">{payload.original_bar}</span></p>
                  </div>
                )}
              </Card>

              <Card>
                <p className="text-xs text-muted uppercase tracking-wider font-display mb-2">
                  🎵 Fill in the blanks
                </p>
                <FillInBlank
                  transcript={buildTranscript(payload.exercise_text)}
                  blanks={buildBlankSlots(payload.blanks)}
                  onComplete={(score) => saveProgress(score)}
                />
              </Card>

              <Card>
                <p className="text-xs text-muted uppercase tracking-wider font-display mb-3">Word Bank</p>
                <div className="flex flex-wrap gap-2">
                  {payload.blanks.flatMap((b) => b.distractor_options).map((opt, i) => (
                    <span key={i} className="px-3 py-1 bg-background border border-border rounded-full text-sm text-muted font-display uppercase">{opt}</span>
                  ))}
                </div>
              </Card>
            </>
          );
        })()}

        {/* ── WRITING — Gemini-powered evaluation ── */}
        {currentModule === "writing" && payload.module_type === "writing" && (
          <Card>
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-3">🎤 Spitting Bars</p>
            <DrillWritingEval
              formalInput={payload.formal_input}
              referenceAnswer={payload.expected_drill_output}
              acceptedVariants={payload.accepted_variants}
              rubric={payload.evaluation_rubric}
              grammarExplanation={payload.grammar_explanation}
              xpReward={payload.xp_reward}
              onComplete={(score) => saveProgress(score)}
            />
          </Card>
        )}
      </div>
    </>
  );
}

// ── Types ─────────────────────────────────────────────────────────────────────

type ModuleType = "reading" | "listening" | "writing";

interface Lesson {
  id: string;
  title: string;
  dialect_segment: "east_coast" | "midwest";
  level_band: string;
  day_order: number;
  audio_url: string;
}

interface BreakdownItem { abbr: string; meaning: string; }

interface ReadingPayload {
  module_type: "reading";
  raw_text: string;
  formal_translation: string;
  breakdown: BreakdownItem[];
  grammar_notes: string[];
  dialect_focus: string;
  cefr_target: string;
  xp_reward: number;
}

interface BlankDef {
  position: number;
  correct_answers: string[];
  hint: string;
  distractor_options: string[];
}

interface ListeningPayload {
  module_type: "listening";
  artist: string;
  dialect_focus: string;
  audio_s3_url: string;
  original_bar: string;
  exercise_text: string;
  blanks: BlankDef[];
  full_translation: string;
  grammar_notes: string[];
  cefr_target: string;
  xp_reward: number;
}

interface WritingPayload {
  module_type: "writing";
  formal_input: string;
  expected_drill_output: string;
  accepted_variants: string[];
  evaluation_rubric: Record<string, { description: string; points: number; example: string }>;
  grammar_explanation: string;
  cefr_target: string;
  xp_reward: number;
}

type Payload = ReadingPayload | ListeningPayload | WritingPayload;

const MODULE_ORDER: ModuleType[] = ["reading", "listening", "writing"];

// ── Helpers ───────────────────────────────────────────────────────────────────

function buildTranscript(exerciseText: string): string {
  let i = 0;
  return exerciseText.replace(/______/g, () => `{{blank_${i++}}}`);
}

function buildBlankSlots(blanks: BlankDef[]): BlankSlot[] {
  return blanks.map((b, i) => ({
    id: `blank_${i}`,
    position: b.position,
    correctAnswer: b.correct_answers[0],
    explanation: b.hint,
  }));
}

// ── Celebration overlay ───────────────────────────────────────────────────────

function CelebrationOverlay({
  xp,
  isLastModule,
  nextModule,
  lessonId,
  onContinue,
}: {
  xp: number;
  isLastModule: boolean;
  nextModule: ModuleType | null;
  lessonId: string;
  onContinue: () => void;
}) {
  return (
    <div className="fixed inset-0 bg-background/90 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-surface border-2 border-accent rounded-2xl p-8 max-w-sm w-full text-center animate-bounce-once">
        <div className="text-6xl mb-4">{isLastModule ? "🏆" : "🔥"}</div>
        <h2 className="font-display text-3xl uppercase text-accent mb-2">
          {isLastModule ? "Lesson Complete!" : "Module Done!"}
        </h2>
        <p className="text-foreground text-lg font-display mb-1">+{xp} XP</p>
        <p className="text-muted text-sm mb-6">
          {isLastModule
            ? "You unlocked the next lesson on your path."
            : `Next up: ${nextModule?.toUpperCase()}`}
        </p>
        {isLastModule ? (
          <Link href="/learn">
            <Button variant="primary" size="md" className="w-full">
              Back to Path →
            </Button>
          </Link>
        ) : (
          <Button variant="primary" size="md" className="w-full" onClick={onContinue}>
            Continue to {nextModule?.toUpperCase()} →
          </Button>
        )}
      </div>
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function GuidedModulePage() {
  const { lessonId, module: moduleParam } = useParams<{ lessonId: string; module: string }>();
  const router = useRouter();
  const currentModule = moduleParam as ModuleType;

  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [payload, setPayload] = useState<Payload | null>(null);
  const [loading, setLoading] = useState(true);
  const [phase, setPhase] = useState<"exercise" | "done">("exercise");
  const [score, setScore] = useState<number | null>(null);
  const [xpAwarded, setXpAwarded] = useState<number>(0);
  const [showCelebration, setShowCelebration] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Reading-specific state
  const [revealedTerms, setRevealedTerms] = useState<string[]>([]);
  const [activeDefinition, setActiveDefinition] = useState<BreakdownItem | null>(null);
  const [readingPhase, setReadingPhase] = useState<"read" | "breakdown">("read");

  useEffect(() => {
    setLoading(true);
    setPhase("exercise");
    setScore(null);
    setShowCelebration(false);
    setReadingPhase("read");
    setRevealedTerms([]);
    setActiveDefinition(null);

    api.get<Lesson>(`/api/content/lessons/${lessonId}`)
      .then((l) => {
        setLesson(l);
        if (l.audio_url.startsWith("{")) {
          const parsed = JSON.parse(l.audio_url) as Payload;
          setPayload(parsed);
        }
      })
      .catch(() => router.push("/login"))
      .finally(() => setLoading(false));
  }, [lessonId, currentModule, router]);

  const currentModuleIndex = MODULE_ORDER.indexOf(currentModule);
  const isLastModule = currentModuleIndex === MODULE_ORDER.length - 1;
  const nextModule = isLastModule ? null : MODULE_ORDER[currentModuleIndex + 1];

  async function saveProgress(finalScore: number) {
    if (!lesson || submitting) return;
    setSubmitting(true);
    try {
      const result = await api.post<{ xp_awarded: number }>("/api/progress/lesson", {
        lesson_id: lesson.id,
        module_type: currentModule,
        score: finalScore,
      });
      setXpAwarded(result.xp_awarded);
    } catch {
      setXpAwarded(0);
    } finally {
      setSubmitting(false);
      setShowCelebration(true);
    }
  }

  function handleContinueToNext() {
    setShowCelebration(false);
    if (nextModule) {
      router.push(`/learn/${lessonId}/${nextModule}`);
    }
  }

  // ── Progress bar ────────────────────────────────────────────────────────────
  const progressPct = ((currentModuleIndex + 1) / MODULE_ORDER.length) * 100;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin h-10 w-10 border-2 border-accent border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!lesson || !payload) {
    return (
      <div className="text-center py-16">
        <p className="text-muted">Lesson not found.</p>
        <Link href="/learn" className="text-accent hover:underline mt-4 block">← Back to Path</Link>
      </div>
    );
  }

  return (
    <>
      {showCelebration && (
        <CelebrationOverlay
          xp={xpAwarded}
          isLastModule={isLastModule}
          nextModule={nextModule}
          lessonId={lessonId}
          onContinue={handleContinueToNext}
        />
      )}

      <div className="max-w-2xl mx-auto space-y-5">
        {/* Top bar: back + progress */}
        <div className="flex items-center gap-4">
          <Link href="/learn" className="text-muted hover:text-foreground transition-colors text-xl">
            ✕
          </Link>
          <div className="flex-1 h-3 bg-border rounded-full overflow-hidden">
            <div
              className="h-full bg-accent rounded-full transition-all duration-500"
              style={{ width: `${progressPct}%` }}
            />
          </div>
          <span className="text-muted text-xs font-display uppercase">
            {currentModuleIndex + 1}/{MODULE_ORDER.length}
          </span>
        </div>

        {/* Module tabs */}
        <div className="flex gap-2">
          {MODULE_ORDER.map((mod, i) => (
            <div
              key={mod}
              className={[
                "flex-1 py-2 rounded-lg text-center text-xs font-display uppercase tracking-wider",
                mod === currentModule
                  ? "bg-accent text-white"
                  : i < currentModuleIndex
                  ? "bg-green-900/40 text-green-400"
                  : "bg-border text-muted",
              ].join(" ")}
            >
              {i < currentModuleIndex ? "✓ " : ""}{mod}
            </div>
          ))}
        </div>

        {/* Lesson title */}
        <div>
          <div className="flex gap-2 mb-1">
            <Badge variant={lesson.dialect_segment}>
              {lesson.dialect_segment === "east_coast" ? "East Coast" : "Midwest"}
            </Badge>
            <Badge variant="muted">{lesson.level_band}</Badge>
          </div>
          <h1 className="font-display text-lg uppercase text-foreground tracking-wide">
            {lesson.title}
          </h1>
        </div>

        {/* ── READING MODULE ── */}
        {currentModule === "reading" && payload.module_type === "reading" && (
          <>
            {readingPhase === "read" && (
              <>
                <Card>
                  <p className="text-xs text-muted uppercase tracking-wider font-display mb-3">
                    📱 Incoming DM — {payload.dialect_focus}
                  </p>
                  <ChatBubble
                    message={payload.raw_text}
                    sender="other"
                    highlightedTerms={payload.breakdown.map((b) => ({ term: b.abbr, index: 0 }))}
                    onTermClick={(term) => {
                      const item = payload.breakdown.find(
                        (b) => b.abbr.toLowerCase() === term.toLowerCase()
                      );
                      if (item) {
                        setRevealedTerms((prev) =>
                          prev.includes(term.toLowerCase())
                            ? prev
                            : [...prev, term.toLowerCase()]
                        );
                        setActiveDefinition(item);
                      }
                    }}
                    timestamp="just now"
                  />
                  <p className="text-xs text-muted mt-3">
                    Tap <span className="text-accent font-bold">highlighted words</span> to decode them.
                  </p>
                </Card>

                {activeDefinition && (
                  <Card accent>
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-display text-lg uppercase text-accent">{activeDefinition.abbr}</p>
                        <p className="text-foreground mt-1">{activeDefinition.meaning}</p>
                      </div>
                      <button onClick={() => setActiveDefinition(null)} className="text-muted hover:text-foreground ml-4 text-xl">×</button>
                    </div>
                  </Card>
                )}

                <div className="flex items-center justify-between text-sm text-muted">
                  <span>{revealedTerms.length}/{payload.breakdown.length} decoded</span>
                  <Button variant="primary" size="md" onClick={() => setReadingPhase("breakdown")}>
                    See Breakdown →
                  </Button>
                </div>
              </>
            )}

            {readingPhase === "breakdown" && (
              <>
                <Card accent>
                  <p className="text-xs text-muted uppercase tracking-wider font-display mb-2">Translation</p>
                  <p className="text-foreground leading-relaxed">{payload.formal_translation}</p>
                </Card>

                <div className="space-y-2">
                  {payload.breakdown.map((item) => (
                    <div key={item.abbr} className="flex items-start gap-3 bg-surface border border-border rounded-lg px-4 py-3">
                      <span className="font-display text-accent uppercase text-sm w-28 flex-shrink-0">{item.abbr}</span>
                      <span className="text-foreground text-sm">{item.meaning}</span>
                    </div>
                  ))}
                </div>

                {payload.grammar_notes.length > 0 && (
                  <Card>
                    <p className="text-xs text-muted uppercase tracking-wider font-display mb-3">Grammar Notes</p>
                    <ul className="space-y-2">
                      {payload.grammar_notes.map((note, i) => (
                        <li key={i} className="flex gap-2 text-sm text-foreground">
                          <span className="text-accent flex-shrink-0">•</span>
                          <span>{note}</span>
                        </li>
                      ))}
                    </ul>
                  </Card>
                )}

                <Button
                  variant="primary" size="md" className="w-full"
                  loading={submitting}
                  onClick={() => saveProgress(100)}
                >
                  Complete Reading (+{payload.xp_reward} XP)
                </Button>
              </>
            )}
          </>
        )}

        {/* ── LISTENING MODULE ── */}
        {currentModule === "listening" && payload.module_type === "listening" && (
          <>
            <Card>
              <p className="text-xs text-muted uppercase tracking-wider font-display mb-1">Artist</p>
              <p className="font-display text-2xl uppercase text-foreground mb-3">{payload.artist}</p>
              <AudioPlayer audioUrl={payload.audio_s3_url} title={`${payload.artist} — The Cypher`} />
            </Card>

            <Card>
              <p className="text-xs text-muted uppercase tracking-wider font-display mb-2">Fill in the blanks</p>
              <FillInBlank
                transcript={buildTranscript(payload.exercise_text)}
                blanks={buildBlankSlots(payload.blanks)}
                onComplete={(finalScore) => saveProgress(finalScore)}
              />
            </Card>

            <Card>
              <p className="text-xs text-muted uppercase tracking-wider font-display mb-3">Word Bank</p>
              <div className="flex flex-wrap gap-2">
                {payload.blanks.flatMap((b) => b.distractor_options).map((opt, i) => (
                  <span key={i} className="px-3 py-1 bg-background border border-border rounded-full text-sm text-muted font-display uppercase">
                    {opt}
                  </span>
                ))}
              </div>
            </Card>
          </>
        )}

        {/* ── WRITING MODULE ── */}
        {currentModule === "writing" && payload.module_type === "writing" && (
          <>
            <Card>
              <p className="text-xs text-muted uppercase tracking-wider font-display mb-3">Scoring Rubric</p>
              <div className="space-y-2">
                {Object.entries(payload.evaluation_rubric).map(([key, criterion]) => (
                  <div key={key} className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <p className="text-foreground text-sm">{criterion.description}</p>
                      <p className="text-muted text-xs mt-0.5 font-mono">{criterion.example}</p>
                    </div>
                    <span className="text-accent font-display text-sm flex-shrink-0">+{criterion.points}pts</span>
                  </div>
                ))}
              </div>
            </Card>

            <Card>
              <p className="text-xs text-muted uppercase tracking-wider font-display mb-3">🎤 Translate to Drill</p>
              <TranslationInput
                formalPhrase={payload.formal_input}
                acceptedAnswers={payload.accepted_variants}
                explanation={payload.grammar_explanation}
                onResult={(isCorrect) => saveProgress(isCorrect ? 100 : 40)}
              />
            </Card>
          </>
        )}
      </div>
    </>
  );
}
