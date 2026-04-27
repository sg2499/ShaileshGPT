(function () {
  const script = document.currentScript;
  const apiBase = script.dataset.apiBase || "http://localhost:8000";
  const accent = script.dataset.accent || "#60a5fa";
  const storageKey = "shaileshgpt_visitor";

  const root = document.createElement("div");
  root.id = "sg-portfolio-chat-widget";
  root.innerHTML = `
    <style>
      #sg-portfolio-chat-widget * { box-sizing: border-box; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
      #sg-chat-bubble { position: fixed; right: 24px; bottom: 24px; width: 62px; height: 62px; border-radius: 999px; border: 1px solid rgba(255,255,255,.18); cursor: pointer; background: linear-gradient(135deg, ${accent}, #22d3ee); color: white; box-shadow: 0 18px 55px rgba(0,0,0,.36); font-size: 26px; z-index: 999999; }
      #sg-chat-panel { position: fixed; right: 24px; bottom: 100px; width: 430px; max-width: calc(100vw - 28px); height: 700px; background: #070b14; border: 1px solid rgba(148,163,184,.20); border-radius: 24px; box-shadow: 0 24px 85px rgba(0,0,0,.44); overflow: hidden; display: none; z-index: 999999; }
      #sg-chat-header { padding: 18px; background: linear-gradient(135deg, rgba(96,165,250,.20), rgba(34,211,238,.10)); color: #f4f7fb; border-bottom: 1px solid rgba(148,163,184,.14); }
      #sg-chat-header strong { display:block; font-size: 16px; letter-spacing: -.01em; }
      #sg-chat-header span { display:block; color:#a8b8d8; font-size:13px; margin-top:4px; line-height:1.4; }
      #sg-tabs { display:flex; gap:8px; padding:10px 12px; background:#07101f; border-bottom:1px solid rgba(148,163,184,.12); }
      .sg-tab { flex:1; border:1px solid rgba(148,163,184,.14); background:rgba(255,255,255,.055); color:#dbeafe; border-radius:999px; padding:8px 10px; cursor:pointer; font-weight:700; font-size:13px; }
      .sg-tab.active { background:linear-gradient(135deg, rgba(96,165,250,.28), rgba(34,211,238,.15)); border-color:rgba(125,211,252,.24); }
      #sg-gate-view, #sg-chat-view, #sg-lead-view { display:none; }
      #sg-gate-view.active, #sg-chat-view.active, #sg-lead-view.active { display:block; }
      #sg-chat-messages { height: 470px; overflow-y: auto; padding: 16px; background: #050914; }
      .sg-msg { max-width: 85%; padding: 11px 13px; border-radius: 17px; margin-bottom: 11px; line-height: 1.52; font-size: 14px; white-space: pre-wrap; }
      .sg-user { margin-left: auto; background: linear-gradient(135deg, rgba(96,165,250,.28), rgba(34,211,238,.15)); color:#f4f7fb; border: 1px solid rgba(125,211,252,.16); }
      .sg-assistant { background: rgba(15,23,42,.96); color:#e6eefb; border: 1px solid rgba(148,163,184,.13); }
      .sg-typing { opacity: .78; }
      #sg-chat-input-wrap { display:flex; gap:10px; padding: 12px; border-top: 1px solid rgba(148,163,184,.14); background:#07101f; }
      #sg-chat-input, .sg-input, .sg-textarea { width:100%; border-radius: 15px; border:1px solid rgba(148,163,184,.18); background:#0b1426; color:#f4f7fb; padding: 11px 12px; outline:none; }
      #sg-chat-send, #sg-lead-send, #sg-gate-submit { border:none; border-radius: 15px; padding: 11px 16px; background: linear-gradient(135deg, ${accent}, #22d3ee); color:white; cursor:pointer; font-weight:800; }
      #sg-chat-send:disabled, #sg-lead-send:disabled, #sg-gate-submit:disabled { opacity:.55; cursor:not-allowed; }
      #sg-lead-view, #sg-gate-view { height: 592px; overflow-y:auto; padding:16px; background:#050914; color:#e6eefb; }
      .sg-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
      .sg-field { margin-bottom:10px; }
      .sg-field label { display:block; color:#a8b8d8; font-size:12px; margin-bottom:5px; }
      .sg-textarea { resize:vertical; min-height:76px; }
      .sg-status { color:#dbeafe; font-size:13px; line-height:1.45; margin-top:10px; }
      .sg-note { color:#a8b8d8; line-height:1.5; font-size:13px; margin-bottom:12px; }
    </style>
    <button id="sg-chat-bubble">💬</button>
    <div id="sg-chat-panel">
      <div id="sg-chat-header"><div style="display:flex;align-items:center;gap:10px;"><img src="https://raw.githubusercontent.com/sg2499/Personal-Documents/main/PP.jpg" style="width:38px;height:38px;border-radius:999px;object-fit:cover;border:2px solid rgba(125,211,252,.45);" /><div><strong>ShaileshGPT</strong><span>Enter details once, then ask anything about Shailesh.</span></div></div></div>
      <div id="sg-tabs">
        <button class="sg-tab active" id="sg-tab-gate">Access</button>
        <button class="sg-tab" id="sg-tab-chat">Chat</button>
        <button class="sg-tab" id="sg-tab-lead">Connect</button>
      </div>
      <div id="sg-gate-view" class="active">
        <div class="sg-note">Please enter your name and email before using the bot. This helps Shailesh understand who is exploring the product. Your questions may be logged for product insights.</div>
        <div class="sg-field"><label>Name *</label><input class="sg-input" id="sg-gate-name" /></div>
        <div class="sg-field"><label>Email *</label><input class="sg-input" id="sg-gate-email" /></div>
        <div class="sg-grid">
          <div class="sg-field"><label>Phone</label><input class="sg-input" id="sg-gate-phone" /></div>
          <div class="sg-field"><label>LinkedIn</label><input class="sg-input" id="sg-gate-linkedin" /></div>
          <div class="sg-field"><label>GitHub</label><input class="sg-input" id="sg-gate-github" /></div>
          <div class="sg-field"><label>Website</label><input class="sg-input" id="sg-gate-website" /></div>
        </div>
        <div class="sg-field"><label>Other contact</label><input class="sg-input" id="sg-gate-other" /></div>
        <button id="sg-gate-submit">Start using ShaileshGPT</button>
        <div id="sg-gate-status" class="sg-status"></div>
      </div>
      <div id="sg-chat-view">
        <div id="sg-chat-messages"><div class="sg-msg sg-assistant">Hey, I’m ShaileshGPT — the portfolio twin. Ask me anything about Shailesh after completing Visitor Access.</div></div>
        <div id="sg-chat-input-wrap"><input id="sg-chat-input" placeholder="Ask something..." /><button id="sg-chat-send">Send</button></div>
      </div>
      <div id="sg-lead-view">
        <div class="sg-note">Want Shailesh to get back to you? Leave any extra contact route you prefer.</div>
        <div class="sg-grid">
          <div class="sg-field"><label>Name</label><input class="sg-input" id="sg-lead-name" /></div>
          <div class="sg-field"><label>Email</label><input class="sg-input" id="sg-lead-email" /></div>
          <div class="sg-field"><label>Phone</label><input class="sg-input" id="sg-lead-phone" /></div>
          <div class="sg-field"><label>LinkedIn</label><input class="sg-input" id="sg-lead-linkedin" /></div>
          <div class="sg-field"><label>GitHub</label><input class="sg-input" id="sg-lead-github" /></div>
          <div class="sg-field"><label>Website</label><input class="sg-input" id="sg-lead-website" /></div>
        </div>
        <div class="sg-field"><label>Other contact</label><input class="sg-input" id="sg-lead-other" /></div>
        <div class="sg-field"><label>Message / Intent</label><textarea class="sg-textarea" id="sg-lead-message"></textarea></div>
        <button id="sg-lead-send">Send details to Shailesh</button><div id="sg-lead-status" class="sg-status"></div>
      </div>
    </div>`;
  document.body.appendChild(root);

  const $ = (selector) => root.querySelector(selector);
  const bubble = $("#sg-chat-bubble"), panel = $("#sg-chat-panel"), messages = $("#sg-chat-messages"), input = $("#sg-chat-input"), send = $("#sg-chat-send");
  const tabs = { gate: $("#sg-tab-gate"), chat: $("#sg-tab-chat"), lead: $("#sg-tab-lead") };
  const views = { gate: $("#sg-gate-view"), chat: $("#sg-chat-view"), lead: $("#sg-lead-view") };
  const history = [];
  let visitor = null;

  try { visitor = JSON.parse(localStorage.getItem(storageKey) || "null"); } catch(e) { visitor = null; }

  function switchTab(tab) {
    if ((tab === "chat" || tab === "lead") && !visitor) tab = "gate";
    Object.keys(tabs).forEach(k => tabs[k].classList.toggle("active", k === tab));
    Object.keys(views).forEach(k => views[k].classList.toggle("active", k === tab));
  }
  function addMsg(role, text, extraClass = "") { const div = document.createElement("div"); div.className = `sg-msg ${role === "user" ? "sg-user" : "sg-assistant"} ${extraClass}`; div.textContent = text; messages.appendChild(div); messages.scrollTop = messages.scrollHeight; return div; }
  async function registerVisitor() {
    const payload = { name: $("#sg-gate-name").value, email: $("#sg-gate-email").value, phone: $("#sg-gate-phone").value, linkedin: $("#sg-gate-linkedin").value, github: $("#sg-gate-github").value, website: $("#sg-gate-website").value, other_contact: $("#sg-gate-other").value, source: "Website widget", user_agent: navigator.userAgent };
    $("#sg-gate-status").textContent = "Saving...";
    try {
      const res = await fetch(`${apiBase}/visitor/start`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Could not save details");
      visitor = { visitor_id: data.visitor_id, name: data.name, email: data.email };
      localStorage.setItem(storageKey, JSON.stringify(visitor));
      $("#sg-lead-name").value = payload.name; $("#sg-lead-email").value = payload.email; $("#sg-lead-phone").value = payload.phone; $("#sg-lead-linkedin").value = payload.linkedin; $("#sg-lead-github").value = payload.github; $("#sg-lead-website").value = payload.website; $("#sg-lead-other").value = payload.other_contact;
      $("#sg-gate-status").textContent = data.message || "You can now use ShaileshGPT.";
      switchTab("chat");
    } catch(e) { $("#sg-gate-status").textContent = e.message; }
  }
  async function streamAnswer(text) {
    if (!visitor) { switchTab("gate"); return; }
    const assistant = addMsg("assistant", "", "sg-typing"); let finalText = "";
    const res = await fetch(`${apiBase}/chat_stream`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message: text, history: history.slice(0, -1), visitor_id: visitor.visitor_id }) });
    if (!res.ok || !res.body) throw new Error("stream unavailable");
    const reader = res.body.getReader(); const decoder = new TextDecoder("utf-8"); let buffer = "";
    while (true) { const { value, done } = await reader.read(); if (done) break; buffer += decoder.decode(value, { stream: true }); const events = buffer.split("\\n\\n"); buffer = events.pop() || ""; for (const event of events) { const line = event.split("\\n").find((l) => l.startsWith("data: ")); if (!line) continue; const payload = JSON.parse(line.slice(6)); if (payload.error) throw new Error(payload.error); if (payload.token) { finalText += payload.token; assistant.textContent = finalText; messages.scrollTop = messages.scrollHeight; } } }
    assistant.classList.remove("sg-typing"); history.push({ role: "assistant", content: finalText });
  }
  async function submit() { const text = input.value.trim(); if (!text || send.disabled) return; if (!visitor) { switchTab("gate"); return; } addMsg("user", text); history.push({ role: "user", content: text }); input.value = ""; send.disabled = true; try { await streamAnswer(text); } catch(e) { addMsg("assistant", "The portfolio assistant is temporarily unavailable or taking a short breather."); } finally { send.disabled = false; input.focus(); } }
  async function submitLead() { const payload = { visitor_id: visitor ? visitor.visitor_id : "", name: $("#sg-lead-name").value, email: $("#sg-lead-email").value, phone: $("#sg-lead-phone").value, linkedin: $("#sg-lead-linkedin").value, github: $("#sg-lead-github").value, website: $("#sg-lead-website").value, other_contact: $("#sg-lead-other").value, message: $("#sg-lead-message").value, source: "Website widget" }; $("#sg-lead-status").textContent = "Sending..."; try { const res = await fetch(`${apiBase}/lead`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) }); const data = await res.json(); $("#sg-lead-status").textContent = data.message || "Sent."; } catch(e) { $("#sg-lead-status").textContent = "Could not send details right now."; } }

  bubble.onclick = () => { panel.style.display = panel.style.display === "block" ? "none" : "block"; if (!visitor) switchTab("gate"); };
  tabs.gate.onclick = () => switchTab("gate"); tabs.chat.onclick = () => switchTab("chat"); tabs.lead.onclick = () => switchTab("lead");
  $("#sg-gate-submit").onclick = registerVisitor; send.onclick = submit; $("#sg-lead-send").onclick = submitLead; input.addEventListener("keydown", (e) => { if (e.key === "Enter") submit(); });
  if (visitor) switchTab("chat"); else switchTab("gate");
})();
