(function () {
  const script = document.currentScript;
  const apiBase = script.dataset.apiBase || "http://localhost:8000";
  const accent = script.dataset.accent || "#60a5fa";

  const root = document.createElement("div");
  root.id = "sg-portfolio-chat-widget";
  root.innerHTML = `
    <style>
      #sg-portfolio-chat-widget * { box-sizing: border-box; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
      #sg-chat-bubble { position: fixed; right: 24px; bottom: 24px; width: 62px; height: 62px; border-radius: 999px; border: 1px solid rgba(255,255,255,.18); cursor: pointer; background: linear-gradient(135deg, ${accent}, #22d3ee); color: white; box-shadow: 0 18px 55px rgba(0,0,0,.36); font-size: 26px; z-index: 999999; }
      #sg-chat-panel { position: fixed; right: 24px; bottom: 100px; width: 430px; max-width: calc(100vw - 28px); height: 700px; background: #070b14; border: 1px solid rgba(148,163,184,.20); border-radius: 24px; box-shadow: 0 24px 85px rgba(0,0,0,.44); overflow: hidden; display: none; z-index: 999999; }
      #sg-chat-header { padding: 18px 18px 15px; background: linear-gradient(135deg, rgba(96,165,250,.20), rgba(34,211,238,.10)); color: #f4f7fb; border-bottom: 1px solid rgba(148,163,184,.14); }
      #sg-chat-header strong { display:block; font-size: 16px; letter-spacing: -.01em; }
      #sg-chat-header span { display:block; color:#a8b8d8; font-size:13px; margin-top:4px; line-height:1.4; }
      #sg-tabs { display:flex; gap:8px; padding:10px 12px; background:#07101f; border-bottom:1px solid rgba(148,163,184,.12); }
      .sg-tab { flex:1; border:1px solid rgba(148,163,184,.14); background:rgba(255,255,255,.055); color:#dbeafe; border-radius:999px; padding:8px 10px; cursor:pointer; font-weight:700; font-size:13px; }
      .sg-tab.active { background:linear-gradient(135deg, rgba(96,165,250,.28), rgba(34,211,238,.15)); border-color:rgba(125,211,252,.24); }
      #sg-chat-view, #sg-lead-view { display:none; }
      #sg-chat-view.active, #sg-lead-view.active { display:block; }
      #sg-chat-messages { height: 470px; overflow-y: auto; padding: 16px; background: #050914; }
      .sg-msg { max-width: 85%; padding: 11px 13px; border-radius: 17px; margin-bottom: 11px; line-height: 1.52; font-size: 14px; white-space: pre-wrap; }
      .sg-user { margin-left: auto; background: linear-gradient(135deg, rgba(96,165,250,.28), rgba(34,211,238,.15)); color:#f4f7fb; border: 1px solid rgba(125,211,252,.16); }
      .sg-assistant { background: rgba(15,23,42,.96); color:#e6eefb; border: 1px solid rgba(148,163,184,.13); }
      .sg-typing { opacity: .78; }
      #sg-chat-input-wrap { display:flex; gap:10px; padding: 12px; border-top: 1px solid rgba(148,163,184,.14); background:#07101f; }
      #sg-chat-input, .sg-lead-input, .sg-lead-textarea { width:100%; border-radius: 15px; border:1px solid rgba(148,163,184,.18); background:#0b1426; color:#f4f7fb; padding: 11px 12px; outline:none; }
      #sg-chat-send, #sg-lead-send { border:none; border-radius: 15px; padding: 0 16px; background: linear-gradient(135deg, ${accent}, #22d3ee); color:white; cursor:pointer; font-weight:800; }
      #sg-chat-send:disabled, #sg-lead-send:disabled { opacity:.55; cursor:not-allowed; }
      #sg-lead-view { height: 592px; overflow-y:auto; padding:16px; background:#050914; color:#e6eefb; }
      .sg-lead-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
      .sg-lead-field { margin-bottom:10px; }
      .sg-lead-field label { display:block; color:#a8b8d8; font-size:12px; margin-bottom:5px; }
      .sg-lead-textarea { resize:vertical; min-height:76px; }
      #sg-lead-status { color:#dbeafe; font-size:13px; line-height:1.45; margin-top:10px; }
      .sg-note { color:#a8b8d8; line-height:1.5; font-size:13px; margin-bottom:12px; }
    </style>
    <button id="sg-chat-bubble">💬</button>
    <div id="sg-chat-panel">
      <div id="sg-chat-header"><div style="display:flex;align-items:center;gap:10px;"><img src="https://raw.githubusercontent.com/sg2499/Personal-Documents/main/PP.jpg" style="width:38px;height:38px;border-radius:999px;object-fit:cover;border:2px solid rgba(125,211,252,.45);" /><div><strong>ShaileshGPT</strong><span>Ask about Shailesh or drop your details to connect.</span></div></div></div>
      <div id="sg-tabs">
        <button class="sg-tab active" id="sg-tab-chat">Chat</button>
        <button class="sg-tab" id="sg-tab-lead">Connect</button>
      </div>
      <div id="sg-chat-view" class="active">
        <div id="sg-chat-messages">
          <div class="sg-msg sg-assistant">Hey, I’m ShaileshGPT — the portfolio twin. Ask me anything about Shailesh, and I’ll keep it useful, sharp, and mildly less boring than a resume PDF.</div>
        </div>
        <div id="sg-chat-input-wrap">
          <input id="sg-chat-input" placeholder="Ask something..." />
          <button id="sg-chat-send">Send</button>
        </div>
      </div>
      <div id="sg-lead-view">
        <div class="sg-note">Want Shailesh to get back to you? Leave any contact route you prefer. Email, phone, LinkedIn, GitHub, website — your call.</div>
        <div class="sg-lead-grid">
          <div class="sg-lead-field"><label>Name</label><input class="sg-lead-input" id="sg-lead-name" /></div>
          <div class="sg-lead-field"><label>Email</label><input class="sg-lead-input" id="sg-lead-email" /></div>
          <div class="sg-lead-field"><label>Phone</label><input class="sg-lead-input" id="sg-lead-phone" /></div>
          <div class="sg-lead-field"><label>LinkedIn</label><input class="sg-lead-input" id="sg-lead-linkedin" /></div>
          <div class="sg-lead-field"><label>GitHub</label><input class="sg-lead-input" id="sg-lead-github" /></div>
          <div class="sg-lead-field"><label>Website</label><input class="sg-lead-input" id="sg-lead-website" /></div>
        </div>
        <div class="sg-lead-field"><label>Other contact</label><input class="sg-lead-input" id="sg-lead-other" /></div>
        <div class="sg-lead-field"><label>Message / Intent</label><textarea class="sg-lead-textarea" id="sg-lead-message" placeholder="Hiring, collaboration, project feedback, cricket debate..."></textarea></div>
        <button id="sg-lead-send">Send details to Shailesh</button>
        <div id="sg-lead-status"></div>
      </div>
    </div>`;
  document.body.appendChild(root);

  const bubble = root.querySelector("#sg-chat-bubble");
  const panel = root.querySelector("#sg-chat-panel");
  const messages = root.querySelector("#sg-chat-messages");
  const input = root.querySelector("#sg-chat-input");
  const send = root.querySelector("#sg-chat-send");
  const history = [];

  const tabChat = root.querySelector("#sg-tab-chat");
  const tabLead = root.querySelector("#sg-tab-lead");
  const chatView = root.querySelector("#sg-chat-view");
  const leadView = root.querySelector("#sg-lead-view");
  const leadSend = root.querySelector("#sg-lead-send");
  const leadStatus = root.querySelector("#sg-lead-status");

  function switchTab(tab) {
    const isLead = tab === "lead";
    tabLead.classList.toggle("active", isLead);
    tabChat.classList.toggle("active", !isLead);
    leadView.classList.toggle("active", isLead);
    chatView.classList.toggle("active", !isLead);
  }

  function addMsg(role, text, extraClass = "") {
    const div = document.createElement("div");
    div.className = `sg-msg ${role === "user" ? "sg-user" : "sg-assistant"} ${extraClass}`;
    div.textContent = text;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
    return div;
  }

  async function streamAnswer(text) {
    const assistant = addMsg("assistant", "", "sg-typing");
    let finalText = "";

    const res = await fetch(`${apiBase}/chat_stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, history: history.slice(0, -1) })
    });

    if (!res.ok || !res.body) throw new Error("stream unavailable");

    const reader = res.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split("\\n\\n");
      buffer = events.pop() || "";

      for (const event of events) {
        const line = event.split("\\n").find((l) => l.startsWith("data: "));
        if (!line) continue;
        const payload = JSON.parse(line.slice(6));
        if (payload.error) throw new Error(payload.error);
        if (payload.token) {
          finalText += payload.token;
          assistant.textContent = finalText;
          messages.scrollTop = messages.scrollHeight;
        }
      }
    }

    assistant.classList.remove("sg-typing");
    history.push({ role: "assistant", content: finalText });
  }

  async function submit() {
    const text = input.value.trim();
    if (!text || send.disabled) return;

    addMsg("user", text);
    history.push({ role: "user", content: text });
    input.value = "";
    send.disabled = true;

    try {
      await streamAnswer(text);
    } catch (e) {
      addMsg("assistant", "The portfolio assistant is temporarily unavailable or taking a short breather. Even bots need a timeout sometimes.");
    } finally {
      send.disabled = false;
      input.focus();
    }
  }

  async function submitLead() {
    if (leadSend.disabled) return;
    leadSend.disabled = true;
    leadStatus.textContent = "Sending...";
    const payload = {
      name: root.querySelector("#sg-lead-name").value,
      email: root.querySelector("#sg-lead-email").value,
      phone: root.querySelector("#sg-lead-phone").value,
      linkedin: root.querySelector("#sg-lead-linkedin").value,
      github: root.querySelector("#sg-lead-github").value,
      website: root.querySelector("#sg-lead-website").value,
      other_contact: root.querySelector("#sg-lead-other").value,
      message: root.querySelector("#sg-lead-message").value,
      source: "Website widget"
    };

    try {
      const res = await fetch(`${apiBase}/lead`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      leadStatus.textContent = data.message || "Sent.";
    } catch (e) {
      leadStatus.textContent = "Could not send details right now. The bot tried; the internet chose violence.";
    } finally {
      leadSend.disabled = false;
    }
  }

  bubble.onclick = () => { panel.style.display = panel.style.display === "block" ? "none" : "block"; };
  tabChat.onclick = () => switchTab("chat");
  tabLead.onclick = () => switchTab("lead");
  send.onclick = submit;
  leadSend.onclick = submitLead;
  input.addEventListener("keydown", (e) => { if (e.key === "Enter") submit(); });
})();
