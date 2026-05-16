import React from "react";

interface CardProps {
  children: React.ReactNode;
  className?: string;
  /** Adds a red accent left border */
  accent?: boolean;
}

export default function Card({ children, className = "", accent = false }: CardProps) {
  return (
    // Req 12.1: surface color #242424
    <div
      className={[
        "bg-surface rounded-lg p-6",
        accent ? "border-l-4 border-accent" : "border border-border",
        className,
      ].join(" ")}
    >
      {children}
    </div>
  );
}
