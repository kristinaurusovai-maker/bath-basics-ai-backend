from __future__ import annotations

import os
import re
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

TELEGRAM_URL = "https://t.me/bath_basics"

OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.4")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GOOGLE_SHEETS_WEBHOOK_URL = os.environ.get("GOOGLE_SHEETS_WEBHOOK_URL")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

app = FastAPI(title="BATH BASICS Assistant", version="5.0.0")
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

AROMA_ALIASES = {
    "butter + popcorn": "Карамельный попкорн",
    "caramel popcorn": "Карамельный попкорн",
    "popcorn": "Карамельный попкорн",
    "patchouli + tobacco": "Пачули + табак",
    "patchouli tobacco": "Пачули + табак",
    "pepper + amber": "Перец + амбра",
    "pepper amber": "Перец + амбра",
    "vanilla + sugar": "Ваниль + сахар",
    "vanilla sugar": "Ваниль + сахар",
    "oakmoss + amber": "Мох + амбра",
    "oak moss + amber": "Мох + амбра",
    "moss + amber": "Мох + амбра",
    "moss amber": "Мох + амбра",
    "mango sorbet": "Манговый сорбет",
    "cotton + iris": "Хлопок + ирис",
    "cotton iris": "Хлопок + ирис",
    "white linen": "Хлопок + ирис",
    "sea salt + orchid": "Морская соль + орхидея",
    "sea salt orchid": "Морская соль + орхидея",
    "bergamot": "Бергамот",
    "burnt wood": "Жженая древесина",
    "anise + spices": "Анис + специи",
    "anise spices": "Анис + специи",
    "anise + cassia spice": "Анис + специи",
    "cassia spice": "Анис + специи",
    "olive tree": "Оливковое дерево",
    "cranberry forest": "Клюквенный лес",
    "rose petals": "Лепестки роз",
    "fig harvest": "Сбор инжира",
    "fig collection": "Сбор инжира",
    "ripe fig": "Сбор инжира",
    "fig": "Сбор инжира",
    "lime + basil": "Лайм + базилик",
    "lime basil": "Лайм + базилик",
    "frosted juniper": "Морозный можжевельник",
    "juniper frost": "Морозный можжевельник",
    "blue spruce": "Голубая ель",
    "sandal + coconut": "Сандал + кокос",
    "sandal coconut": "Сандал + кокос",
    "pear in brandy": "Груша в бренди",
    "brandy pear": "Груша в бренди",
    "pumpkin latte": "Тыквенный латте",
    "apple + maple bourbon": "Яблоки + кленовый бурбон",
    "apples + maple bourbon": "Яблоки + кленовый бурбон",
    "maple bourbon": "Яблоки + кленовый бурбон",
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
        ("Жидкое мыло 300 мл — Лайм + базилик", "https://bathbasics.ru/tproduct/376917306742-zhidkoe-milo-laim-bazilik"),
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
        ("Жидкое мыло 300 мл — Ваниль + сахар", "https://bathbasics.ru/tproduct/510650016302-zhidkoe-milo-vanil-sahar"),
    ],
    "Пачули + табак": [
        ("Свеча в стекле 120 мл — Пачули + табак", "https://bathbasics.ru/tproduct/544821768482-svecha-pachuli-tabak"),
        ("Диффузор для дома 50/100 мл — Пачули + табак", "https://bathbasics.ru/tproduct/177239159562-diffuzor-pachuli-tabak"),
        ("Интерьерный спрей 50 мл — Пачули + табак", "https://bathbasics.ru/tproduct/741227351732-interernii-sprei-50-ml-pachuli-tabak"),
        ("Крем для рук 50 мл — Пачули + табак", "https://bathbasics.ru/tproduct/426516668042-krem-dlya-ruk-pachuli-tabak"),
        ("Лосьон для тела 300 мл — Пачули + табак", "https://bathbasics.ru/tproduct/936247085382-loson-dlya-tela-pachuli-tabak"),
        ("Жидкое мыло 300 мл — Пачули + табак", "https://bathbasics.ru/tproduct/623573831712-zhidkoe-milo-pachuli-tabak"),
    ],
    "Карамельный попкорн": [
        ("Свеча в стекле 120 мл — Карамельный попкорн", "https://bathbasics.ru/tproduct/363271129392-svecha-karamelnii-popkorn"),
        ("Диффузор для дома 50/100 мл — Карамельный попкорн", "https://bathbasics.ru/tproduct/623161912322-diffuzor-karamelnii-popkorn"),
        ("Интерьерный спрей 50 мл — Карамельный попкорн", "https://bathbasics.ru/tproduct/888015344482-interernii-sprei-50-ml-karamelnii-popkor"),
    ],
}

PRODUCT_FLOW = {
    "product_root": {"reply": "Какая категория вас интересует?", "suggestions": ["Для дома", "Для тела", "Подарочные наборы"], "response_type": "scenario", "matched_intent": "product_root"},
    "Для дома": {"reply": "Какой продукт вас интересует?", "suggestions": ["Свечи", "Диффузоры", "Интерьерные спреи", "Саше для белья"], "response_type": "scenario", "matched_intent": "product_home"},
    "Для тела": {"reply": "Какой продукт вас интересует?", "suggestions": ["Жидкое мыло", "Лосьоны для тела", "Соль для ванны", "Кремы для рук"], "response_type": "scenario", "matched_intent": "product_body"},
    "Подарочные наборы": {"reply": "Вы можете посмотреть готовые подарочные решения или сразу перейти к подбору подарка с менеджером.", "links": [("Готовые подарочные наборы", "http://bathbasics.ru/page135471726.html"), ("Подобрать подарок", TELEGRAM_URL)], "response_type": "scenario", "matched_intent": "gift_sets"},
    "Свечи": {"reply": "Вот наиболее рекомендуемые ароматы для свечей.", "links": [("Пачули + табак", "https://bathbasics.ru/tproduct/544821768482-svecha-pachuli-tabak"), ("Карамельный попкорн", "https://bathbasics.ru/tproduct/363271129392-svecha-karamelnii-popkorn"), ("Мох + амбра", "https://bathbasics.ru/tproduct/744620328512-svecha-moh-ambra"), ("Морская соль + орхидея", "https://bathbasics.ru/tproduct/349689568212-svecha-morskaya-sol-orhideya")], "response_type": "scenario", "matched_intent": "product_reco", "matched_category": "Свечи"},
    "Диффузоры": {"reply": "Вот наиболее рекомендуемые ароматы для диффузоров.", "links": [("Клюквенный лес", "https://bathbasics.ru/tproduct/337662184122-diffuzor-klyukvennii-les"), ("Пачули + табак", "https://bathbasics.ru/tproduct/177239159562-diffuzor-pachuli-tabak"), ("Хлопок + ирис", "https://bathbasics.ru/tproduct/426687082222-diffuzor-hlopok-iris"), ("Манговый сорбет", "https://bathbasics.ru/tproduct/511871058092-diffuzor-mangovii-sorbet")], "response_type": "scenario", "matched_intent": "product_reco", "matched_category": "Диффузоры"},
    "Интерьерные спреи": {"reply": "Вот наиболее рекомендуемые ароматы для интерьерных спреев.", "links": [("Манговый сорбет", "https://bathbasics.ru/tproduct/225998064232-interernii-sprei-50-ml-mangovii-sorbet"), ("Карамельный попкорн", "https://bathbasics.ru/tproduct/888015344482-interernii-sprei-50-ml-karamelnii-popkor"), ("Мох + амбра", "https://bathbasics.ru/tproduct/231116557522-interernii-sprei-50-ml-moh-ambra"), ("Хлопок + ирис", "https://bathbasics.ru/tproduct/985115124462-interernii-sprei-50-ml-hlopok-iris")], "response_type": "scenario", "matched_intent": "product_reco", "matched_category": "Интерьерные спреи"},
    "Саше для белья": {"reply": "Выберите формат саше для белья.", "links": [("Лошадка", "https://bathbasics.ru/tproduct/172411195712-loshadka"), ("Щелкунчик", "https://bathbasics.ru/tproduct/866380938802-schelkuchnik")], "response_type": "scenario", "matched_intent": "product_reco", "matched_category": "Саше для белья"},
    "Жидкое мыло": {"reply": "Вот наиболее рекомендуемые ароматы для жидкого мыла.", "links": [("Пачули + табак", "https://bathbasics.ru/tproduct/623573831712-zhidkoe-milo-pachuli-tabak"), ("Перец + амбра", "https://bathbasics.ru/tproduct/956403805692-zhidkoe-milo-perets-ambra"), ("Жженая древесина", "https://bathbasics.ru/tproduct/882827290282-zhidkoe-milo-zhzhenaya-drevesina"), ("Анис + специи", "https://bathbasics.ru/tproduct/438408709162-zhidkoe-milo-anis-spetsii")], "response_type": "scenario", "matched_intent": "product_reco", "matched_category": "Жидкое мыло"},
    "Лосьоны для тела": {"reply": "Вот наиболее рекомендуемые ароматы для лосьонов для тела.", "links": [("Ваниль + сахар", "https://bathbasics.ru/tproduct/317575227672-loson-dlya-tela-vanil-sahar"), ("Анис + специи", "https://bathbasics.ru/tproduct/234147502032-loson-dlya-tela-anis-spetsii"), ("Пачули + табак", "https://bathbasics.ru/tproduct/936247085382-loson-dlya-tela-pachuli-tabak"), ("Манговый сорбет", "https://bathbasics.ru/tproduct/646799116362-loson-dlya-tela-mangovii-sorbet")], "response_type": "scenario", "matched_intent": "product_reco", "matched_category": "Лосьоны для тела"},
    "Соль для ванны": {"reply": "Вот наиболее рекомендуемые ароматы для соли для ванны.", "links": [("Клюквенный лес", "https://bathbasics.ru/tproduct/944380994792-sol-dlya-vanni-klyukvennii-les"), ("Лепестки роз", "https://bathbasics.ru/tproduct/391350849282-sol-dlya-vanni-rose-petals-")], "response_type": "scenario", "matched_intent": "product_reco", "matched_category": "Соль для ванны"},
    "Кремы для рук": {"reply": "Вот наиболее рекомендуемые ароматы для кремов для рук.", "links": [("Ваниль + сахар", "https://bathbasics.ru/tproduct/960076218692-krem-dlya-ruk-vanil-sahar"), ("Перец + амбра", "https://bathbasics.ru/tproduct/300783060912-krem-dlya-ruk-perets-ambra"), ("Пачули + табак", "https://bathbasics.ru/tproduct/426516668042-krem-dlya-ruk-pachuli-tabak"), ("Бергамот", "https://bathbasics.ru/tproduct/978920199882-krem-dlya-ruk-bergamot")], "response_type": "scenario", "matched_intent": "product_reco", "matched_category": "Кремы для рук"},
}

DELIVERY_FLOW = {
    "root": {"reply": "Что вас интересует?", "suggestions": ["Доставка", "Оплата", "Самовывоз", "Сроки изготовления и отправки"], "response_type": "scenario", "matched_intent": "delivery_root"},
    "Доставка": {"reply": "Бесплатная доставка действует от 5000 ₽ до пвз СДЭК. По стране отправляем СДЭК и Почтой России — стоимость доставки рассчитывается автоматически в корзине.", "suggestions": ["Оплата", "Самовывоз", "Сроки изготовления и отправки"], "response_type": "faq", "matched_intent": "delivery"},
    "Оплата": {"reply": "Оплата возможна через сервисы ROBOKASSA и Т-Банк.", "suggestions": ["Доставка", "Самовывоз", "Сроки изготовления и отправки"], "response_type": "faq", "matched_intent": "payment"},
    "Самовывоз": {"reply": "Самовывоз доступен по адресу: Шелепихинская набережная, 34к4.", "suggestions": ["Доставка", "Сроки изготовления и отправки"], "links": [("Связаться с менеджером", TELEGRAM_URL)], "response_type": "faq", "matched_intent": "pickup"},
    "Сроки изготовления и отправки": {"reply": "Создаем и отправляем заказ от 1 до 5 рабочих дней после оплаты.", "suggestions": ["Доставка", "Самовывоз"], "links": [("Связаться с менеджером", TELEGRAM_URL)], "response_type": "faq", "matched_intent": "timing"},
}

FREE_FAQ = [
    (r"(универсальн.*аромат|без ошибк.*подар)", "Если нужен максимально универсальный вариант, обратите внимание на Хлопок + ирис, Морскую соль + орхидею или Бергамот.", "faq", "universal_aroma"),
    (r"(свеч.*или диффузор|чем отличается свеча от диффузора)", "Свеча подходит для ритуала и атмосферы в моменте, а диффузор дает постоянный фоновый аромат в пространстве.", "faq", "candle_vs_diffuser"),
]

SITE_CONTEXT = """
BATH BASICS — бренд товаров для дома и ухода за телом.
Категории: свечи, диффузоры, интерьерные спреи, саше для белья, жидкое мыло, лосьоны для тела, кремы для рук, соль для ванны, подарочные наборы.
Доставка: бесплатная доставка от 5000 ₽ до пвз СДЭК. По стране — СДЭК и Почта России. Стоимость рассчитывается автоматически в корзине.
Оплата: ROBOKASSA и Т-Банк.
Самовывоз: Шелепихинская набережная, 34к4.
Сроки: 1–5 рабочих дней после оплаты.
Нельзя придумывать новые товары, ароматы, цены, ссылки и условия.
"""

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower().strip().replace("ё", "е"))

def strip_markdown(text: str) -> str:
    text = re.sub(r"[*_`#]+", "", text)
    text = re.sub(r"\n\s*[-•]\s*", "\n", text)
    text = re.sub(r"\n\s*\d+\.\s*", "\n", text)
    return text.strip()

def make_response(reply: str, suggestions=None, links=None, handoff=False):
    return ChatResponse(
        reply=reply,
        suggestions=suggestions or [],
        links=[ChatLink(label=l, url=u) for l, u in (links or [])],
        handoff=handoff,
        handoff_text="Вы можете сразу написать менеджеру BATH BASICS в Telegram." if handoff else "",
    )

def log_to_google_sheets(session_id: str, role: str, message: str, page_url: str = "", source: str = "", response_type: str = "", matched_intent: str = "", matched_aroma: str = "", matched_category: str = ""):
    if not GOOGLE_SHEETS_WEBHOOK_URL:
        return
    try:
        requests.post(
            GOOGLE_SHEETS_WEBHOOK_URL,
            json={
                "session_id": session_id,
                "role": role,
                "message": message,
                "page_url": page_url,
                "source": source,
                "response_type": response_type,
                "matched_intent": matched_intent,
                "matched_aroma": matched_aroma,
                "matched_category": matched_category,
            },
            timeout=5,
        )
    except Exception as e:
        print("GOOGLE_SHEETS_LOG_ERROR:", repr(e))

def respond(payload: ChatRequest, reply: str, suggestions=None, links=None, handoff=False, response_type="", matched_intent="", matched_aroma="", matched_category=""):
    log_to_google_sheets(
        session_id=payload.session_id,
        role="bot",
        message=reply,
        page_url=payload.page_url or "",
        source=payload.source or "",
        response_type=response_type,
        matched_intent=matched_intent,
        matched_aroma=matched_aroma,
        matched_category=matched_category,
    )
    return make_response(reply, suggestions, links, handoff)

def ask_openai(user_message: str) -> str:
    if not client:
        raise RuntimeError("OPENAI_API_KEY is missing")
    response = client.responses.create(
        model=OPENAI_MODEL,
        instructions=(
            "Ты AI-консультант бренда BATH BASICS. "
            "Отвечай только по-русски. "
            "Не используй markdown, звездочки и списки. "
            "Пиши обычным текстом. "
            "Отвечай только на основе переданного контекста сайта. "
            "Ничего не выдумывай. "
            "Если точной информации нет, предложи написать менеджеру в Telegram."
        ),
        input=f"Контекст сайта:\n{SITE_CONTEXT}\n\nВопрос клиента:\n{user_message}",
    )
    return strip_markdown((response.output_text or "").strip())

@app.get("/health")
def health():
    return {"status": "ok", "openai_enabled": bool(client), "model": OPENAI_MODEL, "google_sheets_enabled": bool(GOOGLE_SHEETS_WEBHOOK_URL)}

@app.get("/test-openai")
def test_openai():
    try:
        return {"ok": True, "answer": ask_openai("Хочу что-то уютное, но не сладкое")}
    except Exception as e:
        return {"ok": False, "error": repr(e)}

@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    raw_message = payload.message or ""
    msg = normalize(raw_message)

    log_to_google_sheets(payload.session_id, "user", raw_message, payload.page_url or "", payload.source or "", "user_message")

    if msg in {"start", "привет", "начать", "меню", normalize(MAIN_MENU_LABEL)}:
        return respond(payload, START_REPLY, START_SUGGESTIONS, response_type="scenario", matched_intent="start_menu")

    if msg == normalize(BACK_LABEL):
        return respond(payload, START_REPLY, START_SUGGESTIONS, response_type="scenario", matched_intent="back_to_menu")

    if "менедж" in msg or "человек" in msg:
        return respond(payload, "Вы можете сразу написать менеджеру BATH BASICS в Telegram.", links=[("Перейти в Telegram", TELEGRAM_URL)], handoff=True, response_type="handoff", matched_intent="manager")

    if msg == normalize("Подобрать аромат"):
        return respond(payload, "Выберите группу ароматов.", list(AROMA_GROUPS.keys()) + [MAIN_MENU_LABEL], response_type="scenario", matched_intent="aroma_root")

    if msg == normalize("Подобрать товар"):
        root = PRODUCT_FLOW["product_root"]
        return respond(payload, root["reply"], root["suggestions"] + [MAIN_MENU_LABEL], response_type=root["response_type"], matched_intent=root["matched_intent"])

    if msg == normalize("Подарок"):
        return respond(payload, "Я помогу выбрать подарок. Вы можете посмотреть готовые подарочные наборы или сразу перейти к подбору подарка с менеджером.", suggestions=[MAIN_MENU_LABEL], links=[("Готовые подарочные наборы", "http://bathbasics.ru/page135471726.html"), ("Подобрать подарок", TELEGRAM_URL)], response_type="scenario", matched_intent="gift_root")

    if msg == normalize("Доставка и оплата"):
        root = DELIVERY_FLOW["root"]
        return respond(payload, root["reply"], root["suggestions"] + [MAIN_MENU_LABEL], response_type=root["response_type"], matched_intent=root["matched_intent"])

    if msg == normalize("Связаться с менеджером"):
        return respond(payload, "Вы можете сразу написать менеджеру BATH BASICS в Telegram.", suggestions=[MAIN_MENU_LABEL], links=[("Перейти в Telegram", TELEGRAM_URL)], handoff=True, response_type="handoff", matched_intent="manager")

    for group, aromas in AROMA_GROUPS.items():
        if msg == normalize(group):
            return respond(payload, "Выберите аромат.", aromas + [BACK_LABEL, MAIN_MENU_LABEL], response_type="scenario", matched_intent="aroma_group", matched_category=group)

    for alias, canonical_name in AROMA_ALIASES.items():
        if alias in msg and canonical_name in AROMA_PRODUCTS:
            return respond(payload, f"Да, у нас есть аромат {canonical_name}. Он представлен в таких товарах:", suggestions=[BACK_LABEL, MAIN_MENU_LABEL], links=AROMA_PRODUCTS[canonical_name], response_type="alias_match", matched_intent="aroma_alias", matched_aroma=canonical_name)

    for aroma, products in AROMA_PRODUCTS.items():
        if msg == normalize(aroma):
            return respond(payload, "Этот аромат представлен в таких товарах:", suggestions=[BACK_LABEL, MAIN_MENU_LABEL], links=products, response_type="scenario", matched_intent="aroma_products", matched_aroma=aroma)

    if raw_message in PRODUCT_FLOW:
        node = PRODUCT_FLOW[raw_message]
        suggestions = list(node.get("suggestions", []))
        if BACK_LABEL not in suggestions:
            suggestions.append(BACK_LABEL)
        if MAIN_MENU_LABEL not in suggestions:
            suggestions.append(MAIN_MENU_LABEL)
        return respond(payload, node["reply"], suggestions=suggestions, links=node.get("links", []), handoff=any(u == TELEGRAM_URL for _, u in node.get("links", [])), response_type=node.get("response_type", "scenario"), matched_intent=node.get("matched_intent", ""), matched_category=node.get("matched_category", raw_message if raw_message != "Подарочные наборы" else ""))

    if raw_message in DELIVERY_FLOW:
        node = DELIVERY_FLOW[raw_message]
        suggestions = list(node.get("suggestions", []))
        if BACK_LABEL not in suggestions:
            suggestions.append(BACK_LABEL)
        if MAIN_MENU_LABEL not in suggestions:
            suggestions.append(MAIN_MENU_LABEL)
        return respond(payload, node["reply"], suggestions=suggestions, links=node.get("links", []), handoff=any(u == TELEGRAM_URL for _, u in node.get("links", [])), response_type=node.get("response_type", "faq"), matched_intent=node.get("matched_intent", ""))

    for pattern, answer, response_type, matched_intent in FREE_FAQ:
        if re.search(pattern, msg):
            links = [("Перейти в Telegram", TELEGRAM_URL)] if response_type == "handoff" else []
            return respond(payload, answer, suggestions=[MAIN_MENU_LABEL], links=links, handoff=response_type == "handoff", response_type=response_type, matched_intent=matched_intent)

    try:
        ai_answer = ask_openai(raw_message)
        if ai_answer:
            return respond(payload, ai_answer, suggestions=[MAIN_MENU_LABEL, "Связаться с менеджером"], response_type="ai", matched_intent="open_question")
    except Exception as e:
        print("OPENAI_ERROR:", repr(e))
        return respond(payload, "AI-ответы временно недоступны. Вы можете выбрать раздел ниже или написать менеджеру.", suggestions=[MAIN_MENU_LABEL, "Связаться с менеджером"], links=[("Перейти в Telegram", TELEGRAM_URL)], handoff=True, response_type="handoff", matched_intent="ai_error")

    return respond(payload, START_REPLY, START_SUGGESTIONS, response_type="scenario", matched_intent="fallback_menu")
