"use client";

import {
  Radar,
  RadarChart as RechartsRadar,
  PolarGrid,
  PolarAngleAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

interface RadarScores {
  reading: number;
  listening: number;
  writing: number;
  speaking: number;
  vocabulary: number;
}

interface RadarChartProps {
  scores: RadarScores;
}

export default function RadarChart({ scores }: RadarChartProps) {
  const data = [
    { subject: "Reading", value: scores.reading },
    { subject: "Listening", value: scores.listening },
    { subject: "Writing", value: scores.writing },
    { subject: "Speaking", value: scores.speaking },
    { subject: "Vocab", value: scores.vocabulary },
  ];

  return (
    // Req 9.2: radar chart with 5 dimensions, accent color #FF0033
    <div className="bg-surface border border-border rounded-xl p-6">
      <h3 className="font-display text-sm uppercase tracking-wider text-muted mb-4">
        Skills Radar
      </h3>
      <ResponsiveContainer width="100%" height={280}>
        <RechartsRadar data={data} cx="50%" cy="50%" outerRadius="75%">
          <PolarGrid stroke="#333333" />
          <PolarAngleAxis
            dataKey="subject"
            tick={{ fill: "#6B6B6B", fontSize: 11, fontFamily: "Impact, sans-serif" }}
          />
          <Radar
            name="Score"
            dataKey="value"
            stroke="#FF0033"
            fill="#FF0033"
            fillOpacity={0.25}
            strokeWidth={2}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#242424",
              border: "1px solid #333333",
              borderRadius: "8px",
              color: "#FFFFFF",
              fontFamily: "Impact, sans-serif",
            }}
            formatter={(value: number) => [`${Math.round(value)}`, "Score"]}
          />
        </RechartsRadar>
      </ResponsiveContainer>
    </div>
  );
}
