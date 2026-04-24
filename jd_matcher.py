from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from openai import OpenAI
from pypdf import PdfReader

from agentic_rag import PortfolioAgenticRAG


SUPPORTED_TEXT_EXTENSIONS = {".txt", ".md", ".csv"}
SUPPORTED_DOC_EXTENSIONS = {".pdf", ".txt", ".md", ".csv"}


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_text_from_upload(file_obj: Any) -> str:
    """Extract text from a Gradio-uploaded file.

    Supports PDF and plain-text style files. DOCX is intentionally not included
    to keep the dependency footprint light; convert DOCX to PDF before upload.
    """
    if file_obj is None:
        return ""

    path = Path(file_obj.name if hasattr(file_obj, "name") else str(file_obj))
    suffix = path.suffix.lower()

    if suffix not in SUPPORTED_DOC_EXTENSIONS:
        raise ValueError(
            "Unsupported file type. Please upload a PDF, TXT, MD, or CSV job description."
        )

    if suffix == ".pdf":
        reader = PdfReader(str(path))
        pages: list[str] = []
        for page in reader.pages:
            text = page.extract_text() or ""
            if text.strip():
                pages.append(clean_text(text))
        return "\n\n".join(pages)

    return clean_text(path.read_text(encoding="utf-8", errors="ignore"))


def trim_jd(jd_text: str, max_chars: int = 15000) -> str:
    jd_text = clean_text(jd_text)
    if len(jd_text) <= max_chars:
        return jd_text
    return jd_text[:max_chars] + "\n\n[JD truncated for analysis length.]"


def build_jd_fit_prompt(jd_text: str, extra_question: str, evidence_text: str, history_text: str = "") -> str:
    return f"""
You are Shailesh Gupta's AI portfolio twin.

A recruiter or professional has uploaded a job description. Your job is to evaluate Shailesh against the JD using ONLY:
1. the uploaded JD text, and
2. Shailesh's grounded portfolio evidence below.

Tone:
- professional, sharp, witty, lightly snarky when appropriate
- persuasive but honest
- never desperate
- never claim 100% fit; use a realistic fit range and explain tradeoffs
- if there are gaps, frame them as ramp-up areas, not deal-breakers, when reasonable; do not hide gaps
- encourage the recruiter to leave contact details if there is potential fit

Important:
- Do not expose source IDs, retrieval scores, agent traces, or internal mechanics.
- Do not invent experience or certifications.
- If JD asks for something Shailesh has not shown, say so clearly and then explain adjacent strengths.

Recent chat history:
{history_text or "No prior messages."}

Recruiter's extra question:
{extra_question or "Evaluate Shailesh for this role."}

Uploaded JD:
{jd_text}

Shailesh portfolio evidence:
{evidence_text}

Now produce a concise recruiter-facing answer.

Rules for length and style:
- Keep it between 450 and 750 words unless the recruiter explicitly asks for a deep dive.
- Start with the verdict immediately. No warm-up paragraph.
- Use short sections and bullet points.
- Do not dump every possible match. Pick the strongest proof.
- Be persuasive without sounding desperate.
- End with a clear contact nudge asking the recruiter to leave their details through the Connect section.

Use this structure:

## Verdict: [Strong Fit / Good Fit / Partial Fit / Stretch Fit] — [percentage range]

One sharp 2-3 sentence summary of why.

## Strongest matches
- Requirement → Shailesh proof point
- Requirement → Shailesh proof point
- Requirement → Shailesh proof point
- Requirement → Shailesh proof point

## Gaps / ramp-up areas
- Gap: honest note + why it is manageable, if it is manageable.
- Gap: honest note + adjacent strength.

## Best proof points
- Relevant experience/project/certification 1
- Relevant experience/project/certification 2
- Relevant experience/project/certification 3

## Recruiter takeaway
A persuasive closing that says whether he is worth interviewing and nudges them to leave their email, phone, LinkedIn, or preferred contact route in the Connect section.
"""


def evaluate_jd_fit(
    bot: PortfolioAgenticRAG,
    jd_text: str,
    extra_question: str = "",
    chat_history: list[dict[str, str]] | None = None,
) -> str:
    jd_text = trim_jd(jd_text)
    if not jd_text:
        return "Upload a JD first — I need the role description before I start pretending to be a hiring committee."

    # Retrieve candidate evidence using JD + focused query rewrites.
    retrieval_queries = [
        jd_text[:1200],
        extra_question or "job fit evaluation",
        "skills experience projects certifications AI ML LLM data scientist",
        "Teleperformance Azure Databricks PySpark machine learning deployment",
        "Deep Research Agent RAG agents LLM engineering OpenAI",
    ]

    evidence_pool: dict[str, dict[str, Any]] = {}
    for query in retrieval_queries:
        for chunk in bot.kb.retrieve(
            query,
            allowed_collections=[
                "identity",
                "professional_summary",
                "skills",
                "experience",
                "education",
                "certifications",
                "projects",
                "target_roles_and_industries",
                "strengths_and_values",
                "source_documents",
            ],
            top_k=10,
        ):
            key = chunk["source_id"]
            if key not in evidence_pool or chunk["weighted_score"] > evidence_pool[key]["weighted_score"]:
                evidence_pool[key] = chunk

    evidence = sorted(evidence_pool.values(), key=lambda x: x["weighted_score"], reverse=True)[:14]
    evidence_blocks = []
    for i, item in enumerate(evidence, start=1):
        title = item.get("metadata", {}).get("title") or item["source_id"]
        evidence_blocks.append(f"[{i}] {item['collection']} | {title}\n{item['text']}")
    evidence_text = "\n\n".join(evidence_blocks)

    history_text = ""
    if chat_history:
        compact = []
        for turn in chat_history[-6:]:
            role = turn.get("role", "user").title()
            content = turn.get("content", "")
            if content:
                compact.append(f"{role}: {content}")
        history_text = "\n".join(compact)

    prompt = build_jd_fit_prompt(jd_text, extra_question, evidence_text, history_text)

    response = bot.client.chat.completions.create(
        model=bot.chat_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional recruiter-facing AI assistant representing Shailesh Gupta. "
                    "Be accurate, grounded, persuasive, and memorable. Do not expose internal retrieval details."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.55,
    )
    return response.choices[0].message.content.strip()


def stream_jd_fit(
    bot: PortfolioAgenticRAG,
    jd_text: str,
    extra_question: str = "",
    chat_history: list[dict[str, str]] | None = None,
):
    jd_text = trim_jd(jd_text)
    if not jd_text:
        yield "Upload a JD first — I need the role description before I start pretending to be a hiring committee."
        return

    retrieval_queries = [
        jd_text[:1200],
        extra_question or "job fit evaluation",
        "skills experience projects certifications AI ML LLM data scientist",
        "Teleperformance Azure Databricks PySpark machine learning deployment",
        "Deep Research Agent RAG agents LLM engineering OpenAI",
    ]

    evidence_pool: dict[str, dict[str, Any]] = {}
    for query in retrieval_queries:
        for chunk in bot.kb.retrieve(
            query,
            allowed_collections=[
                "identity",
                "professional_summary",
                "skills",
                "experience",
                "education",
                "certifications",
                "projects",
                "target_roles_and_industries",
                "strengths_and_values",
                "source_documents",
            ],
            top_k=10,
        ):
            key = chunk["source_id"]
            if key not in evidence_pool or chunk["weighted_score"] > evidence_pool[key]["weighted_score"]:
                evidence_pool[key] = chunk

    evidence = sorted(evidence_pool.values(), key=lambda x: x["weighted_score"], reverse=True)[:14]
    evidence_text = "\n\n".join(
        [
            f"[{i}] {item['collection']} | {item.get('metadata', {}).get('title') or item['source_id']}\n{item['text']}"
            for i, item in enumerate(evidence, start=1)
        ]
    )

    history_text = ""
    if chat_history:
        compact = []
        for turn in chat_history[-6:]:
            role = turn.get("role", "user").title()
            content = turn.get("content", "")
            if content:
                compact.append(f"{role}: {content}")
        history_text = "\n".join(compact)

    prompt = build_jd_fit_prompt(jd_text, extra_question, evidence_text, history_text)

    response = bot.client.chat.completions.create(
        model=bot.chat_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional recruiter-facing AI assistant representing Shailesh Gupta. "
                    "Be accurate, grounded, persuasive, and memorable. Do not expose internal retrieval details."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.55,
        stream=True,
    )

    for chunk in response:
        delta = None
        try:
            delta = chunk.choices[0].delta.content
        except Exception:
            pass
        if delta:
            yield delta
