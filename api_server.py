from __future__ import annotations

import json
import os
import tempfile
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Generator

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agentic_rag import get_portfolio_bot
from build_kb import main as build_kb_main
from lead_utils import capture_lead
from jd_matcher import evaluate_jd_fit, extract_text_from_upload
from analytics_db import create_or_update_visitor, export_summary, log_interaction, require_visitor, update_interaction_answer


ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env", override=True)

CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4.1-mini")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
INDEX_PATH = ROOT / "data" / "kb_index.json"

if not INDEX_PATH.exists():
    build_kb_main()

BOT = get_portfolio_bot(CHAT_MODEL, EMBEDDING_MODEL)

RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "30"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "3600"))
_RATE_BUCKETS: dict[str, deque[float]] = defaultdict(deque)


def _client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def enforce_rate_limit(request: Request) -> None:
    key = _client_key(request)
    now = time.time()
    bucket = _RATE_BUCKETS[key]

    while bucket and now - bucket[0] > RATE_LIMIT_WINDOW_SECONDS:
        bucket.popleft()

    if len(bucket) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="Rate limit reached. Please try again later.",
        )

    bucket.append(now)


app = FastAPI(title="ShaileshGPT Portfolio Chat API", version="2.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str
    content: str


class VisitorStartRequest(BaseModel):
    name: str
    email: str
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    website: str = ""
    other_contact: str = ""
    source: str = "ShaileshGPT"
    user_agent: str = ""


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []
    visitor_id: str = ""


class LeadRequest(BaseModel):
    visitor_id: str = ""
    name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    website: str = ""
    other_contact: str = ""
    message: str = ""
    source: str = "Website widget"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/visitor/start")
def visitor_start(payload: VisitorStartRequest, request: Request) -> dict[str, object]:
    enforce_rate_limit(request)
    try:
        visitor = create_or_update_visitor({**payload.model_dump(), "ip_address": _client_key(request)})
        return {
            "ok": True,
            "visitor_id": visitor["visitor_id"],
            "name": visitor["name"],
            "email": visitor["email"],
            "message": "Thanks — you can now use ShaileshGPT.",
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/analytics/summary")
def analytics_summary(request: Request) -> dict[str, object]:
    token = os.getenv("ANALYTICS_ADMIN_TOKEN", "").strip()
    supplied = request.headers.get("x-admin-token", "").strip()
    if not token or supplied != token:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return export_summary(limit=200)


@app.post("/chat")
def chat(payload: ChatRequest, request: Request) -> dict[str, str]:
    enforce_rate_limit(request)
    try:
        require_visitor(payload.visitor_id)
    except Exception as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    history = [item.model_dump() for item in payload.history]
    result = BOT.answer(payload.message, chat_history=history)
    log_interaction(
        payload.visitor_id,
        payload.message,
        answer_preview=result.answer,
        channel="api",
        interaction_type="chat_question",
    )
    return {"answer": result.answer}


@app.post("/chat_stream")
def chat_stream(payload: ChatRequest, request: Request) -> StreamingResponse:
    enforce_rate_limit(request)
    try:
        require_visitor(payload.visitor_id)
    except Exception as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    history = [item.model_dump() for item in payload.history]

    def event_stream() -> Generator[str, None, None]:
        interaction = None
        collected: list[str] = []
        try:
            interaction = log_interaction(
                payload.visitor_id,
                payload.message,
                channel="website_or_api_stream",
                interaction_type="chat_question",
            )
            for token in BOT.answer_stream(payload.message, chat_history=history):
                collected.append(token)
                yield f"data: {json.dumps({'token': token})}\n\n"
            if interaction:
                update_interaction_answer(interaction["interaction_id"], "".join(collected))
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'error': f'{type(exc).__name__}: {exc}'})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/lead")
def lead(payload: LeadRequest, request: Request) -> dict[str, object]:
    enforce_rate_limit(request)
    result = capture_lead(payload.model_dump())
    if payload.visitor_id:
        try:
            log_interaction(
                payload.visitor_id,
                payload.message or "Submitted contact details",
                channel="website_or_gradio",
                interaction_type="lead_submission",
                metadata=payload.model_dump(),
            )
        except Exception:
            pass
    return result


@app.post("/jd_fit")
async def jd_fit(
    request: Request,
    file: UploadFile = File(...),
    question: str = Form("Evaluate Shailesh for this role."),
    visitor_id: str = Form(""),
) -> dict[str, str]:
    enforce_rate_limit(request)
    try:
        require_visitor(visitor_id)
    except Exception as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    suffix = Path(file.filename or "uploaded_jd.txt").suffix or ".txt"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)

    try:
        jd_text = extract_text_from_upload(str(tmp_path))
        answer = evaluate_jd_fit(BOT, jd_text, question)
        log_interaction(
            visitor_id,
            f"JD upload: {file.filename or 'uploaded_jd'} | Question: {question}",
            answer_preview=answer,
            channel="api_jd_fit",
            interaction_type="jd_fit_analysis",
            metadata={"filename": file.filename or "uploaded_jd"},
        )
        return {"answer": answer}
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass
