"""Free open AI integration via Pollinations.ai (OpenAI-compatible, no API key).

Pollinations exposes a free, anonymous, OpenAI-compatible chat completions
endpoint at ``https://text.pollinations.ai/openai`` that supports both JSON
mode and SSE streaming. We use it as a drop-in replacement for paid LLMs so
the app works fully out-of-the-box without any credentials.
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator
from typing import Any

import httpx

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
Never reveal which underlying model you are; refer to yourself as «ИИ-наставник»."""


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
Верни ровно 6 career_paths, отсортированных по match_score по убыванию.
Будь лаконичен: краткие предложения, без воды, не повторяйся.
"""


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
    return text.strip()


def _extract_json_object(text: str) -> str:
    """Find the first balanced ``{...}`` JSON object in ``text``.

    Pollinations sometimes prepends or appends commentary even when asked
    not to; this helper recovers a parseable JSON blob from a noisy reply.
    """
    text = _strip_fences(text)
    depth = 0
    start = -1
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start != -1:
                return text[start : i + 1]
    return text


async def _stream_completion(
    *,
    messages: list[dict[str, Any]],
    json_mode: bool,
    max_tokens: int,
    timeout: float,
) -> AsyncIterator[str]:
    """POST to Pollinations with stream=true and yield content deltas.

    Skips ``delta.reasoning`` chunks (the model emits internal chain-of-thought
    before the answer) and only yields user-visible ``delta.content`` text.
    """
    settings = get_settings()
    payload: dict[str, Any] = {
        "model": settings.pollinations_model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "stream": True,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    if settings.pollinations_referer:
        payload["referrer"] = settings.pollinations_referer

    httpx_timeout = httpx.Timeout(timeout, connect=15.0, read=timeout, write=15.0)
    async with httpx.AsyncClient(timeout=httpx_timeout) as client:
        async with client.stream(
            "POST",
            settings.pollinations_url,
            json=payload,
            headers={"Content-Type": "application/json", "Accept": "text/event-stream"},
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue
                chunk_str = line[5:].strip()
                if not chunk_str or chunk_str == "[DONE]":
                    if chunk_str == "[DONE]":
                        return
                    continue
                try:
                    chunk = json.loads(chunk_str)
                except json.JSONDecodeError:
                    continue
                choices = chunk.get("choices") or []
                if not choices:
                    continue
                delta = choices[0].get("delta") or {}
                content = delta.get("content")
                if content:
                    yield content


async def analyze(scores: dict[str, dict[str, float]], user_name: str | None = None) -> AIAnalysis:
    """Run the full career analysis with Pollinations.ai.

    Uses streaming to avoid TCP read timeouts for slow reasoning models —
    we collect content deltas until the stream completes, then parse the
    full JSON object.

    Falls back to a deterministic placeholder analysis if the network call
    fails or the model returns unparseable output. This keeps the app fully
    usable in sandboxed / offline / rate-limited environments.
    """
    settings = get_settings()
    try:
        parts: list[str] = []
        async for delta in _stream_completion(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(scores, user_name)},
            ],
            json_mode=True,
            max_tokens=16384,
            timeout=settings.pollinations_timeout,
        ):
            parts.append(delta)
        full = "".join(parts)
        raw = _extract_json_object(full)
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            # Model may have been cut off — try to repair a truncated JSON.
            repaired = _repair_truncated_json(raw)
            parsed = json.loads(repaired)
        return AIAnalysis.model_validate(parsed)
    except Exception:
        logger.exception("Pollinations analyze failed, falling back to deterministic analysis")
        return _fallback_analysis(scores)


def _repair_truncated_json(text: str) -> str:
    """Best-effort repair of a JSON object the model failed to close.

    Trims to the last fully-closed top-level field, then balances brackets.
    """
    # Drop any trailing partial unicode escape, etc.
    s = text.rstrip()
    # If we're inside a string, terminate it.
    in_str = False
    escape = False
    for ch in s:
        if escape:
            escape = False
            continue
        if ch == "\\":
            escape = True
            continue
        if ch == '"':
            in_str = not in_str
    if in_str:
        s += '"'
    # Balance braces and brackets.
    open_curly = s.count("{") - s.count("}")
    open_sq = s.count("[") - s.count("]")
    # Remove a trailing comma that would now be illegal.
    s = s.rstrip()
    if s.endswith(","):
        s = s[:-1]
    s += "]" * max(0, open_sq)
    s += "}" * max(0, open_curly)
    return s


async def chat_stream(
    scores: dict[str, dict[str, float]] | None,
    analysis_summary: str | None,
    history: list[dict[str, str]],
) -> AsyncIterator[str]:
    """Stream a chat response from Pollinations as plain text chunks.

    `history` is a list of `{role, content}` dicts where role is 'user' or 'assistant'.
    The final user message must be the most recent in the list.
    """
    settings = get_settings()

    context_blocks: list[str] = []
    if analysis_summary:
        context_blocks.append(f"Резюме профиля студента:\n{analysis_summary}")
    if scores:
        context_blocks.append(
            f"Сырые баллы по тестам:\n{json.dumps(scores, ensure_ascii=False)}"
        )

    system = CHAT_SYSTEM_PROMPT
    if context_blocks:
        system = system + "\n\n" + "\n\n".join(context_blocks)

    api_messages: list[dict[str, Any]] = [{"role": "system", "content": system}]
    for m in history:
        api_messages.append({"role": m["role"], "content": m["content"]})

    try:
        async for delta in _stream_completion(
            messages=api_messages,
            json_mode=False,
            max_tokens=1024,
            timeout=settings.pollinations_timeout,
        ):
            yield delta
    except Exception as e:
        logger.exception("Pollinations chat stream failed")
        yield f"\n[ошибка ИИ: {type(e).__name__}]"


# ---------------------------------------------------------------------------
# Fallback analysis (used when the network call fails).
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
        "Этот фолбэк-анализ сгенерирован без подключения к ИИ — это значит, что "
        "сервис Pollinations.ai сейчас недоступен; обычно подключение бесплатное и не требует ключа."
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
