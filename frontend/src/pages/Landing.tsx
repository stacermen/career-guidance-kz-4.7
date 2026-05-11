import { motion } from "framer-motion";
import {
  Brain,
  GraduationCap,
  Lightbulb,
  Sparkles,
  Target,
  Users,
} from "lucide-react";
import { Link } from "react-router-dom";

const fadeUp = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0 },
};

const stagger = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.08 } },
};

export function LandingPage() {
  return (
    <div>
      <Hero />
      <WhyDifferent />
      <HowItWorks />
      <CTA />
    </div>
  );
}

function Hero() {
  return (
    <section className="relative overflow-hidden">
      <div className="absolute inset-0 -z-10">
        <div className="absolute -top-32 -left-20 h-96 w-96 rounded-full bg-brand-300/30 dark:bg-brand-700/20 blur-3xl" />
        <div className="absolute top-40 right-0 h-96 w-96 rounded-full bg-accent-300/40 dark:bg-accent-700/10 blur-3xl" />
      </div>
      <div className="container py-20 md:py-28">
        <motion.div
          initial="hidden"
          animate="visible"
          variants={stagger}
          className="mx-auto max-w-3xl text-center"
        >
          <motion.div variants={fadeUp} className="inline-flex items-center gap-2 rounded-full border border-brand-200 dark:border-brand-800 bg-white dark:bg-slate-900 px-4 py-1.5 text-xs font-semibold text-brand-800 dark:text-brand-200">
            <Sparkles className="h-3.5 w-3.5" /> Бесплатный ИИ-наставник — без регистрации и ключей
          </motion.div>
          <motion.h1
            variants={fadeUp}
            className="mt-5 text-4xl font-extrabold tracking-tight sm:text-5xl md:text-6xl"
          >
            <span className="gradient-text">Найдите свою</span>
            <br />
            профессию через науку, а не догадки
          </motion.h1>
          <motion.p
            variants={fadeUp}
            className="mt-6 text-lg leading-relaxed text-slate-600 dark:text-slate-300 md:text-xl"
          >
            5 валидированных психологических тестов · 142 вопроса · глубокий ИИ-разбор и
            подбор реальных специальностей в университетах Казахстана.
          </motion.p>
          <motion.div variants={fadeUp} className="mt-9 flex flex-wrap items-center justify-center gap-3">
            <Link to="/onboarding" className="btn-primary text-base">
              <Brain className="h-5 w-5" /> Начать тестирование — бесплатно
            </Link>
            <Link to="/about" className="btn-secondary text-base">
              Как это работает
            </Link>
          </motion.div>
          <motion.p variants={fadeUp} className="mt-4 text-xs text-slate-500">
            Анонимно · занимает ~25 минут · результаты сохраняются по ссылке
          </motion.p>
        </motion.div>
      </div>
    </section>
  );
}

const REASONS = [
  {
    icon: Brain,
    title: "Глубже, чем простые тесты",
    body:
      "Соединяем 5 моделей: RIASEC, Big Five, множественный интеллект Гарднера, ценности и когнитивный стиль.",
  },
  {
    icon: Sparkles,
    title: "ИИ-разбор личности",
    body:
      "ИИ-наставник формирует развёрнутый психологический портрет, объясняя, почему именно вам подходит каждое направление.",
  },
  {
    icon: GraduationCap,
    title: "Реальные университеты Казахстана",
    body:
      "Подбор по каталогу из 55 университетов в 18 городах и сотен специальностей с государственными кодами РК.",
  },
  {
    icon: Target,
    title: "Фильтры под ваш город",
    body: "Алматы, Астана, Шымкент, Қарағанды, Павлодар, Өскемен, Семей, Орал, Ақтөбе и другие — выбирайте, где удобно учиться.",
  },
  {
    icon: Users,
    title: "Персональный ИИ-наставник",
    body: "После результатов с вами останется чат-консультант, помнящий ваш профиль.",
  },
  {
    icon: Lightbulb,
    title: "PDF и ссылка для родителей",
    body: "Сохраняйте отчёт, делитесь с близкими и наставниками одним кликом.",
  },
];

function WhyDifferent() {
  return (
    <section className="border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/40 py-20">
      <div className="container">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold sm:text-4xl">Чем этот тест отличается</h2>
          <p className="mt-3 text-slate-600 dark:text-slate-300">
            Мы строим ваш карьерный путь на проверенных психометриках, а не на гороскопах.
          </p>
        </div>
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={stagger}
          className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-3"
        >
          {REASONS.map((r) => (
            <motion.div
              variants={fadeUp}
              key={r.title}
              className="card p-6"
            >
              <span className="grid h-11 w-11 place-content-center rounded-xl bg-brand-50 dark:bg-brand-900/40 text-brand-700 dark:text-brand-200">
                <r.icon className="h-5 w-5" />
              </span>
              <h3 className="mt-4 text-lg font-semibold">{r.title}</h3>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{r.body}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

const STEPS = [
  {
    n: "01",
    title: "Расскажите о себе",
    body: "Имя, возраст, уровень обучения — без e-mail и регистрации.",
  },
  {
    n: "02",
    title: "Пройдите 5 модулей",
    body: "142 вопроса, разбитых по 8 на странице. Прогресс сохраняется автоматически.",
  },
  {
    n: "03",
    title: "Получите ИИ-разбор",
    body: "Психологический портрет + 12 рекомендованных специальностей с обоснованием.",
  },
];

function HowItWorks() {
  return (
    <section className="py-20">
      <div className="container">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold sm:text-4xl">Три шага до решения</h2>
          <p className="mt-3 text-slate-600 dark:text-slate-300">
            Ничего лишнего — мы оптимизировали процесс под старшеклассника.
          </p>
        </div>
        <div className="mt-12 grid gap-6 md:grid-cols-3">
          {STEPS.map((s) => (
            <div key={s.n} className="card relative overflow-hidden p-7">
              <div className="absolute right-4 top-4 text-5xl font-black text-brand-50 dark:text-brand-900/40">
                {s.n}
              </div>
              <h3 className="text-xl font-semibold">{s.title}</h3>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{s.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function CTA() {
  return (
    <section className="bg-gradient-to-br from-brand-800 via-brand-700 to-accent-500 py-16 text-white">
      <div className="container flex flex-col items-center justify-between gap-5 text-center md:flex-row md:text-left">
        <div>
          <h3 className="text-2xl font-bold sm:text-3xl">Готовы найти свою профессию?</h3>
          <p className="mt-1 text-white/80">
            Запустите тест прямо сейчас — он работает на телефоне, ноутбуке и планшете.
          </p>
        </div>
        <Link to="/onboarding" className="rounded-xl bg-white px-6 py-3 text-base font-semibold text-brand-900 shadow hover:bg-slate-100">
          Пройти тест бесплатно
        </Link>
      </div>
    </section>
  );
}
