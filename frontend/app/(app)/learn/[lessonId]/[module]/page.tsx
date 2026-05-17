"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import ChatBubble from "@/components/modules/ChatBubble";
import DrillYoutubePlayer from "@/components/modules/DrillYoutubePlayer";
import FillInBlank, { BlankSlot } from "@/components/modules/FillInBlank";
import SpeakingRecorder from "@/components/modules/SpeakingRecorder";
import VocabularyMatch from "@/components/modules/VocabularyMatch";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import { api } from "@/lib/api";

// ── Types ─────────────────────────────────────────────────────────────────────

type ModuleType = "reading" | "listening" | "writing" | "speaking";

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

interface SpeakingPayload {
  module_type: "speaking";
  target_phrase: string;
  phonetic_tips: string[];
  cefr_target: string;
  xp_reward: number;
}

type Payload = ReadingPayload | ListeningPayload | WritingPayload | SpeakingPayload;

const MODULE_ORDER: ModuleType[] = ["reading", "listening", "writing", "speaking"];

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

function extractYouTubeId(urlOrId: string): string | null {
  if (!urlOrId) return null;
  if (/^[a-zA-Z0-9_-]{11}$/.test(urlOrId)) return urlOrId;
  const short = urlOrId.match(/youtu\.be\/([a-zA-Z0-9_-]{11})/);
  if (short) return short[1];
  const long = urlOrId.match(/[?&]v=([a-zA-Z0-9_-]{11})/);
  if (long) return long[1];
  return null;
}

// ── Celebration overlay ───────────────────────────────────────────────────────

function CelebrationOverlay({
  xp, isLastModule, nextModule, onClose,
}: {
  xp: number;
  isLastModule: boolean;
  nextModule: ModuleType | null;
  onClose: () => void;
}) {
  useEffect(() => {
    const t = setTimeout(onClose, 2500);
    return () => clearTimeout(t);
  }, [onClose]);

  return (
    <div className="fixed inset-0 bg-background/90 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-surface border-2 border-accent rounded-2xl p-8 max-w-sm w-full text-center animate-in zoom-in duration-300">
        <div className="text-6xl mb-4">{isLastModule ? "🏆" : "🔥"}</div>
        <h2 className="font-display text-3xl uppercase text-accent mb-2">
          {isLastModule ? "Lesson Complete!" : "Module Done!"}
        </h2>
        <p className="text-foreground text-lg font-display mb-1">+{xp} XP</p>
        <p className="text-muted text-sm mt-2">
          {isLastModule ? "You unlocked the next lesson." : `Next up: ${nextModule?.toUpperCase()}`}
        </p>
      </div>
    </div>
  );
}

// ── Writing Module (local evaluation — no Gemini required) ───────────────────

function WritingModule({
  payload,
  onComplete,
  submitting,
  isReview = false,
  lessonId,
}: {
  payload: WritingPayload;
  onComplete: (score: number) => void;
  submitting: boolean;
  isReview?: boolean;
  lessonId: string;
}) {
  const storageKey = `drillingo_ans_${lessonId}_writing`;

  function normalise(s: string): string {
    return s.toLowerCase().trim().replace(/[^\w\s']/g, "").replace(/\s+/g, " ");
  }

  const [answer, setAnswer] = useState(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem(storageKey) || "";
    }
    return "";
  });
  const [submitted, setSubmitted] = useState(isReview || false);
  const [isCorrect, setIsCorrect] = useState(() => {
    if (typeof window !== "undefined") {
      const ans = localStorage.getItem(storageKey);
      if (ans) {
        const norm = normalise(ans);
        return payload.accepted_variants.some((v) => normalise(v) === norm);
      }
    }
    return false;
  });

  function handleSubmit() {
    localStorage.setItem(storageKey, answer);
    const norm = normalise(answer);
    const correct = payload.accepted_variants.some((v) => normalise(v) === norm);
    setIsCorrect(correct);
    setSubmitted(true);
    onComplete(correct ? 100 : 40);
  }

  return (
    <Card>
      <p className="text-xs text-muted uppercase tracking-wider font-display mb-3">🎤 Spitting Bars</p>

      {/* Rubric */}
      <div className="space-y-1 mb-4">
        {Object.entries(payload.evaluation_rubric).map(([key, c]) => (
          <div key={key} className="flex items-start justify-between gap-3 text-xs">
            <span className="text-muted flex-1">{c.description} <span className="font-mono text-muted/60">{c.example}</span></span>
            <span className="text-accent font-display flex-shrink-0">+{c.points}pts</span>
          </div>
        ))}
      </div>

      {/* Formal input */}
      <div className="bg-background border border-border rounded-xl p-4 mb-4">
        <p className="text-xs text-muted uppercase tracking-wider font-display mb-1">Formal English</p>
        <p className="text-foreground text-lg">&ldquo;{payload.formal_input}&rdquo;</p>
      </div>

      {!submitted ? (
        <>
          <label className="block text-xs text-muted uppercase tracking-wider font-display mb-1">Say it in Drill</label>
          <textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            rows={3}
            className="w-full bg-background border border-border rounded-xl px-4 py-3 text-foreground placeholder-muted focus:outline-none focus:border-accent transition-colors resize-none mb-3"
            placeholder="e.g. I ain't finna do allat..."
          />
          <Button variant="primary" size="md" className="w-full" disabled={!answer.trim()} loading={submitting} onClick={handleSubmit}>
            Spit It 🎤
          </Button>
        </>
      ) : (
        <div className="space-y-3">
          {isReview && !answer && (
            <div className="bg-surface border border-green-700 rounded-xl p-3">
              <p className="text-xs text-green-400 uppercase tracking-wider font-display mb-1">✓ Already completed</p>
              <p className="text-foreground text-sm font-bold">&ldquo;{payload.expected_drill_output}&rdquo;</p>
              <p className="text-muted text-xs mt-2">{payload.grammar_explanation}</p>
            </div>
          )}
          {(answer || !isReview) && (
            <>
              <div className={["rounded-xl p-4 border text-center", isCorrect ? "border-green-700 bg-green-900/20" : "border-accent/50 bg-accent/10"].join(" ")}>
                <p className={["font-display text-2xl uppercase mb-1", isCorrect ? "text-green-400" : "text-accent"].join(" ")}>
                  {isCorrect ? "On Point 🔥" : "Keep Drilling"}
                </p>
                {isReview && <p className="text-xs text-muted mb-2">This is what you submitted:</p>}
                <p className="text-foreground text-lg mb-2">&ldquo;{answer}&rdquo;</p>
                <p className="text-muted text-sm">{isCorrect ? "Your translation matches the drill structure." : "Check the reference below."}</p>
              </div>
              <div className="bg-surface border border-border rounded-xl p-3">
                <p className="text-xs text-muted uppercase tracking-wider font-display mb-1">Reference</p>
                <p className="text-foreground text-sm font-bold">&ldquo;{payload.expected_drill_output}&rdquo;</p>
                <p className="text-muted text-xs mt-2">{payload.grammar_explanation}</p>
              </div>
            </>
          )}
        </div>
      )}
    </Card>
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
  // isReview = true when this module was already completed — show content, no re-submit
  const [isReview, setIsReview] = useState(false);

  const [revealedTerms, setRevealedTerms] = useState<string[]>([]);
  const [activeDefinition, setActiveDefinition] = useState<BreakdownItem | null>(null);
  const [readingPhase, setReadingPhase] = useState<"read" | "breakdown" | "match">("read");
  const [videoStarted, setVideoStarted] = useState(false);

  useEffect(() => {
    setLoading(true);
    setShowCelebration(false);
    setReadingPhase("read");
    setRevealedTerms([]);
    setActiveDefinition(null);
    setVideoStarted(false);
    setIsReview(false);

    Promise.all([
      api.get<Lesson>(`/api/content/lessons/${lessonId}`),
      api.get<Array<{ lesson_id: string; module_type: string }>>("/api/progress/lessons")
        .catch(() => [] as Array<{ lesson_id: string; module_type: string }>),
    ])
      .then(([l, progress]) => {
        setLesson(l);
        if (l.audio_url.startsWith("{")) {
          const parsed = JSON.parse(l.audio_url);
          if (parsed.modules && parsed.modules[currentModule]) {
            setPayload(parsed.modules[currentModule] as Payload);
          } else if (parsed.module_type === currentModule) {
            setPayload(parsed as Payload);
          }
        }
        // Check if this module was already completed
        const alreadyDone = progress.some(
          (p) => p.lesson_id === lessonId && p.module_type === currentModule
        );
        setIsReview(alreadyDone);
        // If reviewing, start reading at breakdown view directly
        if (alreadyDone) setReadingPhase("breakdown");
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
      setIsReview(true);
    } catch {
      setXpAwarded(0);
    } finally {
      setSubmitting(false);
      setShowCelebration(true);
    }
  }

  function handleContinueToNext() {
    setShowCelebration(false);
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
          onClose={handleContinueToNext}
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

        {/* Module tabs — clickable for completed modules */}
        <div className="flex gap-2">
          {MODULE_ORDER.map((mod, i) => {
            const isCompleted = i < currentModuleIndex;
            const isCurrent = mod === currentModule;
            return (
              <button
                key={mod}
                disabled={!isCompleted && !isCurrent}
                onClick={() => {
                  if (isCompleted) router.push(`/learn/${lessonId}/${mod}`);
                }}
                className={[
                  "flex-1 py-2 rounded-lg text-center text-xs font-display uppercase tracking-wider transition-colors",
                  isCurrent ? "bg-accent text-white"
                    : isCompleted ? "bg-green-900/40 text-green-400 hover:bg-green-900/60 cursor-pointer"
                    : "bg-border text-muted cursor-not-allowed",
                ].join(" ")}
                title={isCompleted ? `Review ${mod}` : isCurrent ? `Current: ${mod}` : `Complete previous modules first`}
              >
                {isCompleted ? "✓ " : ""}{mod}
              </button>
            );
          })}
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

        {/* Review mode banner */}
        {isReview && (
          <div className="flex items-center gap-2 bg-green-900/20 border border-green-700 rounded-xl px-4 py-2">
            <span className="text-green-400 text-sm">✓</span>
            <p className="text-green-400 text-xs font-display uppercase tracking-wider">
              Review mode — already completed
            </p>
            <button
              onClick={() => {
                const nextModule = MODULE_ORDER[MODULE_ORDER.indexOf(currentModule) + 1];
                if (nextModule) router.push(`/learn/${lessonId}/${nextModule}`);
                else router.push("/learn");
              }}
              className="ml-auto text-xs text-accent hover:underline font-display uppercase"
            >
              Continue →
            </button>
          </div>
        )}

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
                    Toca <span className="text-accent font-bold">las palabras resaltadas</span> para decodificarlas.
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
                  <span>{revealedTerms.length}/{payload.breakdown.length} decodificadas</span>
                  <Button variant="primary" size="md" onClick={() => setReadingPhase("breakdown")}>Ver Análisis →</Button>
                </div>
              </>
            )}

            {readingPhase === "breakdown" && (
              <>
                {/* ── Three-way comparison card ── */}
                <div className="rounded-2xl border border-border overflow-hidden">
                  {/* Row 1: AAVE */}
                  <div className="bg-accent/10 border-b border-border px-4 py-3">
                    <p className="text-xs font-display uppercase tracking-wider text-accent mb-1">🎤 AAVE / Drill</p>
                    <p className="text-foreground text-sm font-bold leading-relaxed">{payload.raw_text}</p>
                  </div>
                  {/* Row 2: Formal English */}
                  <div className="bg-surface border-b border-border px-4 py-3">
                    <p className="text-xs font-display uppercase tracking-wider text-muted mb-1">🇺🇸 Inglés Formal (SAE)</p>
                    <p className="text-foreground text-sm leading-relaxed">
                      {payload.formal_translation.split("|")[0].replace(/^Formal:/i, "").trim()}
                    </p>
                  </div>
                  {/* Row 3: Spanish */}
                  <div className="bg-background px-4 py-3">
                    <p className="text-xs font-display uppercase tracking-wider text-muted mb-1">🇲🇽 En Español</p>
                    <p className="text-foreground text-sm leading-relaxed">
                      {(payload.formal_translation.split("|")[1] || "").replace(/^Español:/i, "").trim()}
                    </p>
                  </div>
                </div>

                {/* ── Vocabulary breakdown ── */}
                <div className="space-y-2">
                  <p className="text-xs text-muted uppercase tracking-wider font-display px-1">Desglose de Vocabulario</p>
                  {payload.breakdown.map((item) => (
                    <div key={item.abbr} className="flex items-start gap-3 bg-surface border border-border rounded-lg px-4 py-3">
                      <span className="font-display text-accent uppercase text-sm w-28 flex-shrink-0">{item.abbr}</span>
                      <span className="text-foreground text-sm">{item.meaning}</span>
                    </div>
                  ))}
                </div>

                {/* ── Grammar notes ── */}
                {payload.grammar_notes.length > 0 && (
                  <Card>
                    <p className="text-xs text-muted uppercase tracking-wider font-display mb-3">Nota Gramatical</p>
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
                <Button variant="primary" size="md" className="w-full" onClick={() => setReadingPhase("match")}>
                  Practicar Vocabulario →
                </Button>
              </>
            )}

            {readingPhase === "match" && (
              <>
                <VocabularyMatch 
                  items={payload.breakdown} 
                  onComplete={() => {
                    if (!isReview) saveProgress(100);
                  }} 
                />
                {isReview && (
                  <div className="mt-4 p-3 bg-green-900/20 border border-green-700 rounded-xl text-center">
                    <p className="text-green-400 font-display uppercase text-sm">✓ Already Completed</p>
                  </div>
                )}
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
                <p className="text-xs text-muted uppercase tracking-wider font-display mb-2">🎵 Fill in the blanks</p>
                <FillInBlank
                  transcript={buildTranscript(payload.exercise_text)}
                  blanks={buildBlankSlots(payload.blanks)}
                  storageKey={`drillingo_ans_${lessonId}_listening`}
                  isReview={isReview}
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

        {/* ── WRITING — Smart local evaluation ── */}
        {currentModule === "writing" && payload.module_type === "writing" && (
          <WritingModule payload={payload} onComplete={saveProgress} submitting={submitting} isReview={isReview} lessonId={lessonId as string} />
        )}

        {/* ── SPEAKING — Live Block Feedback via Gemini Audio ── */}
        {currentModule === "speaking" && payload.module_type === "speaking" && (
          <Card>
            <p className="text-xs text-muted uppercase tracking-wider font-display mb-3">🎙️ Live Block Feedback</p>

            {/* Phonetic tips */}
            {payload.phonetic_tips.length > 0 && (
              <div className="mb-4 space-y-1">
                <p className="text-xs text-muted uppercase tracking-wider font-display mb-2">Phonetic Tips</p>
                {payload.phonetic_tips.map((tip, i) => (
                  <div key={i} className="flex gap-2 text-sm">
                    <span className="text-accent flex-shrink-0">•</span>
                    <span className="text-foreground">{tip}</span>
                  </div>
                ))}
              </div>
            )}

            <SpeakingRecorder
              targetPhrase={payload.target_phrase}
              level={lesson.level_band}
              onComplete={(result) => {
                const avg = Math.round((result.pronunciation_score + result.fluency_score) / 2);
                saveProgress(avg);
              }}
            />
          </Card>
        )}
      </div>
      
      {/* Next Module Action Area */}
      {isReview && (
        <div className="max-w-2xl mx-auto pt-6 pb-12">
          <Button 
            variant="primary" 
            size="md" 
            className="w-full text-lg py-4 shadow-lg shadow-accent/20"
            onClick={() => {
              if (nextModule) router.push(`/learn/${lessonId}/${nextModule}`);
              else router.push("/learn");
            }}
          >
            {isLastModule ? "Finish Lesson →" : `Continue to ${nextModule?.toUpperCase()} →`}
          </Button>
        </div>
      )}
    </>
  );
}
