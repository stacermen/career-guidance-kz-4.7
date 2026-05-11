import { useCallback, useEffect, useMemo, useState } from "react";

import { fetchTests, saveAnswers } from "@/api/endpoints";
import {
  QUESTIONS_PER_PAGE,
  answeredCount,
  pagesForModule,
  totalQuestions,
  useTestStore,
} from "@/stores/testStore";
import type { AnswerValue } from "@/types";

export function useTestFlow() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const modules = useTestStore((s) => s.modules);
  const setModules = useTestStore((s) => s.setModules);
  const session = useTestStore((s) => s.session);
  const answers = useTestStore((s) => s.answers);
  const moduleIdx = useTestStore((s) => s.currentModuleIndex);
  const pageIdx = useTestStore((s) => s.currentPageIndex);
  const setAnswer = useTestStore((s) => s.setAnswer);
  const goToModule = useTestStore((s) => s.goToModule);
  const goToPage = useTestStore((s) => s.goToPage);
  const nextPage = useTestStore((s) => s.nextPage);
  const prevPage = useTestStore((s) => s.prevPage);

  // Lazy-load modules once.
  useEffect(() => {
    if (modules.length > 0) return;
    let cancelled = false;
    setLoading(true);
    fetchTests()
      .then((data) => {
        if (!cancelled) setModules(data);
      })
      .catch((e) => {
        if (!cancelled) setError(e?.message ?? "Не удалось загрузить тест");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [modules.length, setModules]);

  const currentModule = modules[moduleIdx];
  const totalPages = currentModule ? pagesForModule(currentModule) : 0;
  const pageQuestions = useMemo(() => {
    if (!currentModule) return [];
    const start = pageIdx * QUESTIONS_PER_PAGE;
    return currentModule.questions.slice(start, start + QUESTIONS_PER_PAGE);
  }, [currentModule, pageIdx]);

  const total = useMemo(() => totalQuestions(modules), [modules]);
  const answered = useMemo(() => answeredCount(modules, answers), [modules, answers]);
  const progress = total === 0 ? 0 : Math.round((answered / total) * 100);

  const allAnsweredOnPage = pageQuestions.every((q) => answers[q.id] !== undefined);

  // Auto-save answers in batches when moving forward.
  const persistAnswers = useCallback(
    async (questionIds: number[]) => {
      if (!session) return;
      const payload = questionIds
        .filter((id) => answers[id] !== undefined)
        .map((id) => ({ question_id: id, value: answers[id]! }));
      if (payload.length === 0) return;
      try {
        await saveAnswers({ session_id: session.session_id, answers: payload });
      } catch (e) {
        // Network errors are non-fatal — answers are already in localStorage.
        console.warn("Failed to save answers", e);
      }
    },
    [answers, session],
  );

  const goNext = useCallback(async () => {
    if (!currentModule) return;
    const ids = pageQuestions.map((q) => q.id);
    await persistAnswers(ids);
    if (pageIdx + 1 < totalPages) {
      nextPage();
      window.scrollTo({ top: 0, behavior: "smooth" });
    } else if (moduleIdx + 1 < modules.length) {
      goToModule(moduleIdx + 1);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  }, [
    currentModule,
    pageQuestions,
    persistAnswers,
    pageIdx,
    totalPages,
    moduleIdx,
    modules.length,
    nextPage,
    goToModule,
  ]);

  const goPrev = useCallback(() => {
    if (pageIdx > 0) prevPage();
    else if (moduleIdx > 0) {
      const target = moduleIdx - 1;
      const targetModule = modules[target];
      if (targetModule) {
        goToModule(target);
        // Jump straight to last page of the previous module.
        goToPage(pagesForModule(targetModule) - 1);
      }
    }
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, [pageIdx, moduleIdx, prevPage, goToModule, goToPage, modules]);

  const setAnswerWithValue = useCallback(
    (qid: number, value: AnswerValue) => setAnswer(qid, value),
    [setAnswer],
  );

  return {
    loading,
    error,
    modules,
    currentModule,
    moduleIdx,
    pageIdx,
    totalPages,
    pageQuestions,
    progress,
    answered,
    total,
    allAnsweredOnPage,
    setAnswer: setAnswerWithValue,
    goNext,
    goPrev,
    isLastPageOfLastModule:
      moduleIdx === modules.length - 1 && pageIdx === totalPages - 1 && totalPages > 0,
    canGoBack: moduleIdx > 0 || pageIdx > 0,
  };
}
