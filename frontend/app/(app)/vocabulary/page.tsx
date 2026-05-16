"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import { api } from "@/lib/api";

// ── Types ─────────────────────────────────────────────────────────────────────

interface VocabItem {
  id: string;
  term: string;
  definition: string;
  example_sentence: string | null;
  dialect_segment: "east_coast" | "midwest" | null;
  level_band: string | null;
  created_at: string;
}

interface UserVocabProgress {
  vocabulary_item_id: string;
  term: string;
  definition: string;
  example_sentence: string | null;
  dialect_segment: "east_coast" | "midwest" | null;
  level_band: string | null;
  mastered: boolean;
  correct_count: number;
  last_reviewed_at: string | null;
}

type View = "dictionary" | "flashcards";
type DialectFilter = "all" | "east_coast" | "midwest";
type FlashcardSide = "term" | "definition";

// ── Flashcard Component ───────────────────────────────────────────────────────

function FlashcardMode({
  items,
  onClose,
  onInteraction,
}: {
  items: VocabItem[];
  onClose: () => void;
  onInteraction: (itemId: string, correct: boolean) => void;
}) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [side, setSide] = useState<FlashcardSide>("term");
  const [answered, setAnswered] = useState(false);
  const [sessionResults, setSessionResults] = useState<{ correct: number; wrong: number }>({ correct: 0, wrong: 0 });
  const [done, setDone] = useState(false);

  const current = items[currentIndex];

  function handleFlip() {
    setSide((s) => (s === "term" ? "definition" : "term"));
  }

  function handleAnswer(correct: boolean) {
    if (answered) return;
    setAnswered(true);
    onInteraction(current.id, correct);
    setSessionResults((prev) => ({
      correct: prev.correct + (correct ? 1 : 0),
      wrong: prev.wrong + (correct ? 0 : 1),
    }));
  }

  function handleNext() {
    if (currentIndex + 1 >= items.length) {
      setDone(true);
      return;
    }
    setCurrentIndex((i) => i + 1);
    setSide("term");
    setAnswered(false);
  }

  if (done) {
    const total = sessionResults.correct + sessionResults.wrong;
    const pct = total > 0 ? Math.round((sessionResults.correct / total) * 100) : 0;
    return (
      <div className="max-w-md mx-auto text-center space-y-6 py-8">
        <div className="text-6xl mb-2">
          {pct >= 80 ? "🔥" : pct >= 60 ? "💪" : "📚"}
        </div>
        <h2 className="font-display text-3xl uppercase text-accent">Session Complete</h2>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-green-900/20 border border-green-700 rounded-xl p-4 text-center">
            <p className="text-xs text-green-400 uppercase tracking-wider font-display mb-1">Correct</p>
            <p className="font-display text-4xl text-green-400">{sessionResults.correct}</p>
          </div>
          <div className="bg-accent/10 border border-accent/30 rounded-xl p-4 text-center">
            <p className="text-xs text-accent uppercase tracking-wider font-display mb-1">Wrong</p>
            <p className="font-display text-4xl text-accent">{sessionResults.wrong}</p>
          </div>
        </div>
        <p className="text-muted text-sm">
          {pct >= 80 ? "You're killing it. Keep drilling." : pct >= 60 ? "Getting there. Run it back." : "Keep studying — you'll get it."}
        </p>
        <div className="flex gap-3 justify-center">
          <Button variant="secondary" size="md" onClick={() => {
            setCurrentIndex(0);
            setSide("term");
            setAnswered(false);
            setDone(false);
            setSessionResults({ correct: 0, wrong: 0 });
          }}>
            Run it back
          </Button>
          <Button variant="primary" size="md" onClick={onClose}>
            Back to Dictionary
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <button onClick={onClose} className="text-muted hover:text-foreground transition-colors text-sm font-display uppercase tracking-wider">
          ← Dictionary
        </button>
        <span className="text-muted text-sm font-display">
          {currentIndex + 1} / {items.length}
        </span>
      </div>

      {/* Progress bar */}
      <div className="h-2 bg-border rounded-full overflow-hidden">
        <div
          className="h-full bg-accent rounded-full transition-all duration-300"
          style={{ width: `${((currentIndex) / items.length) * 100}%` }}
        />
      </div>

      {/* Flashcard */}
      <div
        onClick={handleFlip}
        className="min-h-64 bg-surface border-2 border-border rounded-2xl p-8 flex flex-col items-center justify-center text-center cursor-pointer hover:border-accent transition-colors select-none"
      >
        <p className="text-xs text-muted uppercase tracking-wider font-display mb-4">
          {side === "term" ? "What does this mean?" : "Definition"}
        </p>

        {side === "term" ? (
          <>
            <h2 className="font-display text-4xl uppercase text-foreground mb-3">{current.term}</h2>
            {current.dialect_segment && (
              <Badge variant={current.dialect_segment}>
                {current.dialect_segment === "east_coast" ? "East Coast" : "Midwest"}
              </Badge>
            )}
            <p className="text-muted text-xs mt-4">Tap to reveal definition</p>
          </>
        ) : (
          <>
            <p className="text-foreground text-base leading-relaxed mb-4">{current.definition}</p>
            {current.example_sentence && (
              <p className="text-muted text-sm italic border-l-2 border-accent pl-3 text-left">
                &ldquo;{current.example_sentence}&rdquo;
              </p>
            )}
          </>
        )}
      </div>

      {/* Answer buttons — only show after flip */}
      {side === "definition" && !answered && (
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => handleAnswer(false)}
            className="py-4 rounded-xl border-2 border-accent/50 text-accent font-display uppercase tracking-wider text-sm hover:bg-accent/10 transition-colors"
          >
            ✗ Didn't know
          </button>
          <button
            onClick={() => handleAnswer(true)}
            className="py-4 rounded-xl border-2 border-green-600 text-green-400 font-display uppercase tracking-wider text-sm hover:bg-green-900/20 transition-colors"
          >
            ✓ Got it
          </button>
        </div>
      )}

      {answered && (
        <Button variant="primary" size="md" className="w-full" onClick={handleNext}>
          {currentIndex + 1 >= items.length ? "See Results" : "Next →"}
        </Button>
      )}

      {/* Session score */}
      <div className="flex justify-center gap-6 text-sm">
        <span className="text-green-400 font-display">✓ {sessionResults.correct}</span>
        <span className="text-accent font-display">✗ {sessionResults.wrong}</span>
      </div>
    </div>
  );
}

// ── Dictionary Card ───────────────────────────────────────────────────────────

function DictCard({ item, progress }: { item: VocabItem; progress?: UserVocabProgress }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className={[
      "rounded-2xl p-5 border-2 transition-colors",
      progress?.mastered ? "border-green-700 bg-green-900/10" : "border-border bg-surface",
    ].join(" ")}>
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2 flex-wrap">
          <h3 className="font-display text-xl uppercase text-foreground">{item.term}</h3>
          {progress?.mastered && <span className="text-green-400 text-xs font-display">✓ MASTERED</span>}
        </div>
        <div className="flex items-center gap-2 flex-shrink-0 ml-2">
          {item.dialect_segment && (
            <Badge variant={item.dialect_segment}>
              {item.dialect_segment === "east_coast" ? "NYC" : "CHI"}
            </Badge>
          )}
          {item.level_band && (
            <span className="text-xs text-muted font-display">{item.level_band}</span>
          )}
        </div>
      </div>

      <p className="text-muted text-sm leading-relaxed mb-3">{item.definition}</p>

      {item.example_sentence && (
        <>
          <button
            onClick={() => setExpanded((e) => !e)}
            className="text-xs text-accent hover:underline font-display uppercase tracking-wider"
          >
            {expanded ? "Hide example" : "Show example"}
          </button>
          {expanded && (
            <p className="text-foreground text-sm italic mt-2 border-l-2 border-accent pl-3">
              &ldquo;{item.example_sentence}&rdquo;
            </p>
          )}
        </>
      )}

      {progress && (
        <div className="flex items-center gap-3 mt-3 pt-3 border-t border-border">
          <span className="text-xs text-muted">
            {progress.correct_count}/3 correct
          </span>
          <div className="flex gap-1">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className={[
                  "w-4 h-1.5 rounded-full",
                  i < progress.correct_count ? "bg-green-500" : "bg-border",
                ].join(" ")}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function VocabularyPage() {
  const router = useRouter();
  const [allItems, setAllItems] = useState<VocabItem[]>([]);
  const [userProgress, setUserProgress] = useState<UserVocabProgress[]>([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<View>("dictionary");
  const [filter, setFilter] = useState<DialectFilter>("all");

  useEffect(() => {
    Promise.all([
      api.get<VocabItem[]>("/api/content/vocabulary"),
      api.get<UserVocabProgress[]>("/api/progress/vocabulary").catch(() => [] as UserVocabProgress[]),
    ])
      .then(([items, progress]) => {
        setAllItems(items);
        setUserProgress(progress);
      })
      .catch(() => router.push("/login"))
      .finally(() => setLoading(false));
  }, [router]);

  async function handleInteraction(itemId: string, correct: boolean) {
    try {
      await api.patch(`/api/progress/vocabulary/${itemId}?correct=${correct}`, {});
      // Refresh progress
      const updated = await api.get<UserVocabProgress[]>("/api/progress/vocabulary").catch(() => userProgress);
      setUserProgress(updated);
    } catch { /* non-fatal */ }
  }

  const progressMap = new Map(userProgress.map((p) => [p.vocabulary_item_id, p]));

  const filtered = allItems.filter((item) => {
    if (filter === "all") return true;
    return item.dialect_segment === filter;
  });

  const masteredCount = userProgress.filter((p) => p.mastered).length;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin h-8 w-8 border-2 border-accent border-t-transparent rounded-full" />
      </div>
    );
  }

  // Flashcard mode
  if (view === "flashcards") {
    const flashItems = filtered.length > 0 ? filtered : allItems;
    return (
      <div className="max-w-4xl mx-auto">
        <FlashcardMode
          items={flashItems}
          onClose={() => setView("dictionary")}
          onInteraction={handleInteraction}
        />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display text-3xl uppercase text-foreground tracking-wider">
            Slang Dictionary
          </h1>
          <p className="text-muted text-sm mt-1">
            {allItems.length} terms · {masteredCount} mastered
          </p>
        </div>
        <Button
          variant="primary"
          size="md"
          onClick={() => setView("flashcards")}
        >
          🃏 Flashcards
        </Button>
      </div>

      {/* Filters */}
      <div className="flex gap-2 mb-6">
        {(["all", "east_coast", "midwest"] as DialectFilter[]).map((d) => (
          <button
            key={d}
            onClick={() => setFilter(d)}
            className={[
              "px-4 py-2 rounded-full text-xs font-display uppercase tracking-wider transition-colors",
              filter === d
                ? "bg-accent text-white"
                : "bg-surface border border-border text-muted hover:text-foreground",
            ].join(" ")}
          >
            {d === "all" ? "All" : d === "east_coast" ? "East Coast" : "Midwest"}
          </button>
        ))}
      </div>

      {/* Stats bar */}
      {masteredCount > 0 && (
        <div className="flex items-center gap-3 mb-6 bg-surface border border-border rounded-xl px-4 py-3">
          <div className="flex gap-1">
            {allItems.slice(0, 6).map((item) => {
              const p = progressMap.get(item.id);
              return (
                <div
                  key={item.id}
                  className={["w-6 h-6 rounded-full flex items-center justify-center text-xs", p?.mastered ? "bg-green-600" : p?.correct_count ? "bg-yellow-700" : "bg-border"].join(" ")}
                  title={item.term}
                >
                  {p?.mastered ? "✓" : p?.correct_count || ""}
                </div>
              );
            })}
          </div>
          <p className="text-muted text-xs">
            {masteredCount}/{allItems.length} mastered — answer correctly 3× to master a term
          </p>
        </div>
      )}

      {/* Dictionary grid */}
      {filtered.length === 0 ? (
        <Card className="text-center py-12">
          <p className="text-4xl mb-3">📚</p>
          <p className="font-display text-xl uppercase text-muted">No terms found</p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {filtered.map((item) => (
            <DictCard
              key={item.id}
              item={item}
              progress={progressMap.get(item.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
