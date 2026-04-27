---
title: ShaileshGPT_-_AI-Powered_Personal_Portfolio
app_file: app.py
sdk: gradio
sdk_version: 5.49.1
---
# 🚀 ShaileshGPT — AI-Powered Personal Portfolio Assistant

![GitHub repo size](https://img.shields.io/github/repo-size/sg2499/ShaileshGPT)
![GitHub stars](https://img.shields.io/github/stars/sg2499/ShaileshGPT?style=social)
![Last Commit](https://img.shields.io/github/last-commit/sg2499/ShaileshGPT)
![Built with React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-blue)
![Backend](https://img.shields.io/badge/Backend-FastAPI-green)
![Powered by OpenAI](https://img.shields.io/badge/Powered%20By-OpenAI-black)
![Agentic RAG](https://img.shields.io/badge/Architecture-Agentic%20RAG-purple)

**Repository:** [https://github.com/sg2499/ShaileshGPT](https://github.com/sg2499/ShaileshGPT)

---

## 🚀 Try the Live Demo

You can try the deployed ShaileshGPT demo on Hugging Face Spaces here:

🔗 **Live Demo:** [ShaileshGPT — AI-Powered Personal Portfolio](https://huggingface.co/spaces/sg2499/ShaileshGPT_-_AI-Powered_Personal_Portfolio)

This demo lets you interact with the chatbot, ask questions about the portfolio, test recruiter-style queries, and explore how the personal AI assistant works.

> ⚠️ **Mandatory API Usage Note**  
> This project uses paid LLM/API services. To keep the public demo available without creating uncontrolled API costs, users must enter their **own OpenAI API key** before using Chat or Recruiter JD-Fit analysis.  
>  
> Your key is used only for your active browser/session request flow. It is not stored in Supabase, not written to disk, not saved in the project database, and not exposed in the repository. Without your own key, the public demo and website bot will not allow AI responses.

---


## 📌 What is ShaileshGPT?

**ShaileshGPT** is a full-stack AI-powered personal portfolio system that turns a static resume website into an interactive, recruiter-ready, AI-driven experience.

Instead of making visitors scroll through a resume, GitHub profile, LinkedIn profile, project cards, blog posts, and certifications manually, this project gives them a personalized AI assistant that can answer questions about:

- Professional Background
- Work Experience
- Technical Skills
- Education
- Certifications
- Portfolio Projects
- AI / LLM / RAG Work
- Hobbies and Personality
- Recruiter Fit
- Job-Description Alignment

The system also includes a **Recruiter Mode**, where a recruiter can upload a job description and ask whether the profile is a good fit for that role. The bot compares the uploaded JD with skills, experience, certifications, education, and projects, then gives a clear fit verdict, strengths, gaps, proof points, and a recruiter takeaway.

This project is not just a chatbot. It is a complete personal AI product.

---

## ⚠️ Important Note — Please Build Your Own Version

This repository uses **my personal knowledge base**.

That means the bot is grounded on information about **me — Shailesh Gupta**, including my:

- Resume
- Work Experience
- Projects
- Skills
- Certifications
- Education
- GitHub Work
- Portfolio Positioning
- Personal Interests
- Personality Traits
- Recruiter-Fit Logic

So please do **not** blindly copy this project and deploy it as-is.

Instead, use this repository as a **reference architecture** and build your own version with your own:

- Resume
- Profile Summary
- Projects
- Skills
- Education
- Certifications
- Personality Layer
- Professional Goals
- Deployment Configuration
- API Keys

The best way to use this project is to understand the system design and then rebuild a version that represents **you**.

> Take reference from my work, improve it, customize it, and make something better than mine.

That is the whole point of sharing this project.

---

## ⚠️ Important Note About API Usage and Public Access

This project uses paid third-party APIs:

- OpenAI API for chat, embeddings, routing, retrieval, and answer generation
- SendGrid API for email notifications
- Pushover API for instant lead notifications
- Supabase for visitor/session analytics and interaction tracking

Because OpenAI usage is billed, unrestricted public usage can create unexpected API costs.

For this reason, the current public version of ShaileshGPT requires users to enter their **own OpenAI API key** before using the AI-powered features.

This applies to:

- Hugging Face demo
- Personal website chatbot
- Chat responses
- Suggestion questions
- Recruiter JD-Fit analysis

Users can still explore the website and project normally, but to generate AI answers they must provide their own key.

### Why I made user API keys mandatory

This decision was made for practical and responsible reasons:

- It prevents uncontrolled usage of my private OpenAI credits
- It keeps the public demo available for everyone
- It allows serious users to test the product using their own credits
- It makes the project safer and more scalable as a public portfolio demo
- It avoids the risk of random users draining the owner’s API quota

### Is it safe to enter your OpenAI API key?

The app is designed so that the user-provided OpenAI API key is used only for the **active session**.

The key is:

- Not stored in Supabase
- Not written to disk
- Not saved in localStorage
- Not committed to GitHub
- Not shown in the UI after entry
- Not added to the personal knowledge base
- Sent only as a request header when Chat or JD-Fit analysis is used

In the website version, the key is kept only in browser memory for that session. In the Hugging Face/Gradio version, it is kept only in the active Gradio session state.

If the page is refreshed or the session is reset, the user may need to enter the key again.

> Use your own OpenAI API key only if you are comfortable testing the live demo. If you are cloning the project, always configure your own backend secrets and never use someone else’s credentials.

Never use someone else’s API key without permission.

---

## 🎯 Why This Project Exists

Most portfolio websites are static.

They show:

- About section
- Experience
- Skills
- Projects
- Resume download
- Contact links

That is useful, but passive.

ShaileshGPT changes the experience into something interactive.

A recruiter, founder, hiring manager, collaborator, or curious visitor can directly ask:

```text
What kind of AI and ML work has Shailesh done?
```

```text
Is Shailesh a good fit for an Applied AI Engineer role?
```

```text
Which project best proves his LLM engineering direction?
```

```text
Compare this JD with Shailesh's profile and tell me if he is a match.
```

The bot answers using a structured knowledge base instead of generic assumptions.

---

## 🧠 What Makes ShaileshGPT an Industry-Grade Product?

This is not a simple prompt wrapper.

It includes:

- Full-Stack Architecture
- React/Vite Portfolio Frontend
- FastAPI Backend
- Structured Personal Knowledge Base
- Agentic RAG Pipeline
- Vector Embeddings
- Hybrid Retrieval
- Streaming Responses
- JD-fit Analysis
- Recruiter Lead Capture
- SendGrid Email Notification
- Pushover Phone Notification
- Mandatory Session-Level User OpenAI API Key
- Supabase Visitor, Session, Conversation, and Question Analytics
- Admin Dashboard for Visitors, Leads, Sessions, Questions, and Usage
- Admin Token Authentication
- Full Conversation History Logging
- Most Asked Questions Analytics
- Usage-Based Estimated Cost Monitoring
- Downloadable Recruiter JD-Fit PDF Reports
- Render Backend Deployment
- Vercel Frontend Deployment
- API Rate Limiting
- Public Website Integration

This makes it closer to a real-world AI product than a basic demo.

---

## ✨ Core Features

### 1. AI Portfolio Chatbot

Visitors can ask natural-language questions about my profile.

Example questions:

```text
What kind of AI and ML work has Shailesh done?
```

```text
Tell me about his Teleperformance experience.
```

```text
What are his strongest technical skills?
```

```text
What is he like outside work?
```

The bot responds in a polished, conversational, professional, slightly witty tone.

---

### 2. Agentic RAG Knowledge Base

The bot uses a structured knowledge base and retrieval pipeline.

The knowledge base includes:

- Identity Layer
- Professional Summary
- Skills
- Work Experience
- Education
- Certifications
- Projects
- Public Presence
- Interests
- Personal Profile
- Target Roles
- Strengths and Values
- Fun Facts
- FAQ Entries
- Raw Source Documents

The bot retrieves relevant context before answering instead of relying only on model memory.

---

### 3. Streaming Chat

The app streams responses token-by-token, giving a professional ChatGPT-like feel.

This makes the bot feel fast, modern, and interactive.

---

### 4. Recruiter JD-Fit Analysis

Recruiters can upload a job description in:

- PDF
- TXT
- MD
- CSV

The bot analyzes the JD against my profile and returns:

- Fit Verdict
- Realistic Fit Percentage Range
- Strongest Matches
- Gaps / Ramp-Up Areas
- Best Proof Points
- Recruiter Takeaway
- Contact CTA

Example verdict:

```text
Verdict: Good Fit — 72–80%
```

This is one of the most important features because it turns the bot into a recruiter-facing evaluation assistant.

---

### 5. Lead Capture

Visitors can leave their details:

- Name
- Email
- Phone
- LinkedIn Profile
- GitHub Profile
- Website
- Other Contact Route
- Message / Intent

Once submitted, the system sends a notification to me.

---

### 6. Pushover Notification

Pushover sends an instant notification to my phone whenever someone submits their contact details.

This is useful for real-time recruiter or collaborator alerts.

---

### 7. SendGrid Email Notification

SendGrid sends an email with the submitted lead details.

This creates a proper notification workflow and keeps a written record of recruiter/collaborator interest.

---

### 8. Mandatory User OpenAI API Key

The public version of ShaileshGPT now requires users to provide their **own OpenAI API key** before using AI-powered features.

This applies to:

- Chat
- Suggestion questions
- Recruiter JD-Fit analysis

This was added to control API costs and keep the demo available publicly without using the owner’s private OpenAI credits.

The key is handled safely:

- It is used only for the active browser/session flow
- It is not stored in Supabase
- It is not written to disk
- It is not stored in localStorage
- It is not saved in the analytics database
- It is not committed to the repository
- It is passed only as an API request header when needed

Without entering a valid OpenAI API key, users cannot generate AI responses.

---

### 9. Website Integration

The chatbot is integrated into the portfolio website as:

- A dedicated ShaileshGPT product section
- A floating chatbot widget
- A recruiter JD-fit tab
- A connect/contact tab
- A featured project card

This turns the portfolio into a working AI product.

---

### 10. Mandatory Visitor Access

Before using ShaileshGPT, users are asked to enter basic visitor details.

Required:

- Name
- Email

Optional:

- Phone
- LinkedIn
- GitHub
- Website
- Other contact route

This helps understand who is exploring the product and creates a useful activity trail for portfolio insights, recruiter follow-ups, and product improvement.

---

### 11. Supabase Visitor, Session, Conversation, and Question Analytics

The project now includes Supabase-backed analytics.

It records:

- Visitor name
- Visitor email
- Optional contact details
- Session source
- Questions asked
- Full conversation messages
- JD-Fit analysis requests
- JD-Fit PDF report downloads
- Lead/contact submissions
- Answer previews
- Timestamps
- Interaction channel
- Most asked questions
- Estimated usage and cost events

The analytics database now contains these main tables:

```text
visitors
interactions
conversation_sessions
conversation_messages
usage_events
```

This makes the project more production-like because public usage is not only interactive but also measurable, auditable, and easier to improve over time.

---

### 12. Admin Dashboard

ShaileshGPT now includes a backend-hosted admin dashboard for monitoring real product activity.

The admin dashboard shows:

- Total visitors
- Total interactions
- Total sessions
- Total conversation messages
- Recent visitors
- Recent questions and interactions
- Most asked questions
- Conversation message history
- Usage and estimated cost analytics
- CSV export of interaction logs

The dashboard is available from the backend route:

```text
/admin
```

Example:

```text
https://your-render-service.onrender.com/admin
```

---

### 13. Admin Authentication

The admin dashboard is protected by a private admin token.

The backend checks:

```env
ANALYTICS_ADMIN_TOKEN=your_private_admin_token
```

Only users who know this token can open analytics data inside the admin dashboard or access protected analytics endpoints.

This protects:

- Visitor details
- Questions asked
- Conversation history
- JD-Fit activity
- Usage/cost estimates
- CSV export

---

### 14. Full Conversation History

Earlier versions stored only individual interactions. The upgraded version stores complete conversation flow.

It now tracks:

- Visitor
- Session
- Message role
- User messages
- Assistant messages
- Timestamp
- Interaction ID

This makes it possible to understand not just what question was asked, but how the entire conversation evolved.

---

### 15. Most Asked Questions Analytics

The admin dashboard includes a **Most Asked Questions** section.

This helps identify:

- What recruiters care about most
- Which skills/projects visitors ask about repeatedly
- What gaps visitors are checking
- Which website sections may need improvement
- Which questions should become public FAQ content

This is useful for improving the portfolio, README, resume, and interview positioning.

---

### 16. Usage-Based Estimated Cost Monitoring

ShaileshGPT now includes internal usage/cost monitoring.

It logs estimated usage for:

- Chat
- Streaming chat
- JD-Fit analysis
- JD-Fit PDF report generation

The dashboard tracks:

- Estimated input tokens
- Estimated output tokens
- Estimated total tokens
- Estimated cost in USD
- Cost by feature
- Cost by model
- Cost by visitor
- Whether the owner key was used

Important safety field:

```text
used_owner_key
```

For normal public usage, this should be:

```text
false
```

If it appears as:

```text
true
```

that means a request used the backend/owner key, which should be investigated immediately.

> Note: This is an internal estimate based on text length and model pricing assumptions. Official billing must always be checked in the OpenAI dashboard.

---

### 17. Downloadable JD-Fit PDF Reports

Recruiter Mode now supports downloadable PDF reports.

After uploading a JD and running the analysis, the user can download a structured PDF report containing:

- Candidate-role fit verdict
- Match percentage range
- Strongest matches
- Gaps / ramp-up areas
- Best proof points
- Recruiter takeaway
- Final recommendation

Backend endpoint:

```http
POST /jd_fit_report
```

This turns the recruiter mode into a more polished hiring-evaluation workflow.

---



## 🏗️ High-Level Architecture

```text
User / Recruiter
   ↓
Visitor Details + User OpenAI API Key
   ↓
React + Vite Portfolio Website / Hugging Face Demo
   ↓
Floating ShaileshGPT Widget / Gradio App
   ↓
FastAPI Backend
   ↓
Admin-Protected Analytics Layer
   ↓
Supabase Visitors + Sessions + Interactions + Messages + Usage Events
   ↓
Agentic RAG Pipeline
   ↓
OpenAI Chat + Embeddings using User-Provided API Key
   ↓
Personal Knowledge Base
   ↓
Grounded Answer / JD Fit / JD PDF Report / Lead Capture
   ↓
SendGrid Email + Pushover Notification
```

---

## 🧩 System Components

### Frontend

Built with:

- React
- Vite
- Tailwind CSS

Main frontend responsibilities:

- Render portfolio website
- Display ShaileshGPT section
- Handle floating chatbot UI
- Stream chat responses
- Upload JD files
- Collect lead details
- Call FastAPI backend endpoints

---

### Backend

Built with:

- FastAPI
- Uvicorn
- OpenAI Python SDK
- Pydantic
- NumPy
- pypdf
- SendGrid via REST API
- Pushover via REST API
- Supabase REST API for visitor and interaction analytics

Main backend responsibilities:

- Build/Load knowledge base
- Embed profile chunks
- Perform retrieval
- Route queries
- Generate grounded responses
- Analyze uploaded JDs
- Capture leads
- Register visitors
- Log questions and JD-Fit activity
- Store analytics in Supabase
- Track sessions and full conversation history
- Analyze most asked questions
- Estimate token usage and approximate cost
- Generate downloadable JD-Fit PDF reports
- Serve the admin dashboard
- Protect admin analytics using token authentication
- Enforce user-provided API key flow for public usage
- Send notifications
- Rate-limit public API usage

---

### Knowledge Base

The knowledge base is created from structured profile files and source documents.

Important files:

```text
data/profile_seed.json
data/source_documents.json
data/raw/
```

`profile_seed.json` contains structured information about the person.

For your own version, this is the most important file to customize.

---

## 📁 Project Structure

A typical full project structure looks like this:

```bash
📦ShaileshGPT/
├── backend/
│   ├── api_server.py              # FastAPI API backend
│   ├── agentic_rag.py             # Agentic RAG orchestration
│   ├── knowledge_base.py          # Chunking, embeddings, retrieval
│   ├── build_kb.py                # Builds vector knowledge base
│   ├── prepare_sources.py         # Prepares source documents
│   ├── jd_matcher.py              # JD-fit analysis logic
│   ├── lead_utils.py              # Pushover + SendGrid lead notification
│   ├── analytics_db.py            # Visitors, sessions, messages, usage/cost analytics
│   ├── supabase_schema.sql        # Supabase schema for analytics tables
│   ├── admin_dashboard.html       # Protected admin dashboard UI
│   ├── widget.js                  # Optional standalone website widget
│   ├── requirements.txt           # Python backend dependencies
│   ├── runtime.txt                # Python version for Render
│   ├── .env.example               # Backend environment template
│   ├── data/
│   │   ├── profile_seed.json      # Structured personal knowledge base
│   │   ├── source_documents.json  # Prepared source documents
│   │   └── raw/
│   │       ├── resume.pdf
│   │       └── profile.pdf
│   └── assets/
│       └── PP.jpg                 # Profile picture
│
├── frontend/
│   ├── index.html                 # Website HTML metadata
│   ├── package.json               # Frontend dependencies
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   ├── vite.config.js
│   ├── public/
│   │   ├── favicon.png
│   │   └── preview.png            # Social sharing preview image
│   └── src/
│       ├── App.jsx                # Main React portfolio + chatbot UI
│       ├── index.css              # Tailwind and custom styling
│       └── main.jsx               # React entry point
│
└── README.md
```

Depending on how you organize your repo, your files may be in one root folder or split into backend/frontend folders.

---

## 🚀 Backend Setup Guide

### 1. Clone the Repository

```bash
git clone https://github.com/sg2499/ShaileshGPT.git
cd ShaileshGPT
```

If your backend is inside a separate folder:

```bash
cd backend
```

---

## 🐍 Python Environment Setup

Use Python 3.11 for best compatibility.

### Option A — Using `venv`

**Windows**

```powershell
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

### Option B — Using Conda

```bash
conda create -n shaileshgpt python=3.11 -y
conda activate shaileshgpt
pip install -r requirements.txt
```

---

### Option C — Using `uv`

```bash
uv venv
```

Activate:

**Windows**

```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

Install:

```bash
uv pip install -r requirements.txt
```

---

## 📦 Backend Dependencies

Typical backend dependencies:

```txt
openai
fastapi
uvicorn
python-dotenv
pydantic
requests
numpy
pypdf
python-multipart
reportlab
```

Install with:

```bash
pip install -r requirements.txt
```

---

## 🔐 Backend Environment Variables

Create a `.env` file in the backend root.

Example:

```env
OPENAI_API_KEY=your_backend_openai_key_for_building_or_local_testing
OPENAI_CHAT_MODEL=gpt-4.1-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Public cost-control mode.
# Set true when the frontend sends the user's key through x-openai-api-key.
REQUIRE_USER_OPENAI_API_KEY=true

# Supabase analytics
ANALYTICS_STORAGE=supabase
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
SUPABASE_VISITORS_TABLE=visitors
SUPABASE_INTERACTIONS_TABLE=interactions
SUPABASE_SESSIONS_TABLE=conversation_sessions
SUPABASE_MESSAGES_TABLE=conversation_messages
SUPABASE_USAGE_TABLE=usage_events

# Admin analytics access
ANALYTICS_ADMIN_TOKEN=choose_a_private_admin_token

# Notifications
PUSHOVER_USER=your_pushover_user_key
PUSHOVER_TOKEN=your_pushover_app_token

SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM_EMAIL=your_verified_sender_email@example.com
LEAD_FROM_EMAIL=your_verified_sender_email@example.com
LEAD_NOTIFY_EMAIL=your_email@example.com

QUESTION_NOTIFY_ENABLED=true
EMAIL_EACH_QUESTION=false
NOTIFY_RETURNING_VISITORS=false

RATE_LIMIT_REQUESTS=30
RATE_LIMIT_WINDOW_SECONDS=3600
ALLOWED_ORIGINS=*
```

---

# 🔑 API Key Setup Guides

---

## 🤖 OpenAI API Key Setup

The OpenAI API is used for:

- Query routing
- Query expansion
- Embeddings
- RAG answer generation
- JD-fit analysis

### Step 1 — Create an OpenAI Platform Account

Go to:

```text
https://platform.openai.com/
```

Sign in or create an account.

### Step 2 — Create an API Key

Go to:

```text
https://platform.openai.com/settings/organization/api-keys
```

Create a new secret key.

### Step 3 — Add Billing

OpenAI API usage requires billing to be enabled for paid API usage. Check your OpenAI Platform billing/settings before deploying publicly.

### Step 4 — Add API Key to `.env`

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Step 5 — Never Commit Your Key

Do not push `.env` to GitHub.

Add this to `.gitignore`:

```gitignore
.env
```

### Mandatory — Use Your Own Key in the Public App

The public demo and website bot now require users to enter their own OpenAI API key before using Chat or JD-Fit analysis.

This is intentional.

A public AI app can quickly become expensive if every visitor uses the owner’s API key. To avoid uncontrolled cost, ShaileshGPT asks each user to run the AI part of the demo on their own OpenAI credits.

### Is the entered key safe?

The user-entered key is used only for the active session.

It is:

- Not stored in Supabase
- Not written to disk
- Not saved in localStorage
- Not committed to GitHub
- Not visible after entry
- Not used for visitor analytics
- Not added to the knowledge base

The frontend sends the key to the backend only as a request header:

```text
x-openai-api-key
```

The backend then uses that key for the current chat or JD-Fit request.

If you clone the project for yourself, you can decide whether to make user-provided keys mandatory or use your own protected backend key.

---

## 📬 SendGrid API Key Setup

SendGrid is used for email notifications when someone submits their contact details.

### Step 1 — Create a SendGrid Account

Go to:

```text
https://sendgrid.com/
```

Create an account and complete onboarding.

### Step 2 — Verify Sender Identity

SendGrid requires sender identity verification before email sending.

You can use either:

### Option A — Single Sender Verification

Best for testing.

Use this if:

- You only need one sender email
- You want quick setup
- You do not want to configure DNS records

### Option B — Domain Authentication

Best for production.

Use this if:

- You own a domain
- You can update DNS records
- You want better deliverability
- You want emails to look more professional

### Step 3 — Create SendGrid API Key

Inside SendGrid:

```text
Settings → API Keys → Create API Key
```

Recommended permission:

```text
Mail Send
```

### Step 4 — Add SendGrid Variables to `.env`

```env
SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM_EMAIL=your_verified_sender_email@example.com
LEAD_FROM_EMAIL=your_verified_sender_email@example.com
LEAD_NOTIFY_EMAIL=your_email@example.com
```

Important:

`SENDGRID_FROM_EMAIL` / `LEAD_FROM_EMAIL` must be verified in SendGrid.

---

## 🔔 Pushover API Key Setup

Pushover is used for instant phone notifications when someone leaves their contact details.

### Step 1 — Create a Pushover Account

Go to:

```text
https://pushover.net/
```

Create an account and install the Pushover app on your phone.

### Step 2 — Get Your User Key

After logging in, your user key is visible in your Pushover dashboard.

Add it to `.env`:

```env
PUSHOVER_USER=your_pushover_user_key
```

### Step 3 — Create a Pushover Application

Go to the Pushover application/API section and create a new application.

Example app name:

```text
ShaileshGPT Lead Bot
```

After creating the app, Pushover gives you an API token.

Add it to `.env`:

```env
PUSHOVER_TOKEN=your_pushover_app_token
```

### Step 4 — Test Lead Capture

Run the backend, open the app, submit contact details, and check whether your phone receives a notification.

---

## 🗄️ Supabase Analytics Setup

Supabase is used to store visitor and interaction analytics.

The current production-style tracking flow records:

- visitor details
- every question asked
- JD-Fit analysis activity
- lead/contact submissions
- source/channel
- timestamps
- answer previews

### Step 1 — Create a Supabase Project

Go to:

```text
https://supabase.com/
```

Create a new project.

### Step 2 — Get Project URL and Service Role Key

Inside Supabase:

```text
Project Settings → API
```

Copy:

```text
Project URL
Service Role Key
```

Use them in your backend environment:

```env
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
```

Important:

`SUPABASE_SERVICE_ROLE_KEY` is a private backend secret. Do not put it in React, Vite, frontend code, GitHub, README, screenshots, or public posts.

### Step 3 — Create Tables

Run the SQL inside:

```text
supabase_schema.sql
```

in:

```text
Supabase → SQL Editor → New Query
```

This creates:

```text
visitors
interactions
conversation_sessions
conversation_messages
usage_events
```

### Step 4 — Add Analytics Environment Variables

```env
ANALYTICS_STORAGE=supabase
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
SUPABASE_VISITORS_TABLE=visitors
SUPABASE_INTERACTIONS_TABLE=interactions
SUPABASE_SESSIONS_TABLE=conversation_sessions
SUPABASE_MESSAGES_TABLE=conversation_messages
SUPABASE_USAGE_TABLE=usage_events
ANALYTICS_ADMIN_TOKEN=choose_a_private_admin_token
```

### Step 5 — View Analytics

Open:

```text
Supabase → Table Editor → visitors
Supabase → Table Editor → interactions
```

You can also use the protected analytics API:

```text
GET /analytics/summary
GET /analytics/interactions.csv
```

Both require:

```text
x-admin-token: YOUR_ANALYTICS_ADMIN_TOKEN
```

---

## 📊 Admin Dashboard and Analytics Monitoring

The backend includes a protected admin dashboard.

Open:

```text
https://your-render-service.onrender.com/admin
```

Enter your private admin token:

```env
ANALYTICS_ADMIN_TOKEN=your_private_admin_token
```

The dashboard displays:

- Visitor activity
- Submitted lead details
- Interaction history
- Full conversation messages
- Most asked questions
- Usage and estimated cost
- CSV export

### Protected Analytics Endpoints

```http
GET /analytics/summary
```

Returns dashboard analytics data.

```http
GET /analytics/interactions.csv
```

Exports recent interaction history as CSV.

Both require:

```text
x-admin-token: YOUR_ANALYTICS_ADMIN_TOKEN
```

or a query parameter:

```text
?token=YOUR_ANALYTICS_ADMIN_TOKEN
```

### Usage and Cost Monitoring

The `usage_events` table stores estimated cost metadata.

It tracks:

- Feature used
- Model used
- Estimated input tokens
- Estimated output tokens
- Estimated total tokens
- Estimated cost in USD
- Whether the owner key was used

Important field:

```text
used_owner_key
```

For public usage, this should normally be:

```text
false
```

If it is ever:

```text
true
```

then the backend/owner key was used for that request and should be investigated.

> Cost values are estimates for product analytics. Official usage must be checked from the OpenAI Platform dashboard.


## 🧠 Customize the Knowledge Base for Yourself

This is the most important part if you want to build your own version.

Do not keep my personal profile data.

Edit:

```text
data/profile_seed.json
```

Replace my information with yours.

Suggested structure:

```json
{
  "identity": {
    "name": "Your Name",
    "headline": "Your Professional Headline",
    "location": "Your Location",
    "email": "your_email@example.com",
    "github": "https://github.com/your_username",
    "linkedin": "https://linkedin.com/in/your_profile",
    "website": "https://yourwebsite.com",
    "blog": "https://yourblog.com"
  },
  "professional_summary": [
    "Write a concise summary of your professional background."
  ],
  "skills": {
    "ml_ai": ["Machine Learning", "LLMs", "RAG"],
    "programming": ["Python", "JavaScript"],
    "deployment": ["FastAPI", "Vercel", "Render"]
  },
  "experience": [],
  "education": [],
  "certifications": [],
  "projects": [],
  "interests": [],
  "personal_profile": [],
  "strengths_and_values": [],
  "fun_facts": []
}
```

Also replace documents inside:

```text
data/raw/
```

with your:

- Resume
- LinkedIn Export/Profile PDF
- Portfolio Notes
- Project Descriptions

Then rebuild the knowledge base.

---

## 🏗️ Build the Knowledge Base

After editing your profile data:

```bash
python build_kb.py
```

This will prepare source documents, create embeddings, and save the index.

Expected output:

```text
Knowledge base built successfully
```

If this step fails, check:

- `OPENAI_API_KEY` is set
- `data/profile_seed.json` exists
- Python environment is active
- Dependencies are installed

---

## ▶️ Run Backend Locally

Start the FastAPI backend:

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

Test health endpoint:

```text
http://localhost:8000/health
```

Expected:

```json
{"status":"ok"}
```

---

## 🧪 Backend API Endpoints

### Health Check

```http
GET /health
```

Returns:

```json
{"status":"ok"}
```

---

### Visitor Registration

```http
POST /visitor/start
```

Registers a visitor before they can use the bot.

Required:

- name
- email

Optional:

- phone
- LinkedIn
- GitHub
- website
- other contact route

The visitor is saved in Supabase and receives a `visitor_id`.

---

### Chat Stream

```http
POST /chat_stream
```

Used by the website frontend to stream chatbot responses.

---

### JD Fit Analysis

```http
POST /jd_fit
```

Accepts:

- Job description file
- Optional recruiter question

Supported file types:

- PDF
- TXT
- MD
- CSV

---

### Lead Capture

```http
POST /lead
```

Captures:

- Name
- Email
- Phone Number
- LinkedIn
- GitHub
- Website
- Other contact
- Message

Then sends:

- Pushover notification
- SendGrid email

---

### Analytics Summary

```http
GET /analytics/summary
```

Returns recent visitors and interactions.

Requires:

```text
x-admin-token: YOUR_ANALYTICS_ADMIN_TOKEN
```

---

### Analytics CSV Export

```http
GET /analytics/interactions.csv
```

Exports recent interaction data as CSV.

Requires:

```text
x-admin-token: YOUR_ANALYTICS_ADMIN_TOKEN
```

---

### Admin Dashboard

```http
GET /admin
```

Serves the protected admin dashboard UI.

The dashboard requires:

```text
ANALYTICS_ADMIN_TOKEN
```

---

### JD-Fit PDF Report

```http
POST /jd_fit_report
```

Accepts:

- Job description file
- Optional recruiter question
- Visitor ID
- Session ID

Returns:

```text
application/pdf
```

The generated report summarizes the candidate-role fit in a recruiter-friendly PDF format.

---

### Usage and Cost Monitoring

Usage is logged internally to:

```text
usage_events
```

This is not a public API endpoint, but it appears inside:

```text
/admin → Usage & Cost
```

---



## 🌐 Frontend Setup Guide

The frontend is a React + Vite portfolio website.

If your frontend is inside a separate folder:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Create a frontend `.env` file:

```env
VITE_SHAILESHGPT_API_BASE=http://localhost:8000
```

Run locally:

```bash
npm run dev
```

Open the local Vite URL in your browser.

---

## 🌍 Deployment Guide

This project uses two deployments:

| Layer | Platform | Purpose |
|---|---|---|
| Backend | Render | FastAPI + OpenAI + RAG + notifications |
| Frontend | Vercel | React portfolio website |

---

## 🚀 Deploy Backend on Render

### Step 1 — Push Backend to GitHub

Make sure your backend folder contains:

```text
api_server.py
agentic_rag.py
build_kb.py
knowledge_base.py
prepare_sources.py
jd_matcher.py
lead_utils.py
analytics_db.py
admin_dashboard.html
supabase_schema.sql
requirements.txt
runtime.txt
data/profile_seed.json
```

Push to GitHub.

---

### Step 2 — Create Render Web Service

On Render:

```text
New → Web Service
```

Select your backend repo.

### Step 3 — Render Settings

Use:

```text
Build Command:
pip install -r requirements.txt
```

```text
Start Command:
uvicorn api_server:app --host 0.0.0.0 --port $PORT
```

### Step 4 — Add Render Environment Variables

Add:

```env
OPENAI_API_KEY=your_backend_openai_key_for_building_or_local_testing
OPENAI_CHAT_MODEL=gpt-4.1-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
REQUIRE_USER_OPENAI_API_KEY=true
ALLOWED_ORIGINS=*

ANALYTICS_STORAGE=supabase
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
SUPABASE_VISITORS_TABLE=visitors
SUPABASE_INTERACTIONS_TABLE=interactions
SUPABASE_SESSIONS_TABLE=conversation_sessions
SUPABASE_MESSAGES_TABLE=conversation_messages
SUPABASE_USAGE_TABLE=usage_events
ANALYTICS_ADMIN_TOKEN=choose_a_private_admin_token
```

Optional:

```env
PUSHOVER_USER=your_pushover_user_key
PUSHOVER_TOKEN=your_pushover_app_token
SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM_EMAIL=your_verified_sender_email@example.com
LEAD_FROM_EMAIL=your_verified_sender_email@example.com
LEAD_NOTIFY_EMAIL=your_email@example.com
RATE_LIMIT_REQUESTS=30
RATE_LIMIT_WINDOW_SECONDS=3600
```

### Step 5 — Test Backend

After deployment, open:

```text
https://your-render-service.onrender.com/health
```

Expected:

```json
{"status":"ok"}
```

If the root URL returns:

```json
{"detail":"Not Found"}
```

that is normal unless you add a custom `/` route.

---

## ▲ Deploy Frontend on Vercel

### Step 1 — Push Frontend to GitHub

Your frontend folder should contain:

```text
index.html
package.json
postcss.config.js
tailwind.config.js
vite.config.js
public/
src/
```

### Step 2 — Import Project into Vercel

Go to Vercel and import the repo.

### Step 3 — Add Vercel Environment Variable

```env
VITE_SHAILESHGPT_API_BASE=https://your-render-service.onrender.com
```

### Step 4 — Build Settings

Vercel usually detects Vite automatically.

Typical settings:

```text
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

### Step 5 — Redeploy

After adding the environment variable, redeploy the site.

---

## 🧪 Testing Checklist

After deployment, test the following:

### Backend

- [ ] `/health` returns `{"status":"ok"}`
- [ ] backend logs show no missing API key
- [ ] no CORS error in browser console

### Frontend

- [ ] website loads normally
- [ ] ShaileshGPT section appears
- [ ] floating chat button appears
- [ ] visitor registration requires name and email
- [ ] Chat/JD Fit are blocked until user enters their own OpenAI API key
- [ ] chat streams responses after user key is saved
- [ ] JD upload works after user key is saved
- [ ] Supabase `visitors` table records visitor details
- [ ] Supabase `interactions` table records questions/JD activity
- [ ] Supabase `conversation_sessions` table records sessions
- [ ] Supabase `conversation_messages` table records full chat history
- [ ] Supabase `usage_events` table records estimated usage/cost
- [ ] `/admin` dashboard opens after admin token entry
- [ ] Most Asked Questions tab updates after repeated questions
- [ ] Usage & Cost tab shows estimated requests/tokens/cost
- [ ] JD-Fit PDF report downloads correctly
- [ ] lead capture works
- [ ] SendGrid email arrives
- [ ] Pushover phone notification arrives
- [ ] preview image appears when sharing the website link

---

## 🧪 Troubleshooting Guide

### 1. `{"detail":"Not Found"}` on Render root URL

This is normal if you open:

```text
https://your-render-service.onrender.com
```

Use:

```text
https://your-render-service.onrender.com/health
```

---

### 2. `OPENAI_API_KEY is missing`

Cause:

- backend environment variable is not set

Fix:

- add `OPENAI_API_KEY` in `.env` locally
- add it in Render environment variables for deployment

---

### 3. `data/profile_seed.json` missing

Cause:

- required knowledge base seed file is not present

Fix:

- add `data/profile_seed.json`
- use your own profile data
- redeploy

---

### 4. `data/source_documents.json` missing

Cause:

- source document folder/file was not created

Fix:

- run `python build_kb.py`
- ensure `prepare_sources.py` creates the `data/` folder
- ensure your deployment includes the `data/` directory

---

### 5. Chatbot does not respond on website

Possible causes:

- `VITE_SHAILESHGPT_API_BASE` is missing
- Backend is asleep or down
- CORS issue
- Wrong Render URL
- Backend route unavailable

Fix:

- Check browser console
- Open `/health`
- Verify Vercel env var
- Redeploy frontend after changing env var

---

### 6. JD Upload Fails

Possible causes:

- Unsupported file type
- Backend missing `python-multipart`
- File too large
- Backend error

Fix:

- Upload PDF/TXT/MD/CSV
- Install `python-multipart`
- Check Render logs

---

### 7. SendGrid Email Does Not Arrive

Possible causes:

- Unverified sender email
- Wrong SendGrid API key
- Missing Mail Send permission
- Email went to spam

Fix:

- Verify sender identity
- Check SendGrid dashboard
- Confirm env vars
- Check Render logs

---

### 8. Pushover Notification Does Not Arrive

Possible causes:

- Wrong user key
- Wrong app token
- Pushover app not installed
- Device not enabled

Fix:

- Check Pushover dashboard
- Confirm `PUSHOVER_USER`
- Confirm `PUSHOVER_TOKEN`
- Send a test notification from Pushover

---

### 9. Vercel Build Fails

Possible causes:

- Wrong Node version
- Missing dependencies
- Incorrect file paths
- JSX syntax issue

Fix:

- Run locally first with `npm run build`
- Check Vercel logs
- Confirm `src/App.jsx`, `src/main.jsx`, and `src/index.css` exist

---

### 10. Chat says user API key is required

Cause:

- Public cost-control mode is active
- User has not entered their own OpenAI API key
- Frontend is not sending `x-openai-api-key`
- Backend has `REQUIRE_USER_OPENAI_API_KEY=true`

Fix:

- Enter a valid OpenAI API key in the UI
- Confirm the frontend sends `x-openai-api-key`
- Keep the key session-only
- For local private testing, set `REQUIRE_USER_OPENAI_API_KEY=false` if needed

---

### 11. Supabase analytics does not record visitors or questions

Possible causes:

- `SUPABASE_URL` is incorrect
- `SUPABASE_SERVICE_ROLE_KEY` is missing or wrong
- `supabase_schema.sql` was not run
- table names are incorrect
- backend was not redeployed after env changes

Fix:

- `SUPABASE_URL` should look like `https://your-project-ref.supabase.co`
- Do not include `/rest/v1` in `SUPABASE_URL`
- Confirm tables `visitors` and `interactions` exist
- Redeploy Render/Hugging Face after adding secrets

---

### 12. Admin Dashboard Does Not Open

Possible causes:

- New `api_server.py` is not deployed
- `admin_dashboard.html` is missing from backend deployment
- Render is still running an older commit
- You are opening the Vercel frontend instead of the Render backend

Fix:

- Open `https://your-render-service.onrender.com/admin`
- Confirm `admin_dashboard.html` exists in the backend repo
- Redeploy Render
- Check Render logs

---

### 13. Admin Token Fails

Possible causes:

- `ANALYTICS_ADMIN_TOKEN` is missing
- Wrong token entered
- Render was not redeployed after adding the token

Fix:

- Add `ANALYTICS_ADMIN_TOKEN` in Render environment variables
- Redeploy Render
- Enter the same value in the admin dashboard login field

---

### 14. Supabase `session_id` Foreign Key Error

Possible cause:

- The backend is inserting an interaction before creating the matching conversation session
- You are using an older `analytics_db.py`

Fix:

- Replace `analytics_db.py` with the latest version
- Redeploy Render
- Confirm `conversation_sessions` exists in Supabase
- Hard refresh the website

---

### 15. Usage & Cost Tab Shows No Data

Possible causes:

- `usage_events` table was not created
- `SUPABASE_USAGE_TABLE=usage_events` is missing
- Latest `analytics_db.py` / `api_server.py` was not deployed
- No chat/JD requests have happened after the update

Fix:

- Run the latest `supabase_schema.sql`
- Add `SUPABASE_USAGE_TABLE=usage_events`
- Redeploy Render
- Ask a chat question or run JD Fit
- Open `/admin → Usage & Cost`

---

### 16. JD PDF Report Does Not Download

Possible causes:

- `reportlab` is missing from `requirements.txt`
- `/jd_fit_report` endpoint is not deployed
- User OpenAI API key was not entered
- JD file upload failed

Fix:

- Add `reportlab` to `requirements.txt`
- Redeploy Render
- Enter your own OpenAI API key in the UI
- Upload a supported JD file
- Click `Download PDF Report`

---

### 17. Social Preview Image Does Not Update

Possible causes:

- Social platforms cache previews
- Wrong `og:image`
- Image not in `public/preview.png`

Fix:

- Confirm `public/preview.png` exists
- Confirm `index.html` contains Open Graph tags
- Use LinkedIn Post Inspector or social preview debugger
- Wait for cache refresh

---

## 🔒 Security Notes

- Never commit `.env`
- Never expose backend OpenAI keys in frontend code
- Never store user-provided OpenAI keys in Supabase or localStorage
- Never put Supabase service role keys in frontend code
- Never put SendGrid keys in React/Vite frontend
- Keep API keys only on the backend
- Use environment variables in Render/Vercel
- Enable rate limiting
- Keep lead-capture endpoints protected from abuse
- Monitor usage and billing
- Monitor the dashboard `used_owner_key` flag
- Keep user-provided API keys session-only
- Rotate keys if exposed accidentally

---

## 💰 Cost Control Tips

This project can consume API credits.

To control costs:

- Use rate limiting
- Keep model choices reasonable
- Avoid exposing unrestricted backend usage
- Monitor OpenAI usage dashboard
- Monitor `/admin → Usage & Cost`
- Require users to use their own OpenAI API key when testing
- Keep JD analysis concise
- Add authentication if scaling publicly

The UI now includes a mandatory OpenAI API key field for public usage. Users must provide their own key to run Chat and JD-Fit analysis. The key is session-only and is not stored.

---

## 📸 Screenshots

### 1. ShaileshGPT Chatbot Interface

This screenshot shows the main ShaileshGPT chatbot interface where users can ask questions about Shailesh’s experience, skills, projects, certifications, and personality.

![ShaileshGPT Chatbot Interface](screenshots/shaileshgpt-preview.png)

---

### 2. Recruiter JD Fit Analysis

This screenshot shows the Recruiter Mode feature where a user can upload a job description and get a structured fit analysis comparing the JD with Shailesh’s profile.

![Recruiter JD Fit Analysis](screenshots/jd-analysis-fit.png)

---

## 📚 Learning Value

By studying or rebuilding this project, you can learn:

- How to convert a portfolio website into an AI product
- How Agentic RAG works in a personal chatbot
- How to build structured personal knowledge bases
- How to stream LLM responses into a frontend
- How to analyze uploaded files with a backend
- How to build recruiter-facing AI tools
- How to integrate SendGrid and Pushover
- How to deploy a full-stack AI app using Render and Vercel
- How to control API cost and manage secrets

---

## 🚧 Future Improvements

Possible future upgrades:

- Add Supabase Auth or OAuth-based admin login
- Add admin UI to update knowledge base
- Add automatic GitHub/blog ingestion with approval flow
- Add voice input
- Add multilingual support
- Add custom response-style controls
- Add richer charts for dashboard analytics
- Add recruiter report templates in DOCX and Markdown
- Add scheduled email digests of visitor activity

---

## ✅ Final Advice for Builders

If you want to build your own version:

1. Do not copy my profile data.
2. Replace the knowledge base with your own story.
3. Keep the architecture.
4. Improve the UX.
5. Add your own personality.
6. Use your own backend secrets and require user-provided keys for public demos when needed.
7. Deploy responsibly.
8. Build something better.

This project is meant to prove one idea:

> Your portfolio does not have to be a static page. It can be a living AI product that represents you.

---

## ✍️ Author

Created and built by **Shailesh Gupta**

- GitHub: [sg2499](https://github.com/sg2499)
- LinkedIn: [Shailesh Gupta](https://www.linkedin.com/in/shailesh-gupta-7b7278188)
- Blog: [Prismatic Metrics](https://prismatic-metrics.blogspot.com/)
- Portfolio: [Personal Website](https://personal-portfolio-ten-virid-75.vercel.app/)
- Email: shaileshgupta841@gmail.com

---

## ⭐ Support

If this project helps you understand how to build an AI-powered portfolio, consider giving the repository a star.

More importantly, build your own version and make it better.

---

> Built with ambition, caffeine, cricket-level obsession, and enough Agentic RAG to make a static resume feel nervous.
