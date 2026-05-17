"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import StreakBadge from "./StreakBadge";
import { removeToken } from "@/lib/auth";

const navLinks = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/learn", label: "Learn" },
  { href: "/practice", label: "Practice" },
  { href: "/vocabulary", label: "Vocab" },
];

interface NavbarProps {
  currentStreak?: number;
}

export default function Navbar({ currentStreak = 0 }: NavbarProps) {
  const pathname = usePathname();
  const router = useRouter();

  function handleLogout() {
    // Clear JWT from localStorage and cookie
    removeToken();
    document.cookie = "drillingo_token=; path=/; max-age=0; SameSite=Lax";
    router.push("/login");
  }

  return (
    <nav
      className="sticky top-0 z-50 bg-surface border-b border-border"
      aria-label="Main navigation"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">
          {/* Logo */}
          <Link
            href="/dashboard"
            className="font-display text-xl sm:text-2xl uppercase tracking-widest text-accent hover:text-red-400 transition-colors flex-shrink-0"
          >
            Drillingo
          </Link>

          {/* Desktop Nav links */}
          <div className="hidden sm:flex items-center gap-6">
            {navLinks.map((link) => {
              const isActive = pathname.startsWith(link.href);
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={[
                    "font-display text-sm uppercase tracking-wider transition-colors",
                    isActive
                      ? "text-accent border-b-2 border-accent pb-0.5"
                      : "text-muted hover:text-foreground",
                  ].join(" ")}
                >
                  {link.label}
                </Link>
              );
            })}
          </div>

          {/* Right side: streak + logout */}
          <div className="flex items-center gap-2 sm:gap-4 flex-shrink-0">
            <StreakBadge currentStreak={currentStreak} />
            <button
              onClick={handleLogout}
              className="flex items-center gap-1 font-display text-[10px] sm:text-xs uppercase tracking-wider text-muted hover:text-accent transition-colors border border-border hover:border-accent rounded px-2 py-1.5 sm:px-3"
              aria-label="Log out"
            >
              <svg className="w-3 h-3 hidden sm:block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Log Out
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Nav links (bottom row) */}
      <div className="sm:hidden flex overflow-x-auto whitespace-nowrap justify-around gap-2 px-2 py-2 border-t border-border bg-surface shadow-sm">
        {navLinks.map((link) => {
          const isActive = pathname.startsWith(link.href);
          return (
            <Link
              key={link.href}
              href={link.href}
              className={[
                "font-display text-xs uppercase tracking-wider transition-colors px-3 py-1.5 rounded-md",
                isActive
                  ? "bg-accent/10 text-accent font-bold"
                  : "text-muted hover:text-foreground",
              ].join(" ")}
            >
              {link.label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
