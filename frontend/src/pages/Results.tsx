import { motion } from "framer-motion";
import {
  Award,
  Brain,
  Compass,
  Download,
  Heart,
  Lightbulb,
  Link2,
  Sparkles,
  Target,
  TrendingUp,
} from "lucide-react";
import { useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { resultsPdfUrl } from "@/api/endpoints";
import { BigFiveBars } from "@/components/Charts/BigFiveBars";
import { HollandRadar } from "@/components/Charts/HollandRadar";
import { MIBars } from "@/components/Charts/MIBars";
import { ChatWidget } from "@/components/ChatWidget";
import { CountUp } from "@/components/CountUp";
import { RecommendationCard } from "@/components/RecommendationCard";
import { useResults } from "@/hooks/useResults";
import { useTestStore } from "@/stores/testStore";
import { initials } from "@/lib/utils";
import {
  CATEGORY_LABEL_RU,
  CATEGORY_OPTIONS,
  CITY_OPTIONS,
  type Recommendation,
} from "@/types";

type SortMode = "match" | "grant";

export function ResultsPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const session = useTestStore((s) => s.session);
  const { data, loading, error } = useResults(sessionId);
  const navigate = useNavigate();

  const [city, setCity] = useState<string>("All");
  const [category, setCategory] = useState<string>("All");
  const [sort, setSort] = useState<SortMode>("match");
  const [showAll, setShowAll] = useState(false);
  const [copied, setCopied] = useState(false);

  const filtered = useMemo(() => {
    const list = data?.recommendations ?? [];
    let next: Recommendation[] = list.slice();
    if (city !== "All") {
      next = next.filter((r) => r.specialization.university.city === city);
    }
    if (category !== "All") {
      next = next.filter((r) => r.specialization.category === category);
    }
    if (sort === "match") {
      next.sort((a, b) => b.match_score - a.match_score);
    } else {
      next.sort((a, b) => Number(b.specialization.grant_available) - Number(a.specialization.grant_available));
    }
    return next;
  }, [data, city, category, sort]);

  if (loading) {
    return (
      <div className="container py-16">
        <div className="space-y-4">
          <div className="skeleton h-8 w-1/3" />
          <div className="skeleton h-40 w-full" />
          <div className="skeleton h-40 w-full" />
        </div>
      </div>
    );
  }
  if (error || !data) {
    return (
      <div className="container py-16 text-center">
        <p className="text-rose-600">{error ?? "Результаты не найдены"}</p>
        <button onClick={() => navigate("/")} className="btn-secondary mt-6">
          На главную
        </button>
      </div>
    );
  }

  const a = data.analysis;
  const big5 = data.raw_scores.big_five ?? {};
  const holland = data.raw_scores.holland ?? {};
  const mi = data.raw_scores.mi ?? {};
  const code = (data.traits?.holland_code as string | undefined) ?? "";
  const visible = showAll ? filtered : filtered.slice(0, 12);

  const shareLink = `${window.location.origin}/results/${data.session_id}`;
  const onCopy = async () => {
    try {
      await navigator.clipboard.writeText(shareLink);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // ignore
    }
  };

  return (
    <div>
      {/* Section 1: Personal Profile */}
      <section className="border-b border-slate-200 dark:border-slate-800 bg-gradient-to-br from-brand-50 via-white to-accent-50 dark:from-slate-900 dark:via-slate-950 dark:to-slate-950 py-12">
        <div className="container">
          <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} className="grid gap-8 lg:grid-cols-[280px_1fr]">
            <div className="card p-6 text-center">
              <div className="mx-auto grid h-24 w-24 place-content-center rounded-full bg-gradient-to-br from-brand-700 to-accent-500 text-3xl font-extrabold text-white">
                {initials(session?.name ?? "")}
              </div>
              <p className="mt-4 text-sm text-slate-500">Студент</p>
              <p className="text-lg font-bold">{session?.name ?? "Аноним"}</p>
              {code && (
                <p className="mt-2 inline-flex rounded-full bg-brand-50 dark:bg-brand-900/40 px-3 py-1 text-xs font-bold tracking-widest text-brand-800 dark:text-brand-200">
                  Код {code}
                </p>
              )}
              <p className="mt-3 text-xs text-slate-500">
                Создано {new Date(data.created_at).toLocaleDateString("ru-RU")}
              </p>
            </div>
            <div>
              <h1 className="text-3xl font-extrabold sm:text-4xl">Ваш психологический портрет</h1>
              <p className="mt-3 text-slate-700 dark:text-slate-300 leading-relaxed">{a.personality_summary}</p>
              <div className="mt-5 flex flex-wrap gap-2">
                <a
                  href={resultsPdfUrl(data.session_id)}
                  target="_blank"
                  rel="noreferrer"
                  className="btn-secondary"
                >
                  <Download className="h-4 w-4" /> Скачать PDF
                </a>
                <button onClick={onCopy} className="btn-secondary">
                  <Link2 className="h-4 w-4" /> {copied ? "Ссылка скопирована!" : "Поделиться"}
                </button>
              </div>
            </div>
          </motion.div>

          <div className="mt-8 grid gap-6 lg:grid-cols-2">
            <div className="card p-5">
              <h2 className="flex items-center gap-2 text-base font-semibold text-slate-700 dark:text-slate-200">
                <Compass className="h-5 w-5 text-brand-700" /> Код Холланда
              </h2>
              <HollandRadar scores={holland} />
              <div className="mt-2 grid grid-cols-3 gap-2 text-center text-xs text-slate-500 sm:grid-cols-6">
                {Object.entries(holland).map(([k, v]) => (
                  <div key={k}>
                    <div className="font-bold text-slate-800 dark:text-slate-100">
                      <CountUp to={v as number} />
                    </div>
                    <div>{k}</div>
                  </div>
                ))}
              </div>
            </div>
            <div className="card p-5">
              <h2 className="flex items-center gap-2 text-base font-semibold text-slate-700 dark:text-slate-200">
                <Brain className="h-5 w-5 text-brand-700" /> Большая пятёрка
              </h2>
              <BigFiveBars scores={big5} />
            </div>
          </div>
          <div className="mt-6 card p-5">
            <h2 className="flex items-center gap-2 text-base font-semibold text-slate-700 dark:text-slate-200">
              <Sparkles className="h-5 w-5 text-brand-700" /> Множественный интеллект
            </h2>
            <MIBars scores={mi} />
          </div>
        </div>
      </section>

      {/* Section 2: Strengths */}
      <section className="container py-12">
        <h2 className="text-2xl font-bold sm:text-3xl">Ваши сильные стороны</h2>
        <div className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {a.strengths.map((s, i) => (
            <div key={i} className="card flex gap-3 p-5">
              <span className="grid h-10 w-10 shrink-0 place-content-center rounded-xl bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300">
                {[<TrendingUp />, <Target />, <Heart />, <Lightbulb />, <Award />][i % 5]}
              </span>
              <p className="text-sm font-medium leading-relaxed text-slate-800 dark:text-slate-100">{s}</p>
            </div>
          ))}
        </div>
        {a.growth_areas.length > 0 && (
          <div className="mt-8 grid gap-4 md:grid-cols-2">
            <div className="card p-5">
              <h3 className="text-base font-semibold">Идеальная среда работы</h3>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{a.ideal_work_environment}</p>
            </div>
            <div className="card p-5">
              <h3 className="text-base font-semibold">Зоны роста</h3>
              <ul className="mt-2 space-y-1 text-sm text-slate-600 dark:text-slate-300">
                {a.growth_areas.map((g, i) => (
                  <li key={i}>• {g}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </section>

      {/* Section 3: Recommendations */}
      <section id="recs" className="border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/40 py-12">
        <div className="container">
          <h2 className="text-2xl font-bold sm:text-3xl">Университеты и специальности для вас</h2>
          <p className="mt-1 text-sm text-slate-500">
            Подобрано из {data.recommendations.length} вариантов на основе вашего профиля.
          </p>
          {/* Sticky filter bar */}
          <div className="sticky top-[60px] z-20 mt-5 -mx-4 px-4 py-3 sm:mx-0 sm:px-0">
            <div className="card flex flex-col gap-3 p-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex flex-wrap gap-2">
                <FilterPill label="Все города" value="All" current={city} onClick={() => setCity("All")} />
                {CITY_OPTIONS.map((c) => (
                  <FilterPill key={c} label={c} value={c} current={city} onClick={() => setCity(c)} />
                ))}
              </div>
              <div className="flex flex-wrap gap-2">
                <FilterPill label="Все" value="All" current={category} onClick={() => setCategory("All")} />
                {CATEGORY_OPTIONS.map((c) => (
                  <FilterPill
                    key={c}
                    label={CATEGORY_LABEL_RU[c]}
                    value={c}
                    current={category}
                    onClick={() => setCategory(c)}
                  />
                ))}
              </div>
              <select
                value={sort}
                onChange={(e) => setSort(e.target.value as SortMode)}
                className="input py-2 sm:w-auto"
                aria-label="Сортировка"
              >
                <option value="match">По совпадению</option>
                <option value="grant">Гранты сверху</option>
              </select>
            </div>
          </div>

          <div className="mt-6 grid gap-5 md:grid-cols-2">
            {visible.map((r) => (
              <RecommendationCard key={r.id} rec={r} />
            ))}
            {visible.length === 0 && (
              <div className="card col-span-full p-10 text-center text-sm text-slate-500">
                По выбранным фильтрам ничего не найдено. Попробуйте сбросить фильтры.
              </div>
            )}
          </div>
          {filtered.length > 12 && !showAll && (
            <div className="mt-6 text-center">
              <button onClick={() => setShowAll(true)} className="btn-secondary">
                Показать ещё ({filtered.length - 12})
              </button>
            </div>
          )}
        </div>
      </section>

      {/* Section: study tips & motivation */}
      <section className="container py-12">
        <div className="grid gap-6 md:grid-cols-2">
          <div className="card p-6">
            <h3 className="flex items-center gap-2 text-lg font-semibold">
              <Lightbulb className="h-5 w-5 text-amber-500" /> Советы по обучению
            </h3>
            <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{a.study_tips}</p>
          </div>
          <div className="card p-6 bg-gradient-to-br from-brand-700 to-accent-500 text-white">
            <h3 className="text-lg font-semibold">Личное напутствие</h3>
            <p className="mt-2 text-sm leading-relaxed">{a.motivational_message}</p>
          </div>
        </div>
      </section>

      <ChatWidget sessionId={data.session_id} />
    </div>
  );
}

function FilterPill({
  label,
  value,
  current,
  onClick,
}: {
  label: string;
  value: string;
  current: string;
  onClick: () => void;
}) {
  const active = value === current;
  return (
    <button
      type="button"
      onClick={onClick}
      className={
        "rounded-full px-3 py-1.5 text-xs font-semibold transition " +
        (active
          ? "bg-brand-700 text-white"
          : "bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 hover:border-brand-400")
      }
      aria-pressed={active}
    >
      {label}
    </button>
  );
}
