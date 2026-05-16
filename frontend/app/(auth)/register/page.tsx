"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { api, ApiError } from "@/lib/api";
import { setToken } from "@/lib/auth";

interface RegisterResponse {
  token: string;
  user_id: string;
  email: string;
  username: string;
}

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Client-side validation (Req 1.4)
  function validate(): string | null {
    if (password.length < 8) return "Password must be at least 8 characters.";
    if (username.trim().length < 2) return "Username must be at least 2 characters.";
    return null;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    try {
      const data = await api.post<RegisterResponse>(
        "/api/auth/register",
        { email, username, password },
        { public: true }
      );
      setToken(data.token);
      document.cookie = `drillingo_token=${data.token}; path=/; max-age=86400; SameSite=Lax`;
      setSuccess(`Welcome, ${data.username}! Account created ✓`);
      setTimeout(() => router.push("/dashboard"), 1200);
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
        Create Account
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
          <label htmlFor="username" className="block text-sm text-muted mb-1 uppercase tracking-wider font-display">
            Username
          </label>
          <input
            id="username"
            type="text"
            autoComplete="username"
            required
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full bg-background border border-border rounded px-4 py-3 text-foreground placeholder-muted focus:outline-none focus:border-accent transition-colors"
            placeholder="drillmaster99"
          />
        </div>

        <div>
          <label htmlFor="password" className="block text-sm text-muted mb-1 uppercase tracking-wider font-display">
            Password
          </label>
          <input
            id="password"
            type="password"
            autoComplete="new-password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full bg-background border border-border rounded px-4 py-3 text-foreground placeholder-muted focus:outline-none focus:border-accent transition-colors"
            placeholder="Min. 8 characters"
          />
        </div>

        {error && (
          <p role="alert" className="text-accent text-sm font-body">
            {error}
          </p>
        )}

        {success && (
          <p role="status" className="text-green-400 text-sm font-body text-center font-bold">
            {success}
          </p>
        )}

        <Button type="submit" variant="primary" size="md" loading={loading} className="w-full">
          Create Account
        </Button>
      </form>

      <p className="mt-4 text-center text-muted text-sm">
        Already have an account?{" "}
        <Link href="/login" className="text-accent hover:underline">
          Log In
        </Link>
      </p>
    </Card>
  );
}
