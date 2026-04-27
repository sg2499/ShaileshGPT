from __future__ import annotations

import json
import os
import tempfile
import time
from collections import defaultdict, deque
from pathlib import Path
from io import BytesIO
from typing import Generator

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response, StreamingResponse
from pydantic import BaseModel
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from agentic_rag import create_portfolio_bot, get_portfolio_bot
from build_kb import main as build_kb_main
from lead_utils import capture_lead
from jd_matcher import evaluate_jd_fit, extract_text_from_upload
from analytics_db import create_or_update_visitor, export_interactions_csv, export_summary, log_interaction, log_usage_event, require_visitor, update_interaction_answer


ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env", override=True)

CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4.1-mini")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
INDEX_PATH = ROOT / "data" / "kb_index.json"

if not INDEX_PATH.exists():
    build_kb_main()

BOT = get_portfolio_bot(CHAT_MODEL, EMBEDDING_MODEL)


def require_user_api_key(request: Request) -> str:
    if os.getenv("REQUIRE_USER_OPENAI_API_KEY", "false").strip().lower() not in {"1", "true", "yes", "y", "on"}:
        return ""
    key = request.headers.get("x-openai-api-key", "").strip()
    if not key:
        raise HTTPException(status_code=403, detail="Please provide your own OpenAI API key to use this public demo.")
    if not key.startswith("sk-"):
        raise HTTPException(status_code=400, detail="Invalid OpenAI API key format.")
    return key


def using_owner_key(request: Request) -> bool:
    return not bool(request.headers.get("x-openai-api-key", "").strip())


def bot_for_request(request: Request):
    session_key = require_user_api_key(request)
    if session_key:
        return create_portfolio_bot(CHAT_MODEL, EMBEDDING_MODEL, api_key=session_key)
    return BOT


def _admin_authorized(request: Request) -> bool:
    token = os.getenv("ANALYTICS_ADMIN_TOKEN", "").strip()
    supplied = request.headers.get("x-admin-token", "").strip() or request.query_params.get("token", "").strip()
    return bool(token and supplied == token)


def _require_admin(request: Request) -> None:
    if not _admin_authorized(request):
        raise HTTPException(status_code=403, detail="Unauthorized")


def build_jd_pdf_report(answer: str) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title="ShaileshGPT JD Fit Report")
    styles = getSampleStyleSheet()
    story = [Paragraph("ShaileshGPT JD Fit Report", styles["Title"]), Spacer(1, 14)]

    for raw in (answer or "").split("\n"):
        line = raw.strip()
        if not line:
            story.append(Spacer(1, 8))
            continue
        if line.startswith("#"):
            story.append(Paragraph(line.replace("#", "").strip(), styles["Heading2"]))
        else:
            safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(safe, styles["BodyText"]))
            story.append(Spacer(1, 5))

    doc.build(story)
    return buffer.getvalue()


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
    session_id: str = ""


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


@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard() -> str:
    path = ROOT / "admin_dashboard.html"
    if not path.exists():
        return "<h1>Admin dashboard file missing</h1>"
    return path.read_text(encoding="utf-8")


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
            "message": "Thanks - you can now use ShaileshGPT.",
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/analytics/summary")
def analytics_summary(request: Request) -> dict[str, object]:
    _require_admin(request)
    return export_summary(limit=300)


@app.get("/analytics/interactions.csv")
def analytics_interactions_csv(request: Request) -> Response:
    _require_admin(request)
    csv_text = export_interactions_csv(limit=2000)
    return Response(
        content=csv_text,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=shaileshgpt_interactions.csv"},
    )


@app.post("/chat")
def chat(payload: ChatRequest, request: Request) -> dict[str, str]:
    enforce_rate_limit(request)
    try:
        require_visitor(payload.visitor_id)
    except Exception as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    history = [item.model_dump() for item in payload.history]
    result = bot_for_request(request).answer(payload.message, chat_history=history)
    log_interaction(
        payload.visitor_id,
        payload.message,
        answer_preview=result.answer,
        channel="api",
        interaction_type="chat_question",
        session_id=payload.session_id,
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
                session_id=payload.session_id,
            )
            for token in bot_for_request(request).answer_stream(payload.message, chat_history=history):
                collected.append(token)
                yield f"data: {json.dumps({'token': token})}\n\n"
            final_answer = "".join(collected)
            if interaction:
                update_interaction_answer(interaction["interaction_id"], final_answer)
                log_usage_event(
                    visitor_id=payload.visitor_id,
                    session_id=payload.session_id,
                    interaction_id=interaction.get("interaction_id", ""),
                    feature="chat_stream",
                    model=CHAT_MODEL,
                    input_text=payload.message + "\n" + json.dumps([m.model_dump() for m in payload.history], ensure_ascii=False),
                    output_text=final_answer,
                    used_owner_key=using_owner_key(request),
                )
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
    session_id: str = Form(""),
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
        answer = evaluate_jd_fit(bot_for_request(request), jd_text, question)
        interaction = log_interaction(
            visitor_id,
            f"JD upload: {file.filename or 'uploaded_jd'} | Question: {question}",
            answer_preview=answer,
            channel="api_jd_fit",
            interaction_type="jd_fit_analysis",
            metadata={"filename": file.filename or "uploaded_jd"},
            session_id=session_id,
        )
        log_usage_event(
            visitor_id=visitor_id,
            session_id=session_id,
            interaction_id=interaction.get("interaction_id", ""),
            feature="jd_fit",
            model=CHAT_MODEL,
            input_text=jd_text + "\n" + question,
            output_text=answer,
            used_owner_key=using_owner_key(request),
        )
        return {"answer": answer}
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass


@app.post("/jd_fit_report")
async def jd_fit_report(
    request: Request,
    file: UploadFile = File(...),
    question: str = Form("Evaluate Shailesh for this role."),
    visitor_id: str = Form(""),
    session_id: str = Form(""),
) -> Response:
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
        answer = evaluate_jd_fit(bot_for_request(request), jd_text, question)
        interaction = log_interaction(
            visitor_id,
            f"Downloadable JD report: {file.filename or 'uploaded_jd'} | Question: {question}",
            answer_preview=answer,
            channel="api_jd_pdf_report",
            interaction_type="jd_fit_pdf_report",
            metadata={"filename": file.filename or "uploaded_jd"},
            session_id=session_id,
        )
        log_usage_event(
            visitor_id=visitor_id,
            session_id=session_id,
            interaction_id=interaction.get("interaction_id", ""),
            feature="jd_pdf_report",
            model=CHAT_MODEL,
            input_text=jd_text + "\n" + question,
            output_text=answer,
            used_owner_key=using_owner_key(request),
        )
        pdf_bytes = build_jd_pdf_report(answer)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=shaileshgpt_jd_fit_report.pdf"},
        )
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass
