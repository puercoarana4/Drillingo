import React from "react";

type BadgeVariant = "accent" | "muted" | "east_coast" | "midwest";

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  className?: string;
}

const variantClasses: Record<BadgeVariant, string> = {
  accent: "bg-accent text-white",
  muted: "bg-border text-muted",
  // Dialect badges (Req 3.4)
  east_coast: "bg-blue-900 text-blue-200",
  midwest: "bg-orange-900 text-orange-200",
};

export default function Badge({
  children,
  variant = "muted",
  className = "",
}: BadgeProps) {
  return (
    <span
      className={[
        "inline-flex items-center px-2.5 py-0.5 rounded text-xs font-display uppercase tracking-wider",
        variantClasses[variant],
        className,
      ].join(" ")}
    >
      {children}
    </span>
  );
}
