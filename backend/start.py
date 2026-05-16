"""
Startup script for Railway deployment.
Order of operations:
  1. Run Alembic migrations (schema up to date)
  2. Run seed.py (idempotent — skips rows that already exist)
  3. Start uvicorn
"""
import os
import subprocess
import sys


def main():
    port = os.environ.get("PORT", "8000")

    # ── Step 1: Migrations ────────────────────────────────────────────────────
    print("=" * 50)
    print("Step 1/3 — Running database migrations...")
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=False,
    )
    if result.returncode != 0:
        print("Migration failed!", file=sys.stderr)
        sys.exit(1)
    print("Migrations complete.")

    # ── Step 2: Seed ──────────────────────────────────────────────────────────
    print("=" * 50)
    print("Step 2/3 — Running database seed (idempotent)...")
    seed_path = os.path.join(os.path.dirname(__file__), "seed.py")
    result = subprocess.run(
        [sys.executable, seed_path],
        capture_output=False,
    )
    if result.returncode != 0:
        # Seed failure is non-fatal — log the warning and continue.
        # The app can still serve requests; seed data may be partially missing.
        print("WARNING: seed.py exited with a non-zero code. "
              "The app will start anyway.", file=sys.stderr)
    else:
        print("Seed complete.")

    # ── Step 3: Start server ──────────────────────────────────────────────────
    print("=" * 50)
    print(f"Step 3/3 — Starting uvicorn on port {port}...")
    os.execvp(
        "uvicorn",
        ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", port],
    )


if __name__ == "__main__":
    main()
