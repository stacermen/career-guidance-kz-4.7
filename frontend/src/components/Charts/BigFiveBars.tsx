import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const LABELS: Record<string, string> = {
  O: "Открытость",
  C: "Добросовестность",
  E: "Экстраверсия",
  A: "Доброжелательность",
  N: "Нейротизм",
};

interface Props {
  scores: Record<string, number>;
}

export function BigFiveBars({ scores }: Props) {
  const data = Object.entries(scores).map(([key, value]) => ({
    key,
    label: LABELS[key] ?? key,
    value: Math.round(value),
  }));
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer>
        <BarChart data={data} layout="vertical" margin={{ left: 32, right: 32 }}>
          <CartesianGrid stroke="rgba(99,102,241,0.15)" horizontal={false} />
          <XAxis type="number" domain={[0, 100]} tick={{ fill: "currentColor", fontSize: 11 }} />
          <YAxis
            dataKey="label"
            type="category"
            width={150}
            tick={{ fill: "currentColor", fontSize: 12 }}
          />
          <Tooltip
            contentStyle={{
              borderRadius: 12,
              border: "1px solid rgba(99,102,241,0.3)",
              background: "rgba(15,23,42,0.92)",
              color: "white",
            }}
            formatter={(v: number) => [`${v}%`, "Балл"]}
          />
          <Bar dataKey="value" fill="url(#bf-gradient)" radius={[0, 8, 8, 0]} />
          <defs>
            <linearGradient id="bf-gradient" x1="0" x2="1" y1="0" y2="0">
              <stop offset="0%" stopColor="#3730a3" />
              <stop offset="100%" stopColor="#f59e0b" />
            </linearGradient>
          </defs>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
