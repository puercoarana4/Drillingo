"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import { api } from "@/lib/api";

interface Lesson {
  id: string;
  title: string;
  dialect_segment: "east_coast" | "midwest";
  level_band: string;
  day_order: number;
  audio_url: string;
}

type DialectFilter = "all" | "east_coast" | "midwest";

export default function LessonsPage() {
  const router = useRouter();
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<DialectFilter>("all");

  useEffect(() => {
    api.get<Lesson[]>("/api/content/lessons")
      .then(setLessons)
      .catch(() => router.push("/login"))
      .finally(() => setLoading(false));
  }, [router]);

  const filtered = lessons.filter((l) =>
    filter === "all" ? true : l.dialect_segment === filter
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin h-8 w-8 border-2 border-accent border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="font-display text-3xl uppercase text-foreground tracking-wider mb-6">
        Lessons
      </h1>

      {/* Dialect filter */}
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

      {filtered.length === 0 ? (
        <Card className="text-center py-12">
          <p className="text-muted">No lessons available yet.</p>
        </Card>
      ) : (
        <div className="space-y-3">
          {filtered.map((lesson) => (
            <Card key={lesson.id} className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <span className="font-display text-2xl text-muted w-8 text-center">
                  {lesson.day_order}
                </span>
                <div>
                  <h3 className="font-display text-lg uppercase text-foreground">
                    {lesson.title}
                  </h3>
                  <div className="flex gap-2 mt-1">
                    <Badge variant={lesson.dialect_segment}>
                      {lesson.dialect_segment === "east_coast" ? "East Coast" : "Midwest"}
                    </Badge>
                    <Badge variant="muted">{lesson.level_band}</Badge>
                  </div>
                </div>
              </div>
              <div className="flex gap-2 flex-shrink-0">
                <Link href={`/modules/reading/${lesson.id}`}>
                  <Button variant="secondary" size="sm">Read</Button>
                </Link>
                <Link href={`/modules/listening/${lesson.id}`}>
                  <Button variant="secondary" size="sm">Listen</Button>
                </Link>
                <Link href={`/modules/writing/${lesson.id}`}>
                  <Button variant="primary" size="sm">Write</Button>
                </Link>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
