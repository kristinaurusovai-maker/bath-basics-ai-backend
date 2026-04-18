from __future__ import annotations

import os
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

TELEGRAM_URL = "https://t.me/bath_basics"
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.4")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

app = FastAPI(title="BATH BASICS Assistant", version="4.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: str
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

START_REPLY = "Здравствуйте. Я AI-помощник BATH BASICS. Помогу выбрать аромат, товар, подарок или ответить на вопросы по доставке и оплате."
START_SUGGESTIONS = ["Подобрать аромат", "Подобрать товар", "Подарок", "Доставка и оплата", "Связаться с менеджером"]
MAIN_MENU_LABEL = "В главное меню"
BACK_LABEL = "Назад"

AROMA_GROUPS = {
    "Свежие": ["Бергамот", "Лайм + базилик", "Морская соль + орхидея", "Оливковое дерево"],
    "Теплые": ["Ваниль + сахар", "Сандал + кокос", "Груша в бренди", "Сбор инжира"],
    "Чистые": ["Хлопок + ирис", "Морская соль + орхидея", "Бергамот", "Лайм + базилик"],
    "Глубокие": ["Пачули + табак", "Мох + амбра", "Жженая древесина", "Перец + амбра"],
    "Пряные": ["Анис + специи", "Перец + амбра", "Яблоки + кленовый бурбон", "Груша в бренди"],
    "Сладкие": ["Карамельный попкорн", "Ваниль + сахар", "Тыквенный латте", "Яблоки + кленовый бурбон"],
    "Цветочные": ["Морская соль + орхидея", "Лепестки роз", "Хлопок + ирис"],
    "Фруктовые": ["Манговый сорбет", "Груша в бренди", "Клюквенный лес", "Сбор инжира"],
    "Хвойные": ["Голубая ель", "Морозный можжевельник", "Клюквенный лес"],
}

AROMA_PRODUCTS = {
    "Бергамот": [
        ("Свеча в стекле 120 мл — Бергамот", "https://bathbasics.ru/tproduct/489220287282-svecha-bergamot"),
        ("Диффузор для дома 50/100 мл — Бергамот", "https://bathbasics.ru/tproduct/797536634052-diffuzor-bergamot"),
        ("Интерьерный спрей 50 мл — Бергамот", "https://bathbasics.ru/tproduct/959690501772-interernii-sprei-50-ml-bergamot"),
        ("Крем для рук 50 мл — Бергамот", "https://bathbasics.ru/tproduct/978920199882-krem-dlya-ruk-bergamot"),
    ],
    "Лайм + базилик": [
        ("Диффузор для дома 50/100 мл — Лайм + базилик", "https://bathbasics.ru/tproduct/860355963292-diffuzor-laim-bazilik"),
        ("Интерьерный спрей 50 мл — Лайм + базилик", "https://bathbasics.ru/tproduct/418285214362-interernii-sprei-50-ml-laim-bazilik"),
        ("Крем для рук 50 мл — Лайм + базилик", "https://bathbasics.ru/tproduct/107271599802-krem-dlya-ruk-laim-bazilik"),
        ("Лосьон для тела 300 мл — Лайм + базилик", "https://bathbasics.ru/tproduct/490606658322-loson-dlya-tela-laim-bazilik"),
        ("Мыло для рук 300 мл — Лайм + базилик", "https://bathbasics.ru/tproduct/376917306742-zhidkoe-milo-laim-bazilik"),
    ],
    "Морская соль + орхидея": [
        ("Свеча в стекле 120 мл — Морская соль + орхидея", "https://bathbasics.ru/tproduct/349689568212-svecha-morskaya-sol-orhideya"),
        ("Диффузор для дома 50/100 мл — Морская соль + орхидея", "https://bathbasics.ru/tproduct/327975560512-diffuzor-morskaya-sol-orhideya"),
        ("Интерьерный спрей 50 мл — Морская соль + орхидея", "https://bathbasics.ru/tproduct/505343214592-interernii-sprei-50-ml-morskaya-sol-orhi"),
        ("Соль для ванны — Морская соль + орхидея", "https://bathbasics.ru/tproduct/294676575742-sol-dlya-vanni-morskaya-sol-orhideya"),
    ],
    "Оливковое дерево": [("Свеча в стекле 120 мл — Оливковое дерево", "https://bathbasics.ru/tproduct/965828595322-svecha-olivkovoe-derevo")],
    "Ваниль + сахар": [
        ("Свеча в стекле 120 мл — Ваниль + сахар", "https://bathbasics.ru/tproduct/150450665012-svecha-vanil-sahar"),
        ("Диффузор для дома 50/100 мл — Ваниль + сахар", "https://bathbasics.ru/tproduct/533571624412-diffuzor-vanil-sahar"),
        ("Крем для рук 50 мл — Ваниль + сахар", "https://bathbasics.ru/tproduct/960076218692-krem-dlya-ruk-vanil-sahar"),
        ("Лосьон для тела 300 мл — Ваниль + сахар", "https://bathbasics.ru/tproduct/317575227672-loson-dlya-tela-vanil-sahar"),
        ("Мыло для рук 300 мл — Ваниль + сахар", "https://bathbasics.ru/tproduct/510650016302-zhidkoe-milo-vanil-sahar"),
    ],
    "Пачули + табак": [
        ("Свеча в стекле 120 мл — Пачули + табак", "https://bathbasics.ru/tproduct/544821768482-svecha-pachuli-tabak"),
        ("Диффузор для дома 50/100 мл — Пачули + табак", "https://bathbasics.ru/tproduct/177239159562-diffuzor-pachuli-tabak"),
        ("Интерьерный спрей 50 мл — Пачули + табак", "https://bathbasics.ru/tproduct/741227351732-interernii-sprei-50-ml-pachuli-tabak"),
        ("Крем для рук 50 мл — Пачули + табак", "https://bathbasics.ru/tproduct/426516668042-krem-dlya-ruk-pachuli-tabak"),
        ("Лосьон для тела 300 мл — Пачули + табак", "https://bathbasics.ru/tproduct/936247085382-loson-dlya-tela-pachuli-tabak"),
        ("Мыло для рук 300 мл — Пачули + табак", "https://bathbasics.ru/tproduct/623573831712-zhidkoe-milo-pachuli-tabak"),
    ],
    "Карамельный попкорн": [
        ("Свеча в стекле 120 мл — Карамельный попкорн", "https://bathbasics.ru/tproduct/363271129392-svecha-karamelnii-popkorn"),
        ("Диффузор для дома 50/100 мл — Карамельный попкорн", "https://bathbasics.ru/tproduct/623161912322-diffuzor-karamelnii-popkorn"),
        ("Интерьерный спрей 50 мл — Карамельный попкорн", "https://bathbasics.ru/tproduct/888015344482-interernii-sprei-50-ml-karamelnii-popkor"),
    ],
}

PRODUCT_FLOW = {
    "product_root": {"reply": "Какая категория вас интересует?", "suggestions": ["Для дома", "Для тела", "Подарочные наборы"]},
    "Для дома": {"reply": "Какой продукт вас интересует?", "suggestions": ["Свечи", "Диффузоры", "Интерьерные спреи", "Саше для белья"]},
    "Для тела": {"reply": "Какой продукт вас интересует?", "suggestions": ["Жидкое мыло", "Лосьоны для тела", "Соль для ванны", "Кремы для рук"]},
    "Подарочные наборы": {"reply": "Вы можете посмотреть готовые подарочные решения или сразу перейти к подбору подарка с менеджером.", "links": [("Готовые подарочные наборы", "http://bathbasics.ru/page135471726.html"), ("Подобрать подарок", TELEGRAM_URL)]},
}

DELIVERY_FLOW = {
    "root": {"reply": "Что вас интересует?", "suggestions": ["Доставка", "Оплата", "Самовывоз", "Сроки изготовления и отправки"]},
    "Доставка": {"reply": "Бесплатная доставка действует от 5000 ₽ до пвз СДЭК. По стране отправляем СДЭК и Почтой России — стоимость доставки рассчитывается автоматически в корзине.", "suggestions": ["Оплата", "Самовывоз", "Сроки изготовления и отправки"]},
    "Оплата": {"reply": "Оплата возможна через сервисы ROBOKASSA и Т-Банк.", "suggestions": ["Доставка", "Самовывоз", "Сроки изготовления и отправки"]},
    "Самовывоз": {"reply": "Самовывоз доступен по адресу: Шелепихинская набережная, 34к4", "suggestions": ["Доставка", "Сроки изготовления и отправки"], "links": [("Связаться с менеджером", TELEGRAM_URL)]},
    "Сроки изготовления и отправки": {"reply": "Создаем и отправляем заказ от 1 до 5 рабочих дней после оплаты.", "suggestions": ["Доставка", "Самовывоз"], "links": [("Связаться с менеджером", TELEGRAM_URL)]},
}

FREE_FAQ = [
    (r"(универсальн.*аромат|без ошибк.*подар)", "Если нужен максимально универсальный вариант, обратите внимание на Хлопок + ирис, Морскую соль + орхидею или Бергамот."),
    (r"(свеч.*или диффузор|чем отличается свеча от диффузора)", "Свеча подходит для ритуала и атмосферы в моменте, а диффузор дает постоянный фоновый аромат в пространстве."),
]

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip().replace("ё", "е"))

def make_response(reply: str, suggestions=None, links=None, handoff=False):
    return ChatResponse(
        reply=reply,
        suggestions=suggestions or [],
        links=[ChatLink(label=l, url=u) for l, u in (links or [])],
        handoff=handoff,
        handoff_text="Вы можете сразу написать менеджеру BATH BASICS в Telegram." if handoff else "",
    )

def ask_openai(user_message: str) -> str:
    if not client:
        raise RuntimeError("OPENAI_API_KEY is missing")
    response = client.responses.create(
        model=OPENAI_MODEL,
        instructions=(
            "Ты AI-консультант бренда BATH BASICS. "
            "Отвечай по-русски. Тон — спокойный, эстетичный, заботливый и лаконичный. "
            "Не выдумывай факты. "
            "Если вопрос про конкретный заказ, трек-номер, повреждение заказа, изменение заказа, "
            "срочный самовывоз или индивидуальный подбор подарка, советуй написать менеджеру в Telegram. "
            "Если вопрос про выбор аромата или товара, отвечай кратко и практично."
        ),
        input=user_message,
    )
    return (response.output_text or "").strip()

@app.get("/health")
def health():
    return {"status": "ok", "openai_enabled": bool(client), "model": OPENAI_MODEL}

@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    raw_message = payload.message or ""
    msg = normalize(raw_message)

    if msg in {"start", "привет", "начать", "меню", normalize(MAIN_MENU_LABEL), normalize(BACK_LABEL)}:
        return make_response(START_REPLY, START_SUGGESTIONS)

    if "менедж" in msg or "человек" in msg:
        return make_response("Вы можете сразу написать менеджеру BATH BASICS в Telegram.", links=[("Перейти в Telegram", TELEGRAM_URL)], handoff=True)

    if msg == normalize("Подобрать аромат"):
        return make_response("Выберите группу ароматов", list(AROMA_GROUPS.keys()) + [MAIN_MENU_LABEL])

    if msg == normalize("Подобрать товар"):
        root = PRODUCT_FLOW["product_root"]
        return make_response(root["reply"], root["suggestions"] + [MAIN_MENU_LABEL])

    if msg == normalize("Подарок"):
        return make_response("Я помогу выбрать подарок. Вы можете посмотреть готовые подарочные наборы или сразу перейти к подбору подарка с менеджером.", suggestions=[MAIN_MENU_LABEL], links=[("Готовые подарочные наборы", "http://bathbasics.ru/page135471726.html"), ("Подобрать подарок", TELEGRAM_URL)])

    if msg == normalize("Доставка и оплата"):
        root = DELIVERY_FLOW["root"]
        return make_response(root["reply"], root["suggestions"] + [MAIN_MENU_LABEL])

    if msg == normalize("Связаться с менеджером"):
        return make_response("Вы можете сразу написать менеджеру BATH BASICS в Telegram.", suggestions=[MAIN_MENU_LABEL], links=[("Перейти в Telegram", TELEGRAM_URL)], handoff=True)

    for group, aromas in AROMA_GROUPS.items():
        if msg == normalize(group):
            return make_response("Выберите аромат", aromas + [BACK_LABEL, MAIN_MENU_LABEL])

    for aroma, products in AROMA_PRODUCTS.items():
        if msg == normalize(aroma):
            return make_response("Этот аромат представлен в таких товарах:", suggestions=[BACK_LABEL, MAIN_MENU_LABEL], links=products)

    if raw_message in PRODUCT_FLOW:
        node = PRODUCT_FLOW[raw_message]
        suggestions = list(node.get("suggestions", []))
        if BACK_LABEL not in suggestions:
            suggestions.append(BACK_LABEL)
        if MAIN_MENU_LABEL not in suggestions:
            suggestions.append(MAIN_MENU_LABEL)
        return make_response(node["reply"], suggestions, node.get("links", []), handoff=any(u == TELEGRAM_URL for _, u in node.get("links", [])))

    if raw_message in DELIVERY_FLOW:
        node = DELIVERY_FLOW[raw_message]
        suggestions = list(node.get("suggestions", []))
        if BACK_LABEL not in suggestions:
            suggestions.append(BACK_LABEL)
        if MAIN_MENU_LABEL not in suggestions:
            suggestions.append(MAIN_MENU_LABEL)
        return make_response(node["reply"], suggestions, node.get("links", []), handoff=any(u == TELEGRAM_URL for _, u in node.get("links", [])))

    for pattern, answer in FREE_FAQ:
        if re.search(pattern, msg):
            return make_response(answer, suggestions=[MAIN_MENU_LABEL])

    try:
        ai_answer = ask_openai(raw_message)
        if ai_answer:
            return make_response(ai_answer, suggestions=[MAIN_MENU_LABEL, "Связаться с менеджером"])
    except Exception:
        pass

    return make_response(START_REPLY, START_SUGGESTIONS)
