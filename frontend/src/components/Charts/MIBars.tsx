import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const MI_LABELS: Record<string, string> = {
  linguistic: "Лингвистический",
  logical: "Логико-матем.",
  spatial: "Пространств.",
  musical: "Музыкальный",
  bodily: "Телесный",
  interpersonal: "Межличностный",
  intrapersonal: "Внутриличн.",
  naturalistic: "Натуралист.",
};

interface Props {
  scores: Record<string, number>;
}

export function MIBars({ scores }: Props) {
  const data = Object.entries(scores).map(([key, value]) => ({
    key,
    label: MI_LABELS[key] ?? key,
    value: Math.round(value),
  }));
  return (
    <div className="h-80 w-full">
      <ResponsiveContainer>
        <BarChart data={data} layout="vertical" margin={{ left: 32, right: 32 }}>
          <CartesianGrid stroke="rgba(99,102,241,0.12)" horizontal={false} />
          <XAxis type="number" domain={[0, 100]} tick={{ fill: "currentColor", fontSize: 11 }} />
          <YAxis dataKey="label" type="category" width={130} tick={{ fill: "currentColor", fontSize: 12 }} />
          <Tooltip
            contentStyle={{
              borderRadius: 12,
              border: "1px solid rgba(99,102,241,0.3)",
              background: "rgba(15,23,42,0.92)",
              color: "white",
            }}
            formatter={(v: number) => [`${v}%`, "Уровень"]}
          />
          <Bar dataKey="value" fill="#6366f1" radius={[0, 8, 8, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
