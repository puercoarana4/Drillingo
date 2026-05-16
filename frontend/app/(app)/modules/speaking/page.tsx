import Card from "@/components/ui/Card";
import OralReportForm from "@/components/modules/OralReportForm";

export default function SpeakingPage() {
  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <h1 className="font-display text-3xl uppercase text-foreground mb-2">
          Live Report Sync
        </h1>
        <p className="text-muted">
          Practice speaking outside the app, then sync your session metrics here.
          Your fluency and pronunciation scores will update your dashboard.
        </p>
      </div>

      <Card accent>
        <h2 className="font-display text-lg uppercase text-muted mb-6">
          Session Report
        </h2>
        <OralReportForm />
      </Card>

      {/* Instructions */}
      <Card className="mt-6">
        <h3 className="font-display text-sm uppercase text-muted mb-3">How it works</h3>
        <ol className="space-y-2 text-sm text-muted list-decimal list-inside">
          <li>Practice speaking Drill English with a partner or AI tool</li>
          <li>Get your fluency and pronunciation scores from your session</li>
          <li>Enter the scores and duration above</li>
          <li>Hit <span className="text-accent font-bold">Sync Report</span> — your dashboard updates instantly</li>
        </ol>
      </Card>
    </div>
  );
}
