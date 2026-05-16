"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { format } from "date-fns";

interface OralHistoryPoint {
  submitted_at: string;
  fluency_score: number;
  pronunciation_score: number;
}

interface OralHistoryChartProps {
  data: OralHistoryPoint[];
}

export default function OralHistoryChart({ data }: OralHistoryChartProps) {
  // Reverse so oldest is on the left
  const chartData = [...data].reverse().map((d) => ({
    date: format(new Date(d.submitted_at), "MMM d"),
    fluency: d.fluency_score,
    pronunciation: d.pronunciation_score,
  }));

  return (
    // Req 9.4: line chart for last 30 oral reports
    <div className="bg-surface border border-border rounded-xl p-6">
      <h3 className="font-display text-sm uppercase tracking-wider text-muted mb-4">
        Oral Progress (Last 30 Sessions)
      </h3>
      {chartData.length === 0 ? (
        <p className="text-muted text-sm text-center py-8">
          No sessions yet. Sync your first oral report.
        </p>
      ) : (
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333333" />
            <XAxis
              dataKey="date"
              tick={{ fill: "#6B6B6B", fontSize: 10 }}
              tickLine={false}
            />
            <YAxis
              domain={[0, 100]}
              tick={{ fill: "#6B6B6B", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#242424",
                border: "1px solid #333333",
                borderRadius: "8px",
                color: "#FFFFFF",
              }}
            />
            <Legend
              wrapperStyle={{ fontSize: "11px", fontFamily: "Impact, sans-serif" }}
            />
            <Line
              type="monotone"
              dataKey="fluency"
              stroke="#FF0033"
              strokeWidth={2}
              dot={false}
              name="Fluency"
            />
            <Line
              type="monotone"
              dataKey="pronunciation"
              stroke="#FFFFFF"
              strokeWidth={2}
              dot={false}
              strokeDasharray="4 2"
              name="Pronunciation"
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
