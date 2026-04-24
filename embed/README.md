# Website embed

1. Deploy `api_server.py` to a Python host such as Railway, Render, Fly.io, or your own VM.
2. Serve `embed/widget.js` from your website or a CDN path.
3. Paste the snippet from `embed-snippet.html` into your portfolio site.
4. Set `data-api-base` to the deployed API URL.

The widget opens as a floating chat bubble and talks to the same agentic RAG backend used by the Gradio app.
