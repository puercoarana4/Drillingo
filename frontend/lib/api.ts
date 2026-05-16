import { getToken, removeToken } from "./auth";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

interface ApiOptions {
  method?: HttpMethod;
  body?: unknown;
  /** Skip auth header (used for login/register) */
  public?: boolean;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string
  ) {
    super(detail);
    this.name = "ApiError";
  }
}

/**
 * Typed fetch wrapper.
 * - Automatically injects JWT from localStorage.
 * - Throws ApiError on non-2xx responses.
 * - Redirects to /login on 401 (expired token).
 */
export async function apiRequest<T>(
  path: string,
  options: ApiOptions = {}
): Promise<T> {
  const { method = "GET", body, public: isPublic = false } = options;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (!isPublic) {
    const token = getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (response.status === 401 && !isPublic) {
    // Token expired — clear and redirect to login
    removeToken();
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
    throw new ApiError(401, "Session expired. Please log in again.");
  }

  if (!response.ok) {
    let detail = `HTTP ${response.status}`;
    try {
      const err = await response.json();
      detail = err.detail ?? err.message ?? detail;
    } catch {
      // ignore JSON parse errors
    }
    throw new ApiError(response.status, detail);
  }

  // 204 No Content
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

// ── Convenience methods ───────────────────────────────────────────────────────

export const api = {
  get: <T>(path: string, opts?: Omit<ApiOptions, "method" | "body">) =>
    apiRequest<T>(path, { ...opts, method: "GET" }),

  post: <T>(path: string, body: unknown, opts?: Omit<ApiOptions, "method">) =>
    apiRequest<T>(path, { ...opts, method: "POST", body }),

  patch: <T>(path: string, body: unknown, opts?: Omit<ApiOptions, "method">) =>
    apiRequest<T>(path, { ...opts, method: "PATCH", body }),

  delete: <T>(path: string, opts?: Omit<ApiOptions, "method" | "body">) =>
    apiRequest<T>(path, { ...opts, method: "DELETE" }),
};
