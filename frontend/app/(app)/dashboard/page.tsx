"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import StreakDisplay from "@/components/dashboard/StreakDisplay";
import LevelProgressBar from "@/components/dashboard/LevelProgressBar";
import RadarChart from "@/components/dashboard/RadarChart";
import OralHistoryChart from "@/components/dashboard/OralHistoryChart";
import Card from "@/components/ui/Card";
import { api } from "@/lib/api";

interface DashboardData {
  user_id: string;
  level_band: "B1" | "B2" | "C1";
  xp_total: number;
  current_streak: number;
  longest_streak: number;
  radar: {
    reading: number;
    listening: number;
    writing: number;
    speaking: number;
    vocabulary: number;
  };
  vocabulary_mastered_count: number;
  oral_history: Array<{
    submitted_at: string;
    fluency_score: number;
    pronunciation_score: number;
  }>;
}

export default function DashboardPage() {
  const router = useRouter();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Req 9.5: single API call for all metrics
    api.get<DashboardData>("/api/dashboard")
      .then(setData)
      .catch((err) => {
        // 401 → session expired, redirect to login
        if (err?.status === 401) {
          router.push("/login");
        } else {
          setError(
            "Could not load dashboard. Make sure the backend is reachable.\n" +
            `(${err?.detail ?? err?.message ?? "Network error"})`
          );
        }
      })
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin h-10 w-10 border-2 border-accent border-t-transparent rounded-full" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4 text-center">
        <p className="text-accent font-display text-xl uppercase">Backend Unreachable</p>
        <p className="text-muted text-sm max-w-md whitespace-pre-line">{error}</p>
        <p className="text-muted text-xs">
          Set <code className="text-accent">NEXT_PUBLIC_API_URL</code> in{" "}
          <code className="text-accent">frontend/.env.local</code> to your Railway URL.
        </p>
        <button
          onClick={() => { setError(null); setLoading(true); api.get<DashboardData>("/api/dashboard").then(setData).catch((e) => setError(e?.detail ?? "Error")).finally(() => setLoading(false)); }}
          className="px-4 py-2 bg-accent text-white rounded font-display uppercase text-sm hover:bg-red-700 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-6">
      {/* Page title */}
      <h1 className="font-display text-3xl uppercase text-foreground tracking-wider">
        Dashboard
      </h1>

      {/* Streak — Req 9.6 */}
      <StreakDisplay
        currentStreak={data.current_streak}
        longestStreak={data.longest_streak}
      />

      {/* Level progress — Req 9.1 */}
      <LevelProgressBar levelBand={data.level_band} xpTotal={data.xp_total} />

      {/* Two-column grid for radar + vocab count */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Radar chart — Req 9.2 */}
        <RadarChart scores={data.radar} />

        {/* Vocabulary mastered — Req 9.3 */}
        <Card className="flex flex-col items-center justify-center text-center">
          <p className="text-muted text-xs uppercase tracking-wider font-display mb-2">
            Slang Mastered
          </p>
          <p className="font-display text-6xl text-accent mb-1">
            {data.vocabulary_mastered_count}
          </p>
          <p className="text-muted text-sm">vocabulary items</p>
        </Card>
      </div>

      {/* Oral history line chart — Req 9.4 */}
      <OralHistoryChart data={data.oral_history} />
    </div>
  );
}
