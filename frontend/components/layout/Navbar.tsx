"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import StreakBadge from "./StreakBadge";
import { removeToken } from "@/lib/auth";

const navLinks = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/lessons", label: "Lessons" },
  { href: "/vocabulary", label: "Vocab" },
  { href: "/modules/speaking", label: "Speaking" },
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
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link
            href="/dashboard"
            className="font-display text-2xl uppercase tracking-widest text-accent hover:text-red-400 transition-colors"
          >
            Drillingo
          </Link>

          {/* Nav links */}
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
          <div className="flex items-center gap-4">
            <StreakBadge currentStreak={currentStreak} />
            <button
              onClick={handleLogout}
              className="font-display text-xs uppercase tracking-wider text-muted hover:text-accent transition-colors"
              aria-label="Log out"
            >
              Log Out
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
