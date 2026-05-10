"""Seed catalogue & psychometric tests.

Universities and specialization codes mirror real Kazakhstan
institutions and the государственный классификатор специальностей РК
(post-2024 codification, e.g. ``6B06101 — Информатика``). Test items are
adapted from validated Russian-language translations of the original
RIASEC, Big Five (BFI), Multiple Intelligences (Gardner) and Schwartz
work-values inventories — re-worded to fit a high-school applicant audience.

Run via ``python -m app.db.seed`` after ``alembic upgrade head``.
The seed is idempotent: it skips inserts where the row already exists.
"""

from __future__ import annotations

import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import AsyncSessionLocal
from app.models import Question, Specialization, Test, University

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Universities & specializations
# ---------------------------------------------------------------------------

UNIVERSITIES: list[dict] = [
    {
        "name_ru": "Назарбаев Университет",
        "name_en": "Nazarbayev University",
        "short_name": "NU",
        "city": "Астана",
        "website": "https://nu.edu.kz",
    },
    {
        "name_ru": "Евразийский национальный университет имени Л. Н. Гумилёва",
        "name_en": "L. N. Gumilyov Eurasian National University",
        "short_name": "ЕНУ",
        "city": "Астана",
        "website": "https://www.enu.kz",
    },
    {
        "name_ru": "Astana IT University",
        "name_en": "Astana IT University",
        "short_name": "AITU",
        "city": "Астана",
        "website": "https://astanait.edu.kz",
    },
    {
        "name_ru": "Университет КАЗГЮУ им. М. С. Нарикбаева",
        "name_en": "M. Narikbayev KAZGUU University",
        "short_name": "KAZGUU",
        "city": "Астана",
        "website": "https://kazguu.kz",
    },
    {
        "name_ru": "Казахский национальный университет имени аль-Фараби",
        "name_en": "Al-Farabi Kazakh National University",
        "short_name": "КазНУ",
        "city": "Алматы",
        "website": "https://www.kaznu.kz",
    },
    {
        "name_ru": "Казахстанско-Британский технический университет",
        "name_en": "Kazakh-British Technical University",
        "short_name": "КБТУ",
        "city": "Алматы",
        "website": "https://kbtu.edu.kz",
    },
    {
        "name_ru": "Международный университет информационных технологий",
        "name_en": "International Information Technology University",
        "short_name": "МУИТ",
        "city": "Алматы",
        "website": "https://iitu.edu.kz",
    },
    {
        "name_ru": "Almaty Management University",
        "name_en": "Almaty Management University",
        "short_name": "AlmaU",
        "city": "Алматы",
        "website": "https://almau.edu.kz",
    },
    {
        "name_ru": "Университет Нархоз",
        "name_en": "Narxoz University",
        "short_name": "Narxoz",
        "city": "Алматы",
        "website": "https://narxoz.kz",
    },
    {
        "name_ru": "Казахский национальный медицинский университет имени С. Д. Асфендиярова",
        "name_en": "Asfendiyarov Kazakh National Medical University",
        "short_name": "КазНМУ",
        "city": "Алматы",
        "website": "https://kaznmu.edu.kz",
    },
    {
        "name_ru": "Университет имени Сулеймана Демиреля",
        "name_en": "Suleyman Demirel University",
        "short_name": "SDU",
        "city": "Алматы",
        "website": "https://sdu.edu.kz",
    },
    {
        "name_ru": "Торайгыров университет",
        "name_en": "Toraighyrov University",
        "short_name": "ТОУ",
        "city": "Павлодар",
        "website": "https://tou.edu.kz",
    },
    {
        "name_ru": "Карагандинский университет имени академика Е. А. Букетова",
        "name_en": "Karaganda Buketov University",
        "short_name": "КарУ",
        "city": "Қарағанды",
        "website": "https://buketov.edu.kz",
    },
    {
        "name_ru": "Медицинский университет Караганды",
        "name_en": "Karaganda Medical University",
        "short_name": "МУК",
        "city": "Қарағанды",
        "website": "https://qmu.kz",
    },
    {
        "name_ru": "Южно-Казахстанский университет имени М. Ауэзова",
        "name_en": "M. Auezov South Kazakhstan University",
        "short_name": "ЮКУ",
        "city": "Шымкент",
        "website": "https://auezov.edu.kz",
    },
    {
        "name_ru": "Международный казахско-турецкий университет имени Х. А. Ясави (филиал)",
        "name_en": "Akhmet Yassawi International Kazakh-Turkish University",
        "short_name": "МКТУ",
        "city": "Шымкент",
        "website": "https://ayu.edu.kz",
    },
    {
        "name_ru": "Южно-Казахстанская медицинская академия",
        "name_en": "South Kazakhstan Medical Academy",
        "short_name": "ЮКМА",
        "city": "Шымкент",
        "website": "https://skma.edu.kz",
    },
]


# Specializations: code, name_ru, name_en, description_ru, category, university short_name(s)
SPECIALIZATIONS: list[dict] = [
    # ------------------- IT (12) -------------------
    ("6B06101", "Информатика", "Computer Science", "Алгоритмы, структуры данных, разработка ПО.", "IT", ["KAZGUU", "AITU", "КазНУ", "КБТУ", "SDU"]),
    ("6B06102", "Программная инженерия", "Software Engineering", "Промышленная разработка ПО, тестирование, DevOps.", "IT", ["AITU", "КБТУ", "МУИТ", "NU", "ТОУ"]),
    ("6B06103", "Информационные системы", "Information Systems", "Проектирование корпоративных информационных систем.", "IT", ["МУИТ", "ЕНУ", "ЮКУ"]),
    ("6B06104", "Кибербезопасность", "Cybersecurity", "Защита информации, криптография, реагирование на инциденты.", "IT", ["AITU", "КБТУ", "МУИТ"]),
    ("6B06105", "Искусственный интеллект", "Artificial Intelligence", "Машинное обучение, нейросети, обработка языка и зрения.", "IT", ["AITU", "NU", "КБТУ"]),
    ("6B06106", "Анализ данных и Big Data", "Data Science & Big Data", "Статистика, BI, инженерия данных.", "IT", ["МУИТ", "AITU", "Narxoz"]),
    ("6B06107", "Робототехника и мехатроника", "Robotics & Mechatronics", "Встраиваемые системы, ROS, промышленная автоматизация.", "IT", ["NU", "КБТУ", "ЕНУ"]),
    ("6B06108", "Вычислительная техника и ПО", "Computer Engineering", "Архитектура ЭВМ, низкоуровневое программирование.", "IT", ["КарУ", "ТОУ"]),
    ("6B06109", "Геймдев и компьютерная графика", "Game Development & CG", "Движки, шейдеры, дизайн уровней.", "IT", ["AITU", "SDU"]),
    ("6B06110", "Цифровая трансформация бизнеса", "Digital Business Transformation", "FinTech, продуктовый менеджмент, дата-driven процессы.", "IT", ["AlmaU", "Narxoz"]),
    ("6B06111", "Облачные технологии", "Cloud Computing", "AWS / Azure / GCP, k8s, SRE.", "IT", ["МУИТ", "AITU"]),
    ("6B06112", "Web и мобильная разработка", "Web & Mobile Development", "Frontend, backend, iOS / Android.", "IT", ["AITU", "SDU", "КБТУ"]),

    # ------------------- Engineering (10) -------------------
    ("6B07101", "Электроэнергетика", "Electric Power Engineering", "Энергосистемы, возобновляемая энергетика.", "Engineering", ["ЕНУ", "ТОУ", "КарУ"]),
    ("6B07102", "Автоматизация и управление", "Automation & Control", "АСУ ТП, SCADA, промышленная робототехника.", "Engineering", ["ЕНУ", "КарУ", "ТОУ"]),
    ("6B07103", "Нефтегазовое дело", "Oil and Gas Engineering", "Бурение, добыча, переработка углеводородов.", "Engineering", ["КБТУ", "NU", "ТОУ", "ЮКУ"]),
    ("6B07104", "Машиностроение", "Mechanical Engineering", "CAD/CAM, проектирование машин и механизмов.", "Engineering", ["ЕНУ", "КарУ", "ТОУ"]),
    ("6B07301", "Строительство", "Civil Engineering", "Расчёт конструкций, BIM, организация СМР.", "Engineering", ["ЕНУ", "ЮКУ", "КарУ"]),
    ("6B07401", "Архитектура", "Architecture", "Градостроение, архитектурное проектирование.", "Engineering", ["ЮКУ", "ЕНУ"]),
    ("6B07501", "Транспорт и логистика", "Transport & Logistics", "Цепочки поставок, smart-логистика.", "Engineering", ["AlmaU", "Narxoz", "ТОУ"]),
    ("6B07601", "Геология и разведка месторождений", "Geology & Exploration", "Минеральные ресурсы, геофизика.", "Engineering", ["КБТУ", "ТОУ", "КарУ"]),
    ("6B07701", "Металлургия", "Metallurgy", "Чёрная и цветная металлургия, материаловедение.", "Engineering", ["КарУ", "ТОУ"]),
    ("6B07801", "Прикладная физика", "Applied Physics", "Эксперимент, моделирование, лазерные системы.", "Engineering", ["NU", "КазНУ", "ЕНУ"]),

    # ------------------- Medicine (8) -------------------
    ("6B10101", "Лечебное дело", "General Medicine", "Подготовка врачей широкого профиля.", "Medicine", ["КазНМУ", "МУК", "ЮКМА", "МКТУ"]),
    ("6B10102", "Стоматология", "Dentistry", "Терапевтическая, ортопедическая, детская стоматология.", "Medicine", ["КазНМУ", "МУК", "ЮКМА"]),
    ("6B10103", "Педиатрия", "Pediatrics", "Здоровье детей, неонатология.", "Medicine", ["КазНМУ", "МУК"]),
    ("6B10104", "Фармация", "Pharmacy", "Фармакология, технологии лекарственных форм.", "Medicine", ["КазНМУ", "ЮКМА"]),
    ("6B10201", "Общественное здравоохранение", "Public Health", "Эпидемиология, организация здравоохранения.", "Medicine", ["МУК", "КазНМУ"]),
    ("6B10301", "Сестринское дело", "Nursing", "Подготовка специалистов сестринского дела.", "Medicine", ["МУК", "ЮКМА", "КазНМУ"]),
    ("6B10401", "Биомедицинская инженерия", "Biomedical Engineering", "Медицинская техника, биосигналы.", "Medicine", ["NU", "КазНМУ"]),
    ("6B10501", "Психология здоровья", "Health Psychology", "Психосоматика, поведенческая медицина.", "Medicine", ["КазНУ", "КарУ"]),

    # ------------------- Economics (10) -------------------
    ("6B04101", "Экономика", "Economics", "Микро- и макроэкономика, эконометрика.", "Economics", ["Narxoz", "AlmaU", "ЕНУ", "КазНУ"]),
    ("6B04102", "Финансы", "Finance", "Банковское дело, корпоративные финансы.", "Economics", ["Narxoz", "AlmaU", "КБТУ"]),
    ("6B04103", "Учёт и аудит", "Accounting & Auditing", "МСФО, внутренний контроль.", "Economics", ["Narxoz", "AlmaU", "ЕНУ"]),
    ("6B04104", "Менеджмент", "Management", "Стратегия, операционный менеджмент.", "Economics", ["AlmaU", "Narxoz", "КБТУ"]),
    ("6B04105", "Маркетинг", "Marketing", "Бренд-менеджмент, цифровой маркетинг.", "Economics", ["AlmaU", "SDU"]),
    ("6B04106", "Государственное и местное управление", "Public Administration", "Госслужба, политика, бюджетирование.", "Economics", ["ЕНУ", "AlmaU"]),
    ("6B04107", "Международные отношения и торговля", "International Relations & Trade", "ВЭД, дипломатия.", "Economics", ["KAZGUU", "КазНУ"]),
    ("6B04108", "Бизнес-аналитика", "Business Analytics", "BI, продуктовая аналитика.", "Economics", ["AlmaU", "Narxoz", "AITU"]),
    ("6B04109", "Туризм и гостиничное дело", "Tourism & Hospitality", "Гостеприимство, ивент-менеджмент.", "Economics", ["ЮКУ", "AlmaU"]),
    ("6B04110", "Логистика и SCM", "Logistics & SCM", "Управление цепями поставок.", "Economics", ["ТОУ", "Narxoz"]),

    # ------------------- Law (6) -------------------
    ("6B04201", "Юриспруденция", "Jurisprudence", "Гражданское, уголовное, конституционное право.", "Law", ["KAZGUU", "КазНУ", "ЕНУ", "ЮКУ"]),
    ("6B04202", "Международное право", "International Law", "Право ВТО, EAЭС, договорное право.", "Law", ["KAZGUU", "КазНУ"]),
    ("6B04203", "Таможенное дело", "Customs Affairs", "Таможенное регулирование, ВЭД.", "Law", ["ЕНУ", "ЮКУ"]),
    ("6B04204", "Право интеллектуальной собственности", "IP Law", "Патентное и авторское право.", "Law", ["KAZGUU"]),
    ("6B04205", "Криминалистика и судебная экспертиза", "Forensic Science", "Расследование, экспертиза.", "Law", ["KAZGUU", "КарУ"]),
    ("6B04206", "Юриспруденция в IT", "Tech & IT Law", "GDPR, защита персональных данных, e-commerce.", "Law", ["KAZGUU", "AITU"]),

    # ------------------- Pedagogy (8) -------------------
    ("6B01101", "Педагогика и психология", "Pedagogy & Psychology", "Возрастная психология, инклюзивное образование.", "Pedagogy", ["КазНУ", "ЕНУ", "КарУ"]),
    ("6B01201", "Дошкольное обучение и воспитание", "Pre-school Education", "Развитие речи, игровые методики.", "Pedagogy", ["ЮКУ", "КарУ", "МКТУ"]),
    ("6B01301", "Педагогика и методика начального обучения", "Primary Education", "Подготовка учителей начальных классов.", "Pedagogy", ["ЕНУ", "ЮКУ", "ТОУ"]),
    ("6B01401", "Подготовка учителей информатики", "ICT Teacher Training", "Методика преподавания информатики.", "Pedagogy", ["AITU", "ЕНУ"]),
    ("6B01402", "Подготовка учителей физики", "Physics Teacher Training", "Эксперимент в школе, методика.", "Pedagogy", ["ЕНУ", "КарУ"]),
    ("6B01403", "Подготовка учителей математики", "Mathematics Teacher Training", "Алгебра, геометрия, методика.", "Pedagogy", ["ЕНУ", "КарУ", "ЮКУ"]),
    ("6B01404", "Подготовка учителей казахского языка и литературы", "Kazakh Language & Lit Teacher", "Литературоведение, методика.", "Pedagogy", ["ЕНУ", "КазНУ", "МКТУ"]),
    ("6B01405", "Подготовка учителей английского языка", "English Teacher Training", "TEFL, билингвальное обучение.", "Pedagogy", ["SDU", "ЕНУ", "ЮКУ"]),

    # ------------------- Arts (6) -------------------
    ("6B02101", "Дизайн", "Design", "Графический, промышленный, цифровой дизайн.", "Arts", ["AlmaU", "ЮКУ", "AITU"]),
    ("6B02102", "Изобразительное искусство", "Fine Arts", "Живопись, графика, скульптура.", "Arts", ["КазНУ", "ЮКУ"]),
    ("6B02103", "Журналистика", "Journalism", "Цифровые медиа, расследовательская журналистика.", "Arts", ["КазНУ", "ЕНУ", "AlmaU"]),
    ("6B02104", "Связи с общественностью", "Public Relations", "PR, корпоративные коммуникации.", "Arts", ["AlmaU", "Narxoz"]),
    ("6B02105", "Кино и телережиссура", "Film & TV Directing", "Сценарий, монтаж, режиссура.", "Arts", ["КазНУ", "AlmaU"]),
    ("6B02106", "Музыка и звукорежиссура", "Music & Sound Design", "Композиция, аранжировка, звукорежиссура.", "Arts", ["КазНУ", "ЮКУ"]),
]


# ---------------------------------------------------------------------------
# Tests + questions
# ---------------------------------------------------------------------------

# Holland Code (RIASEC) — 42 items, Likert 1..5, 7 per dimension.
HOLLAND_QUESTIONS: list[tuple[str, str]] = [
    # Realistic
    ("Мне нравится разбирать и собирать механизмы, чтобы понять, как они работают.", "R"),
    ("Я с удовольствием работаю руками: ремонтирую, мастерю, что-то собираю.", "R"),
    ("Мне комфортнее на свежем воздухе, чем в офисе.", "R"),
    ("Я бы выбрал работу, где видны конкретные физические результаты труда.", "R"),
    ("Меня привлекает обращение с инструментами и техникой.", "R"),
    ("Я охотно занимаюсь спортом или физическими упражнениями.", "R"),
    ("Мне нравятся практические задачи больше, чем абстрактные.", "R"),
    # Investigative
    ("Я люблю изучать, как устроены явления, и докапываться до первопричин.", "I"),
    ("Мне интересно проводить эксперименты и анализировать результаты.", "I"),
    ("Я с удовольствием решаю задачи, где нужно много думать.", "I"),
    ("Мне нравится читать научные статьи и книги.", "I"),
    ("Я готов(а) подолгу разбираться в одной теме, чтобы понять её глубоко.", "I"),
    ("Мне нравится математика, физика, биология или другие точные/естественные науки.", "I"),
    ("Я бы хотел(а) работать в исследовательской лаборатории.", "I"),
    # Artistic
    ("Я часто придумываю что-то новое: рисую, пишу, сочиняю.", "A"),
    ("Мне нравится самовыражаться через искусство, музыку или текст.", "A"),
    ("Я предпочитаю свободу и нестандартный подход формальностям.", "A"),
    ("Мне интересны фильмы, выставки, театр.", "A"),
    ("Я могу долго работать над эстетикой деталей в проекте.", "A"),
    ("Я охотно беру творческие задачи без чётких инструкций.", "A"),
    ("Мне комфортно в среде, где ценят креативность и оригинальность.", "A"),
    # Social
    ("Мне нравится помогать другим людям решать их проблемы.", "S"),
    ("Я легко нахожу общий язык с разными людьми.", "S"),
    ("Я охотно объясняю сложные вещи простыми словами.", "S"),
    ("Мне приятно поддерживать тех, кому трудно.", "S"),
    ("Я бы хотел(а) работать в школе, больнице или общественной организации.", "S"),
    ("Мне нравится работать в команде больше, чем в одиночку.", "S"),
    ("Я внимателен/внимательна к чувствам и эмоциям окружающих.", "S"),
    # Enterprising
    ("Мне нравится убеждать людей и вести их за собой.", "E"),
    ("Я готов(а) брать на себя ответственность за общий результат.", "E"),
    ("Мне интересно открывать собственное дело.", "E"),
    ("Меня привлекает соревнование и амбициозные цели.", "E"),
    ("Я умею договариваться и нахожу взаимовыгодные решения.", "E"),
    ("Мне нравится организовывать мероприятия и проекты.", "E"),
    ("Я не боюсь публично выступать перед большой аудиторией.", "E"),
    # Conventional
    ("Мне нравится работать с цифрами, документами и таблицами.", "C"),
    ("Я люблю, когда дела разложены по полочкам и есть чёткий порядок.", "C"),
    ("Я внимателен/внимательна к деталям и редко делаю ошибки в мелочах.", "C"),
    ("Мне комфортно следовать установленным процедурам и правилам.", "C"),
    ("Я хорошо планирую время и придерживаюсь графика.", "C"),
    ("Мне нравится систематизировать информацию.", "C"),
    ("Я ответственно отношусь к выполнению инструкций.", "C"),
]


# Big Five (BFI extended) — 30 items.
BIG_FIVE_QUESTIONS: list[tuple[str, str, bool]] = [
    # Openness (O) — 6
    ("У меня яркое воображение и я часто погружаюсь в фантазии.", "O", False),
    ("Мне интересны новые идеи и философские темы.", "O", False),
    ("Я ценю произведения искусства и красоту.", "O", False),
    ("Я предпочитаю проторённые пути необычным экспериментам.", "O", True),
    ("Мне быстро становится скучно от однообразных задач.", "O", False),
    ("Я люблю изучать новые культуры и традиции.", "O", False),
    # Conscientiousness (C) — 6
    ("Я довожу начатое до конца, даже если становится сложно.", "C", False),
    ("Я тщательно готовлюсь к важным задачам.", "C", False),
    ("Я часто откладываю дела на последний момент.", "C", True),
    ("У меня обычно порядок в вещах и в делах.", "C", False),
    ("Я бываю беспечным/беспечной в важных вопросах.", "C", True),
    ("Я стараюсь придерживаться чёткого расписания.", "C", False),
    # Extraversion (E) — 6
    ("Я заряжаюсь энергией от общения с людьми.", "E", False),
    ("Я предпочитаю проводить время в одиночестве, чем в шумной компании.", "E", True),
    ("Я легко завожу новые знакомства.", "E", False),
    ("Мне комфортно быть в центре внимания.", "E", False),
    ("Меня часто называют молчаливым/молчаливой.", "E", True),
    ("Я с удовольствием вступаю в живые дискуссии.", "E", False),
    # Agreeableness (A) — 6
    ("Я склонен(а) доверять людям с первой встречи.", "A", False),
    ("Я готов(а) сотрудничать, даже если это не выгодно мне лично.", "A", False),
    ("Я могу быть жёстким/жёсткой и принципиальным/принципиальной.", "A", True),
    ("Мне важно поддерживать гармонию в отношениях.", "A", False),
    ("Я с уважением отношусь к чужим точкам зрения.", "A", False),
    ("Я легко прощаю людям ошибки.", "A", False),
    # Neuroticism (N) — 6
    ("Я часто волнуюсь без видимой причины.", "N", False),
    ("Я остаюсь спокойным/спокойной в стрессовых ситуациях.", "N", True),
    ("Меня легко расстроить.", "N", False),
    ("Я часто переживаю из-за мелочей.", "N", False),
    ("Я уверенно держусь даже под давлением.", "N", True),
    ("У меня бывают резкие перепады настроения.", "N", False),
]


# Multiple Intelligences (Gardner) — 40 items, 5 per type.
MI_QUESTIONS: list[tuple[str, str]] = [
    # Linguistic
    ("Я легко подбираю точные слова, когда хочу что-то выразить.", "linguistic"),
    ("Я люблю читать книги в свободное время.", "linguistic"),
    ("У меня хорошая память на стихи, цитаты и афоризмы.", "linguistic"),
    ("Мне нравится играть со словами: каламбуры, рифмы, ребусы.", "linguistic"),
    ("Мне хорошо даётся изучение иностранных языков.", "linguistic"),
    # Logical
    ("Я быстро вижу логические закономерности в данных.", "logical"),
    ("Мне нравятся задачи на логику и математику.", "logical"),
    ("Я люблю играть в шахматы или другие стратегические игры.", "logical"),
    ("Мне комфортно работать с числовой информацией.", "logical"),
    ("Я часто проверяю аргументы на наличие логических ошибок.", "logical"),
    # Spatial
    ("Я могу легко представить объект в 3D в уме.", "spatial"),
    ("Я хорошо ориентируюсь в незнакомом городе по карте.", "spatial"),
    ("Мне нравится рисовать, чертить или строить модели.", "spatial"),
    ("Я замечаю визуальные детали, которые упускают другие.", "spatial"),
    ("Мне легко пользоваться графическими редакторами или CAD-программами.", "spatial"),
    # Musical
    ("Я различаю фальшивые ноты и тонкие нюансы звука.", "musical"),
    ("Мне легко запоминать мелодии после первого прослушивания.", "musical"),
    ("Я ловлю себя на том, что напеваю или отбиваю ритм.", "musical"),
    ("Я играю на музыкальном инструменте или хотел(а) бы научиться.", "musical"),
    ("Музыка сильно влияет на моё настроение.", "musical"),
    # Bodily
    ("Я хорошо координирую движения тела.", "bodily"),
    ("Мне нравятся виды деятельности, требующие физической ловкости.", "bodily"),
    ("Я часто учусь чему-то новому через практику, а не теорию.", "bodily"),
    ("Я легко осваиваю новые виды спорта или танцы.", "bodily"),
    ("Я могу долго заниматься рукоделием, не уставая.", "bodily"),
    # Interpersonal
    ("Я хорошо считываю эмоции других по их мимике и интонации.", "interpersonal"),
    ("Друзья часто обращаются ко мне за советом.", "interpersonal"),
    ("Мне нравится работать в команде.", "interpersonal"),
    ("Я быстро понимаю мотивы поведения людей.", "interpersonal"),
    ("Я могу мирить ссорящихся между собой людей.", "interpersonal"),
    # Intrapersonal
    ("Я хорошо понимаю свои сильные и слабые стороны.", "intrapersonal"),
    ("Я регулярно размышляю о своих целях и ценностях.", "intrapersonal"),
    ("Я веду дневник или планирую жизнь долгосрочно.", "intrapersonal"),
    ("Мне комфортно одному/одной со своими мыслями.", "intrapersonal"),
    ("Я редко делаю что-то, что противоречит моим внутренним принципам.", "intrapersonal"),
    # Naturalistic
    ("Меня интересует природа, животные и растения.", "naturalistic"),
    ("Я различаю породы животных, виды деревьев или птиц.", "naturalistic"),
    ("Мне нравится бывать на природе и в походах.", "naturalistic"),
    ("Я переживаю по поводу экологических проблем.", "naturalistic"),
    ("Я с удовольствием смотрю документальные фильмы про природу.", "naturalistic"),
]


# Work values — 14 Likert + 1 ranking + 5 paired choice = 20 items.
VALUES_LIKERT: list[tuple[str, str]] = [
    ("Для меня важно самостоятельно принимать решения о том, как и что делать.", "autonomy"),
    ("Я стремлюсь работать над уникальными, нестандартными проектами.", "creativity"),
    ("Мне важна стабильная и предсказуемая занятость.", "stability"),
    ("Высокий уровень дохода — важный фактор моего выбора профессии.", "income"),
    ("Я хочу, чтобы моя работа приносила пользу обществу.", "social_impact"),
    ("Мне важно, чтобы моя профессия вызывала уважение окружающих.", "prestige"),
    ("Мне быстро надоедает однообразная деятельность.", "variety"),
    ("Я готов(а) работать без чёткого графика, если задачи интересные.", "autonomy"),
    ("Я люблю придумывать новые идеи и подходы.", "creativity"),
    ("Я предпочитаю гарантированный оклад любым переменным выплатам.", "stability"),
    ("Хорошая зарплата мотивирует меня сильнее, чем интересные задачи.", "income"),
    ("Я хочу решать важные социальные или экологические проблемы.", "social_impact"),
    ("Мне приятно, когда статус моей профессии заметен в обществе.", "prestige"),
    ("Я хочу, чтобы каждый день в работе был чем-то непохож на предыдущий.", "variety"),
]

# Final ranking question across all 7 value dims.
VALUES_RANKING: list[tuple[str, dict]] = [
    (
        "Расположите ценности от наиболее важной для вас (вверху) к наименее важной (внизу).",
        {
            "items": [
                {"key": "autonomy", "label": "Автономия — свобода решать самому"},
                {"key": "creativity", "label": "Творчество — создавать новое"},
                {"key": "stability", "label": "Стабильность — предсказуемость"},
                {"key": "income", "label": "Доход — высокая зарплата"},
                {"key": "social_impact", "label": "Социальное воздействие — польза людям"},
                {"key": "prestige", "label": "Престиж — уважение и статус"},
                {"key": "variety", "label": "Разнообразие — много разных задач"},
            ]
        },
    ),
]

# Paired choice (forced choice) — gives extra weight to the chosen value.
VALUES_CHOICE: list[tuple[str, dict, str]] = [
    (
        "Что для вас важнее: высокая зарплата или интересные задачи?",
        {"options": [{"key": "income", "label": "Высокая зарплата"}, {"key": "creativity", "label": "Интересные задачи"}]},
        "choice",
    ),
    (
        "Что предпочтёте: стабильную работу в крупной компании или собственный проект?",
        {"options": [{"key": "stability", "label": "Стабильная работа"}, {"key": "autonomy", "label": "Собственный проект"}]},
        "choice",
    ),
    (
        "Где вам комфортнее: работа с чёткими процессами или работа без шаблонов?",
        {"options": [{"key": "stability", "label": "Чёткие процессы"}, {"key": "variety", "label": "Без шаблонов"}]},
        "choice",
    ),
    (
        "Что мотивирует сильнее: видимое влияние на общество или быстрый карьерный рост?",
        {"options": [{"key": "social_impact", "label": "Влияние на общество"}, {"key": "prestige", "label": "Карьерный рост"}]},
        "choice",
    ),
    (
        "Что вам интереснее: разнообразие проектов или глубокое мастерство в одной теме?",
        {"options": [{"key": "variety", "label": "Разнообразие"}, {"key": "autonomy", "label": "Глубокое мастерство"}]},
        "choice",
    ),
]


# Cognitive style — 10 items, Likert 1..5.
COGNITIVE_QUESTIONS: list[tuple[str, str]] = [
    ("Я предпочитаю принимать решения на основе фактов и анализа, а не интуиции.", "analytical"),
    ("В сложной ситуации я составляю план и пошагово его выполняю.", "analytical"),
    ("Я часто полагаюсь на «внутренний голос» при принятии решений.", "intuitive"),
    ("Я могу быстро принять решение, не имея всех данных.", "intuitive"),
    ("Я люблю детально разбирать вопрос перед действием.", "detail"),
    ("Я замечаю мелкие несоответствия в текстах или таблицах.", "detail"),
    ("Я мыслю крупными категориями: вижу систему целиком.", "big_picture"),
    ("Я охотнее работаю над стратегией, чем над операционными деталями.", "big_picture"),
    ("Мне нравится разбираться в нюансах, даже если это занимает много времени.", "detail"),
    ("Я могу одновременно держать в уме несколько связанных идей.", "big_picture"),
]


# ---------------------------------------------------------------------------
# Seeding logic
# ---------------------------------------------------------------------------


async def _seed_universities(db: AsyncSession) -> dict[str, University]:
    res = await db.execute(select(University))
    existing = {u.short_name: u for u in res.scalars().all()}
    by_short: dict[str, University] = dict(existing)
    for u in UNIVERSITIES:
        if u["short_name"] in by_short:
            continue
        uni = University(**u)
        db.add(uni)
        by_short[u["short_name"]] = uni
    await db.flush()
    return by_short


async def _seed_specializations(
    db: AsyncSession, universities: dict[str, University]
) -> None:
    res = await db.execute(select(Specialization))
    existing = {(s.code, s.university_id) for s in res.scalars().all()}
    for code, name_ru, name_en, desc, category, uni_shorts in SPECIALIZATIONS:
        for short in uni_shorts:
            uni = universities.get(short)
            if uni is None:
                continue
            if (code, uni.id) in existing:
                continue
            # Mostly grant-available (true), with some on contract for variety.
            grant_available = (hash((code, short)) % 3) != 0
            tuition = 600_000 + (abs(hash((code, short))) % 12) * 100_000
            db.add(
                Specialization(
                    university_id=uni.id,
                    code=code,
                    name_ru=name_ru,
                    name_en=name_en,
                    description_ru=desc,
                    category=category,
                    grant_available=grant_available,
                    tuition_cost=tuition,
                )
            )
    await db.flush()


async def _seed_test(
    db: AsyncSession,
    *,
    slug: str,
    title_ru: str,
    title_en: str,
    description_ru: str,
    category: str,
    order_num: int,
    questions: list[dict],
) -> None:
    res = await db.execute(select(Test).where(Test.slug == slug))
    test = res.scalar_one_or_none()
    if test is None:
        test = Test(
            slug=slug,
            title_ru=title_ru,
            title_en=title_en,
            description_ru=description_ru,
            category=category,
            order_num=order_num,
        )
        db.add(test)
        await db.flush()
    # If questions already exist, skip — keeps re-seed idempotent.
    res = await db.execute(select(Question).where(Question.test_id == test.id))
    if res.scalars().first():
        return
    for idx, q in enumerate(questions, start=1):
        db.add(
            Question(
                test_id=test.id,
                order_num=idx,
                text_ru=q["text_ru"],
                question_type=q["question_type"],
                options=q.get("options"),
                meta=q.get("meta"),
            )
        )
    await db.flush()


def _holland_questions_payload() -> list[dict]:
    return [
        {
            "text_ru": text,
            "question_type": "scale",
            "options": {"min": 1, "max": 5, "min_label": "Совсем не про меня", "max_label": "Полностью про меня"},
            "meta": {"trait": trait, "reverse": False},
        }
        for text, trait in HOLLAND_QUESTIONS
    ]


def _big_five_questions_payload() -> list[dict]:
    return [
        {
            "text_ru": text,
            "question_type": "scale",
            "options": {"min": 1, "max": 5, "min_label": "Совсем не согласен", "max_label": "Полностью согласен"},
            "meta": {"trait": trait, "reverse": reverse},
        }
        for text, trait, reverse in BIG_FIVE_QUESTIONS
    ]


def _mi_questions_payload() -> list[dict]:
    return [
        {
            "text_ru": text,
            "question_type": "scale",
            "options": {"min": 1, "max": 5, "min_label": "Совсем не про меня", "max_label": "Полностью про меня"},
            "meta": {"trait": trait, "reverse": False},
        }
        for text, trait in MI_QUESTIONS
    ]


def _values_questions_payload() -> list[dict]:
    payload: list[dict] = []
    for text, trait in VALUES_LIKERT:
        payload.append(
            {
                "text_ru": text,
                "question_type": "scale",
                "options": {"min": 1, "max": 5, "min_label": "Не важно", "max_label": "Очень важно"},
                "meta": {"trait": trait, "reverse": False},
            }
        )
    for text, options in VALUES_RANKING:
        payload.append(
            {
                "text_ru": text,
                "question_type": "ranking",
                "options": options,
                "meta": {"reverse": False},
            }
        )
    for text, options, _qtype in VALUES_CHOICE:
        payload.append(
            {
                "text_ru": text,
                "question_type": "choice",
                "options": options,
                "meta": {"reverse": False},
            }
        )
    return payload


def _cognitive_questions_payload() -> list[dict]:
    return [
        {
            "text_ru": text,
            "question_type": "scale",
            "options": {"min": 1, "max": 5, "min_label": "Совсем не про меня", "max_label": "Полностью про меня"},
            "meta": {"trait": trait, "reverse": False},
        }
        for text, trait in COGNITIVE_QUESTIONS
    ]


async def seed(db: AsyncSession) -> None:
    universities = await _seed_universities(db)
    await _seed_specializations(db, universities)

    await _seed_test(
        db,
        slug="holland",
        title_ru="Тест Холланда (RIASEC)",
        title_en="Holland Code (RIASEC)",
        description_ru=(
            "42 вопроса о ваших профессиональных интересах. Помогает определить, "
            "к какому из шести типов профессий вы тяготеете."
        ),
        category="interests",
        order_num=1,
        questions=_holland_questions_payload(),
    )
    await _seed_test(
        db,
        slug="big_five",
        title_ru="Большая пятёрка личности",
        title_en="Big Five Personality",
        description_ru=(
            "30 утверждений, которые описывают ключевые черты вашей личности по модели Big Five."
        ),
        category="personality",
        order_num=2,
        questions=_big_five_questions_payload(),
    )
    await _seed_test(
        db,
        slug="mi",
        title_ru="Множественный интеллект (Гарднер)",
        title_en="Multiple Intelligences",
        description_ru=(
            "40 вопросов о восьми типах интеллекта: лингвистическом, логико-математическом, "
            "пространственном, музыкальном, телесном, межличностном, внутриличностном и натуралистическом."
        ),
        category="intelligence",
        order_num=3,
        questions=_mi_questions_payload(),
    )
    await _seed_test(
        db,
        slug="values",
        title_ru="Ценности в работе",
        title_en="Work Values",
        description_ru=(
            "20 заданий, чтобы выявить, что для вас в работе ключевое: автономия, "
            "стабильность, доход, творчество, влияние и т.д."
        ),
        category="values",
        order_num=4,
        questions=_values_questions_payload(),
    )
    await _seed_test(
        db,
        slug="cognitive",
        title_ru="Когнитивный стиль",
        title_en="Cognitive Style",
        description_ru=(
            "10 вопросов о том, как вы думаете: аналитически или интуитивно, "
            "видите детали или общую картину."
        ),
        category="cognition",
        order_num=5,
        questions=_cognitive_questions_payload(),
    )

    await db.commit()


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    async with AsyncSessionLocal() as db:
        await seed(db)
    logger.info("Seed completed successfully.")


if __name__ == "__main__":
    asyncio.run(main())
