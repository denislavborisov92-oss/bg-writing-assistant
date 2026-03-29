import os
from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY environment variable is missing.")

MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
client = OpenAI(api_key=api_key)

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "Frontend"


class TextRequest(BaseModel):
    text: str
    mode: Literal[
        "fix",
        "professional",
        "short",
        "email",
        "polite",
        "clear",
        "confident",
        "reply",
    ] = "fix"
    tone: Literal[
        "default",
        "professional",
        "friendly",
        "formal",
        "confident",
        "polite",
    ] = "default"
    length: Literal[
        "default",
        "shorter",
        "longer",
    ] = "default"
    instruction: str = ""


def build_prompt(text: str, mode: str, tone: str, length: str, instruction: str) -> str:
    common_rules = """
Пиши на естествен, съвременен и грамотно оформен български език.
Запази оригиналния смисъл, освен ако задачата не изисква преформулиране.
Не добавяй ненужна или измислена информация.
Не използвай прекалено сложни, изкуствени или неестествени думи.
Ако текстът е кратък и разговорен, запази естествения тон.
Върни само крайния резултат, без обяснения, без номериране и без кавички.
""".strip()

    if mode == "fix":
        task = """
Поправи правопис, граматика и пунктуация.
Запази максимално близък стил до оригинала.
""".strip()
    elif mode == "professional":
        task = """
Пренапиши текста в по-професионален, ясен и учтив стил.
Нека звучи подходящо за работа, имейл или бизнес комуникация.
""".strip()
    elif mode == "short":
        task = """
Съкратено и ясно пренапиши текста.
Премахни излишните думи, но запази смисъла.
""".strip()
    elif mode == "email":
        task = """
Превърни текста в добре написан имейл на български език.
Добави подходящо начало и добър завършек, когато е уместно.
Нека звучи естествено, ясно и професионално.
""".strip()
    elif mode == "polite":
        task = """
Пренапиши текста в по-учтив и уважителен тон.
Нека звучи меко, културно и подходящо за комуникация с клиент, колега или мениджър.
""".strip()
    elif mode == "clear":
        task = """
Пренапиши текста по-ясно, подредено и лесно за разбиране.
""".strip()
    elif mode == "confident":
        task = """
Пренапиши текста така, че да звучи по-уверено, стегнато и професионално.
Да не звучи грубо.
""".strip()
    elif mode == "reply":
        task = """
На базата на текста напиши подходящ кратък отговор на български език.
Отговорът да е естествен, уместен и готов за изпращане.
""".strip()
    else:
        task = "Поправи текста на правилен и естествен български език."

    tone_instruction = ""
    if tone == "professional":
        tone_instruction = "Използвай професионален тон."
    elif tone == "friendly":
        tone_instruction = "Използвай приятелски и естествен тон."
    elif tone == "formal":
        tone_instruction = "Използвай по-официален тон."
    elif tone == "confident":
        tone_instruction = "Използвай уверен и ясен тон."
    elif tone == "polite":
        tone_instruction = "Използвай учтив и уважителен тон."

    length_instruction = ""
    if length == "shorter":
        length_instruction = "Направи текста по-кратък."
    elif length == "longer":
        length_instruction = "Направи текста малко по-подробен, без излишно разтягане."

    extra_instruction = instruction.strip()

    parts = [
        common_rules,
        "",
        "Задача:",
        task,
    ]

    if tone_instruction:
        parts.extend(["", "Тон:", tone_instruction])

    if length_instruction:
        parts.extend(["", "Дължина:", length_instruction])

    if extra_instruction:
        parts.extend(["", "Допълнителна инструкция:", extra_instruction])

    parts.extend(["", "Текст:", text.strip()])

    return "\n".join(parts).strip()


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/process")
def process_text(req: TextRequest):
    clean_text = req.text.strip()

    if not clean_text:
        return {"result": "Моля, въведи текст."}

    if len(clean_text) > 12000:
        return {"result": "Текстът е твърде дълъг. Моля, съкрати го и опитай отново."}

    prompt = build_prompt(
        text=clean_text,
        mode=req.mode,
        tone=req.tone,
        length=req.length,
        instruction=req.instruction,
    )

    response = client.responses.create(
        model=MODEL,
        input=prompt,
    )

    return {"result": response.output_text.strip()}


app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/")
def serve_home():
    return FileResponse(str(FRONTEND_DIR / "index.html"))
