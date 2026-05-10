import { ExternalLink, Globe2, MapPin, Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { fetchSpecializations, fetchUniversities } from "@/api/endpoints";
import {
  CATEGORY_LABEL_RU,
  CATEGORY_OPTIONS,
  CITY_OPTIONS,
  type Specialization,
  type University,
} from "@/types";

export function UniversitiesPage() {
  const [universities, setUniversities] = useState<University[]>([]);
  const [specializations, setSpecializations] = useState<Specialization[]>([]);
  const [city, setCity] = useState<string>("All");
  const [category, setCategory] = useState<string>("All");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    Promise.all([
      fetchUniversities(city === "All" ? null : city),
      fetchSpecializations({
        city: city === "All" ? null : city,
        category: category === "All" ? null : category,
      }),
    ])
      .then(([u, s]) => {
        if (cancelled) return;
        setUniversities(u.items);
        setSpecializations(s.items);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [city, category]);

  const specsByUni = useMemo(() => {
    const grouped = new Map<number, Specialization[]>();
    for (const s of specializations) {
      const arr = grouped.get(s.university.id) ?? [];
      arr.push(s);
      grouped.set(s.university.id, arr);
    }
    return grouped;
  }, [specializations]);

  const filteredUnis = useMemo(() => {
    const q = query.trim().toLocaleLowerCase("ru");
    return universities.filter((u) => {
      if (!q) return true;
      return (
        u.name_ru.toLocaleLowerCase("ru").includes(q) ||
        (u.short_name?.toLocaleLowerCase("ru").includes(q) ?? false) ||
        u.city.toLocaleLowerCase("ru").includes(q)
      );
    });
  }, [universities, query]);

  return (
    <div className="container py-12">
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold">Университеты Казахстана</h1>
          <p className="mt-1 text-sm text-slate-500">
            17 университетов · 60+ специальностей · фильтр по городам и направлениям
          </p>
        </div>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Поиск по названию или городу"
            className="input pl-9 sm:w-80"
            aria-label="Поиск университетов"
          />
        </div>
      </div>

      <div className="card flex flex-col gap-3 p-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap gap-2">
          <Pill label="Все города" active={city === "All"} onClick={() => setCity("All")} />
          {CITY_OPTIONS.map((c) => (
            <Pill key={c} label={c} active={city === c} onClick={() => setCity(c)} />
          ))}
        </div>
        <div className="flex flex-wrap gap-2">
          <Pill label="Все направления" active={category === "All"} onClick={() => setCategory("All")} />
          {CATEGORY_OPTIONS.map((c) => (
            <Pill
              key={c}
              label={CATEGORY_LABEL_RU[c]}
              active={category === c}
              onClick={() => setCategory(c)}
            />
          ))}
        </div>
      </div>

      <div className="mt-6 grid gap-5 md:grid-cols-2">
        {loading ? (
          <>
            <div className="skeleton h-44" />
            <div className="skeleton h-44" />
            <div className="skeleton h-44" />
            <div className="skeleton h-44" />
          </>
        ) : filteredUnis.length === 0 ? (
          <div className="card col-span-full p-10 text-center text-sm text-slate-500">
            Ничего не найдено по выбранным фильтрам.
          </div>
        ) : (
          filteredUnis.map((u) => {
            const specs = specsByUni.get(u.id) ?? [];
            return (
              <article key={u.id} className="card p-5">
                <header className="flex items-start gap-3">
                  <div className="grid h-11 w-11 place-content-center rounded-xl bg-gradient-to-br from-brand-700 to-accent-500 text-base font-bold text-white">
                    {(u.short_name ?? u.name_ru).slice(0, 3).toUpperCase()}
                  </div>
                  <div className="flex-1">
                    <h2 className="text-base font-bold">{u.name_ru}</h2>
                    <p className="mt-1 inline-flex items-center gap-1 text-xs text-slate-500">
                      <MapPin className="h-3 w-3" /> {u.city}
                    </p>
                  </div>
                  {u.website && (
                    <a
                      href={u.website}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1 text-xs text-brand-700 hover:underline dark:text-brand-300"
                    >
                      сайт <ExternalLink className="h-3 w-3" />
                    </a>
                  )}
                </header>
                <p className="mt-3 text-xs text-slate-500">
                  Специальностей в этом разделе: <strong>{specs.length}</strong>
                </p>
                {specs.length > 0 && (
                  <ul className="mt-2 space-y-1 text-sm text-slate-600 dark:text-slate-300">
                    {specs.slice(0, 5).map((s) => (
                      <li key={s.id} className="flex items-baseline justify-between gap-2">
                        <span>
                          <span className="text-slate-400">{s.code}</span> {s.name_ru}
                        </span>
                        {s.grant_available && (
                          <span className="shrink-0 rounded-full bg-emerald-50 dark:bg-emerald-900/30 px-2 py-0.5 text-[10px] font-bold text-emerald-700 dark:text-emerald-300">
                            ГРАНТ
                          </span>
                        )}
                      </li>
                    ))}
                    {specs.length > 5 && (
                      <li className="text-xs italic text-slate-400">
                        … и ещё {specs.length - 5}
                      </li>
                    )}
                  </ul>
                )}
                <div className="mt-4 flex items-center justify-between gap-2">
                  <span className="inline-flex items-center gap-1 text-xs text-slate-500">
                    <Globe2 className="h-3 w-3" /> {u.name_en}
                  </span>
                </div>
              </article>
            );
          })
        )}
      </div>
    </div>
  );
}

function Pill({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      className={
        "rounded-full px-3 py-1.5 text-xs font-semibold transition " +
        (active
          ? "bg-brand-700 text-white"
          : "bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 hover:border-brand-400")
      }
    >
      {label}
    </button>
  );
}
