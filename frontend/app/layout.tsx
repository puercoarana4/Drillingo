import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Drillingo — Learn Drill English",
  description:
    "Gamified platform to learn AAVE and Drill culture English (B1–C1). East Coast & Midwest Drill.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    // dark class forces dark mode globally (Req 12.1)
    <html lang="en" className="dark">
      <body className="bg-background text-foreground min-h-screen antialiased">
        {children}
      </body>
    </html>
  );
}
