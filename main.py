from __future__ import annotations

import re
from typing import Literal
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

TELEGRAM_URL = "https://t.me/bath_basics"

app = FastAPI(title="BATH BASICS Assistant v2", version="2.0.0")
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
    "Бергамот": ["Свеча в стекле 120 мл — Бергамот", "Диффузор для дома 50/100 мл — Бергамот", "Интерьерный спрей 50 мл — Бергамот", "Крем для рук 50 мл — Бергамот"],
    "Лайм + базилик": ["Диффузор для дома 50/100 мл — Лайм + базилик", "Интерьерный спрей 50 мл — Лайм + базилик", "Крем для рук 50 мл — Лайм + базилик", "Лосьон для тела 300 мл — Лайм + базилик", "Мыло для рук 300 мл — Лайм + базилик"],
    "Морская соль + орхидея": ["Свеча в стекле 120 мл — Морская соль + орхидея", "Диффузор для дома 50/100 мл — Морская соль + орхидея", "Интерьерный спрей 50 мл — Морская соль + орхидея", "Соль для ванны — Морская соль + орхидея"],
    "Оливковое дерево": ["Свеча в стекле 120 мл — Оливковое дерево"],
    "Ваниль + сахар": ["Свеча в стекле 120 мл — Ваниль + сахар", "Диффузор для дома 50/100 мл — Ваниль + сахар", "Крем для рук 50 мл — Ваниль + сахар", "Лосьон для тела 300 мл — Ваниль + сахар", "Мыло для рук 300 мл — Ваниль + сахар"],
    "Сандал + кокос": ["Свеча в стекле 120 мл — Сандал + кокос", "Диффузор для дома 50/100 мл — Сандал + кокос", "Интерьерный спрей 50 мл — Сандал + кокос"],
    "Груша в бренди": ["Свеча в стекле 120 мл — Груша в бренди", "Диффузор для дома 50/100 мл — Груша в бренди", "Интерьерный спрей 50 мл — Груша в бренди"],
    "Сбор инжира": ["Свеча в стекле 120 мл — Сбор инжира", "Лосьон для тела 300 мл — Сбор инжира", "Мыло для рук 300 мл — Сбор инжира"],
    "Хлопок + ирис": ["Свеча в стекле 120 мл — Хлопок + ирис", "Диффузор для дома 50/100 мл — Хлопок + ирис", "Интерьерный спрей 50 мл — Хлопок + ирис", "Крем для рук 50 мл — Хлопок + ирис", "Лосьон для тела 300 мл — Хлопок + ирис", "Мыло для рук 300 мл — Хлопок + ирис", "Саше для белья"],
    "Пачули + табак": ["Свеча в стекле 120 мл — Пачули + табак", "Диффузор для дома 50/100 мл — Пачули + табак", "Интерьерный спрей 50 мл — Пачули + табак", "Крем для рук 50 мл — Пачули + табак", "Лосьон для тела 300 мл — Пачули + табак", "Мыло для рук 300 мл — Пачули + табак"],
    "Мох + амбра": ["Свеча в стекле 120 мл — Мох + амбра", "Диффузор для дома 50/100 мл — Мох + амбра", "Интерьерный спрей 50 мл — Мох + амбра"],
    "Жженая древесина": ["Диффузор для дома 50/100 мл — Жженая древесина", "Интерьерный спрей 50 мл — Жженая древесина", "Крем для рук 50 мл — Жженая древесина", "Лосьон для тела 300 мл — Жженая древесина", "Мыло для рук 300 мл — Жженая древесина"],
    "Перец + амбра": ["Диффузор для дома 50/100 мл — Перец + амбра", "Интерьерный спрей 50 мл — Перец + амбра", "Крем для рук 50 мл — Перец + амбра", "Лосьон для тела 300 мл — Перец + амбра", "Мыло для рук 300 мл — Перец + амбра"],
    "Анис + специи": ["Свеча в стекле 120 мл — Анис + специи", "Диффузор для дома 50/100 мл — Анис + специи", "Крем для рук 50 мл — Анис + специи", "Лосьон для тела 300 мл — Анис + специи", "Мыло для рук 300 мл — Анис + специи"],
    "Яблоки + кленовый бурбон": ["Свеча в стекле 120 мл — Яблоки + кленовый бурбон", "Диффузор для дома 50/100 мл — Яблоки + кленовый бурбон", "Интерьерный спрей 50 мл — Яблоки + кленовый бурбон"],
    "Карамельный попкорн": ["Свеча в стекле 120 мл — Карамельный попкорн", "Диффузор для дома 50/100 мл — Карамельный попкорн", "Интерьерный спрей 50 мл — Карамельный попкорн", "Лосьон для тела 300 мл — Карамельный попкорн", "Мыло для рук 300 мл — Карамельный попкорн"],
    "Тыквенный латте": ["Свеча в стекле 120 мл — Тыквенный латте"],
    "Лепестки роз": ["Соль для ванны — Лепестки роз"],
    "Манговый сорбет": ["Свеча в стекле 120 мл — Манговый сорбет", "Диффузор для дома 50/100 мл — Манговый сорбет", "Интерьерный спрей 50 мл — Манговый сорбет", "Крем для рук 50 мл — Манговый сорбет", "Лосьон для тела 300 мл — Манговый сорбет", "Мыло для рук 300 мл — Манговый сорбет"],
    "Клюквенный лес": ["Свеча в стекле 120 мл — Клюквенный лес", "Диффузор для дома 50/100 мл — Клюквенный лес", "Интерьерный спрей 50 мл — Клюквенный лес", "Соль для ванны — Клюквенный лес"],
    "Голубая ель": ["Диффузор для дома 50/100 мл — Голубая ель", "Интерьерный спрей 50 мл — Голубая ель"],
    "Морозный можжевельник": ["Свеча в стекле 120 мл — Морозный можжевельник"],
}

PRODUCT_FLOW = {
    "product_root": {
        "reply": "Какая категория вас интересует?",
        "suggestions": ["Для дома", "Для тела", "Подарочные наборы"],
    },
    "Для дома": {
        "reply": "Какой продукт вас интересует?",
        "suggestions": ["Свечи", "Диффузоры", "Интерьерные спреи", "Саше для белья"],
    },
    "Для тела": {
        "reply": "Какой продукт вас интересует?",
        "suggestions": ["Жидкое мыло", "Лосьоны для тела", "Соль для ванны", "Кремы для рук"],
    },
    "Подарочные наборы": {
        "reply": "Вы можете посмотреть готовые подарочные решения или сразу перейти к подбору подарка с менеджером.",
        "links": [
            ("Готовые подарочные наборы", "http://bathbasics.ru/page135471726.html"),
            ("Подобрать подарок", TELEGRAM_URL),
        ],
    },
    "Свечи": {
        "reply": "Вот популярные ароматы для свечей",
        "links": [
            ("Пачули + табак", "https://bathbasics.ru/tproduct/544821768482-svecha-pachuli-tabak"),
            ("Карамельный попкорн", "https://bathbasics.ru/tproduct/363271129392-svecha-karamelnii-popkorn"),
            ("Мох + амбра", "https://bathbasics.ru/tproduct/744620328512-svecha-moh-ambra"),
            ("Морская соль + орхидея", "https://bathbasics.ru/tproduct/349689568212-svecha-morskaya-sol-orhideya"),
        ],
    },
    "Диффузоры": {
        "reply": "Вот популярные ароматы для диффузоров",
        "links": [
            ("Клюквенный лес", "https://bathbasics.ru/tproduct/337662184122-diffuzor-klyukvennii-les"),
            ("Пачули + табак", "https://bathbasics.ru/tproduct/177239159562-diffuzor-pachuli-tabak"),
            ("Хлопок + ирис", "https://bathbasics.ru/tproduct/426687082222-diffuzor-hlopok-iris"),
            ("Манговый сорбет", "https://bathbasics.ru/tproduct/511871058092-diffuzor-mangovii-sorbet"),
        ],
    },
    "Интерьерные спреи": {
        "reply": "Вот популярные ароматы для интерьерных спреев",
        "links": [
            ("Манговый сорбет", "https://bathbasics.ru/tproduct/225998064232-interernii-sprei-50-ml-mangovii-sorbet"),
            ("Карамельный попкорн", "https://bathbasics.ru/tproduct/888015344482-interernii-sprei-50-ml-karamelnii-popkor"),
            ("Мох + амбра", "https://bathbasics.ru/tproduct/231116557522-interernii-sprei-50-ml-moh-ambra"),
            ("Хлопок + ирис", "https://bathbasics.ru/tproduct/985115124462-interernii-sprei-50-ml-hlopok-iris"),
        ],
    },
    "Саше для белья": {
        "reply": "Выберите формат саше для белья",
        "links": [
            ("Лошадка", "https://bathbasics.ru/tproduct/172411195712-loshadka"),
            ("Щелкунчик", "https://bathbasics.ru/tproduct/866380938802-schelkuchnik"),
        ],
    },
    "Жидкое мыло": {
        "reply": "Вот популярные ароматы для жидкого мыла",
        "links": [
            ("Пачули + табак", "https://bathbasics.ru/tproduct/623573831712-zhidkoe-milo-pachuli-tabak"),
            ("Перец + амбра", "https://bathbasics.ru/tproduct/956403805692-zhidkoe-milo-perets-ambra"),
            ("Жженая древесина", "https://bathbasics.ru/tproduct/882827290282-zhidkoe-milo-zhzhenaya-drevesina"),
            ("Анис + специи", "https://bathbasics.ru/tproduct/438408709162-zhidkoe-milo-anis-spetsii"),
        ],
    },
    "Лосьоны для тела": {
        "reply": "Вот популярные ароматы для лосьонов для тела",
        "links": [
            ("Ваниль + сахар", "https://bathbasics.ru/tproduct/317575227672-loson-dlya-tela-vanil-sahar"),
            ("Анис + специи", "https://bathbasics.ru/tproduct/234147502032-loson-dlya-tela-anis-spetsii"),
            ("Пачули + табак", "https://bathbasics.ru/tproduct/936247085382-loson-dlya-tela-pachuli-tabak"),
            ("Манговый сорбет", "https://bathbasics.ru/tproduct/646799116362-loson-dlya-tela-mangovii-sorbet"),
        ],
    },
    "Соль для ванны": {
        "reply": "Вот популярные ароматы для соли для ванны",
        "links": [
            ("Клюквенный лес", "https://bathbasics.ru/tproduct/944380994792-sol-dlya-vanni-klyukvennii-les"),
            ("Лепестки роз", "https://bathbasics.ru/tproduct/391350849282-sol-dlya-vanni-rose-petals-"),
        ],
    },
    "Кремы для рук": {
        "reply": "Вот популярные ароматы для кремов для рук",
        "links": [
            ("Ваниль + сахар", "https://bathbasics.ru/tproduct/960076218692-krem-dlya-ruk-vanil-sahar"),
            ("Перец + амбра", "https://bathbasics.ru/tproduct/300783060912-krem-dlya-ruk-perets-ambra"),
            ("Пачули + табак", "https://bathbasics.ru/tproduct/426516668042-krem-dlya-ruk-pachuli-tabak"),
            ("Бергамот", "https://bathbasics.ru/tproduct/978920199882-krem-dlya-ruk-bergamot"),
        ],
    },
}

DELIVERY_FLOW = {
    "root": {
        "reply": "Что вас интересует?",
        "suggestions": ["Доставка", "Оплата", "Самовывоз", "Сроки изготовления и отправки"],
    },
    "Доставка": {
        "reply": "Бесплатная доставка действует от 5000 ₽ до пвз СДЭК. По стране отправляем СДЭК и Почтой России — стоимость доставки рассчитывается автоматически в корзине.",
        "suggestions": ["Оплата", "Самовывоз", "Сроки изготовления и отправки"],
    },
    "Оплата": {
        "reply": "Оплата возможна через сервисы ROBOKASSA и Т-Банк.",
        "suggestions": ["Доставка", "Самовывоз", "Сроки изготовления и отправки"],
    },
    "Самовывоз": {
        "reply": "Самовывоз доступен по адресу: Шелепихинская набережная, 34к4",
        "suggestions": ["Доставка", "Сроки изготовления и отправки"],
        "links": [("Связаться с менеджером", TELEGRAM_URL)],
    },
    "Сроки изготовления и отправки": {
        "reply": "Создаем и отправляем заказ от 1 до 5 рабочих дней после оплаты.",
        "suggestions": ["Доставка", "Самовывоз"],
        "links": [("Связаться с менеджером", TELEGRAM_URL)],
    },
}

FREE_FAQ = [
    (r"(универсальн.*аромат|без ошибк.*подар)", "Если нужен максимально универсальный вариант, обратите внимание на Хлопок + ирис, Морскую соль + орхидею или Бергамот."),
    (r"(свеч.*или диффузор|чем отличается свеча от диффузора)", "Свеча подходит для ритуала и атмосферы в моменте, а диффузор дает постоянный фоновый аромат в пространстве."),
    (r"(интерьерн.*спрей|зачем интерьерный спрей)", "Интерьерный спрей подходит для быстрого ароматического акцента: освежить комнату, текстиль или быстро изменить настроение в пространстве."),
    (r"(шкаф|белье|саше)", "Для белья, шкафа и ящиков лучше всего подходят саше для белья."),
    (r"(готов.*подарочн.*набор|подарочн.*наборы)", "Готовые подарочные решения можно посмотреть в отдельном разделе на сайте."),
    (r"(где мой заказ|отследить заказ|трек|поврежден|изменить заказ)", "По вопросам конкретного заказа лучше сразу написать менеджеру BATH BASICS в Telegram."),
    (r"(офлайн|понюхать|вживую)", "Если вам важно познакомиться с ароматами вживую, лучше посмотреть офлайн-точки бренда или уточнить у менеджера."),
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

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    msg = normalize(payload.message)

    # start
    if msg in {"start", "привет", "начать", "меню"}:
        return make_response(START_REPLY, START_SUGGESTIONS)

    # direct manager
    if "менедж" in msg or "человек" in msg:
        return make_response(
            "Вы можете сразу написать менеджеру BATH BASICS в Telegram.",
            links=[("Перейти в Telegram", TELEGRAM_URL)],
            handoff=True,
        )

    # top-level buttons
    if msg == normalize("Подобрать аромат"):
        return make_response("Выберите группу ароматов", list(AROMA_GROUPS.keys()))
    if msg == normalize("Подобрать товар"):
        root = PRODUCT_FLOW["product_root"]
        return make_response(root["reply"], root["suggestions"])
    if msg == normalize("Подарок"):
        return make_response(
            "Я помогу выбрать подарок. Вы можете посмотреть готовые подарочные наборы или сразу перейти к подбору подарка с менеджером.",
            links=[("Готовые подарочные наборы", "http://bathbasics.ru/page135471726.html"), ("Подобрать подарок", TELEGRAM_URL)],
        )
    if msg == normalize("Доставка и оплата"):
        root = DELIVERY_FLOW["root"]
        return make_response(root["reply"], root["suggestions"])
    if msg == normalize("Связаться с менеджером"):
        return make_response("Вы можете сразу написать менеджеру BATH BASICS в Telegram.", links=[("Перейти в Telegram", TELEGRAM_URL)], handoff=True)

    # aroma flow
    for group, aromas in AROMA_GROUPS.items():
        if msg == normalize(group):
            return make_response("Выберите аромат", aromas)
    for aroma, products in AROMA_PRODUCTS.items():
        if msg == normalize(aroma):
            return make_response("Этот аромат представлен в таких товарах:\n" + "\n".join(f"• {p}" for p in products),
                                 suggestions=["Выбрать другую группу", "Связаться с менеджером"])

    # product flow
    if payload.message in PRODUCT_FLOW:
        node = PRODUCT_FLOW[payload.message]
        return make_response(node["reply"], node.get("suggestions", []), node.get("links", []), handoff=any(u == TELEGRAM_URL for _, u in node.get("links", [])))

    # delivery flow
    if payload.message in DELIVERY_FLOW:
        node = DELIVERY_FLOW[payload.message]
        return make_response(node["reply"], node.get("suggestions", []), node.get("links", []), handoff=any(u == TELEGRAM_URL for _, u in node.get("links", [])))

    # extended faq
    for pattern, answer in FREE_FAQ:
        if re.search(pattern, msg):
            links = [("Перейти в Telegram", TELEGRAM_URL)] if "Telegram" in answer or "менеджеру" in answer else []
            return make_response(answer, links=links, handoff=bool(links))

    # fallback helpers
    if "аромат" in msg:
        return make_response("Выберите группу ароматов", list(AROMA_GROUPS.keys()))
    if any(x in msg for x in ["свеч", "диффуз", "спрей", "мыло", "лосьон", "крем", "соль"]):
        root = PRODUCT_FLOW["product_root"]
        return make_response(root["reply"], root["suggestions"])
    if "достав" in msg or "оплат" in msg or "самовывоз" in msg:
        root = DELIVERY_FLOW["root"]
        return make_response(root["reply"], root["suggestions"])
    if "подар" in msg:
        return make_response(
            "Я помогу выбрать подарок. Вы можете посмотреть готовые подарочные наборы или сразу перейти к подбору подарка с менеджером.",
            links=[("Готовые подарочные наборы", "http://bathbasics.ru/page135471726.html"), ("Подобрать подарок", TELEGRAM_URL)],
        )

    return make_response(START_REPLY, START_SUGGESTIONS)
