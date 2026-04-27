from __future__ import annotations

import csv
import io
import json
import os
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests

from lead_utils import send_pushover_notification, send_sendgrid_email

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DEFAULT_DB_PATH = DATA_DIR / "visitor_analytics.db"

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _env_true(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "y", "on"}


def validate_email(email: str) -> bool:
    return bool(EMAIL_RE.match((email or "").strip()))


# ---------------------------------------------------------------------------
# Storage selection
# ---------------------------------------------------------------------------

def use_supabase() -> bool:
    explicit = os.getenv("ANALYTICS_STORAGE", "").strip().lower()
    if explicit in {"supabase", "postgres"}:
        return True
    if explicit in {"sqlite", "local"}:
        return False
    return bool(os.getenv("SUPABASE_URL", "").strip() and os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip())


def visitors_table() -> str:
    return os.getenv("SUPABASE_VISITORS_TABLE", "visitors").strip() or "visitors"


def interactions_table() -> str:
    return os.getenv("SUPABASE_INTERACTIONS_TABLE", "interactions").strip() or "interactions"


# ---------------------------------------------------------------------------
# Supabase REST helpers
# ---------------------------------------------------------------------------

def _supabase_base_url() -> str:
    url = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
    if not url:
        raise RuntimeError("SUPABASE_URL is missing. Add it in Render/Hugging Face secrets.")
    return f"{url}/rest/v1"


def _supabase_headers(prefer: str | None = None) -> dict[str, str]:
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not key:
        raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY is missing. Add it in backend secrets.")
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    if prefer:
        headers["Prefer"] = prefer
    return headers


def _sb_get(table: str, params: dict[str, str] | None = None) -> list[dict[str, Any]]:
    response = requests.get(
        f"{_supabase_base_url()}/{table}",
        headers=_supabase_headers(),
        params=params or {},
        timeout=20,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"Supabase GET failed: {response.status_code} {response.text}")
    return response.json()


def _sb_insert(table: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(
        f"{_supabase_base_url()}/{table}",
        headers=_supabase_headers("return=representation"),
        data=json.dumps(payload, ensure_ascii=False),
        timeout=20,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"Supabase INSERT failed: {response.status_code} {response.text}")
    data = response.json()
    return data[0] if isinstance(data, list) and data else payload


def _sb_patch(table: str, query: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.patch(
        f"{_supabase_base_url()}/{table}?{query}",
        headers=_supabase_headers("return=representation"),
        data=json.dumps(payload, ensure_ascii=False),
        timeout=20,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"Supabase UPDATE failed: {response.status_code} {response.text}")
    data = response.json()
    return data[0] if isinstance(data, list) and data else payload


# ---------------------------------------------------------------------------
# SQLite fallback helpers
# ---------------------------------------------------------------------------

def get_db_path() -> Path:
    configured = os.getenv("VISITOR_DB_PATH", "").strip()
    return Path(configured) if configured else DEFAULT_DB_PATH


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_sqlite_db() -> None:
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
                visitor_name TEXT,
                visitor_email TEXT,
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
        # Backward-compatible migrations for old local SQLite DBs.
        existing_cols = {row["name"] for row in conn.execute("PRAGMA table_info(interactions)").fetchall()}
        if "visitor_name" not in existing_cols:
            conn.execute("ALTER TABLE interactions ADD COLUMN visitor_name TEXT")
        if "visitor_email" not in existing_cols:
            conn.execute("ALTER TABLE interactions ADD COLUMN visitor_email TEXT")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_interactions_visitor ON interactions(visitor_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_interactions_created ON interactions(created_at)")
        conn.commit()


def init_db() -> None:
    # Supabase tables must be created once using supabase_schema.sql.
    if use_supabase():
        return
    init_sqlite_db()


# ---------------------------------------------------------------------------
# Public data operations used by app.py and api_server.py
# ---------------------------------------------------------------------------

def create_or_update_visitor(payload: dict[str, Any]) -> dict[str, Any]:
    name = _clean(payload.get("name"))
    email = _clean(payload.get("email")).lower()
    if not name:
        raise ValueError("Name is required before using ShaileshGPT.")
    if not email or not validate_email(email):
        raise ValueError("A valid email is required before using ShaileshGPT.")

    now = utc_now()
    record = {
        "name": name,
        "email": email,
        "phone": _clean(payload.get("phone")),
        "linkedin": _clean(payload.get("linkedin")),
        "github": _clean(payload.get("github")),
        "website": _clean(payload.get("website")),
        "other_contact": _clean(payload.get("other_contact")),
        "source": _clean(payload.get("source")) or "ShaileshGPT",
        "user_agent": _clean(payload.get("user_agent")),
        "ip_address": _clean(payload.get("ip_address")),
        "last_seen_at": now,
    }

    if use_supabase():
        existing = _sb_get(visitors_table(), {"email": f"eq.{email}", "select": "*", "limit": "1"})
        if existing:
            visitor_id = existing[0]["visitor_id"]
            visitor = _sb_patch(visitors_table(), f"visitor_id=eq.{quote(visitor_id)}", record)
            is_new = False
        else:
            visitor_id = str(uuid.uuid4())
            visitor = _sb_insert(visitors_table(), {"visitor_id": visitor_id, **record, "created_at": now})
            is_new = True
    else:
        init_sqlite_db()
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
                        record["name"],
                        record["phone"],
                        record["linkedin"],
                        record["github"],
                        record["website"],
                        record["other_contact"],
                        record["source"],
                        record["user_agent"],
                        record["ip_address"],
                        record["last_seen_at"],
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
                        record["name"],
                        record["email"],
                        record["phone"],
                        record["linkedin"],
                        record["github"],
                        record["website"],
                        record["other_contact"],
                        record["source"],
                        record["user_agent"],
                        record["ip_address"],
                        now,
                        now,
                    ),
                )
                is_new = True
            conn.commit()
        visitor = get_visitor(visitor_id) or {"visitor_id": visitor_id, **record, "created_at": now}

    if visitor and (is_new or _env_true("NOTIFY_RETURNING_VISITORS", "false")):
        notify_visitor_registered(visitor, is_new=is_new)

    return visitor


def get_visitor(visitor_id: str) -> dict[str, Any] | None:
    if not visitor_id:
        return None

    if use_supabase():
        rows = _sb_get(visitors_table(), {"visitor_id": f"eq.{visitor_id}", "select": "*", "limit": "1"})
        return rows[0] if rows else None

    init_sqlite_db()
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
    visitor = require_visitor(visitor_id)
    interaction_id = str(uuid.uuid4())
    now = utc_now()
    question = _clean(question)
    answer_preview = _clean(answer_preview)[:1500]
    metadata_json = json.dumps(metadata or {}, ensure_ascii=False)

    record = {
        "interaction_id": interaction_id,
        "visitor_id": visitor_id,
        "visitor_name": visitor.get("name", ""),
        "visitor_email": visitor.get("email", ""),
        "channel": channel,
        "interaction_type": interaction_type,
        "question": question,
        "answer_preview": answer_preview,
        "metadata_json": metadata_json,
        "created_at": now,
    }

    if use_supabase():
        _sb_insert(interactions_table(), record)
        _sb_patch(visitors_table(), f"visitor_id=eq.{quote(visitor_id)}", {"last_seen_at": now})
    else:
        init_sqlite_db()
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO interactions
                (interaction_id, visitor_id, visitor_name, visitor_email, channel, interaction_type, question, answer_preview, metadata_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    interaction_id,
                    visitor_id,
                    record["visitor_name"],
                    record["visitor_email"],
                    channel,
                    interaction_type,
                    question,
                    answer_preview,
                    metadata_json,
                    now,
                ),
            )
            conn.execute("UPDATE visitors SET last_seen_at=? WHERE visitor_id=?", (now, visitor_id))
            conn.commit()

    response_record = {
        **record,
        "metadata": metadata or {},
    }

    if _env_true("QUESTION_NOTIFY_ENABLED", "true"):
        notify_interaction(visitor, response_record)

    return response_record


def update_interaction_answer(interaction_id: str, answer_preview: str) -> None:
    answer_preview = _clean(answer_preview)[:1500]
    if not interaction_id:
        return

    if use_supabase():
        _sb_patch(interactions_table(), f"interaction_id=eq.{quote(interaction_id)}", {"answer_preview": answer_preview})
        return

    init_sqlite_db()
    with get_connection() as conn:
        conn.execute(
            "UPDATE interactions SET answer_preview=? WHERE interaction_id=?",
            (answer_preview, interaction_id),
        )
        conn.commit()


def export_summary(limit: int = 100) -> dict[str, Any]:
    limit = max(1, min(int(limit), 500))

    if use_supabase():
        visitors = _sb_get(
            visitors_table(),
            {
                "select": "*",
                "order": "last_seen_at.desc",
                "limit": str(limit),
            },
        )
        interactions = _sb_get(
            interactions_table(),
            {
                "select": "*",
                "order": "created_at.desc",
                "limit": str(limit),
            },
        )
    else:
        init_sqlite_db()
        with get_connection() as conn:
            visitors = [dict(row) for row in conn.execute("SELECT * FROM visitors ORDER BY last_seen_at DESC LIMIT ?", (limit,)).fetchall()]
            interactions = [
                dict(row)
                for row in conn.execute(
                    """
                    SELECT i.*, v.name AS joined_name, v.email AS joined_email
                    FROM interactions i
                    JOIN visitors v ON v.visitor_id = i.visitor_id
                    ORDER BY i.created_at DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
            ]

    return {
        "storage": "supabase" if use_supabase() else "sqlite",
        "visitors": visitors,
        "interactions": interactions,
    }


def export_interactions_csv(limit: int = 1000) -> str:
    payload = export_summary(limit=limit)
    output = io.StringIO()
    fieldnames = [
        "created_at",
        "visitor_name",
        "visitor_email",
        "channel",
        "interaction_type",
        "question",
        "answer_preview",
        "metadata_json",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in payload.get("interactions", []):
        writer.writerow({key: row.get(key, "") for key in fieldnames})
    return output.getvalue()


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

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
    if _env_true("EMAIL_EACH_QUESTION", "false"):
        send_sendgrid_email(f"ShaileshGPT question from {visitor.get('name')}", message)
