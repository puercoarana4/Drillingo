"use client";

interface StreakBadgeProps {
  currentStreak: number;
}

export default function StreakBadge({ currentStreak }: StreakBadgeProps) {
  return (
    // Req 8.4: fire icon + current_streak displayed prominently
    <div className="flex items-center gap-1.5 bg-surface border border-border rounded-full px-3 py-1.5">
      <span className="text-xl" role="img" aria-label="streak fire">
        🔥
      </span>
      <span className="font-display text-foreground text-sm uppercase tracking-wider">
        {currentStreak}
        <span className="text-muted ml-1 text-xs normal-case font-body">day streak</span>
      </span>
    </div>
  );
}
