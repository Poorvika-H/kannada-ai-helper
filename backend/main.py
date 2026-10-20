from dotenv import load_dotenv
load_dotenv()  # reads GEMINI_API_KEY from backend/.env when running locally

from google import genai
from google.genai import types
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()
client = genai.Client()  # reads GEMINI_API_KEY automatically
MODEL = "gemini-flash-latest"

PROMPTS = {
    "kn": (
        "You are a kind, patient helper for a woman who does not know English. "
        "Always reply ONLY in simple spoken Kannada, written in Kannada script. "
        "Use short sentences and everyday words. Avoid English words and technical jargon. "
        "Give steps one at a time. For health or legal matters, give general guidance "
        "and tell her to consult a doctor or professional. "
        "In an emergency, tell her to call 108 (ambulance) or 181 (women's helpline)."
    ),
    "en": (
        "You are a friendly study helper for students. Explain concepts step by step "
        "in simple English, give examples, and ask a follow-up question to check understanding."
    ),
}


class ChatRequest(BaseModel):
    lang: str
    messages: list[dict]


@app.get("/")
def home():
    return HTMLResponse(INDEX_HTML)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(req: ChatRequest):
    contents = [
        types.Content(
            role="model" if m["role"] == "assistant" else "user",
            parts=[types.Part(text=m["content"])],
        )
        for m in req.messages
    ]
    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=PROMPTS.get(req.lang, PROMPTS["kn"])
        ),
    )
    return {"reply": response.text}


INDEX_HTML = r"""<!DOCTYPE html>
<html lang="kn">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#1F5C4A">
<title>ನಿಮ್ಮ ಸಹಾಯಕ</title>
<style>
  * { box-sizing: border-box; }
  html, body { height: 100%; margin: 0; }
  body {
    display: flex; flex-direction: column;
    background: #FBF8F1; color: #1b1b1b;
    font-family: system-ui, "Noto Sans Kannada", "Nirmala UI", sans-serif;
  }
  header {
    background: #1F5C4A; color: #fff; padding: 14px 16px;
    display: flex; justify-content: space-between; align-items: center; gap: 12px;
  }
  header h1 { font-size: 22px; margin: 0; }
  .toggle { display: flex; background: #174638; border-radius: 24px; }
  .toggle button {
    border: 0; background: transparent; color: #cfe3da;
    font: inherit; font-size: 16px; padding: 8px 14px; border-radius: 24px; cursor: pointer;
  }
  .toggle button.on { background: #F2B544; color: #1b1b1b; font-weight: 700; }
  #chat { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
  .empty { margin: auto; text-align: center; font-size: 22px; color: #555; padding: 24px; }
  .bubble {
    max-width: 88%; padding: 14px; border-radius: 16px;
    font-size: 19px; line-height: 1.6; white-space: pre-wrap; overflow-wrap: anywhere;
  }
  .user { align-self: flex-end; background: #1F5C4A; color: #fff; }
  .bot { align-self: flex-start; background: #fff; border: 1px solid #e3dccb; }
  .wait { color: #777; font-style: italic; }
  footer { display: flex; gap: 8px; padding: 12px; align-items: flex-end; }
  textarea {
    flex: 1; font: inherit; font-size: 19px; padding: 12px; resize: none;
    border: 1px solid #d6cfbd; border-radius: 14px; background: #fff; max-height: 120px;
  }
  textarea:focus-visible, button:focus-visible { outline: 3px solid #F2B544; outline-offset: 2px; }
  #send {
    border: 0; background: #1F5C4A; color: #fff; font: inherit;
    font-size: 18px; font-weight: 700; padding: 14px 18px; border-radius: 14px; cursor: pointer;
  }
  #send:disabled { opacity: .5; }
</style>
</head>
<body>
<header>
  <h1 id="title"></h1>
  <div class="toggle">
    <button id="btn-kn" type="button">ಕನ್ನಡ</button>
    <button id="btn-en" type="button">English</button>
  </div>
</header>
<main id="chat" aria-live="polite"></main>
<footer>
  <textarea id="input" rows="1"></textarea>
  <button id="send" type="button"></button>
</footer>

<script>
const UI = {
  kn: { title: "ನಿಮ್ಮ ಸಹಾಯಕ", hint: "ನಿಮ್ಮ ಪ್ರಶ್ನೆ ಇಲ್ಲಿ ಬರೆಯಿರಿ", send: "ಕಳುಹಿಸಿ",
        empty: "ನಿಮಗೆ ಏನು ತಿಳಿಯಬೇಕು? ಕೇಳಿ.", wait: "ಸ್ವಲ್ಪ ಕಾಯಿರಿ...",
        error: "ಏನೋ ತೊಂದರೆ ಆಯಿತು. ಇಂಟರ್ನೆಟ್ ನೋಡಿ, ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ." },
  en: { title: "Study Helper", hint: "Type your question here", send: "Send",
        empty: "What would you like to learn today?", wait: "One moment...",
        error: "Something went wrong. Check your internet and try again." }
};

let lang = "kn";
let messages = [];
let loading = false;

const chat = document.getElementById("chat");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send");

function addBubble(text, cls) {
  const div = document.createElement("div");
  div.className = "bubble " + cls;
  div.textContent = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
  return div;
}

function render() {
  const t = UI[lang];
  document.documentElement.lang = lang;
  document.getElementById("title").textContent = t.title;
  input.placeholder = t.hint;
  sendBtn.textContent = t.send;
  document.getElementById("btn-kn").classList.toggle("on", lang === "kn");
  document.getElementById("btn-en").classList.toggle("on", lang === "en");
  chat.innerHTML = "";
  if (messages.length === 0) {
    const e = document.createElement("div");
    e.className = "empty";
    e.textContent = t.empty;
    chat.appendChild(e);
  }
  messages.forEach(m => addBubble(m.content, m.role === "user" ? "user" : "bot"));
}

function setLang(next) {
  lang = next;
  messages = [];
  render();
}

async function send() {
  const text = input.value.trim();
  if (!text || loading) return;
  loading = true;
  sendBtn.disabled = true;
  input.value = "";

  messages.push({ role: "user", content: text });
  render();
  addBubble(UI[lang].wait, "bot wait");

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lang, messages })
    });
    if (!res.ok) throw new Error("HTTP " + res.status);
    const data = await res.json();
    messages.push({ role: "assistant", content: data.reply });
  } catch (e) {
    messages.push({ role: "assistant", content: UI[lang].error });
  } finally {
    loading = false;
    sendBtn.disabled = false;
    render();
    input.focus();
  }
}

document.getElementById("btn-kn").onclick = () => setLang("kn");
document.getElementById("btn-en").onclick = () => setLang("en");
sendBtn.onclick = send;
input.addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
});

render();
</script>
</body>
</html>
"""
