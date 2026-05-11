"""Anthropic Claude integration: deep career analysis + streaming chat."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator

from anthropic import AsyncAnthropic

from app.core.config import get_settings
from app.schemas.schemas import AIAnalysis
from app.services.scoring_service import (
    BIG_FIVE_LABELS,
    holland_code_letters,
)

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """\
You are an expert career counselor and psychologist specializing in Kazakhstan's education system.
You will receive psychometric test results and produce a deep, personalized career analysis in Russian.
You always reply in fluent natural Russian (the student is from Kazakhstan).
Output ONLY valid JSON. No markdown, no preamble, no postscript, no code fences."""


CHAT_SYSTEM_PROMPT = """\
You are a warm, empathetic career counselor speaking with a high-school or university applicant from Kazakhstan.
You already know the student's full psychological profile (provided as context).
You ALWAYS reply in Russian, in a friendly conversational tone, no more than 4-5 short paragraphs per reply.
You may suggest specific Kazakhstan universities and specializations from the catalogue if relevant.
Never reveal that you are Claude or an AI; refer to yourself as «ИИ-наставник»."""


def _client() -> AsyncAnthropic:
    settings = get_settings()
    return AsyncAnthropic(api_key=settings.anthropic_api_key, timeout=settings.anthropic_timeout)


def build_user_prompt(scores: dict[str, dict[str, float]], user_name: str | None = None) -> str:
    holland = scores.get("holland", {})
    big5 = scores.get("big_five", {})
    mi = scores.get("mi", {})
    vals = scores.get("values", {})
    cog = scores.get("cognitive", {})

    code = holland_code_letters(holland) if holland else "—"

    return f"""\
Имя студента: {user_name or 'аноним'}.

КОД ХОЛЛАНДА (RIASEC, %): {json.dumps(holland, ensure_ascii=False)}
Трёхбуквенный код: {code}

БОЛЬШАЯ ПЯТЁРКА (%): {json.dumps({BIG_FIVE_LABELS.get(k, k): v for k, v in big5.items()}, ensure_ascii=False)}

МНОЖЕСТВЕННЫЙ ИНТЕЛЛЕКТ (%): {json.dumps(mi, ensure_ascii=False)}

ЦЕННОСТИ В РАБОТЕ (%): {json.dumps(vals, ensure_ascii=False)}

КОГНИТИВНЫЙ СТИЛЬ (%): {json.dumps(cog, ensure_ascii=False)}

Проанализируй полный психологический профиль студента и порекомендуй карьерные пути.

Верни JSON со СТРОГО такой структурой (без обёрток, без ```json):
{{
  "personality_summary": "3-4 содержательных предложения, кто этот человек глубинно",
  "strengths": ["сильная сторона 1", "сильная сторона 2", "сильная сторона 3", "сильная сторона 4", "сильная сторона 5"],
  "growth_areas": ["зона роста 1", "зона роста 2"],
  "ideal_work_environment": "описание идеальной рабочей среды",
  "career_paths": [
    {{
      "title_ru": "название карьерного пути на русском",
      "match_score": число от 0 до 100,
      "why_match": "2-3 предложения, ПОЧЕМУ именно этот путь подходит, ссылаясь на конкретные баллы профиля",
      "specialization_categories": ["IT", "Engineering", "Medicine", "Economics", "Law", "Pedagogy", "Arts"]
    }}
  ],
  "study_tips": "персональные советы по обучению, исходя из когнитивного стиля и интеллекта",
  "motivational_message": "тёплое мотивирующее сообщение лично студенту"
}}

Категории в specialization_categories ОБЯЗАТЕЛЬНО выбирай только из списка: IT, Engineering, Medicine, Economics, Law, Pedagogy, Arts.
Верни от 6 до 10 carrier_paths, отсортированных по match_score по убыванию.
"""


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[: -3]
    return text.strip()


async def analyze(scores: dict[str, dict[str, float]], user_name: str | None = None) -> AIAnalysis:
    """Run the full career analysis with Claude.

    Falls back to a deterministic placeholder analysis if the API key is unset
    or the call fails — this keeps the app usable in demo / offline modes.
    """
    settings = get_settings()
    if not settings.anthropic_api_key:
        logger.warning("ANTHROPIC_API_KEY is empty; returning fallback analysis")
        return _fallback_analysis(scores)

    try:
        client = _client()
        message = await client.messages.create(
            model=settings.anthropic_model,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_user_prompt(scores, user_name)}],
        )
        raw = "".join(b.text for b in message.content if getattr(b, "type", "") == "text")
        raw = _strip_fences(raw)
        data = json.loads(raw)
        return AIAnalysis.model_validate(data)
    except Exception:
        logger.exception("Claude analyze failed, falling back")
        return _fallback_analysis(scores)


async def chat_stream(
    scores: dict[str, dict[str, float]] | None,
    analysis_summary: str | None,
    history: list[dict[str, str]],
) -> AsyncIterator[str]:
    """Stream a chat response from Claude as plain text chunks.

    `history` is a list of `{role, content}` dicts where role is 'user' or 'assistant'.
    The final user message must be the most recent in the list.
    """
    settings = get_settings()
    if not settings.anthropic_api_key:
        yield (
            "ИИ-наставник временно недоступен (не задан API-ключ). "
            "Однако ваши результаты сохранены — обратитесь к ним позже."
        )
        return

    context_blocks: list[str] = []
    if analysis_summary:
        context_blocks.append(f"Резюме профиля студента:\n{analysis_summary}")
    if scores:
        context_blocks.append(f"Сырые баллы по тестам:\n{json.dumps(scores, ensure_ascii=False)}")

    system = CHAT_SYSTEM_PROMPT
    if context_blocks:
        system = system + "\n\n" + "\n\n".join(context_blocks)

    api_messages = [{"role": m["role"], "content": m["content"]} for m in history]

    client = _client()
    try:
        async with client.messages.stream(
            model=settings.anthropic_model,
            max_tokens=1024,
            system=system,
            messages=api_messages,
        ) as stream:
            async for chunk in stream.text_stream:
                if chunk:
                    yield chunk
    except Exception as e:
        logger.exception("Claude chat stream failed")
        yield f"\n[ошибка ИИ: {type(e).__name__}]"


# ---------------------------------------------------------------------------
# Fallback analysis (used when key is missing or Claude errors out).
# ---------------------------------------------------------------------------


def _top_dim(d: dict[str, float], n: int = 1) -> list[tuple[str, float]]:
    return sorted(d.items(), key=lambda x: x[1], reverse=True)[:n]


def _fallback_analysis(scores: dict[str, dict[str, float]]) -> AIAnalysis:
    holland = scores.get("holland", {})
    big5 = scores.get("big_five", {})
    mi = scores.get("mi", {})
    code = holland_code_letters(holland) if holland else "RIA"
    top_mi = _top_dim(mi, 2)
    top_big5 = _top_dim(big5, 2)

    holland_label = {
        "R": "практическим",
        "I": "исследовательским",
        "A": "творческим",
        "S": "социальным",
        "E": "предприимчивым",
        "C": "организованным",
    }
    summary = (
        f"Ваш код Холланда — {code}. По профилю вы склонны к "
        f"{holland_label.get(code[0], 'разностороннему')} типам деятельности, "
        f"а ведущие виды интеллекта — {', '.join(d for d, _ in top_mi) or 'разнообразные'}. "
        "Этот фолбэк-анализ сгенерирован без ИИ — добавьте ANTHROPIC_API_KEY и запустите снова, "
        "чтобы получить полноценный персонализированный разбор."
    )

    return AIAnalysis(
        personality_summary=summary,
        strengths=[
            "Любознательность и тяга к новым знаниям",
            "Способность глубоко погружаться в задачу",
            "Чёткое следование собственным ценностям",
            "Развитая саморефлексия",
            "Готовность учиться и расти",
        ],
        growth_areas=[
            "Усилить навыки публичной презентации идей",
            "Тренировать привычку доводить начатое до конца",
        ],
        ideal_work_environment=(
            "Среда с понятными целями, возможностью углублённой работы "
            "и регулярной обратной связью от наставников."
        ),
        career_paths=[
            {
                "title_ru": "Программная инженерия и анализ данных",
                "match_score": 88,
                "why_match": (
                    "Высокий исследовательский тип Холланда и логико-математический интеллект "
                    "указывают на склонность к работе со структурой и абстракциями."
                ),
                "specialization_categories": ["IT", "Engineering"],
            },
            {
                "title_ru": "Прикладная инженерия и робототехника",
                "match_score": 80,
                "why_match": (
                    "Сочетание практического и исследовательского типов делает естественной работу "
                    "руками с одновременным проектированием решений."
                ),
                "specialization_categories": ["Engineering", "IT"],
            },
            {
                "title_ru": "Экономика и финансовая аналитика",
                "match_score": 74,
                "why_match": (
                    "Развитая добросовестность и логическое мышление помогают системно работать "
                    "с цифрами и закономерностями."
                ),
                "specialization_categories": ["Economics"],
            },
            {
                "title_ru": "Биомедицина и здравоохранение",
                "match_score": 70,
                "why_match": (
                    "Натуралистический и логический интеллект, а также ценность социального воздействия "
                    "хорошо ложатся на медицинские специальности."
                ),
                "specialization_categories": ["Medicine"],
            },
            {
                "title_ru": "Юриспруденция и государственное управление",
                "match_score": 62,
                "why_match": (
                    "Высокая добросовестность и лингвистический интеллект подходят для работы "
                    "с текстами законов и аргументацией."
                ),
                "specialization_categories": ["Law"],
            },
            {
                "title_ru": "Педагогика и образовательные технологии",
                "match_score": 60,
                "why_match": (
                    "Развитый межличностный и внутриличностный интеллект делает преподавание "
                    "органичным выбором карьеры."
                ),
                "specialization_categories": ["Pedagogy"],
            },
            {
                "title_ru": "Творческие индустрии и дизайн",
                "match_score": 55,
                "why_match": (
                    "Творческие склонности по Холланду и пространственный интеллект "
                    "поддерживают карьеру в дизайне и медиа."
                ),
                "specialization_categories": ["Arts"],
            },
        ],
        study_tips=(
            f"Опираясь на ведущие черты ({', '.join(d for d, _ in top_big5) or 'C, O'}), "
            "стройте обучение через регулярные короткие сессии глубокой работы, "
            "ведите дневник идей и обсуждайте материал с одногруппниками."
        ),
        motivational_message=(
            "Ваш профиль уникален — нет одной «правильной» специальности. "
            "Используйте эти рекомендации как карту, а не как приговор: "
            "пробуйте, ошибайтесь, адаптируйтесь. У вас всё получится."
        ),
    )
