import { Compass, FlaskConical, ShieldCheck } from "lucide-react";
import { Link } from "react-router-dom";

const TEST_DESCRIPTIONS = [
  {
    title: "Тест Холланда (RIASEC)",
    body:
      "42 вопроса, шесть типов профессиональной ориентации: Realistic, Investigative, Artistic, Social, Enterprising, Conventional. По результатам формируется трёхбуквенный код, который десятилетиями используется карьерными консультантами.",
  },
  {
    title: "Большая пятёрка (Big Five)",
    body:
      "30 утверждений по модели OCEAN — самой проверенной таксономии личности в современной психологии (Costa, McCrae).",
  },
  {
    title: "Множественный интеллект (Гарднер)",
    body:
      "40 вопросов, восемь типов интеллекта: лингвистический, логико-математический, пространственный, музыкальный, телесный, межличностный, внутриличностный, натуралистический.",
  },
  {
    title: "Ценности в работе",
    body:
      "20 заданий: что для вас важно — стабильность, доход, социальное воздействие, разнообразие, автономия, престиж или творчество.",
  },
  {
    title: "Когнитивный стиль",
    body:
      "10 вопросов, аналитика vs интуиция, детали vs «большая картина». Помогает подобрать стиль обучения.",
  },
];

const FAQ = [
  {
    q: "Это правда бесплатно?",
    a: "Да. Сервис работает без оплаты, регистрации и e-mail.",
  },
  {
    q: "Откуда берётся ИИ-разбор?",
    a: "После расчёта баллов мы отправляем структурированный профиль в открытый бесплатный сервис Pollinations.ai (OpenAI-совместимый, без регистрации и API-ключа). Он генерирует развёрнутый персональный комментарий и список карьерных направлений.",
  },
  {
    q: "Как подбираются университеты?",
    a: "Мы держим каталог реальных университетов Казахстана и специальностей с государственными кодами (государственный классификатор специальностей РК). По категориям, предложенным ИИ, мы подбираем лучшие варианты с акцентом на доступные гранты.",
  },
  {
    q: "Безопасны ли мои данные?",
    a: "Тест анонимный — мы не запрашиваем e-mail, не используем cookies для рекламы. Ответы хранятся в зашифрованной БД и привязаны только к UUID-сессии.",
  },
  {
    q: "Можно ли вернуться к тесту позже?",
    a: "Да. Прогресс сохраняется в браузере локально и в БД. Просто откройте сайт снова на этом же устройстве.",
  },
];

export function AboutPage() {
  return (
    <div className="container py-12">
      <header className="max-w-2xl">
        <h1 className="text-3xl font-bold sm:text-4xl">О тестах и науке за ними</h1>
        <p className="mt-3 text-slate-600 dark:text-slate-300">
          Мы соединяем психологические инструменты с проверенной репутацией и современную ИИ-аналитику.
          Никаких эзотерических методик.
        </p>
      </header>

      <section className="mt-10 grid gap-4 md:grid-cols-3">
        <Feature
          icon={<FlaskConical className="h-5 w-5" />}
          title="Доказательная психометрия"
          body="Все тесты адаптированы из академических русскоязычных переводов оригинальных опросников."
        />
        <Feature
          icon={<Compass className="h-5 w-5" />}
          title="Применимость в Казахстане"
          body="Подбор привязан к реальному списку университетов и кодам специальностей РК."
        />
        <Feature
          icon={<ShieldCheck className="h-5 w-5" />}
          title="Анонимно"
          body="Ни регистрации, ни e-mail. Только UUID-сессия в вашем браузере."
        />
      </section>

      <section className="mt-12">
        <h2 className="text-2xl font-bold">Состав теста</h2>
        <div className="mt-5 space-y-4">
          {TEST_DESCRIPTIONS.map((t) => (
            <div key={t.title} className="card p-5">
              <h3 className="text-lg font-semibold">{t.title}</h3>
              <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">{t.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mt-12">
        <h2 className="text-2xl font-bold">Часто задаваемые вопросы</h2>
        <div className="mt-5 space-y-3">
          {FAQ.map((f) => (
            <details key={f.q} className="card cursor-pointer p-5 [&_summary]:list-none">
              <summary className="flex cursor-pointer items-center justify-between text-base font-semibold">
                {f.q}
                <span className="ml-3 text-slate-400">+</span>
              </summary>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{f.a}</p>
            </details>
          ))}
        </div>
      </section>

      <section className="mt-12 rounded-3xl bg-gradient-to-br from-brand-800 to-accent-500 p-8 text-white">
        <h3 className="text-2xl font-bold">Готовы попробовать?</h3>
        <p className="mt-2 max-w-xl text-white/90">
          Тест занимает 25 минут, и его можно проходить с перерывами — прогресс сохраняется автоматически.
        </p>
        <div className="mt-5">
          <Link to="/onboarding" className="rounded-xl bg-white px-5 py-3 text-sm font-semibold text-brand-900">
            Начать тест
          </Link>
        </div>
      </section>
    </div>
  );
}

function Feature({ icon, title, body }: { icon: React.ReactNode; title: string; body: string }) {
  return (
    <div className="card p-5">
      <span className="grid h-10 w-10 place-content-center rounded-xl bg-brand-50 dark:bg-brand-900/40 text-brand-700 dark:text-brand-200">
        {icon}
      </span>
      <h3 className="mt-3 font-semibold">{title}</h3>
      <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">{body}</p>
    </div>
  );
}
