"""FastAPI app entrypoint."""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    analyze,
    answers,
    chat,
    health,
    results,
    sessions,
    tests,
    universities,
)
from app.core.config import get_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

settings = get_settings()

app = FastAPI(
    title="Career Guidance KZ API",
    version="0.1.0",
    description="AI-powered psychological career guidance for Kazakhstan students.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api"
for r in (sessions, answers, analyze, results, universities, tests, chat, health):
    app.include_router(r.router, prefix=API_PREFIX)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": "Career Guidance KZ API",
        "docs": "/docs",
        "health": f"{API_PREFIX}/health",
    }
