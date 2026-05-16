// Auth group layout — centered card, no navbar
export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <h1 className="font-display text-4xl uppercase tracking-widest text-accent text-center mb-8">
          Drillingo
        </h1>
        {children}
      </div>
    </div>
  );
}
