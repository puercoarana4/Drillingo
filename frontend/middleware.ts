import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Routes that require authentication
const PROTECTED_PREFIXES = ["/dashboard", "/lessons", "/modules", "/vocabulary", "/reports"];
// Routes that should redirect to dashboard if already authenticated
const AUTH_ROUTES = ["/login", "/register"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Check for JWT in cookies (set by the login page after auth)
  const token = request.cookies.get("drillingo_token")?.value;

  const isProtected = PROTECTED_PREFIXES.some((prefix) =>
    pathname.startsWith(prefix)
  );
  const isAuthRoute = AUTH_ROUTES.some((route) => pathname.startsWith(route));

  // Redirect unauthenticated users away from protected routes
  if (isProtected && !token) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("from", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Redirect authenticated users away from login/register
  if (isAuthRoute && token) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!api|_next/static|_next/image|favicon.ico).*)",
  ],
};
