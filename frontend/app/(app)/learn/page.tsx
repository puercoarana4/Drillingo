"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

// ── Types ─────────────────────────────────────────────────────────────────────

interface Lesson {
  id: string;
  title: string;
  dialect_segment: "east_coast" | "midwest";
  level_band: string;
  day_order: number;
}

interface ProgressRecord {
  lesson_id: string;
  module_type: "reading" | "listening" | "writing" | "speaking";
  score: number;
}

type NodeStatus = "completed" | "active" | "locked";

interface LessonNode {
  lesson: Lesson;
  status: NodeStatus;
  completedModules: Set<string>;
}

// ── Helpers ───────────────────────────────────────────────────────────────────

const REQUIRED_MODULES = ["reading", "listening", "writing", "speaking"] as const;

function buildNodes(lessons: Lesson[], progress: ProgressRecord[]): LessonNode[] {
  // Group progress by lesson_id
  const progressMap = new Map<string, Set<string>>();
  for (const p of progress) {
    if (!progressMap.has(p.lesson_id)) progressMap.set(p.lesson_id, new Set());
    progressMap.get(p.lesson_id)!.add(p.module_type);
  }

  const nodes: LessonNode[] = [];
  let previousCompleted = true; // first node always unlocked

  for (const lesson of lessons) {
    const completedModules = progressMap.get(lesson.id) ?? new Set<string>();
    const isFullyComplete = REQUIRED_MODULES.every((m) => completedModules.has(m));

    let status: NodeStatus;
    if (isFullyComplete) {
      status = "completed";
    } else if (previousCompleted) {
      status = "active";
    } else {
      status = "locked";
    }

    nodes.push({ lesson, status, completedModules });
    previousCompleted = isFullyComplete;
  }

  return nodes;
}

function getDialectColor(dialect: "east_coast" | "midwest") {
  return dialect === "east_coast" ? "#3B82F6" : "#F97316";
}

function getDialectLabel(dialect: "east_coast" | "midwest") {
  return dialect === "east_coast" ? "East Coast" : "Midwest";
}

// ── Node Component ────────────────────────────────────────────────────────────

function LessonNodeCard({
  node,
  index,
  onStart,
  justUnlocked,
}: {
  node: LessonNode;
  index: number;
  onStart: (lessonId: string) => void;
  justUnlocked: boolean;
}) {
  const { lesson, status, completedModules } = node;
  const isLeft = index % 2 === 0;
  const dialectColor = getDialectColor(lesson.dialect_segment);

  const moduleIcons = {
    reading: "📖",
    listening: "🎵",
    writing: "✍️",
    speaking: "🎙️",
  };

  return (
    <div className={`flex items-center gap-4 ${isLeft ? "flex-row" : "flex-row-reverse"}`}>
      {/* Connector line placeholder for alignment */}
      <div className="w-16 flex-shrink-0" />

      {/* Node card */}
      <div
        className={[
          "flex-1 max-w-sm rounded-2xl p-5 border-2 transition-all duration-500",
          status === "completed"
            ? "border-green-600 bg-green-900/20"
            : status === "active"
            ? "border-accent bg-surface shadow-lg shadow-accent/20"
            : "border-border bg-surface/50 opacity-50",
          justUnlocked ? "animate-pulse" : "",
        ].join(" ")}
      >
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span
                className="text-xs font-display uppercase tracking-wider px-2 py-0.5 rounded"
                style={{ backgroundColor: `${dialectColor}22`, color: dialectColor }}
              >
                {getDialectLabel(lesson.dialect_segment)}
              </span>
              <span className="text-xs text-muted font-display">{lesson.level_band}</span>
            </div>
            <h3
              className={[
                "font-display text-base uppercase tracking-wide leading-tight",
                status === "locked" ? "text-muted" : "text-foreground",
              ].join(" ")}
            >
              {lesson.title}
            </h3>
          </div>

          {/* Status icon */}
          <div className="flex-shrink-0 ml-2">
            {status === "completed" && (
              <div className="w-10 h-10 rounded-full bg-green-600 flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              </div>
            )}
            {status === "active" && (
              <div className="w-10 h-10 rounded-full bg-accent flex items-center justify-center animate-bounce">
                <span className="text-white font-display text-sm">{index + 1}</span>
              </div>
            )}
            {status === "locked" && (
              <div className="w-10 h-10 rounded-full bg-border flex items-center justify-center">
                <svg className="w-5 h-5 text-muted" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 1C8.676 1 6 3.676 6 7v1H4v15h16V8h-2V7c0-3.324-2.676-6-6-6zm0 2c2.276 0 4 1.724 4 4v1H8V7c0-2.276 1.724-4 4-4zm0 9a2 2 0 110 4 2 2 0 010-4z" />
                </svg>
              </div>
            )}
          </div>
        </div>

        {/* Module progress pills */}
        <div className="flex gap-2 mb-4">
          {REQUIRED_MODULES.map((mod) => (
            <div
              key={mod}
              className={[
                "flex items-center gap-1 px-2 py-1 rounded-full text-xs font-display uppercase",
                completedModules.has(mod)
                  ? "bg-green-900/40 text-green-400"
                  : status === "active"
                  ? "bg-border text-muted"
                  : "bg-border/50 text-muted/50",
              ].join(" ")}
            >
              <span>{moduleIcons[mod]}</span>
              <span>{mod}</span>
              {completedModules.has(mod) && <span>✓</span>}
            </div>
          ))}
        </div>

        {/* CTA */}
        {status === "active" && (
          <button
            onClick={() => onStart(lesson.id)}
            className="w-full py-3 rounded-xl bg-accent text-white font-display uppercase tracking-wider text-sm hover:bg-red-700 active:bg-red-800 transition-colors"
          >
            {completedModules.size === 0
              ? "Start Lesson"
              : completedModules.size < 3
              ? `Continue (${completedModules.size}/3)`
              : "Review"}
          </button>
        )}
        {status === "completed" && (
          <button
            onClick={() => onStart(lesson.id)}
            className="w-full py-2 rounded-xl border border-green-600 text-green-400 font-display uppercase tracking-wider text-xs hover:bg-green-900/20 transition-colors"
          >
            Review
          </button>
        )}
        {status === "locked" && (
          <div className="w-full py-2 text-center text-muted font-display uppercase tracking-wider text-xs">
            Complete previous lesson to unlock
          </div>
        )}
      </div>
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function LearnPage() {
  const router = useRouter();
  const [nodes, setNodes] = useState<LessonNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [justUnlockedId, setJustUnlockedId] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      api.get<Lesson[]>("/api/content/lessons"),
      api.get<ProgressRecord[]>("/api/progress/lessons").catch(() => [] as ProgressRecord[]),
    ])
      .then(([lessons, progress]) => {
        const sorted = [...lessons].sort((a, b) => a.day_order - b.day_order);
        setNodes(buildNodes(sorted, progress));
      })
      .catch(() => router.push("/login"))
      .finally(() => setLoading(false));
  }, [router]);

  function handleStart(lessonId: string) {
    const node = nodes.find((n) => n.lesson.id === lessonId);
    if (!node || node.status === "locked") return;

    // Find the next incomplete module in order
    const nextModule = REQUIRED_MODULES.find((m) => !node.completedModules.has(m));
    if (nextModule) {
      router.push(`/learn/${lessonId}/${nextModule}`);
    } else {
      // All done — go to reading for review
      router.push(`/learn/${lessonId}/reading`);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin h-10 w-10 border-2 border-accent border-t-transparent rounded-full" />
      </div>
    );
  }

  const completedCount = nodes.filter((n) => n.status === "completed").length;
  const totalCount = nodes.length;

  return (
    <div className="max-w-lg mx-auto pb-16">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="font-display text-4xl uppercase text-foreground tracking-widest mb-2">
          Your Path
        </h1>
        <p className="text-muted text-sm">
          {completedCount} / {totalCount} lessons complete
        </p>
        {/* Overall progress bar */}
        <div className="mt-3 h-2 bg-border rounded-full overflow-hidden">
          <div
            className="h-full bg-accent rounded-full transition-all duration-700"
            style={{ width: totalCount > 0 ? `${(completedCount / totalCount) * 100}%` : "0%" }}
          />
        </div>
      </div>

      {/* Path */}
      <div className="relative space-y-6">
        {/* Vertical line */}
        <div className="absolute left-1/2 top-0 bottom-0 w-0.5 bg-border -translate-x-1/2 z-0" />

        {nodes.map((node, i) => (
          <div key={node.lesson.id} className="relative z-10">
            {/* Connector dot */}
            <div
              className={[
                "absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-4 h-4 rounded-full border-2 z-20",
                node.status === "completed"
                  ? "bg-green-600 border-green-600"
                  : node.status === "active"
                  ? "bg-accent border-accent"
                  : "bg-background border-border",
              ].join(" ")}
            />
            <LessonNodeCard
              node={node}
              index={i}
              onStart={handleStart}
              justUnlocked={justUnlockedId === node.lesson.id}
            />
          </div>
        ))}

        {/* End of path */}
        {totalCount > 0 && (
          <div className="relative z-10 flex justify-center pt-4">
            <div className="text-center">
              <div className="w-16 h-16 rounded-full bg-border flex items-center justify-center mx-auto mb-2">
                <span className="text-2xl">🏆</span>
              </div>
              <p className="text-muted text-xs font-display uppercase tracking-wider">
                More coming soon
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
