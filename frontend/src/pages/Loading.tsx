import { motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { analyze } from "@/api/endpoints";
import { useTestStore } from "@/stores/testStore";

const PHRASES = [
  "Считаем баллы по 142 вопросам…",
  "Сопоставляем код Холланда с профилем личности…",
  "Учитываем ваш когнитивный стиль и ценности…",
  "Подбираем университеты Казахстана с грантами…",
  "ИИ-наставник пишет ваш персональный разбор…",
];

export function LoadingPage() {
  const navigate = useNavigate();
  const session = useTestStore((s) => s.session);
  const [phrase, setPhrase] = useState(PHRASES[0]!);
  const [displayed, setDisplayed] = useState("");
  const [error, setError] = useState<string | null>(null);
  const startedRef = useRef(false);

  // Rotating typewriter.
  useEffect(() => {
    let phraseIdx = 0;
    let charIdx = 0;
    let direction: "typing" | "pausing" | "deleting" = "typing";
    let timer: number;
    const tick = () => {
      const current = PHRASES[phraseIdx]!;
      if (direction === "typing") {
        charIdx += 1;
        setDisplayed(current.slice(0, charIdx));
        if (charIdx === current.length) {
          direction = "pausing";
          timer = window.setTimeout(tick, 1400);
          return;
        }
        timer = window.setTimeout(tick, 28);
      } else if (direction === "pausing") {
        direction = "deleting";
        timer = window.setTimeout(tick, 0);
      } else {
        charIdx -= 2;
        if (charIdx <= 0) {
          charIdx = 0;
          phraseIdx = (phraseIdx + 1) % PHRASES.length;
          setPhrase(PHRASES[phraseIdx]!);
          direction = "typing";
        }
        setDisplayed(current.slice(0, charIdx));
        timer = window.setTimeout(tick, 18);
      }
    };
    tick();
    return () => window.clearTimeout(timer);
  }, []);

  // Kick off the analysis exactly once.
  useEffect(() => {
    if (!session) {
      navigate("/onboarding", { replace: true });
      return;
    }
    if (startedRef.current) return;
    startedRef.current = true;
    let cancelled = false;
    analyze(session.session_id)
      .then((res) => {
        if (cancelled) return;
        navigate(`/results/${res.session_id}`, { replace: true });
      })
      .catch((e) => {
        if (cancelled) return;
        const detail = e?.response?.data?.detail ?? e?.message ?? "Ошибка анализа";
        setError(detail);
      });
    return () => {
      cancelled = true;
    };
  }, [session, navigate]);

  return (
    <div className="container flex min-h-[70vh] flex-col items-center justify-center py-16 text-center">
      <NeuralAnimation />
      <p className="mt-8 text-lg font-semibold text-slate-700 dark:text-slate-200" aria-live="polite">
        {phrase}
      </p>
      <p className="mt-3 max-w-md text-sm text-slate-500" aria-hidden>
        {displayed}
        <span className="ml-0.5 inline-block w-2 animate-blink bg-brand-600 align-baseline">
          &nbsp;
        </span>
      </p>
      {error && (
        <div className="mt-6 max-w-md rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-300">
          {error}
          <button
            className="ml-3 underline"
            onClick={() => {
              startedRef.current = false;
              window.location.reload();
            }}
          >
            Повторить
          </button>
        </div>
      )}
    </div>
  );
}

function NeuralAnimation() {
  return (
    <motion.div
      className="relative h-32 w-32"
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.4 }}
    >
      <svg viewBox="0 0 120 120" className="h-full w-full">
        <defs>
          <linearGradient id="brain-grad" x1="0" x2="1" y1="0" y2="1">
            <stop offset="0%" stopColor="#3730a3" />
            <stop offset="100%" stopColor="#f59e0b" />
          </linearGradient>
        </defs>
        <circle cx="60" cy="60" r="48" fill="none" stroke="url(#brain-grad)" strokeWidth="2.5" opacity="0.4" />
        {Array.from({ length: 8 }).map((_, i) => {
          const angle = (i / 8) * Math.PI * 2;
          const x = 60 + Math.cos(angle) * 36;
          const y = 60 + Math.sin(angle) * 36;
          return (
            <motion.g key={i}>
              <motion.line
                x1="60"
                y1="60"
                x2={x}
                y2={y}
                stroke="url(#brain-grad)"
                strokeWidth="1.5"
                opacity="0.6"
                animate={{ opacity: [0.2, 0.9, 0.2] }}
                transition={{ duration: 2, repeat: Infinity, delay: i * 0.15 }}
              />
              <motion.circle
                cx={x}
                cy={y}
                r="4"
                fill="url(#brain-grad)"
                animate={{ scale: [1, 1.4, 1] }}
                transition={{ duration: 2, repeat: Infinity, delay: i * 0.15 }}
              />
            </motion.g>
          );
        })}
        <motion.circle
          cx="60"
          cy="60"
          r="10"
          fill="url(#brain-grad)"
          animate={{ scale: [1, 1.15, 1] }}
          transition={{ duration: 1.6, repeat: Infinity }}
        />
      </svg>
    </motion.div>
  );
}
