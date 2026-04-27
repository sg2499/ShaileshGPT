from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Generator

import gradio as gr
from dotenv import load_dotenv

from agentic_rag import create_portfolio_bot, get_portfolio_bot
from lead_utils import capture_lead
from jd_matcher import extract_text_from_upload, stream_jd_fit
from analytics_db import create_or_update_visitor, log_interaction
from build_kb import main as build_kb_main


ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env", override=True)

CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4.1-mini")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
PROFILE_PATH = ROOT / "data" / "profile_seed.json"
INDEX_PATH = ROOT / "data" / "kb_index.json"
AVATAR_PATH = ROOT / "assets" / "PP.jpg"

with open(PROFILE_PATH, "r", encoding="utf-8") as f:
    PROFILE = json.load(f)

IDENTITY = PROFILE.get("identity", {})
NAME = IDENTITY.get("name", "Shailesh Gupta")
TAGLINE = IDENTITY.get("headline", "Data Scientist | Aspiring AI / LLM Engineer")

DEFAULT_SUGGESTIONS = [
    "What kind of AI and ML work has Shailesh done?",
    "Which project best represents his move into LLM engineering?",
    "Tell me about his Teleperformance experience.",
    "What makes him a strong fit for Applied AI roles?",
    "What is he like outside work?",
    "Give me a recruiter-style summary of Shailesh.",
]
SUGGESTED_QUESTIONS = PROFILE.get("suggested_questions") or DEFAULT_SUGGESTIONS

CUSTOM_CSS = """
:root {
  --page: #070b14;
  --muted: #97a6bd;
  --text: #f4f7fb;
  --line: rgba(148, 163, 184, 0.15);
  --chip: rgba(255, 255, 255, 0.065);
  --chip-hover: rgba(96, 165, 250, 0.17);
}

.gradio-container {
  max-width: 100% !important;
  min-height: 100vh;
  background:
    radial-gradient(circle at 20% 0%, rgba(96,165,250,.13), transparent 28%),
    radial-gradient(circle at 90% 8%, rgba(34,211,238,.10), transparent 28%),
    linear-gradient(180deg, #070b14 0%, #09111f 52%, #070b14 100%) !important;
  color: var(--text) !important;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}

#app-shell {
  max-width: 1040px;
  margin: 0 auto;
  padding: 28px 20px 24px;
}

#hero {
  border: 1px solid var(--line);
  background: linear-gradient(135deg, rgba(15,23,42,.88), rgba(15,23,42,.55));
  border-radius: 28px;
  padding: 24px 26px;
  box-shadow: 0 24px 90px rgba(0,0,0,.34);
  backdrop-filter: blur(18px);
}

.hero-kicker {
  color: #8cc7ff;
  letter-spacing: .12em;
  text-transform: uppercase;
  font-size: .78rem;
  font-weight: 800;
  margin-bottom: 10px;
}

.hero-title {
  font-size: clamp(2rem, 4vw, 3.25rem);
  line-height: 1.02;
  font-weight: 900;
  letter-spacing: -.045em;
  margin: 0;
}

.hero-title span {
  background: linear-gradient(90deg, #fff 0%, #bfdbfe 42%, #67e8f9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  max-width: 820px;
  color: var(--muted);
  line-height: 1.72;
  margin-top: 12px;
  font-size: 1rem;
}

.status-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 18px;
}

.status-pill {
  border: 1px solid rgba(148,163,184,.18);
  background: rgba(255,255,255,.055);
  color: #dbeafe;
  border-radius: 999px;
  padding: 8px 12px;
  font-size: .88rem;
}

#chat-card {
  margin-top: 18px;
  border: 1px solid var(--line);
  background: rgba(8, 13, 24, 0.72);
  border-radius: 28px;
  padding: 14px;
  box-shadow: 0 24px 80px rgba(0,0,0,.32);
  backdrop-filter: blur(18px);
}

#chatbot {
  border: 0 !important;
  background: transparent !important;
}

#chatbot .message {
  font-size: 15.5px !important;
  line-height: 1.7 !important;
}

#chatbot .message.bot {
  border: 1px solid rgba(148,163,184,.13) !important;
  background: rgba(15,23,42,.82) !important;
  border-radius: 20px !important;
}

#chatbot img.avatar, #chatbot .avatar img {
  border: 2px solid rgba(125,211,252,.45) !important;
  box-shadow: 0 0 0 3px rgba(96,165,250,.10), 0 10px 30px rgba(0,0,0,.28) !important;
}

#chatbot .message.user {
  background: linear-gradient(135deg, rgba(96,165,250,.24), rgba(34,211,238,.16)) !important;
  border: 1px solid rgba(125,211,252,.20) !important;
  border-radius: 20px !important;
}

#composer-wrap {
  border: 1px solid var(--line);
  background: rgba(15,23,42,.82);
  border-radius: 22px;
  padding: 10px;
  margin-top: 12px;
}

#composer textarea {
  border: 0 !important;
  background: transparent !important;
  color: var(--text) !important;
  font-size: 15px !important;
}

#send-btn {
  border-radius: 16px !important;
  min-width: 110px !important;
  border: 1px solid rgba(125,211,252,.22) !important;
  background: linear-gradient(135deg, #2563eb, #0891b2) !important;
  color: white !important;
  font-weight: 800 !important;
}

#suggestion-panel {
  margin-top: 18px;
  padding: 18px;
  border: 1px solid var(--line);
  background: rgba(15,23,42,.45);
  border-radius: 24px;
}

.suggestion-title {
  color: #dbeafe;
  font-weight: 800;
  margin-bottom: 12px;
  font-size: .98rem;
}

#suggestion-row {
  display: grid !important;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

#suggestion-row button {
  min-height: 48px !important;
  border-radius: 18px !important;
  border: 1px solid rgba(148,163,184,.16) !important;
  background: var(--chip) !important;
  color: #eaf2ff !important;
  font-weight: 750 !important;
  padding: 10px 14px !important;
  box-shadow: none !important;
  white-space: normal !important;
  line-height: 1.25 !important;
}

#suggestion-row button:hover {
  background: var(--chip-hover) !important;
  border-color: rgba(96,165,250,.32) !important;
}

#jd-card .prose, #jd-card .markdown {
  font-size: 15px !important;
  line-height: 1.65 !important;
}

#jd-card h1, #jd-card h2, #jd-card h3 {
  margin-top: 14px !important;
  margin-bottom: 8px !important;
}

#jd-card ul, #jd-card ol {
  margin-top: 6px !important;
}


#contact-card, #key-card, #jd-card, #visitor-card {
  margin-top: 18px;
  padding: 18px;
  border: 1px solid rgba(96,165,250,.18);
  background: linear-gradient(135deg, rgba(15,23,42,.62), rgba(15,23,42,.36));
  border-radius: 24px;
  box-shadow: 0 16px 45px rgba(0,0,0,.18);
}

#contact-card:hover, #key-card:hover, #jd-card:hover {
  border-color: rgba(125,211,252,.30);
}

#contact-card input, #contact-card textarea, #key-card input {
  background: rgba(15,23,42,.78) !important;
  color: var(--text) !important;
  border: 1px solid rgba(148,163,184,.16) !important;
  border-radius: 14px !important;
}

#lead-submit, #key-save {
  border-radius: 14px !important;
  background: linear-gradient(135deg, #2563eb, #0891b2) !important;
  color: white !important;
  font-weight: 800 !important;
}

.small-muted {
  color: rgba(151,166,189,.9);
  line-height: 1.6;
  font-size: .9rem;
}

#footer-note {
  text-align: center;
  color: rgba(151,166,189,.82);
  font-size: .86rem;
  margin-top: 18px;
}

footer { display: none !important; }
"""


def ensure_index() -> None:
    if not INDEX_PATH.exists():
        build_kb_main()


ensure_index()
BOT = get_portfolio_bot(CHAT_MODEL, EMBEDDING_MODEL)


def get_runtime_bot(session_api_key: str | None):
    session_api_key = (session_api_key or "").strip()
    if session_api_key:
        return create_portfolio_bot(CHAT_MODEL, EMBEDDING_MODEL, api_key=session_api_key)
    return BOT


def register_visitor(name, email, phone, linkedin, github, website, other_contact):
    try:
        visitor = create_or_update_visitor(
            {
                "name": name,
                "email": email,
                "phone": phone,
                "linkedin": linkedin,
                "github": github,
                "website": website,
                "other_contact": other_contact,
                "source": "Hugging Face / Gradio demo",
            }
        )
        msg = f"✅ Thanks, **{visitor['name']}**. You can now use ShaileshGPT. Your questions may be logged to help improve the product."
        return visitor, msg
    except Exception as exc:
        return {}, f"⚠️ {exc}"


def save_session_key(api_key: str):
    api_key = (api_key or "").strip()
    if not api_key:
        return "", "No key saved. The app will use the server-side key if configured."
    if not api_key.startswith("sk-"):
        return "", "That does not look like a standard OpenAI API key. I did not save it."
    return api_key, "Session key saved for this browser session only. It is not written to disk."


def submit_lead(name, email, phone, linkedin, github, website, other_contact, message):
    result = capture_lead(
        {
            "name": name,
            "email": email,
            "phone": phone,
            "linkedin": linkedin,
            "github": github,
            "website": website,
            "other_contact": other_contact,
            "message": message,
            "source": "Gradio app",
        }
    )
    return result["message"]


def stream_jd_analysis(file_obj, jd_question: str, session_api_key: str | None, visitor_state: dict | None):
    if not visitor_state or not visitor_state.get("visitor_id"):
        yield "Please enter your name and email in the **Visitor Access** section before using Recruiter Mode."
        return

    if file_obj is None:
        yield "Upload the JD first. Even the best all-rounder needs to know the pitch before batting."
        return

    try:
        jd_text = extract_text_from_upload(file_obj)
        bot = get_runtime_bot(session_api_key)
        output = ""
        for token in stream_jd_fit(bot, jd_text, jd_question):
            output += token
            yield output

        cta = (
            "\n\n---\n\n"
            "### Interested in moving this forward?\n"
            "Open **Connect with Shailesh** below and leave your email, phone, LinkedIn, website, or preferred contact route. "
            "Shailesh will get notified directly — no résumé black hole, no awkward carrier pigeon situation."
        )
        final_output = output + cta
        log_interaction(
            visitor_state["visitor_id"],
            f"JD upload: {getattr(file_obj, 'name', 'uploaded_jd')} | Question: {jd_question}",
            answer_preview=final_output,
            channel="gradio",
            interaction_type="jd_fit_analysis",
        )
        yield final_output
    except Exception as exc:
        yield f"Could not analyze that JD. Error: `{type(exc).__name__}: {exc}`"



def hero_html() -> str:
    location = IDENTITY.get("location", "Kolkata, India")
    status = IDENTITY.get("current_status", "Open to Work")
    email = IDENTITY.get("email", "shaileshgupta841@gmail.com")
    return f"""
    <section id="hero">
      <div class="hero-kicker">Personal AI Twin · Portfolio Assistant</div>
      <h1 class="hero-title"><span>Ask ShaileshGPT.</span><br/>Career, projects, skills — minus the corporate small talk.</h1>
      <div class="hero-subtitle">
        A clean, recruiter-friendly chatbot that answers questions about {NAME}'s data science work,
        AI/LLM direction, projects, education, certifications, strengths, hobbies, and work style.
        It is designed to sound like him: sharp, grounded, a little witty, and useful without pretending to be a crystal ball.
      </div>
      <div class="status-row">
        <span class="status-pill">{TAGLINE}</span>
        <span class="status-pill">{location}</span>
        <span class="status-pill">{status}</span>
        <span class="status-pill">{email}</span>
      </div>
    </section>
    """


WELCOME = (
    "Hey, I’m **ShaileshGPT** — the portfolio twin that answers questions about Shailesh without making you scroll "
    "through five tabs like it’s a treasure hunt.\n\n"
    "Ask me about his experience, projects, skills, education, certifications, AI/LLM work, hobbies, or whether he’s "
    "more cricket-crazy than is medically advisable."
)


def add_user_message(message: str, history: list[dict[str, str]] | None, visitor_state: dict | None):
    history = history or []
    message = (message or "").strip()
    if not message:
        return "", history
    if not visitor_state or not visitor_state.get("visitor_id"):
        history.append({
            "role": "assistant",
            "content": "Please enter your **name and email** in the Visitor Access section before using ShaileshGPT. I promise, no secret handshake required."
        })
        return message, history
    history.append({"role": "user", "content": message})
    return "", history


def stream_bot_message(history: list[dict[str, str]] | None, session_api_key: str | None, visitor_state: dict | None) -> Generator[list[dict[str, str]], None, None]:
    history = history or []
    if not history or history[-1].get("role") != "user":
        yield history
        return

    if not visitor_state or not visitor_state.get("visitor_id"):
        yield history
        return

    user_message = history[-1]["content"]
    prior_history = history[:-1]
    history.append({"role": "assistant", "content": ""})

    try:
        bot = get_runtime_bot(session_api_key)
        for token in bot.answer_stream(user_message, chat_history=prior_history):
            history[-1]["content"] += token
            yield history
        log_interaction(
            visitor_state["visitor_id"],
            user_message,
            answer_preview=history[-1]["content"],
            channel="gradio",
            interaction_type="chat_question",
        )
    except Exception as exc:
        history[-1]["content"] = (
            "I hit a technical snag while answering that. Very dramatic of the backend, I know.\n\n"
            f"Error: `{type(exc).__name__}: {exc}`"
        )
        yield history


def set_suggestion(question: str):
    return question


with gr.Blocks(theme=gr.themes.Soft(), css=CUSTOM_CSS, title=f"{NAME} | ShaileshGPT") as demo:
    with gr.Column(elem_id="app-shell"):
        gr.HTML(hero_html())

        with gr.Accordion("Visitor Access — required before using ShaileshGPT", open=True, elem_id="visitor-card"):
            gr.HTML("<div class='small-muted'>Please enter your name and email before using the bot. This helps Shailesh understand who is exploring the product. Your questions may be logged for product insights and follow-up context.</div>")
            with gr.Row():
                visitor_name = gr.Textbox(label="Name *", placeholder="Your name")
                visitor_email = gr.Textbox(label="Email *", placeholder="you@example.com")
            with gr.Row():
                visitor_phone = gr.Textbox(label="Phone", placeholder="Optional")
                visitor_linkedin = gr.Textbox(label="LinkedIn", placeholder="Optional")
            with gr.Row():
                visitor_github = gr.Textbox(label="GitHub", placeholder="Optional")
                visitor_website = gr.Textbox(label="Website", placeholder="Optional")
            visitor_other = gr.Textbox(label="Other contact", placeholder="Optional")
            visitor_submit = gr.Button("Start using ShaileshGPT", elem_id="lead-submit")
            visitor_status = gr.Markdown()
            visitor_state = gr.State({})

        with gr.Column(elem_id="chat-card"):

            chatbot = gr.Chatbot(
                label="ShaileshGPT",
                value=[{"role": "assistant", "content": WELCOME}],
                type="messages",
                height=520,
                show_copy_button=True,
                elem_id="chatbot",
                avatar_images=(None, str(AVATAR_PATH) if AVATAR_PATH.exists() else None),
                bubble_full_width=False,
            )

            with gr.Row(elem_id="composer-wrap"):
                msg = gr.Textbox(
                    placeholder="Ask anything about Shailesh...",
                    lines=2,
                    max_lines=5,
                    show_label=False,
                    elem_id="composer",
                    container=False,
                    scale=8,
                )
                send = gr.Button("Send", elem_id="send-btn", scale=1)

        with gr.Column(elem_id="suggestion-panel"):
            gr.HTML("<div class='suggestion-title'>Try asking</div>")
            with gr.Row(elem_id="suggestion-row"):
                suggestion_buttons = [gr.Button(q) for q in SUGGESTED_QUESTIONS[:6]]

        with gr.Accordion("Recruiter Mode: Upload a JD and check Shailesh's fit", open=False, elem_id="jd-card"):
            gr.HTML("<div class='small-muted'>Upload a job description and I’ll give a recruiter-ready fit analysis: verdict, matched strengths, gaps, proof points, and a clear next step. Honest where needed, persuasive where deserved — no bloated HR essay energy.</div>")
            jd_file = gr.File(label="Upload JD", file_types=[".pdf", ".txt", ".md", ".csv"])
            jd_question = gr.Textbox(
                label="Optional recruiter question",
                placeholder="Example: Is Shailesh a good fit for this AI Engineer role?",
                lines=2,
            )
            jd_analyze = gr.Button("Analyze JD fit", elem_id="lead-submit")
            jd_output = gr.Markdown(value="Upload a JD and click **Analyze JD fit**. I’ll keep the answer tight, recruiter-friendly, and useful enough to justify an interview call.")

        with gr.Accordion("Connect with Shailesh", open=False, elem_id="contact-card"):
            gr.HTML("<div class='small-muted'>Recruiter, founder, collaborator, or fellow cricket tragic? Drop your details and Shailesh will get a Pushover notification plus an email via SendGrid.</div>")
            with gr.Row():
                lead_name = gr.Textbox(label="Name", placeholder="Your name")
                lead_email = gr.Textbox(label="Email", placeholder="you@example.com")
            with gr.Row():
                lead_phone = gr.Textbox(label="Phone", placeholder="+91 ...")
                lead_linkedin = gr.Textbox(label="LinkedIn", placeholder="https://linkedin.com/in/...")
            with gr.Row():
                lead_github = gr.Textbox(label="GitHub", placeholder="https://github.com/...")
                lead_website = gr.Textbox(label="Website", placeholder="https://...")
            lead_other = gr.Textbox(label="Other way to connect", placeholder="Telegram, portfolio, Calendly, anything useful")
            lead_message = gr.Textbox(label="Message / Intent", lines=3, placeholder="Tell Shailesh why you want to connect.")
            lead_submit = gr.Button("Send my details to Shailesh", elem_id="lead-submit")
            lead_status = gr.Markdown()

        with gr.Accordion("Optional: use your own OpenAI API key for this session", open=False, elem_id="key-card"):
            gr.HTML("<div class='small-muted'>Prefer to run the conversation on your own OpenAI credits? Add your key here for this active session. It stays session-only and is not written to disk.</div>")
            api_key_input = gr.Textbox(label="OpenAI API key", type="password", placeholder="sk-...")
            key_save = gr.Button("Use this key for my session", elem_id="key-save")
            key_status = gr.Markdown()

        session_api_key = gr.State("")

        gr.HTML("<div id='footer-note'>Designed and Built by Shailesh Gupta.</div>")


    visitor_submit.click(
        register_visitor,
        [visitor_name, visitor_email, visitor_phone, visitor_linkedin, visitor_github, visitor_website, visitor_other],
        [visitor_state, visitor_status],
    )

    msg.submit(add_user_message, [msg, chatbot, visitor_state], [msg, chatbot], queue=False).then(
        stream_bot_message, [chatbot, session_api_key, visitor_state], [chatbot]
    )
    send.click(add_user_message, [msg, chatbot, visitor_state], [msg, chatbot], queue=False).then(
        stream_bot_message, [chatbot, session_api_key, visitor_state], [chatbot]
    )

    for btn in suggestion_buttons:
        btn.click(set_suggestion, inputs=[btn], outputs=[msg], queue=False).then(
            add_user_message, [msg, chatbot, visitor_state], [msg, chatbot], queue=False
        ).then(
            stream_bot_message, [chatbot, session_api_key, visitor_state], [chatbot]
        )

    jd_analyze.click(
        stream_jd_analysis,
        [jd_file, jd_question, session_api_key, visitor_state],
        [jd_output],
    )

    lead_submit.click(
        submit_lead,
        [lead_name, lead_email, lead_phone, lead_linkedin, lead_github, lead_website, lead_other, lead_message],
        [lead_status],
    )

    key_save.click(save_session_key, [api_key_input], [session_api_key, key_status])


if __name__ == "__main__":
    demo.queue(default_concurrency_limit=8).launch()
