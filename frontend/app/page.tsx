import { redirect } from "next/navigation";

// Root route redirects to dashboard (authenticated) or login
export default function RootPage() {
  redirect("/dashboard");
}
