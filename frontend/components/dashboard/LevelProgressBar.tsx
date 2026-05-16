"use client";

interface LevelProgressBarProps {
  levelBand: "B1" | "B2" | "C1";
  xpTotal: number;
}

const LEVELS = ["B1", "B2", "C1"] as const;
const XP_THRESHOLDS: Record<string, number> = {
  B1: 0,
  B2: 500,
  C1: 2000,
};
const XP_MAX = 2000;

export default function LevelProgressBar({ levelBand, xpTotal }: LevelProgressBarProps) {
  const currentThreshold = XP_THRESHOLDS[levelBand] ?? 0;
  const nextLevel = LEVELS[LEVELS.indexOf(levelBand as typeof LEVELS[number]) + 1];
  const nextThreshold = nextLevel ? XP_THRESHOLDS[nextLevel] : XP_MAX;

  // Progress within current level band
  const rangeSize = nextThreshold - currentThreshold;
  const progressInRange = Math.min(xpTotal - currentThreshold, rangeSize);
  const pct = rangeSize > 0 ? Math.round((progressInRange / rangeSize) * 100) : 100;

  return (
    // Req 9.1: level progression bar B1 → B2 → C1
    <div className="bg-surface border border-border rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-display text-sm uppercase tracking-wider text-muted">
          Level Progress
        </h3>
        <span className="font-display text-accent text-lg">{xpTotal} XP</span>
      </div>

      {/* Level markers */}
      <div className="flex justify-between mb-2">
        {LEVELS.map((lvl) => (
          <span
            key={lvl}
            className={[
              "font-display text-sm uppercase",
              lvl === levelBand
                ? "text-accent"
                : LEVELS.indexOf(lvl) < LEVELS.indexOf(levelBand as typeof LEVELS[number])
                ? "text-green-400"
                : "text-muted",
            ].join(" ")}
          >
            {lvl}
          </span>
        ))}
      </div>

      {/* Progress bar */}
      <div className="w-full bg-border rounded-full h-3 overflow-hidden">
        <div
          className="h-full bg-accent rounded-full transition-all duration-500"
          style={{ width: `${pct}%` }}
          role="progressbar"
          aria-valuenow={pct}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`Level progress: ${pct}%`}
        />
      </div>

      {nextLevel && (
        <p className="text-muted text-xs mt-2 text-right">
          {nextThreshold - xpTotal} XP to {nextLevel}
        </p>
      )}
    </div>
  );
}
