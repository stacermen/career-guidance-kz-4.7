import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { AnswerValue, SessionInfo, TestModule } from "@/types";

interface TestState {
  session: SessionInfo | null;
  modules: TestModule[];
  // Map from question_id → answered value.
  answers: Record<number, AnswerValue>;
  currentModuleIndex: number;
  currentPageIndex: number;

  setSession: (s: SessionInfo) => void;
  setModules: (m: TestModule[]) => void;
  setAnswer: (questionId: number, value: AnswerValue) => void;
  setManyAnswers: (rows: Array<{ questionId: number; value: AnswerValue }>) => void;
  goToModule: (idx: number) => void;
  goToPage: (idx: number) => void;
  nextPage: () => void;
  prevPage: () => void;
  reset: () => void;
}

export const useTestStore = create<TestState>()(
  persist(
    (set) => ({
      session: null,
      modules: [],
      answers: {},
      currentModuleIndex: 0,
      currentPageIndex: 0,

      setSession: (s) => set({ session: s }),
      setModules: (m) => set({ modules: m }),
      setAnswer: (questionId, value) =>
        set((state) => ({ answers: { ...state.answers, [questionId]: value } })),
      setManyAnswers: (rows) =>
        set((state) => {
          const next = { ...state.answers };
          for (const r of rows) next[r.questionId] = r.value;
          return { answers: next };
        }),
      goToModule: (idx) => set({ currentModuleIndex: idx, currentPageIndex: 0 }),
      goToPage: (idx) => set({ currentPageIndex: idx }),
      nextPage: () => set((s) => ({ currentPageIndex: s.currentPageIndex + 1 })),
      prevPage: () =>
        set((s) => ({ currentPageIndex: Math.max(0, s.currentPageIndex - 1) })),
      reset: () =>
        set({
          session: null,
          modules: [],
          answers: {},
          currentModuleIndex: 0,
          currentPageIndex: 0,
        }),
    }),
    {
      name: "career-guidance-kz:test-state",
      partialize: (state) => ({
        session: state.session,
        answers: state.answers,
        currentModuleIndex: state.currentModuleIndex,
        currentPageIndex: state.currentPageIndex,
      }),
    },
  ),
);

export const QUESTIONS_PER_PAGE = 8;

export function pagesForModule(m: TestModule): number {
  return Math.max(1, Math.ceil(m.questions.length / QUESTIONS_PER_PAGE));
}

export function totalQuestions(modules: TestModule[]): number {
  return modules.reduce((acc, m) => acc + m.questions.length, 0);
}

export function answeredCount(
  modules: TestModule[],
  answers: Record<number, AnswerValue>,
): number {
  let count = 0;
  for (const m of modules) {
    for (const q of m.questions) {
      if (answers[q.id] !== undefined) count += 1;
    }
  }
  return count;
}
