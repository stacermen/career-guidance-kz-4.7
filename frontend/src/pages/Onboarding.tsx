import { motion } from "framer-motion";
import { ArrowRight, ShieldCheck } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { Spinner } from "@/components/Spinner";
import { useSession } from "@/hooks/useSession";

const EDUCATION_LEVELS = [
  "9 класс",
  "10 класс",
  "11 класс",
  "Колледж",
  "1 курс университета",
  "2 курс университета",
  "Старше",
];

export function OnboardingPage() {
  const navigate = useNavigate();
  const { start } = useSession();
  const [name, setName] = useState("");
  const [age, setAge] = useState<string>("");
  const [educationLevel, setEducationLevel] = useState<string>("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError("Пожалуйста, введите имя");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await start({
        name: name.trim(),
        age: age ? Number(age) : null,
        education_level: educationLevel || null,
      });
      navigate("/test");
    } catch (e) {
      const err = e as { response?: { data?: { detail?: string } }; message?: string };
      setError(err.response?.data?.detail ?? err.message ?? "Не удалось создать сессию");
      setSubmitting(false);
    }
  };

  return (
    <div className="container max-w-xl py-12 md:py-16">
      <motion.div
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="card p-6 sm:p-8"
      >
        <h1 className="text-2xl font-bold sm:text-3xl">Знакомство</h1>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
          Подскажите немного о себе — это помогает ИИ обращаться к вам по имени.
        </p>

        <form onSubmit={onSubmit} className="mt-6 space-y-5">
          <div>
            <label htmlFor="name" className="mb-1 block text-sm font-medium">
              Как вас зовут? <span className="text-rose-500">*</span>
            </label>
            <input
              id="name"
              required
              autoComplete="given-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Айдана"
              className="input"
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label htmlFor="age" className="mb-1 block text-sm font-medium">
                Возраст <span className="text-slate-400 font-normal">(необязательно)</span>
              </label>
              <input
                id="age"
                type="number"
                min={10}
                max={60}
                value={age}
                onChange={(e) => setAge(e.target.value)}
                placeholder="17"
                className="input"
              />
            </div>
            <div>
              <label htmlFor="edu" className="mb-1 block text-sm font-medium">
                Класс / уровень обучения
              </label>
              <select
                id="edu"
                value={educationLevel}
                onChange={(e) => setEducationLevel(e.target.value)}
                className="input"
              >
                <option value="">— выбрать —</option>
                {EDUCATION_LEVELS.map((l) => (
                  <option key={l} value={l}>
                    {l}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {error && (
            <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-300">
              {error}
            </div>
          )}

          <div className="flex flex-col gap-3 pt-2 sm:flex-row sm:items-center sm:justify-between">
            <p className="inline-flex items-center gap-2 text-xs text-slate-500">
              <ShieldCheck className="h-4 w-4" /> Анонимно. Данные хранятся локально и привязаны к вашей сессии.
            </p>
            <button type="submit" disabled={submitting} className="btn-primary">
              {submitting ? <Spinner /> : <ArrowRight className="h-4 w-4" />}
              {submitting ? "Создаём сессию…" : "К тестированию"}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
}
