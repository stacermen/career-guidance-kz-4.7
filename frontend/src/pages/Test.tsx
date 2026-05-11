import { AnimatePresence, motion } from "framer-motion";
import { ArrowLeft, ArrowRight, CheckCircle2, Clock, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { ProgressBar } from "@/components/ProgressBar";
import { Spinner } from "@/components/Spinner";
import { TestQuestion } from "@/components/TestQuestion";
import { useTestFlow } from "@/hooks/useTestFlow";
import { useTestStore } from "@/stores/testStore";

const MODULE_DURATION_MIN: Record<string, number> = {
  holland: 7,
  big_five: 5,
  mi: 6,
  values: 4,
  cognitive: 2,
};

export function TestPage() {
  const navigate = useNavigate();
  const session = useTestStore((s) => s.session);
  const answers = useTestStore((s) => s.answers);
  const flow = useTestFlow();
  const [showIntro, setShowIntro] = useState(true);

  useEffect(() => {
    if (!session) navigate("/onboarding", { replace: true });
  }, [session, navigate]);

  // Show intro on entering a new module.
  useEffect(() => {
    setShowIntro(true);
  }, [flow.moduleIdx]);

  if (flow.loading || !flow.currentModule) {
    return (
      <div className="container py-20 text-center">
        <Spinner className="mx-auto h-7 w-7 text-brand-700" />
        <p className="mt-3 text-sm text-slate-500">Загружаем тестовые модули…</p>
      </div>
    );
  }
  if (flow.error) {
    return (
      <div className="container py-20 text-center text-rose-600">{flow.error}</div>
    );
  }

  return (
    <div>
      <StickyProgress
        moduleTitle={flow.currentModule.title_ru}
        moduleIdx={flow.moduleIdx}
        totalModules={flow.modules.length}
        progress={flow.progress}
      />

      <div className="container max-w-3xl pb-24 pt-6">
        <AnimatePresence mode="wait">
          {showIntro ? (
            <motion.div
              key={`intro-${flow.moduleIdx}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.35 }}
              className="card p-8 text-center"
            >
              <div className="mx-auto inline-flex items-center gap-2 rounded-full bg-brand-50 dark:bg-brand-900/40 px-3 py-1 text-xs font-semibold text-brand-700 dark:text-brand-200">
                Модуль {flow.moduleIdx + 1} из {flow.modules.length}
                <span>·</span>
                <Clock className="h-3 w-3" />~{MODULE_DURATION_MIN[flow.currentModule.slug] ?? 5} мин
              </div>
              <h2 className="mt-4 text-3xl font-bold">{flow.currentModule.title_ru}</h2>
              <p className="mx-auto mt-3 max-w-xl text-slate-600 dark:text-slate-300">
                {flow.currentModule.description_ru}
              </p>
              <button
                type="button"
                onClick={() => setShowIntro(false)}
                className="btn-primary mt-7"
              >
                Начать модуль <ArrowRight className="h-4 w-4" />
              </button>
            </motion.div>
          ) : (
            <motion.div
              key={`page-${flow.moduleIdx}-${flow.pageIdx}`}
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -30 }}
              transition={{ duration: 0.3 }}
              className="space-y-4"
            >
              <div className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Стр. {flow.pageIdx + 1} из {flow.totalPages}
              </div>
              {flow.pageQuestions.map((q, idx) => (
                <TestQuestion
                  key={q.id}
                  question={q}
                  index={flow.pageIdx * 8 + idx}
                  value={answers[q.id]}
                  onChange={(v) => flow.setAnswer(q.id, v)}
                />
              ))}

              <div className="sticky bottom-3 z-30 mt-6 flex flex-col-reverse gap-3 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white/95 dark:bg-slate-950/95 p-3 backdrop-blur sm:flex-row sm:items-center sm:justify-between">
                <button
                  type="button"
                  onClick={flow.goPrev}
                  disabled={!flow.canGoBack}
                  className="btn-secondary"
                >
                  <ArrowLeft className="h-4 w-4" /> Назад
                </button>
                <div className="flex items-center justify-center gap-3 text-xs text-slate-500">
                  <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                  Сохранение автоматическое
                </div>
                <NextButton flow={flow} />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

function NextButton({ flow }: { flow: ReturnType<typeof useTestFlow> }) {
  const navigate = useNavigate();
  const [working, setWorking] = useState(false);

  const onNext = async () => {
    setWorking(true);
    try {
      await flow.goNext();
      if (flow.isLastPageOfLastModule) {
        navigate("/loading");
      }
    } finally {
      setWorking(false);
    }
  };

  const lastEverPage = flow.isLastPageOfLastModule;
  return (
    <button
      type="button"
      onClick={onNext}
      disabled={working || !flow.allAnsweredOnPage}
      className="btn-primary"
    >
      {working && <Spinner />} {lastEverPage ? (
        <>
          К результатам <Sparkles className="h-4 w-4" />
        </>
      ) : (
        <>
          Далее <ArrowRight className="h-4 w-4" />
        </>
      )}
    </button>
  );
}

function StickyProgress({
  moduleTitle,
  moduleIdx,
  totalModules,
  progress,
}: {
  moduleTitle: string;
  moduleIdx: number;
  totalModules: number;
  progress: number;
}) {
  return (
    <div className="sticky top-[60px] z-30 border-b border-slate-200 dark:border-slate-800 bg-white/95 dark:bg-slate-950/95 backdrop-blur">
      <div className="container py-3">
        <div className="flex items-center justify-between text-xs text-slate-500">
          <span className="font-medium text-slate-700 dark:text-slate-300">
            Модуль {moduleIdx + 1}/{totalModules} · {moduleTitle}
          </span>
          <span>{progress}%</span>
        </div>
        <ProgressBar value={progress} className="mt-2" />
      </div>
    </div>
  );
}
