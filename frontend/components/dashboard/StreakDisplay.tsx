"use client";

interface StreakDisplayProps {
  currentStreak: number;
  longestStreak: number;
}

export default function StreakDisplay({ currentStreak, longestStreak }: StreakDisplayProps) {
  return (
    // Req 9.6: current_streak and longest_streak displayed prominently
    <div className="bg-surface border border-border rounded-xl p-6 flex items-center gap-6">
      <div className="text-center">
        <span className="text-5xl" role="img" aria-label="streak fire">🔥</span>
      </div>
      <div className="flex gap-8">
        <div>
          <p className="text-muted text-xs uppercase tracking-wider font-display mb-1">
            Current Streak
          </p>
          <p className="font-display text-4xl text-accent">{currentStreak}</p>
          <p className="text-muted text-xs">days</p>
        </div>
        <div>
          <p className="text-muted text-xs uppercase tracking-wider font-display mb-1">
            Best Streak
          </p>
          <p className="font-display text-4xl text-foreground">{longestStreak}</p>
          <p className="text-muted text-xs">days</p>
        </div>
      </div>
    </div>
  );
}
