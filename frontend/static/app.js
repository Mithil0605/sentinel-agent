"use strict";

const $ = (sel) => document.querySelector(sel);

let sessionId = localStorage.getItem("sa_session") || `sess_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
localStorage.setItem("sa_session", sessionId);

const TOOL_ICONS = {
  calculator: "🧮",
  get_weather: "🌤️",
  get_time: "🕒",
  create_ticket: "🎫",
  knowledge_lookup: "📚",
};

const toolDescriptions = {
  calculator: "Evaluate a safe arithmetic expression (+, -, *, /, **, %).",
  get_weather: "Get the current weather conditions for a known city.",
  get_time: "Return the current UTC date and time.",
  create_ticket: "Create an internal support ticket.",
  knowledge_lookup: "Search the internal company knowledge base.",
};

const messagesEl = $("#messages");
const form = $("#chat-form");
const input = $("#input");
const sendBtn = $(".send-btn");

function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = `message ${role}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  div.appendChild(bubble);
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return div;
}

function addToolTurn(turn) {
  const div = document.createElement("div");
  div.className = "message tool";
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  if (turn.type === "tool_call") {
    bubble.textContent = `⚙ ${turn.name}(${JSON.stringify(turn.arguments || {})})`;
  } else {
    bubble.textContent = `↳ ${turn.content || "(no result)"}`;
  }
  div.appendChild(bubble);
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

async function sendMessage(text) {
  form.reset();
  input.style.height = "auto";
  const userMsg = addMessage("user", text);

  const typing = addMessage("assistant", "");
  const bubble = typing.querySelector(".bubble");
  bubble.classList.add("typing");
  bubble.textContent = "Thinking";

  sendBtn.disabled = true;
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, session_id: sessionId }),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || `Request failed (${res.status})`);
    }
    const data = await res.json();

    (data.turns || []).forEach((t) => addToolTurn(t));

    typing.querySelector(".bubble").classList.remove("typing");
    bubble.textContent = data.response || "(no response)";
  } catch (err) {
    typing.querySelector(".bubble").classList.remove("typing");
    bubble.textContent = `Error: ${err.message}`;
    bubble.style.color = "var(--danger)";
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  sendMessage(text);
});

input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 160) + "px";
});

$("#new-chat").addEventListener("click", () => {
  sessionId = `sess_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
  localStorage.setItem("sa_session", sessionId);
  messagesEl.innerHTML = "";
  addMessage("assistant", "Hi, I'm the Sentinel Agent. How can I help?");
});

async function loadTools() {
  const list = $("#tools-list");
  try {
    const res = await fetch("/api/tools");
    const data = await res.json();
    data.tools.forEach((tool) => {
      const card = document.createElement("div");
      card.className = "card";
      const icon = TOOL_ICONS[tool.name] || "🔧";
      card.innerHTML =
        `<h3><span class="tool-icon">${icon}</span>${tool.name}</h3>` +
        `<p>${toolDescriptions[tool.name] || tool.description}</p>` +
        `<span class="mono">✓ registered</span>`;
      list.appendChild(card);
    });
  } catch (err) {
    list.innerHTML = `<div class="empty">Could not load tools: ${err.message}</div>`;
  }
}

async function loadSessions() {
  const list = $("#sessions-list");
  try {
    const res = await fetch("/api/sessions");
    const data = await res.json();
    if (!data.sessions.length) {
      list.innerHTML = '<div class="empty">No sessions yet.</div>';
      return;
    }
    data.sessions.forEach((id) => {
      const card = document.createElement("div");
      card.className = "card";
      card.innerHTML = `<div class="mono">${id}</div><p>Session conversation</p>`;
      list.appendChild(card);
    });
  } catch (err) {
    list.innerHTML = `<div class="empty">Could not load sessions: ${err.message}</div>`;
  }
}

document.querySelectorAll(".nav-item").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".nav-item").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    document.querySelectorAll(".view").forEach((v) => v.classList.remove("active"));
    $("#view-" + btn.dataset.view).classList.add("active");
    if (btn.dataset.view === "tools") loadTools();
    if (btn.dataset.view === "sessions") loadSessions();
  });
});
