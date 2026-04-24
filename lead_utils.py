from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from typing import Any

import requests


def _clean(value: str | None) -> str:
    return (value or "").strip()


def _has_meaningful_contact(payload: dict[str, Any]) -> bool:
    fields = ["email", "phone", "linkedin", "github", "website", "other_contact"]
    return any(_clean(str(payload.get(field, ""))) for field in fields)


def _valid_email(email: str) -> bool:
    if not email:
        return True
    return re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", email) is not None


def format_lead_message(payload: dict[str, Any]) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        "New portfolio chatbot lead",
        f"Time: {timestamp}",
        "",
        f"Name: {_clean(payload.get('name')) or 'Not provided'}",
        f"Email: {_clean(payload.get('email')) or 'Not provided'}",
        f"Phone: {_clean(payload.get('phone')) or 'Not provided'}",
        f"LinkedIn: {_clean(payload.get('linkedin')) or 'Not provided'}",
        f"GitHub: {_clean(payload.get('github')) or 'Not provided'}",
        f"Website: {_clean(payload.get('website')) or 'Not provided'}",
        f"Other contact: {_clean(payload.get('other_contact')) or 'Not provided'}",
        "",
        f"Intent / Message: {_clean(payload.get('message')) or 'Not provided'}",
        f"Source: {_clean(payload.get('source')) or 'Portfolio chatbot'}",
    ]
    return "\n".join(lines)


def send_pushover_notification(message: str) -> bool:
    user = os.getenv("PUSHOVER_USER")
    token = os.getenv("PUSHOVER_TOKEN")
    if not user or not token:
        return False

    try:
        response = requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": token,
                "user": user,
                "message": message[:1024],
                "title": "Portfolio Chatbot Lead",
                "priority": 0,
            },
            timeout=12,
        )
        return response.ok
    except Exception:
        return False


def send_sendgrid_email(subject: str, message: str) -> bool:
    api_key = os.getenv("SENDGRID_API_KEY")
    to_email = os.getenv("LEAD_NOTIFY_EMAIL") or os.getenv("OWNER_EMAIL") or "shaileshgupta841@gmail.com"
    from_email = os.getenv("LEAD_FROM_EMAIL") or os.getenv("SENDGRID_FROM_EMAIL")

    if not api_key or not from_email or not to_email:
        return False

    payload = {
        "personalizations": [
            {
                "to": [{"email": to_email}],
                "subject": subject,
            }
        ],
        "from": {"email": from_email, "name": "ShaileshGPT Lead Bot"},
        "content": [
            {
                "type": "text/plain",
                "value": message,
            }
        ],
    }

    try:
        response = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=15,
        )
        return response.status_code in {200, 202}
    except Exception:
        return False


def capture_lead(payload: dict[str, Any]) -> dict[str, Any]:
    cleaned = {
        "name": _clean(payload.get("name")),
        "email": _clean(payload.get("email")),
        "phone": _clean(payload.get("phone")),
        "linkedin": _clean(payload.get("linkedin")),
        "github": _clean(payload.get("github")),
        "website": _clean(payload.get("website")),
        "other_contact": _clean(payload.get("other_contact")),
        "message": _clean(payload.get("message")),
        "source": _clean(payload.get("source")) or "Portfolio chatbot",
    }

    if not _has_meaningful_contact(cleaned):
        return {
            "ok": False,
            "message": "Please share at least one contact method so Shailesh can get back to you.",
            "pushover_sent": False,
            "email_sent": False,
        }

    if not _valid_email(cleaned["email"]):
        return {
            "ok": False,
            "message": "That email format looks off. Please check it once.",
            "pushover_sent": False,
            "email_sent": False,
        }

    lead_message = format_lead_message(cleaned)
    pushover_sent = send_pushover_notification(lead_message)
    email_sent = send_sendgrid_email("New lead from ShaileshGPT portfolio chatbot", lead_message)

    return {
        "ok": True,
        "message": "Done — I sent Shailesh your details. Now the ball is in his court, and thankfully he likes cricket.",
        "pushover_sent": pushover_sent,
        "email_sent": email_sent,
    }
