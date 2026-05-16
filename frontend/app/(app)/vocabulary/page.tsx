"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import { api } from "@/lib/api";

interface VocabItem {
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

type DialectFilter = "all" | "east_coast" | "midwest";

export default function VocabularyPage() {
  const router = useRouter();
  const [items, setItems] = useState<VocabItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<DialectFilter>("all");

  useEffect(() => {
    // Req 11.2: show all mastered vocabulary items
    api.get<VocabItem[]>("/api/progress/vocabulary")
      .then((data) => setItems(data.filter((v) => v.mastered)))
      .catch(() => router.push("/login"))
      .finally(() => setLoading(false));
  }, [router]);

  // Req 11.5: filter by dialect_segment
  const filtered = items.filter((item) => {
    if (filter === "all") return true;
    return item.dialect_segment === filter;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin h-8 w-8 border-2 border-accent border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display text-3xl uppercase text-foreground tracking-wider">
            Vocab Mastered
          </h1>
          <p className="text-muted text-sm mt-1">
            {items.length} term{items.length !== 1 ? "s" : ""} in your collection
          </p>
        </div>
      </div>

      {/* Dialect filter toggles — Req 11.5 */}
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

      {/* Vocabulary grid */}
      {filtered.length === 0 ? (
        <Card className="text-center py-12">
          <p className="text-4xl mb-3">📚</p>
          <p className="font-display text-xl uppercase text-muted">
            {filter === "all"
              ? "No mastered vocab yet"
              : `No ${filter === "east_coast" ? "East Coast" : "Midwest"} vocab mastered yet`}
          </p>
          <p className="text-muted text-sm mt-2">
            Answer a term correctly 3 times to master it.
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((item) => (
            <VocabCard key={item.vocabulary_item_id} item={item} />
          ))}
        </div>
      )}
    </div>
  );
}

function VocabCard({ item }: { item: VocabItem }) {
  const [expanded, setExpanded] = useState(false);

  return (
    // Req 11.3: show term, definition, dialect_segment, example
    <Card
      accent
      className="cursor-pointer hover:border-accent/60 transition-colors"
    >
      <div className="flex items-start justify-between mb-2">
        <h3 className="font-display text-xl uppercase text-foreground">
          {item.term}
        </h3>
        {item.dialect_segment && (
          <Badge variant={item.dialect_segment}>
            {item.dialect_segment === "east_coast" ? "NYC" : "CHI"}
          </Badge>
        )}
      </div>

      <p className="text-muted text-sm mb-3">{item.definition}</p>

      {item.example_sentence && (
        <button
          onClick={() => setExpanded((e) => !e)}
          className="text-xs text-accent hover:underline font-display uppercase tracking-wider"
        >
          {expanded ? "Hide example" : "Show example"}
        </button>
      )}

      {expanded && item.example_sentence && (
        <p className="text-foreground text-sm italic mt-2 border-l-2 border-accent pl-3">
          &ldquo;{item.example_sentence}&rdquo;
        </p>
      )}

      <div className="flex items-center justify-between mt-3 pt-3 border-t border-border">
        <span className="text-xs text-muted">
          ✓ {item.correct_count} correct
        </span>
        {item.level_band && (
          <span className="text-xs text-muted font-display">{item.level_band}</span>
        )}
      </div>
    </Card>
  );
}
