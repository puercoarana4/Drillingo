import React from "react";

type Variant = "primary" | "secondary" | "ghost";
type Size = "sm" | "md" | "lg";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
  children: React.ReactNode;
}

const variantClasses: Record<Variant, string> = {
  // Req 12.2: accent red for primary actions
  primary:
    "bg-accent text-white hover:bg-red-700 active:bg-red-800 focus-visible:ring-accent",
  secondary:
    "bg-surface text-foreground border border-border hover:border-accent hover:text-accent focus-visible:ring-accent",
  ghost:
    "bg-transparent text-foreground hover:bg-surface focus-visible:ring-accent",
};

const sizeClasses: Record<Size, string> = {
  sm: "px-4 py-2 text-sm min-h-[40px]",
  // Req 12.4: min height 48px for primary actions
  md: "px-6 py-3 text-base min-h-[48px]",
  lg: "px-8 py-4 text-lg min-h-[56px]",
};

export default function Button({
  variant = "primary",
  size = "md",
  loading = false,
  disabled,
  className = "",
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      disabled={disabled || loading}
      className={[
        // Req 12.4: uppercase text for primary actions
        "inline-flex items-center justify-center gap-2 rounded font-display",
        "uppercase tracking-wider transition-colors duration-150",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-background",
        "disabled:opacity-50 disabled:cursor-not-allowed",
        variantClasses[variant],
        sizeClasses[size],
        className,
      ].join(" ")}
      {...props}
    >
      {loading ? (
        <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
      ) : null}
      {children}
    </button>
  );
}
