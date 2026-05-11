import { Route, Routes } from "react-router-dom";

import { NavBar } from "@/components/NavBar";
import { AboutPage } from "@/pages/About";
import { LandingPage } from "@/pages/Landing";
import { LoadingPage } from "@/pages/Loading";
import { NotFoundPage } from "@/pages/NotFound";
import { OnboardingPage } from "@/pages/Onboarding";
import { ResultsPage } from "@/pages/Results";
import { TestPage } from "@/pages/Test";
import { UniversitiesPage } from "@/pages/Universities";

export default function App() {
  return (
    <div className="flex min-h-full flex-col">
      <NavBar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/onboarding" element={<OnboardingPage />} />
          <Route path="/test" element={<TestPage />} />
          <Route path="/loading" element={<LoadingPage />} />
          <Route path="/results/:sessionId" element={<ResultsPage />} />
          <Route path="/universities" element={<UniversitiesPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </main>
      <footer className="border-t border-slate-200 dark:border-slate-800 py-6">
        <div className="container flex flex-col gap-2 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between">
          <span>© {new Date().getFullYear()} Career Guidance KZ — построено с ИИ-наставником.</span>
          <span>Психометрия не заменяет консультацию специалиста.</span>
        </div>
      </footer>
    </div>
  );
}
