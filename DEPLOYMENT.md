# Deployment guide

## Option 1 — Hugging Face Spaces

- SDK: Gradio
- App file: `app.py`
- Python version: default modern runtime
- Required secret: `OPENAI_API_KEY`
- Optional secrets: `PUSHOVER_USER`, `PUSHOVER_TOKEN`

Steps:
1. Create a new Space.
2. Upload the whole project folder.
3. Add secrets.
4. Restart the Space.

## Option 2 — Portfolio website widget

### API backend
Deploy with a command like:

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

### Frontend embed
Host `embed/widget.js` and paste this into the website:

```html
<script
  src="https://YOUR_DOMAIN/embed/widget.js"
  data-api-base="https://YOUR_API_DOMAIN"
  data-accent="#60a5fa"
></script>
```

## Suggested hosting stack

- Hugging Face Spaces for the public standalone demo
- Railway / Render / Fly.io for the FastAPI endpoint
- Vercel-hosted portfolio using the floating widget

## Operational notes

- Rebuild the KB after updating profile or raw PDF files:

```bash
python build_kb.py
```

- Pushover notifications are optional and used for weakly grounded queries or potential lead capture.
