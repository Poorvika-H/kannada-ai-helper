from dotenv import load_dotenv
load_dotenv()  # reads ANTHROPIC_API_KEY from backend/.env

import anthropic
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
client = anthropic.Anthropic()  # picks up ANTHROPIC_API_KEY automatically

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
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(req: ChatRequest):
    response = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=1000,
        system=PROMPTS.get(req.lang, PROMPTS["kn"]),
        messages=req.messages,
    )
    return {"reply": response.content[0].text}
