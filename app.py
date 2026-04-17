from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_PATH = BASE_DIR / "BATH_BASICS_AI_final_package.xlsx"
DATA_PATH = Path(os.getenv("BB_DATA_PATH", DEFAULT_DATA_PATH))
TELEGRAM_URL = os.getenv("BB_TELEGRAM_URL", "https://t.me/bath_basics")


class ChatRequest(BaseModel):
    session_id: str = Field(default_factory=lambda: f"bb_{uuid4().hex}")
    message: str
    page_url: str | None = None
    source: str | None = "tilda_widget"


class ChatLink(BaseModel):
    label: str
    url: str


class ChatResponse(BaseModel):
    reply: str
    suggestions: list[str] = []
    links: list[ChatLink] = []
    handoff: bool = False
    handoff_text: str = ""
    telegram_url: str = TELEGRAM_URL


app = FastAPI(title="BATH BASICS AI Backend", version="1.0.0")

cors_origins = os.getenv("BB_CORS_ORIGINS", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in cors_origins.split(",")] if cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@lru_cache(maxsize=1)
def load_data() -> dict[str, pd.DataFrame]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Knowledge base file not found: {DATA_PATH}")

    required = {
        "products",
        "aromas",
        "faq",
        "contacts",
        "escalation_rules",
        "response_templates",
    }
    xls = pd.ExcelFile(DATA_PATH)
    missing = required - set(xls.sheet_names)
    if missing:
        raise RuntimeError(f"Missing required sheets: {', '.join(sorted(missing))}")

    data = {sheet: pd.read_excel(DATA_PATH, sheet_name=sheet).fillna("") for sheet in required}
    for name, df in data.items():
        data[name] = normalize_df(df)
    return data


def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()
    return df


def norm(text: str) -> str:
    text = (text or "").lower().strip()
    text = text.replace("ё", "е")
    text = re.sub(r"\s+", " ", text)
    return text


def tokenize(text: str) -> set[str]:
    text = norm(text)
    return {t for t in re.findall(r"[a-zA-Zа-яА-Я0-9\+\-]+", text) if len(t) > 1}


def contains_any(text: str, patterns: list[str]) -> bool:
    nt = norm(text)
    return any(norm(p) in nt for p in patterns if p)


def score_overlap(query: str, haystack: str) -> int:
    q = tokenize(query)
    h = tokenize(haystack)
    return len(q & h)


def first_row(df: pd.DataFrame, **conditions: str) -> Optional[pd.Series]:
    mask = pd.Series([True] * len(df))
    for col, val in conditions.items():
        mask &= df[col].astype(str).str.lower() == str(val).lower()
    out = df[mask]
    return out.iloc[0] if not out.empty else None


def get_contact_url(contact_type: str) -> str:
    contacts = load_data()["contacts"]
    row = first_row(contacts, contact_type=contact_type)
    if row is None:
        return ""
    return row["contact_url"]


def get_template(intent_type: str) -> Optional[pd.Series]:
    templates = load_data()["response_templates"]
    row = first_row(templates, intent_type=intent_type)
    return row


def detect_handoff(message: str) -> Optional[pd.Series]:
    rules = load_data()["escalation_rules"]
    m = norm(message)
    best_row = None
    best_score = 0
    for _, row in rules.iterrows():
        phrases = [p.strip() for p in str(row["trigger_phrase_examples"]).split(",") if p.strip()]
        score = sum(1 for p in phrases if norm(p) in m)
        if score > best_score:
            best_score = score
            best_row = row
    return best_row if best_score > 0 else None


def search_faq(message: str) -> Optional[pd.Series]:
    faq = load_data()["faq"]
    best_row = None
    best_score = 0
    for _, row in faq.iterrows():
        text = " ".join(
            [
                row.get("faq_question", ""),
                row.get("faq_keywords", ""),
                row.get("short_answer", ""),
                row.get("topic", ""),
            ]
        )
        score = score_overlap(message, text)
        if score > best_score:
            best_score = score
            best_row = row
    return best_row if best_score >= 1 else None


def search_aromas(message: str, limit: int = 3) -> pd.DataFrame:
    aromas = load_data()["aromas"].copy()
    aromas["_score"] = aromas.apply(
        lambda r: score_overlap(
            message,
            " ".join(
                [
                    r.get("aroma_name", ""),
                    r.get("short_profile", ""),
                    r.get("detailed_profile", ""),
                    r.get("family", ""),
                    r.get("mood", ""),
                    r.get("tags", ""),
                ]
            ),
        ),
        axis=1,
    )
    aromas = aromas[aromas["_score"] > 0].sort_values("_score", ascending=False)
    return aromas.head(limit)


def search_products(message: str, limit: int = 4) -> pd.DataFrame:
    products = load_data()["products"].copy()
    products["_score"] = products.apply(
        lambda r: score_overlap(
            message,
            " ".join(
                [
                    r.get("product_name", ""),
                    r.get("category_name", ""),
                    r.get("aroma_name", ""),
                    r.get("short_description", ""),
                    r.get("tags", ""),
                ]
            ),
        ),
        axis=1,
    )
    products = products[products["_score"] > 0].sort_values("_score", ascending=False)
    return products.head(limit)


def intent_from_message(message: str) -> str:
    m = norm(message)

    if contains_any(m, ["доставка", "оплата", "самовывоз", "трек", "заказ", "срок", "поврежден", "сертификат"]):
        return "faq"
    if contains_any(m, ["аромат", "запах", "свежий", "пряный", "гурманский", "цветочный", "древесный"]):
        return "aroma_selection"
    if contains_any(m, ["подарок", "подарить", "набор", "комплект"]):
        return "gift_selection"
    if contains_any(m, ["свеч", "диффузор", "спрей", "мыло", "лосьон", "крем", "соль", "саше", "товар"]):
        return "product_selection"
    if contains_any(m, ["где купить", "оффлайн", "контакты", "телеграм", "telegram", "менеджер"]):
        return "navigation"
    return "fallback"


def build_faq_response(row: pd.Series) -> ChatResponse:
    suggestions = ["Подобрать аромат", "Подобрать товар", "Подарок", "Связаться с менеджером"]
    links = []
    if row.get("related_link"):
        links.append(ChatLink(label="Подробнее", url=row["related_link"]))
    return ChatResponse(
        reply=row.get("short_answer") or row.get("full_answer") or "Нашла ответ в базе знаний.",
        suggestions=suggestions,
        links=links,
        handoff=False,
        handoff_text="",
        telegram_url=TELEGRAM_URL,
    )


def build_aroma_response(message: str) -> ChatResponse:
    matches = search_aromas(message, limit=3)
    if matches.empty:
        return ChatResponse(
            reply="Я помогу подобрать аромат. Подскажите, вам ближе свежие, теплые, чистые, цветочные или более глубокие композиции?",
            suggestions=["Свежие", "Теплые", "Чистые", "Глубокие"],
            links=[ChatLink(label="Все ароматы", url=get_contact_url("aromas_page") or "https://bathbasics.ru/page134854276.html")],
            telegram_url=TELEGRAM_URL,
        )

    names = matches["aroma_name"].tolist()
    reply = "Под ваш запрос могут хорошо подойти эти ароматы:\n- " + "\n- ".join(names)
    return ChatResponse(
        reply=reply,
        suggestions=names + ["Связаться с менеджером"],
        links=[ChatLink(label="Все ароматы", url=get_contact_url("aromas_page") or "https://bathbasics.ru/page134854276.html")],
        telegram_url=TELEGRAM_URL,
    )


def build_product_response(message: str) -> ChatResponse:
    matches = search_products(message, limit=4)
    if matches.empty:
        return ChatResponse(
            reply="Я помогу подобрать формат. Подскажите, вы выбираете для дома, для тела или в подарок?",
            suggestions=["Для дома", "Для тела", "Подарок", "Связаться с менеджером"],
            telegram_url=TELEGRAM_URL,
        )

    lines = []
    links: list[ChatLink] = []
    for _, row in matches.iterrows():
        lines.append(f"{row['product_name']} — {row['price']} ₽")
        if row.get("product_url"):
            links.append(ChatLink(label=row["product_name"], url=row["product_url"]))

    reply = "Вот что может подойти:\n- " + "\n- ".join(lines)
    return ChatResponse(
        reply=reply,
        suggestions=["Подобрать аромат", "Подарок", "Связаться с менеджером"],
        links=links[:4],
        telegram_url=TELEGRAM_URL,
    )


def build_navigation_response(message: str) -> ChatResponse:
    links = [
        ChatLink(label="Главная", url=get_contact_url("home_page") or "https://bathbasics.ru/"),
        ChatLink(label="Все ароматы", url=get_contact_url("aromas_page") or "https://bathbasics.ru/page134854276.html"),
        ChatLink(label="Где купить офлайн", url=get_contact_url("offline_page") or "https://bathbasics.ru/page130674493.html"),
    ]
    return ChatResponse(
        reply="Я могу направить вас в нужный раздел сайта или сразу к менеджеру в Telegram.",
        suggestions=["Все ароматы", "Где купить офлайн", "Связаться с менеджером"],
        links=links,
        telegram_url=TELEGRAM_URL,
    )


def build_handoff_response(rule: pd.Series) -> ChatResponse:
    return ChatResponse(
        reply=rule.get("handoff_text") or "Лучше сразу перейти к менеджеру.",
        suggestions=[],
        links=[],
        handoff=True,
        handoff_text=rule.get("handoff_text") or "Лучше сразу перейти к менеджеру.",
        telegram_url=TELEGRAM_URL,
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def api_chat(payload: ChatRequest) -> ChatResponse:
    message = (payload.message or "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message is required.")

    # 1. hot lead / handoff
    handoff_rule = detect_handoff(message)
    if handoff_rule is not None:
        return build_handoff_response(handoff_rule)

    # 2. FAQ
    intent = intent_from_message(message)
    if intent == "faq":
        faq_item = search_faq(message)
        if faq_item is not None:
            return build_faq_response(faq_item)

    # 3. Aroma / Product / Navigation
    if intent in {"aroma_selection", "gift_selection"}:
        return build_aroma_response(message)
    if intent == "product_selection":
        return build_product_response(message)
    if intent == "navigation":
        return build_navigation_response(message)

    # 4. fallback search
    faq_item = search_faq(message)
    if faq_item is not None:
        return build_faq_response(faq_item)

    product_matches = search_products(message, limit=3)
    if not product_matches.empty:
        return build_product_response(message)

    aroma_matches = search_aromas(message, limit=3)
    if not aroma_matches.empty:
        return build_aroma_response(message)

    return ChatResponse(
        reply="Я помогу с выбором. Подскажите, вы ищете аромат, товар, подарок или у вас вопрос по заказу и доставке?",
        suggestions=["Подобрать аромат", "Подобрать товар", "Подарок", "Доставка и оплата", "Связаться с менеджером"],
        telegram_url=TELEGRAM_URL,
    )
