from __future__ import annotations

import csv
import io
import json
import os
import re
import sqlite3
import uuid
from collections import Counter
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


def normalize_question(question: str) -> str:
    q = re.sub(r"\s+", " ", (question or "").strip().lower())
    q = re.sub(r"[^\w\s?.:/-]", "", q)
    return q[:240]


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


def sessions_table() -> str:
    return os.getenv("SUPABASE_SESSIONS_TABLE", "conversation_sessions").strip() or "conversation_sessions"


def messages_table() -> str:
    return os.getenv("SUPABASE_MESSAGES_TABLE", "conversation_messages").strip() or "conversation_messages"


def usage_table() -> str:
    return os.getenv("SUPABASE_USAGE_TABLE", "usage_events").strip() or "usage_events"


def _supabase_base_url() -> str:
    url = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
    if not url:
        raise RuntimeError("SUPABASE_URL is missing.")
    if url.endswith("/rest/v1"):
        url = url[:-8].rstrip("/")
    return f"{url}/rest/v1"


def _supabase_headers(prefer: str | None = None) -> dict[str, str]:
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not key:
        raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY is missing.")
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
        timeout=25,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"Supabase GET failed: {response.status_code} {response.text}")
    return response.json()


def _sb_insert(table: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(
        f"{_supabase_base_url()}/{table}",
        headers=_supabase_headers("return=representation"),
        data=json.dumps(payload, ensure_ascii=False),
        timeout=25,
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
        timeout=25,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"Supabase UPDATE failed: {response.status_code} {response.text}")
    data = response.json()
    return data[0] if isinstance(data, list) and data else payload


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


def _sqlite_cols(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}


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
            CREATE TABLE IF NOT EXISTS conversation_sessions (
                session_id TEXT PRIMARY KEY,
                visitor_id TEXT NOT NULL,
                visitor_name TEXT,
                visitor_email TEXT,
                source TEXT,
                created_at TEXT NOT NULL,
                last_activity_at TEXT NOT NULL
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
                session_id TEXT,
                channel TEXT NOT NULL,
                interaction_type TEXT NOT NULL,
                question TEXT NOT NULL,
                normalized_question TEXT,
                answer_preview TEXT,
                metadata_json TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversation_messages (
                message_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                visitor_id TEXT NOT NULL,
                interaction_id TEXT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        cols = _sqlite_cols(conn, "interactions")
        additions = {
            "visitor_name": "ALTER TABLE interactions ADD COLUMN visitor_name TEXT",
            "visitor_email": "ALTER TABLE interactions ADD COLUMN visitor_email TEXT",
            "session_id": "ALTER TABLE interactions ADD COLUMN session_id TEXT",
            "normalized_question": "ALTER TABLE interactions ADD COLUMN normalized_question TEXT",
        }
        for col, ddl in additions.items():
            if col not in cols:
                conn.execute(ddl)

        conn.execute("CREATE INDEX IF NOT EXISTS idx_interactions_created ON interactions(created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_interactions_question ON interactions(normalized_question)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS usage_events (
                usage_id TEXT PRIMARY KEY,
                visitor_id TEXT,
                visitor_name TEXT,
                visitor_email TEXT,
                session_id TEXT,
                interaction_id TEXT,
                feature TEXT NOT NULL,
                model TEXT NOT NULL,
                input_tokens_estimate INTEGER NOT NULL,
                output_tokens_estimate INTEGER NOT NULL,
                total_tokens_estimate INTEGER NOT NULL,
                estimated_cost_usd REAL NOT NULL,
                used_owner_key INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_session ON conversation_messages(session_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_created ON usage_events(created_at)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_visitor ON usage_events(visitor_id)")
        conn.commit()


def init_db() -> None:
    if use_supabase():
        return
    init_sqlite_db()


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
            existing = conn.execute("SELECT * FROM visitors WHERE email=?", (email,)).fetchone()
            if existing:
                visitor_id = existing["visitor_id"]
                conn.execute(
                    """
                    UPDATE visitors
                    SET name=?, phone=?, linkedin=?, github=?, website=?, other_contact=?, source=?, user_agent=?, ip_address=?, last_seen_at=?
                    WHERE visitor_id=?
                    """,
                    (
                        record["name"], record["phone"], record["linkedin"], record["github"], record["website"],
                        record["other_contact"], record["source"], record["user_agent"], record["ip_address"],
                        record["last_seen_at"], visitor_id
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
                        visitor_id, record["name"], record["email"], record["phone"], record["linkedin"],
                        record["github"], record["website"], record["other_contact"], record["source"],
                        record["user_agent"], record["ip_address"], now, now
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
        row = conn.execute("SELECT * FROM visitors WHERE visitor_id=?", (visitor_id,)).fetchone()
    return dict(row) if row else None


def require_visitor(visitor_id: str) -> dict[str, Any]:
    visitor = get_visitor(visitor_id)
    if not visitor:
        raise ValueError("Please enter your name and email before using ShaileshGPT.")
    return visitor


def create_session(visitor: dict[str, Any], source: str = "ShaileshGPT") -> str:
    now = utc_now()
    session_id = str(uuid.uuid4())
    record = {
        "session_id": session_id,
        "visitor_id": visitor["visitor_id"],
        "visitor_name": visitor.get("name", ""),
        "visitor_email": visitor.get("email", ""),
        "source": source,
        "created_at": now,
        "last_activity_at": now,
    }
    if use_supabase():
        _sb_insert(sessions_table(), record)
    else:
        init_sqlite_db()
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO conversation_sessions
                (session_id, visitor_id, visitor_name, visitor_email, source, created_at, last_activity_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record["session_id"], record["visitor_id"], record["visitor_name"], record["visitor_email"],
                    record["source"], record["created_at"], record["last_activity_at"]
                ),
            )
            conn.commit()
    return session_id


def session_exists(session_id: str) -> bool:
    session_id = _clean(session_id)
    if not session_id:
        return False

    if use_supabase():
        rows = _sb_get(sessions_table(), {"session_id": f"eq.{session_id}", "select": "session_id", "limit": "1"})
        return bool(rows)

    init_sqlite_db()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT session_id FROM conversation_sessions WHERE session_id=?",
            (session_id,),
        ).fetchone()
    return bool(row)


def create_session_with_id(visitor: dict[str, Any], session_id: str, source: str = "ShaileshGPT") -> str:
    session_id = _clean(session_id) or str(uuid.uuid4())
    now = utc_now()
    record = {
        "session_id": session_id,
        "visitor_id": visitor["visitor_id"],
        "visitor_name": visitor.get("name", ""),
        "visitor_email": visitor.get("email", ""),
        "source": source,
        "created_at": now,
        "last_activity_at": now,
    }

    if use_supabase():
        _sb_insert(sessions_table(), record)
    else:
        init_sqlite_db()
        with get_connection() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO conversation_sessions
                (session_id, visitor_id, visitor_name, visitor_email, source, created_at, last_activity_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record["session_id"],
                    record["visitor_id"],
                    record["visitor_name"],
                    record["visitor_email"],
                    record["source"],
                    record["created_at"],
                    record["last_activity_at"],
                ),
            )
            conn.commit()

    return session_id


def get_or_create_session(visitor: dict[str, Any], session_id: str = "", source: str = "ShaileshGPT") -> str:
    session_id = _clean(session_id)

    if not session_id:
        return create_session(visitor, source=source)

    if session_exists(session_id):
        return session_id

    return create_session_with_id(visitor, session_id=session_id, source=source)


def insert_message(visitor_id: str, session_id: str, role: str, content: str, interaction_id: str = "") -> None:
    if not session_id or not content:
        return
    now = utc_now()
    record = {
        "message_id": str(uuid.uuid4()),
        "session_id": session_id,
        "visitor_id": visitor_id,
        "interaction_id": interaction_id or None,
        "role": role,
        "content": content,
        "created_at": now,
    }
    try:
        if use_supabase():
            _sb_insert(messages_table(), record)
            _sb_patch(sessions_table(), f"session_id=eq.{quote(session_id)}", {"last_activity_at": now})
        else:
            init_sqlite_db()
            with get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO conversation_messages
                    (message_id, session_id, visitor_id, interaction_id, role, content, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record["message_id"], record["session_id"], record["visitor_id"], record["interaction_id"],
                        record["role"], record["content"], record["created_at"]
                    ),
                )
                conn.execute("UPDATE conversation_sessions SET last_activity_at=? WHERE session_id=?", (now, session_id))
                conn.commit()
    except Exception:
        return


def log_interaction(
    visitor_id: str,
    question: str,
    answer_preview: str = "",
    channel: str = "unknown",
    interaction_type: str = "chat_question",
    metadata: dict[str, Any] | None = None,
    session_id: str = "",
) -> dict[str, Any]:
    visitor = require_visitor(visitor_id)
    session_id = get_or_create_session(visitor, session_id=session_id, source=channel)
    interaction_id = str(uuid.uuid4())
    now = utc_now()
    question = _clean(question)
    answer_preview = _clean(answer_preview)[:4000]
    normalized_question = normalize_question(question)
    metadata_json = json.dumps(metadata or {}, ensure_ascii=False)

    record = {
        "interaction_id": interaction_id,
        "visitor_id": visitor_id,
        "visitor_name": visitor.get("name", ""),
        "visitor_email": visitor.get("email", ""),
        "session_id": session_id,
        "channel": channel,
        "interaction_type": interaction_type,
        "question": question,
        "normalized_question": normalized_question,
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
                (interaction_id, visitor_id, visitor_name, visitor_email, session_id, channel, interaction_type, question, normalized_question, answer_preview, metadata_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    interaction_id, visitor_id, record["visitor_name"], record["visitor_email"], session_id, channel,
                    interaction_type, question, normalized_question, answer_preview, metadata_json, now
                ),
            )
            conn.execute("UPDATE visitors SET last_seen_at=? WHERE visitor_id=?", (now, visitor_id))
            conn.commit()

    insert_message(visitor_id, session_id, "user", question, interaction_id)
    if answer_preview:
        insert_message(visitor_id, session_id, "assistant", answer_preview, interaction_id)

    response_record = {**record, "metadata": metadata or {}}
    if _env_true("QUESTION_NOTIFY_ENABLED", "true"):
        notify_interaction(visitor, response_record)
    return response_record


def update_interaction_answer(interaction_id: str, answer_preview: str) -> None:
    answer_preview = _clean(answer_preview)[:4000]
    if not interaction_id:
        return

    visitor_id = ""
    session_id = ""

    if use_supabase():
        try:
            rows = _sb_get(interactions_table(), {"interaction_id": f"eq.{interaction_id}", "select": "visitor_id,session_id", "limit": "1"})
            if rows:
                visitor_id = rows[0].get("visitor_id", "")
                session_id = rows[0].get("session_id", "")
            _sb_patch(interactions_table(), f"interaction_id=eq.{quote(interaction_id)}", {"answer_preview": answer_preview})
        except Exception:
            return
    else:
        init_sqlite_db()
        with get_connection() as conn:
            row = conn.execute("SELECT visitor_id, session_id FROM interactions WHERE interaction_id=?", (interaction_id,)).fetchone()
            if row:
                visitor_id = row["visitor_id"]
                session_id = row["session_id"]
            conn.execute("UPDATE interactions SET answer_preview=? WHERE interaction_id=?", (answer_preview, interaction_id))
            conn.commit()

    if visitor_id and session_id and answer_preview:
        insert_message(visitor_id, session_id, "assistant", answer_preview, interaction_id)



MODEL_PRICING_USD_PER_1M = {
    "gpt-4.1-mini": {"input": 0.40, "output": 1.60},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4.1": {"input": 2.00, "output": 8.00},
    "gpt-4o": {"input": 2.50, "output": 10.00},
}


def estimate_tokens(text: str) -> int:
    # Lightweight approximation: 1 token ~= 4 characters.
    return max(1, int(len(text or "") / 4))


def estimate_cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    pricing = MODEL_PRICING_USD_PER_1M.get(model, MODEL_PRICING_USD_PER_1M.get("gpt-4.1-mini"))
    return round(
        (input_tokens / 1_000_000) * pricing["input"]
        + (output_tokens / 1_000_000) * pricing["output"],
        8,
    )


def log_usage_event(
    visitor_id: str = "",
    session_id: str = "",
    interaction_id: str = "",
    feature: str = "chat",
    model: str = "gpt-4.1-mini",
    input_text: str = "",
    output_text: str = "",
    used_owner_key: bool = False,
) -> dict[str, Any]:
    visitor = get_visitor(visitor_id) if visitor_id else None
    input_tokens = estimate_tokens(input_text)
    output_tokens = estimate_tokens(output_text)
    total_tokens = input_tokens + output_tokens
    cost = estimate_cost_usd(model, input_tokens, output_tokens)
    now = utc_now()

    record = {
        "usage_id": str(uuid.uuid4()),
        "visitor_id": visitor_id or None,
        "visitor_name": visitor.get("name", "") if visitor else "",
        "visitor_email": visitor.get("email", "") if visitor else "",
        "session_id": session_id or None,
        "interaction_id": interaction_id or None,
        "feature": feature,
        "model": model,
        "input_tokens_estimate": input_tokens,
        "output_tokens_estimate": output_tokens,
        "total_tokens_estimate": total_tokens,
        "estimated_cost_usd": cost,
        "used_owner_key": bool(used_owner_key),
        "created_at": now,
    }

    try:
        if use_supabase():
            _sb_insert(usage_table(), record)
        else:
            init_sqlite_db()
            with get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO usage_events
                    (usage_id, visitor_id, visitor_name, visitor_email, session_id, interaction_id, feature, model,
                     input_tokens_estimate, output_tokens_estimate, total_tokens_estimate, estimated_cost_usd,
                     used_owner_key, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record["usage_id"],
                        record["visitor_id"],
                        record["visitor_name"],
                        record["visitor_email"],
                        record["session_id"],
                        record["interaction_id"],
                        record["feature"],
                        record["model"],
                        record["input_tokens_estimate"],
                        record["output_tokens_estimate"],
                        record["total_tokens_estimate"],
                        record["estimated_cost_usd"],
                        int(record["used_owner_key"]),
                        record["created_at"],
                    ),
                )
                conn.commit()
    except Exception:
        # Usage tracking should never break the actual user experience.
        return record

    return record


def summarize_usage_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    total_input = sum(int(e.get("input_tokens_estimate") or 0) for e in events)
    total_output = sum(int(e.get("output_tokens_estimate") or 0) for e in events)
    total_tokens = sum(int(e.get("total_tokens_estimate") or 0) for e in events)
    total_cost = sum(float(e.get("estimated_cost_usd") or 0) for e in events)
    owner_key_requests = sum(1 for e in events if bool(e.get("used_owner_key")))
    user_key_requests = len(events) - owner_key_requests

    by_feature: dict[str, dict[str, Any]] = {}
    by_model: dict[str, dict[str, Any]] = {}
    by_visitor: dict[str, dict[str, Any]] = {}

    def bump(bucket: dict[str, dict[str, Any]], key: str, event: dict[str, Any]) -> None:
        key = key or "Unknown"
        if key not in bucket:
            bucket[key] = {"requests": 0, "tokens": 0, "estimated_cost_usd": 0.0}
        bucket[key]["requests"] += 1
        bucket[key]["tokens"] += int(event.get("total_tokens_estimate") or 0)
        bucket[key]["estimated_cost_usd"] += float(event.get("estimated_cost_usd") or 0)

    for event in events:
        bump(by_feature, event.get("feature", ""), event)
        bump(by_model, event.get("model", ""), event)
        visitor_key = event.get("visitor_email") or event.get("visitor_name") or "Unknown"
        bump(by_visitor, visitor_key, event)

    for bucket in (by_feature, by_model, by_visitor):
        for value in bucket.values():
            value["estimated_cost_usd"] = round(value["estimated_cost_usd"], 8)

    return {
        "requests": len(events),
        "input_tokens_estimate": total_input,
        "output_tokens_estimate": total_output,
        "total_tokens_estimate": total_tokens,
        "estimated_cost_usd": round(total_cost, 8),
        "owner_key_requests": owner_key_requests,
        "user_key_requests": user_key_requests,
        "by_feature": by_feature,
        "by_model": by_model,
        "by_visitor": by_visitor,
    }


def export_summary(limit: int = 100) -> dict[str, Any]:
    limit = max(1, min(int(limit), 500))
    if use_supabase():
        visitors = _sb_get(visitors_table(), {"select": "*", "order": "last_seen_at.desc", "limit": str(limit)})
        interactions = _sb_get(interactions_table(), {"select": "*", "order": "created_at.desc", "limit": str(limit)})
        sessions = _sb_get(sessions_table(), {"select": "*", "order": "last_activity_at.desc", "limit": str(limit)})
        messages = _sb_get(messages_table(), {"select": "*", "order": "created_at.desc", "limit": str(limit)})
        usage_events = _sb_get(usage_table(), {"select": "*", "order": "created_at.desc", "limit": str(limit)})
    else:
        init_sqlite_db()
        with get_connection() as conn:
            visitors = [dict(row) for row in conn.execute("SELECT * FROM visitors ORDER BY last_seen_at DESC LIMIT ?", (limit,)).fetchall()]
            interactions = [dict(row) for row in conn.execute("SELECT * FROM interactions ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()]
            sessions = [dict(row) for row in conn.execute("SELECT * FROM conversation_sessions ORDER BY last_activity_at DESC LIMIT ?", (limit,)).fetchall()]
            messages = [dict(row) for row in conn.execute("SELECT * FROM conversation_messages ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()]
            usage_events = [dict(row) for row in conn.execute("SELECT * FROM usage_events ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()]

    counter: Counter[str] = Counter()
    display: dict[str, str] = {}
    for item in interactions:
        if item.get("interaction_type") != "chat_question":
            continue
        normalized = item.get("normalized_question") or normalize_question(item.get("question", ""))
        if not normalized:
            continue
        counter[normalized] += 1
        display.setdefault(normalized, item.get("question", ""))

    return {
        "storage": "supabase" if use_supabase() else "sqlite",
        "counts": {
            "visitors": len(visitors),
            "interactions": len(interactions),
            "sessions": len(sessions),
            "messages": len(messages),
            "usage_events": len(usage_events),
        },
        "usage_summary": summarize_usage_events(usage_events),
        "usage_events": usage_events,
        "visitors": visitors,
        "interactions": interactions,
        "sessions": sessions,
        "messages": messages,
        "top_questions": [
            {"question": display.get(q, q), "normalized_question": q, "count": c}
            for q, c in counter.most_common(20)
        ],
    }


def export_interactions_csv(limit: int = 1000) -> str:
    payload = export_summary(limit=limit)
    output = io.StringIO()
    fieldnames = [
        "created_at", "visitor_name", "visitor_email", "session_id", "channel", "interaction_type",
        "question", "answer_preview", "metadata_json"
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in payload.get("interactions", []):
        writer.writerow({key: row.get(key, "") for key in fieldnames})
    return output.getvalue()


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
