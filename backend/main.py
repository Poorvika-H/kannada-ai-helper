from dotenv import load_dotenv
load_dotenv()  # reads ANTHROPIC_API_KEY from backend/.env

from google import genai
from google.genai import types
from fastapi import FastAPI
from fastapi.responses import FileResponse
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
    return FileResponse(Path(__file__).parent / "index.html")


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
