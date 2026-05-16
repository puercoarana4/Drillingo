"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { api, ApiError } from "@/lib/api";
import { setToken } from "@/lib/auth";

interface LoginResponse {
  token: string;
  user_id: string;
  email: string;
  username: string;
}

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const data = await api.post<LoginResponse>(
        "/api/auth/login",
        { email, password },
        { public: true }
      );
      setToken(data.token);
      // Set cookie for middleware and force a full navigation so
      // Next.js middleware re-evaluates the cookie on the new request
      document.cookie = `drillingo_token=${data.token}; path=/; max-age=86400; SameSite=Lax`;
      window.location.href = "/dashboard";
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError("Something went wrong. Try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card>
      <h2 className="font-display text-2xl uppercase tracking-wider text-foreground mb-6">
        Log In
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        <div>
          <label htmlFor="email" className="block text-sm text-muted mb-1 uppercase tracking-wider font-display">
            Email
          </label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full bg-background border border-border rounded px-4 py-3 text-foreground placeholder-muted focus:outline-none focus:border-accent transition-colors"
            placeholder="you@example.com"
          />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm text-muted mb-1 uppercase tracking-wider font-display">
            Password
          </label>
          <input
            id="password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full bg-background border border-border rounded px-4 py-3 text-foreground placeholder-muted focus:outline-none focus:border-accent transition-colors"
            placeholder="••••••••"
          />
        </div>

        {error && (
          <p role="alert" className="text-accent text-sm font-body">
            {error}
          </p>
        )}

        <Button type="submit" variant="primary" size="md" loading={loading} className="w-full">
          Log In
        </Button>
      </form>

      <p className="mt-4 text-center text-muted text-sm">
        No account?{" "}
        <Link href="/register" className="text-accent hover:underline">
          Register
        </Link>
      </p>
    </Card>
  );
}
