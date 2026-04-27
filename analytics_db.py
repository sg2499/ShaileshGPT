from __future__ import annotations

import json
import os
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lead_utils import send_pushover_notification, send_sendgrid_email

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DEFAULT_DB_PATH = DATA_DIR / "visitor_analytics.db"

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def get_db_path() -> Path:
    configured = os.getenv("VISITOR_DB_PATH", "").strip()
    if configured:
        return Path(configured)
    return DEFAULT_DB_PATH


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS visitors (
                visitor_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT,
                linkedin TEXT,
                github TEXT,
                website TEXT,
                other_contact TEXT,
                source TEXT,
                user_agent TEXT,
                ip_address TEXT,
                created_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS interactions (
                interaction_id TEXT PRIMARY KEY,
                visitor_id TEXT NOT NULL,
                channel TEXT NOT NULL,
                interaction_type TEXT NOT NULL,
                question TEXT NOT NULL,
                answer_preview TEXT,
                metadata_json TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(visitor_id) REFERENCES visitors(visitor_id)
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_interactions_visitor ON interactions(visitor_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_interactions_created ON interactions(created_at)")
        conn.commit()


def validate_email(email: str) -> bool:
    return bool(EMAIL_RE.match((email or "").strip()))


def create_or_update_visitor(payload: dict[str, Any]) -> dict[str, Any]:
    init_db()
    name = str(payload.get("name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    if not name:
        raise ValueError("Name is required before using ShaileshGPT.")
    if not email or not validate_email(email):
        raise ValueError("A valid email is required before using ShaileshGPT.")

    now = utc_now()
    optional = {
        "phone": str(payload.get("phone", "")).strip(),
        "linkedin": str(payload.get("linkedin", "")).strip(),
        "github": str(payload.get("github", "")).strip(),
        "website": str(payload.get("website", "")).strip(),
        "other_contact": str(payload.get("other_contact", "")).strip(),
        "source": str(payload.get("source", "ShaileshGPT")).strip() or "ShaileshGPT",
        "user_agent": str(payload.get("user_agent", "")).strip(),
        "ip_address": str(payload.get("ip_address", "")).strip(),
    }

    with get_connection() as conn:
        existing = conn.execute("SELECT * FROM visitors WHERE email = ?", (email,)).fetchone()
        if existing:
            visitor_id = existing["visitor_id"]
            conn.execute(
                """
                UPDATE visitors
                SET name=?, phone=?, linkedin=?, github=?, website=?, other_contact=?, source=?, user_agent=?, ip_address=?, last_seen_at=?
                WHERE visitor_id=?
                """,
                (
                    name,
                    optional["phone"],
                    optional["linkedin"],
                    optional["github"],
                    optional["website"],
                    optional["other_contact"],
                    optional["source"],
                    optional["user_agent"],
                    optional["ip_address"],
                    now,
                    visitor_id,
                ),
            )
            is_new = False
        else:
            visitor_id = str(uuid.uuid4())
            conn.execute(
                """
                INSERT INTO visitors
                (visitor_id, name, email, phone, linkedin, github, website, other_contact, source, user_agent, ip_address, created_at, last_seen_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    visitor_id,
                    name,
                    email,
                    optional["phone"],
                    optional["linkedin"],
                    optional["github"],
                    optional["website"],
                    optional["other_contact"],
                    optional["source"],
                    optional["user_agent"],
                    optional["ip_address"],
                    now,
                    now,
                ),
            )
            is_new = True
        conn.commit()

    visitor = get_visitor(visitor_id)
    if visitor and (is_new or os.getenv("NOTIFY_RETURNING_VISITORS", "false").lower() == "true"):
        notify_visitor_registered(visitor, is_new=is_new)
    return visitor or {"visitor_id": visitor_id, "name": name, "email": email}


def get_visitor(visitor_id: str) -> dict[str, Any] | None:
    init_db()
    if not visitor_id:
        return None
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM visitors WHERE visitor_id = ?", (visitor_id,)).fetchone()
    return dict(row) if row else None


def require_visitor(visitor_id: str) -> dict[str, Any]:
    visitor = get_visitor(visitor_id)
    if not visitor:
        raise ValueError("Please enter your name and email before using ShaileshGPT.")
    return visitor


def log_interaction(
    visitor_id: str,
    question: str,
    answer_preview: str = "",
    channel: str = "unknown",
    interaction_type: str = "chat_question",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    init_db()
    visitor = require_visitor(visitor_id)
    interaction_id = str(uuid.uuid4())
    now = utc_now()
    question = (question or "").strip()
    answer_preview = (answer_preview or "").strip()[:1500]
    metadata_json = json.dumps(metadata or {}, ensure_ascii=False)

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO interactions
            (interaction_id, visitor_id, channel, interaction_type, question, answer_preview, metadata_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (interaction_id, visitor_id, channel, interaction_type, question, answer_preview, metadata_json, now),
        )
        conn.execute("UPDATE visitors SET last_seen_at=? WHERE visitor_id=?", (now, visitor_id))
        conn.commit()

    record = {
        "interaction_id": interaction_id,
        "visitor_id": visitor_id,
        "channel": channel,
        "interaction_type": interaction_type,
        "question": question,
        "answer_preview": answer_preview,
        "metadata": metadata or {},
        "created_at": now,
    }
    if os.getenv("QUESTION_NOTIFY_ENABLED", "true").lower() == "true":
        notify_interaction(visitor, record)
    return record


def update_interaction_answer(interaction_id: str, answer_preview: str) -> None:
    init_db()
    with get_connection() as conn:
        conn.execute(
            "UPDATE interactions SET answer_preview=? WHERE interaction_id=?",
            ((answer_preview or "").strip()[:1500], interaction_id),
        )
        conn.commit()


def notify_visitor_registered(visitor: dict[str, Any], is_new: bool = True) -> None:
    status = "New visitor registered" if is_new else "Returning visitor updated details"
    message = (
        f"{status}\n"
        f"Time: {utc_now()}\n\n"
        f"Name: {visitor.get('name')}\n"
        f"Email: {visitor.get('email')}\n"
        f"Phone: {visitor.get('phone') or 'Not provided'}\n"
        f"LinkedIn: {visitor.get('linkedin') or 'Not provided'}\n"
        f"GitHub: {visitor.get('github') or 'Not provided'}\n"
        f"Website: {visitor.get('website') or 'Not provided'}\n"
        f"Other: {visitor.get('other_contact') or 'Not provided'}\n"
        f"Source: {visitor.get('source') or 'ShaileshGPT'}"
    )
    send_pushover_notification(message)
    send_sendgrid_email(f"ShaileshGPT visitor: {visitor.get('name')}", message)


def notify_interaction(visitor: dict[str, Any], record: dict[str, Any]) -> None:
    message = (
        f"ShaileshGPT interaction\n"
        f"Time: {record.get('created_at')}\n\n"
        f"Name: {visitor.get('name')}\n"
        f"Email: {visitor.get('email')}\n"
        f"Channel: {record.get('channel')}\n"
        f"Type: {record.get('interaction_type')}\n\n"
        f"Question:\n{record.get('question')}"
    )
    send_pushover_notification(message[:1024])
    if os.getenv("EMAIL_EACH_QUESTION", "false").lower() == "true":
        send_sendgrid_email(f"ShaileshGPT question from {visitor.get('name')}", message)


def export_summary(limit: int = 100) -> dict[str, Any]:
    init_db()
    with get_connection() as conn:
        visitors = conn.execute("SELECT * FROM visitors ORDER BY last_seen_at DESC LIMIT ?", (limit,)).fetchall()
        interactions = conn.execute(
            """
            SELECT i.*, v.name, v.email
            FROM interactions i
            JOIN visitors v ON v.visitor_id = i.visitor_id
            ORDER BY i.created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return {
        "visitors": [dict(row) for row in visitors],
        "interactions": [dict(row) for row in interactions],
    }
