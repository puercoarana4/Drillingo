"use client";

import { useState, useEffect } from "react";
import Button from "@/components/ui/Button";

interface BreakdownItem {
  abbr: string;
  meaning: string;
}

export default function VocabularyMatch({
  items,
  onComplete,
}: {
  items: BreakdownItem[];
  onComplete: () => void;
}) {
  const [terms, setTerms] = useState<{ id: string; text: string }[]>([]);
  const [meanings, setMeanings] = useState<{ id: string; text: string }[]>([]);
  
  const [selectedTerm, setSelectedTerm] = useState<string | null>(null);
  const [selectedMeaning, setSelectedMeaning] = useState<string | null>(null);
  const [matchedPairs, setMatchedPairs] = useState<Set<string>>(new Set());
  const [errorPair, setErrorPair] = useState<{ term: string; meaning: string } | null>(null);

  useEffect(() => {
    // Shuffle the items for the game
    const shuffledTerms = [...items].sort(() => Math.random() - 0.5).map((i) => ({ id: i.abbr, text: i.abbr }));
    const shuffledMeanings = [...items].sort(() => Math.random() - 0.5).map((i) => ({ id: i.abbr, text: i.meaning }));
    setTerms(shuffledTerms);
    setMeanings(shuffledMeanings);
  }, [items]);

  useEffect(() => {
    if (selectedTerm && selectedMeaning) {
      if (selectedTerm === selectedMeaning) {
        // Match!
        setMatchedPairs((prev) => {
          const next = new Set(prev);
          next.add(selectedTerm);
          return next;
        });
        setSelectedTerm(null);
        setSelectedMeaning(null);
      } else {
        // Mismatch
        setErrorPair({ term: selectedTerm, meaning: selectedMeaning });
        setTimeout(() => {
          setErrorPair(null);
          setSelectedTerm(null);
          setSelectedMeaning(null);
        }, 800);
      }
    }
  }, [selectedTerm, selectedMeaning]);

  useEffect(() => {
    if (matchedPairs.size === items.length && items.length > 0) {
      setTimeout(onComplete, 1000);
    }
  }, [matchedPairs, items, onComplete]);

  return (
    <div className="bg-surface border border-border rounded-xl p-5">
      <p className="text-xs text-muted uppercase tracking-wider font-display mb-4 text-center">
        Match the words to their meanings
      </p>
      
      <div className="grid grid-cols-2 gap-4">
        {/* Terms Column */}
        <div className="space-y-3">
          {terms.map((t) => {
            const isMatched = matchedPairs.has(t.id);
            const isSelected = selectedTerm === t.id;
            const isError = errorPair?.term === t.id;
            return (
              <button
                key={`term-${t.id}`}
                disabled={isMatched}
                onClick={() => setSelectedTerm(isSelected ? null : t.id)}
                className={[
                  "w-full px-4 py-3 rounded-lg border-2 transition-all duration-200 text-sm font-display uppercase",
                  isMatched ? "border-green-700 bg-green-900/20 text-green-400 opacity-50 cursor-not-allowed" :
                  isError ? "border-red-500 bg-red-900/20 text-red-400 animate-pulse" :
                  isSelected ? "border-accent bg-accent/20 text-accent" :
                  "border-border bg-background text-foreground hover:border-muted",
                ].join(" ")}
              >
                {t.text}
              </button>
            );
          })}
        </div>

        {/* Meanings Column */}
        <div className="space-y-3">
          {meanings.map((m) => {
            const isMatched = matchedPairs.has(m.id);
            const isSelected = selectedMeaning === m.id;
            const isError = errorPair?.meaning === m.id;
            return (
              <button
                key={`meaning-${m.id}`}
                disabled={isMatched}
                onClick={() => setSelectedMeaning(isSelected ? null : m.id)}
                className={[
                  "w-full px-4 py-3 rounded-lg border-2 transition-all duration-200 text-sm",
                  isMatched ? "border-green-700 bg-green-900/20 text-green-400 opacity-50 cursor-not-allowed" :
                  isError ? "border-red-500 bg-red-900/20 text-red-400 animate-pulse" :
                  isSelected ? "border-accent bg-accent/20 text-accent" :
                  "border-border bg-background text-foreground hover:border-muted",
                ].join(" ")}
              >
                {m.text}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
