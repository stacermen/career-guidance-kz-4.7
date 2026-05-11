import { Brain, Moon, Sun } from "lucide-react";
import { Link, NavLink } from "react-router-dom";

import { useTheme } from "@/stores/themeStore";
import { cn } from "@/lib/utils";

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  cn(
    "px-3 py-2 rounded-lg text-sm font-medium transition",
    isActive
      ? "bg-brand-50 text-brand-800 dark:bg-brand-900/40 dark:text-brand-200"
      : "text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-slate-100",
  );

export function NavBar() {
  const { theme, toggle } = useTheme();
  return (
    <header className="sticky top-0 z-40 border-b border-slate-200/60 dark:border-slate-800/60 bg-white/80 dark:bg-slate-950/80 backdrop-blur">
      <div className="container flex items-center justify-between py-3">
        <Link to="/" className="flex items-center gap-2 font-bold text-lg" aria-label="На главную">
          <span className="grid h-9 w-9 place-content-center rounded-xl bg-gradient-to-br from-brand-700 to-accent-500 text-white">
            <Brain className="h-5 w-5" />
          </span>
          <span className="hidden sm:inline gradient-text">Career Guidance KZ</span>
        </Link>
        <nav className="hidden items-center gap-1 md:flex" aria-label="Главная навигация">
          <NavLink to="/" end className={navLinkClass}>
            Главная
          </NavLink>
          <NavLink to="/universities" className={navLinkClass}>
            Университеты
          </NavLink>
          <NavLink to="/about" className={navLinkClass}>
            О тестах
          </NavLink>
        </nav>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={toggle}
            className="btn-ghost"
            aria-label={theme === "dark" ? "Включить светлую тему" : "Включить тёмную тему"}
          >
            {theme === "dark" ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </button>
          <Link to="/onboarding" className="btn-primary px-4 py-2 text-sm">
            Пройти тест
          </Link>
        </div>
      </div>
    </header>
  );
}
