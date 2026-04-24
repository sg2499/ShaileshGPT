(function () {
  const script = document.currentScript;
  const apiBase = script.dataset.apiBase || "http://localhost:8000";
  const accent = script.dataset.accent || "#60a5fa";

  const root = document.createElement("div");
  root.id = "sg-portfolio-chat-widget";
  root.innerHTML = `
    <style>
      #sg-portfolio-chat-widget * { box-sizing: border-box; font-family: Inter, system-ui, sans-serif; }
      #sg-chat-bubble { position: fixed; right: 24px; bottom: 24px; width: 64px; height: 64px; border-radius: 999px; border: none; cursor: pointer; background: linear-gradient(135deg, ${accent}, #22d3ee); color: white; box-shadow: 0 12px 40px rgba(0,0,0,.28); font-size: 28px; z-index: 999999; }
      #sg-chat-panel { position: fixed; right: 24px; bottom: 100px; width: 390px; max-width: calc(100vw - 24px); height: 620px; background: #07101f; border: 1px solid rgba(148,163,184,.18); border-radius: 22px; box-shadow: 0 20px 60px rgba(0,0,0,.32); overflow: hidden; display: none; z-index: 999999; }
      #sg-chat-header { padding: 16px 18px; background: linear-gradient(135deg, rgba(96,165,250,.18), rgba(34,211,238,.12)); color: #eef4ff; border-bottom: 1px solid rgba(148,163,184,.15); }
      #sg-chat-header strong { display:block; font-size: 15px; }
      #sg-chat-header span { color:#a8b8d8; font-size:13px; }
      #sg-chat-messages { height: 470px; overflow-y: auto; padding: 14px; background: #050b18; }
      .sg-msg { max-width: 82%; padding: 11px 13px; border-radius: 16px; margin-bottom: 10px; line-height: 1.45; font-size: 14px; white-space: pre-wrap; }
      .sg-user { margin-left: auto; background: rgba(96,165,250,.18); color:#eef4ff; }
      .sg-assistant { background: rgba(15,23,42,.95); color:#dfe8f8; border: 1px solid rgba(148,163,184,.12); }
      #sg-chat-input-wrap { display:flex; gap:10px; padding: 12px; border-top: 1px solid rgba(148,163,184,.14); background:#07101f; }
      #sg-chat-input { flex:1; border-radius: 14px; border:1px solid rgba(148,163,184,.18); background:#0b1426; color:#eef4ff; padding: 12px; }
      #sg-chat-send { border:none; border-radius: 14px; padding: 0 16px; background: linear-gradient(135deg, ${accent}, #22d3ee); color:white; cursor:pointer; font-weight:600; }
    </style>
    <button id="sg-chat-bubble">💬</button>
    <div id="sg-chat-panel">
      <div id="sg-chat-header"><strong>Ask about Shailesh</strong><span>AI portfolio assistant</span></div>
      <div id="sg-chat-messages">
        <div class="sg-msg sg-assistant">Hi — I can answer questions about Shailesh's experience, projects, skills, education, certifications, hobbies, and work style.</div>
      </div>
      <div id="sg-chat-input-wrap">
        <input id="sg-chat-input" placeholder="Ask something..." />
        <button id="sg-chat-send">Send</button>
      </div>
    </div>`;
  document.body.appendChild(root);

  const bubble = root.querySelector("#sg-chat-bubble");
  const panel = root.querySelector("#sg-chat-panel");
  const messages = root.querySelector("#sg-chat-messages");
  const input = root.querySelector("#sg-chat-input");
  const send = root.querySelector("#sg-chat-send");
  const history = [];

  function addMsg(role, text) {
    const div = document.createElement("div");
    div.className = `sg-msg ${role === 'user' ? 'sg-user' : 'sg-assistant'}`;
    div.textContent = text;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  async function submit() {
    const text = input.value.trim();
    if (!text) return;
    addMsg('user', text);
    history.push({ role: 'user', content: text });
    input.value = '';
    try {
      const res = await fetch(`${apiBase}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, history: history.slice(0, -1) })
      });
      const data = await res.json();
      addMsg('assistant', data.answer || 'Sorry, something went wrong.');
      history.push({ role: 'assistant', content: data.answer || '' });
    } catch (e) {
      addMsg('assistant', 'The portfolio assistant is temporarily unavailable.');
    }
  }

  bubble.onclick = () => { panel.style.display = panel.style.display === 'block' ? 'none' : 'block'; };
  send.onclick = submit;
  input.addEventListener('keydown', (e) => { if (e.key === 'Enter') submit(); });
})();
