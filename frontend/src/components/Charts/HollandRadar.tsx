import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
} from "recharts";

const HOLLAND_LABELS: Record<string, string> = {
  R: "Практический",
  I: "Исследоват.",
  A: "Творческий",
  S: "Социальный",
  E: "Предприим.",
  C: "Конвенц.",
};

interface Props {
  scores: Record<string, number>;
}

export function HollandRadar({ scores }: Props) {
  const data = Object.entries(scores).map(([key, value]) => ({
    key,
    label: HOLLAND_LABELS[key] ?? key,
    value: Math.round(value),
  }));
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer>
        <RadarChart data={data} cx="50%" cy="50%" outerRadius="78%">
          <PolarGrid stroke="rgba(99,102,241,0.25)" />
          <PolarAngleAxis dataKey="label" tick={{ fill: "currentColor", fontSize: 12 }} />
          <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: "rgba(100,116,139,0.6)", fontSize: 10 }} />
          <Radar
            name="Холланд"
            dataKey="value"
            stroke="#3730a3"
            fill="#6366f1"
            fillOpacity={0.45}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
