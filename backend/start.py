"""
Startup script for Railway deployment.
Runs Alembic migrations then starts uvicorn.
"""
import os
import subprocess
import sys


def main():
    port = os.environ.get("PORT", "8000")

    print("Running database migrations...")
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=False,
    )
    if result.returncode != 0:
        print("Migration failed!", file=sys.stderr)
        sys.exit(1)

    print(f"Starting uvicorn on port {port}...")
    os.execvp(
        "uvicorn",
        ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", port],
    )


if __name__ == "__main__":
    main()
