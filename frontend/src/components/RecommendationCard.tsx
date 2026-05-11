import { Award, ExternalLink, MapPin } from "lucide-react";

import { CircularScore } from "@/components/CircularScore";
import { formatTenge } from "@/lib/utils";
import type { Recommendation } from "@/types";

interface Props {
  rec: Recommendation;
}

export function RecommendationCard({ rec }: Props) {
  const spec = rec.specialization;
  const uni = spec.university;
  return (
    <article className="card flex h-full flex-col gap-4 p-5 sm:p-6">
      <div className="flex items-start gap-4">
        <div className="grid h-12 w-12 shrink-0 place-content-center rounded-xl bg-gradient-to-br from-brand-700 to-accent-500 text-base font-bold text-white">
          {(uni.short_name ?? uni.name_ru).slice(0, 3).toUpperCase()}
        </div>
        <div className="flex-1">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            {uni.short_name ?? uni.name_ru}
          </p>
          <p className="mt-0.5 inline-flex items-center gap-1 text-xs text-slate-500">
            <MapPin className="h-3 w-3" /> {uni.city}
          </p>
        </div>
        <CircularScore value={rec.match_score} />
      </div>
      <h3 className="text-lg font-bold leading-snug text-slate-900 dark:text-slate-100">
        {spec.code} — {spec.name_ru}
      </h3>
      <p className="text-sm text-slate-600 dark:text-slate-300">{rec.reason_ru}</p>
      <div className="mt-auto flex flex-wrap items-center gap-2 pt-2">
        {spec.grant_available ? (
          <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 dark:bg-emerald-900/30 px-3 py-1 text-xs font-semibold text-emerald-700 dark:text-emerald-300">
            <Award className="h-3 w-3" /> Грант возможен
          </span>
        ) : (
          <span className="chip">{formatTenge(spec.tuition_cost)}/год</span>
        )}
        <span className="chip">{spec.category}</span>
        {uni.website && (
          <a
            href={uni.website}
            target="_blank"
            rel="noreferrer"
            className="ml-auto inline-flex items-center gap-1 text-sm font-semibold text-brand-700 hover:underline dark:text-brand-300"
          >
            Узнать больше <ExternalLink className="h-3.5 w-3.5" />
          </a>
        )}
      </div>
    </article>
  );
}
