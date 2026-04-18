from __future__ import annotations

import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

TELEGRAM_URL = "https://t.me/bath_basics"

app = FastAPI(title="BATH BASICS Assistant", version="3.0.0")
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
    "Сандал + кокос": [
        ("Свеча в стекле 120 мл — Сандал + кокос", "https://bathbasics.ru/tproduct/694755355742-svecha-sandal-kokos"),
        ("Диффузор для дома 50/100 мл — Сандал + кокос", "https://bathbasics.ru/tproduct/313130844952-diffuzor-santal-kokos"),
        ("Интерьерный спрей 50 мл — Сандал + кокос", "https://bathbasics.ru/tproduct/871417258212-interernii-sprei-50-ml-santal-kokos"),
    ],
    "Груша в бренди": [
        ("Свеча в стекле 120 мл — Груша в бренди", "https://bathbasics.ru/tproduct/576971823822-svecha-grusha-v-brendi"),
        ("Диффузор для дома 50/100 мл — Груша в бренди", "https://bathbasics.ru/tproduct/689715464902-diffuzor-grusha-v-brendi"),
        ("Интерьерный спрей 50 мл — Груша в бренди", "https://bathbasics.ru/tproduct/605801616532-interernii-sprei-50-ml-grusha-v-brendi"),
    ],
    "Сбор инжира": [
        ("Свеча в стекле 120 мл — Сбор инжира", "https://bathbasics.ru/tproduct/531487274632-svecha-sbor-inzhira"),
        ("Лосьон для тела 300 мл — Сбор инжира", "https://bathbasics.ru/tproduct/635013785322-loson-dlya-tela-sbor-inzhira"),
        ("Мыло для рук 300 мл — Сбор инжира", "https://bathbasics.ru/tproduct/334795672472-zhidkoe-milo-sbor-inzhira"),
    ],
    "Хлопок + ирис": [
        ("Свеча в стекле 120 мл — Хлопок + ирис", "https://bathbasics.ru/tproduct/238168627992-svecha-hlopok-iris"),
        ("Диффузор для дома 50/100 мл — Хлопок + ирис", "https://bathbasics.ru/tproduct/426687082222-diffuzor-hlopok-iris"),
        ("Интерьерный спрей 50 мл — Хлопок + ирис", "https://bathbasics.ru/tproduct/985115124462-interernii-sprei-50-ml-hlopok-iris"),
        ("Крем для рук 50 мл — Хлопок + ирис", "https://bathbasics.ru/tproduct/323780190542-krem-dlya-ruk-hlopok-iris"),
        ("Лосьон для тела 300 мл — Хлопок + ирис", "https://bathbasics.ru/tproduct/760670042532-loson-dlya-tela-hlopok-iris"),
        ("Мыло для рук 300 мл — Хлопок + ирис", "https://bathbasics.ru/tproduct/502121303962-zhidkoe-milo-hlopok-iris"),
        ("Саше для белья — Лошадка", "https://bathbasics.ru/tproduct/172411195712-loshadka"),
        ("Саше для белья — Щелкунчик", "https://bathbasics.ru/tproduct/866380938802-schelkuchnik"),
    ],
    "Пачули + табак": [
        ("Свеча в стекле 120 мл — Пачули + табак", "https://bathbasics.ru/tproduct/544821768482-svecha-pachuli-tabak"),
        ("Диффузор для дома 50/100 мл — Пачули + табак", "https://bathbasics.ru/tproduct/177239159562-diffuzor-pachuli-tabak"),
        ("Интерьерный спрей 50 мл — Пачули + табак", "https://bathbasics.ru/tproduct/741227351732-interernii-sprei-50-ml-pachuli-tabak"),
        ("Крем для рук 50 мл — Пачули + табак", "https://bathbasics.ru/tproduct/426516668042-krem-dlya-ruk-pachuli-tabak"),
        ("Лосьон для тела 300 мл — Пачули + табак", "https://bathbasics.ru/tproduct/936247085382-loson-dlya-tela-pachuli-tabak"),
        ("Мыло для рук 300 мл — Пачули + табак", "https://bathbasics.ru/tproduct/623573831712-zhidkoe-milo-pachuli-tabak"),
    ],
    "Мох + амбра": [
        ("Свеча в стекле 120 мл — Мох + амбра", "https://bathbasics.ru/tproduct/744620328512-svecha-moh-ambra"),
        ("Диффузор для дома 50/100 мл — Мох + амбра", "https://bathbasics.ru/tproduct/177424065322-diffuzor-moh-ambra"),
        ("Интерьерный спрей 50 мл — Мох + амбра", "https://bathbasics.ru/tproduct/231116557522-interernii-sprei-50-ml-moh-ambra"),
    ],
    "Жженая древесина": [
        ("Диффузор для дома 50/100 мл — Жженая древесина", "https://bathbasics.ru/tproduct/455023822762-diffuzor-zhzhenaya-drevesina"),
        ("Интерьерный спрей 50 мл — Жженая древесина", "https://bathbasics.ru/tproduct/774355587642-interernii-sprei-50-ml-zhzhenaya-drevesi"),
        ("Крем для рук 50 мл — Жженая древесина", "https://bathbasics.ru/tproduct/228500873942-krem-dlya-ruk-zhzhenaya-drevesina"),
        ("Лосьон для тела 300 мл — Жженая древесина", "https://bathbasics.ru/tproduct/652455564262-loson-dlya-tela-zhzhenaya-drevesina"),
        ("Мыло для рук 300 мл — Жженая древесина", "https://bathbasics.ru/tproduct/882827290282-zhidkoe-milo-zhzhenaya-drevesina"),
    ],
    "Перец + амбра": [
        ("Диффузор для дома 50/100 мл — Перец + амбра", "https://bathbasics.ru/tproduct/312272682942-diffuzor-perets-ambra"),
        ("Интерьерный спрей 50 мл — Перец + амбра", "https://bathbasics.ru/tproduct/596966631352-interernii-sprei-50-ml-perets-ambra"),
        ("Крем для рук 50 мл — Перец + амбра", "https://bathbasics.ru/tproduct/300783060912-krem-dlya-ruk-perets-ambra"),
        ("Лосьон для тела 300 мл — Перец + амбра", "https://bathbasics.ru/tproduct/503371305972-loson-dlya-tela-perets-ambra"),
        ("Мыло для рук 300 мл — Перец + амбра", "https://bathbasics.ru/tproduct/956403805692-zhidkoe-milo-perets-ambra"),
    ],
    "Анис + специи": [
        ("Свеча в стекле 120 мл — Анис + специи", "https://bathbasics.ru/tproduct/665617753872-svecha-anis-spetsii"),
        ("Диффузор для дома 50/100 мл — Анис + специи", "https://bathbasics.ru/tproduct/369465618352-diffuzor-anis-koritsa"),
        ("Крем для рук 50 мл — Анис + специи", "https://bathbasics.ru/tproduct/852349106582-krem-dlya-ruk-anis-spetsii"),
        ("Лосьон для тела 300 мл — Анис + специи", "https://bathbasics.ru/tproduct/234147502032-loson-dlya-tela-anis-spetsii"),
        ("Мыло для рук 300 мл — Анис + специи", "https://bathbasics.ru/tproduct/438408709162-zhidkoe-milo-anis-spetsii"),
    ],
    "Яблоки + кленовый бурбон": [
        ("Свеча в стекле 120 мл — Яблоки + кленовый бурбон", "https://bathbasics.ru/tproduct/309972024652-svecha-yabloki-klenovii-burbon-"),
        ("Диффузор для дома 50/100 мл — Яблоки + кленовый бурбон", "https://bathbasics.ru/tproduct/400578914522-diffuzor-yabloki-klenovii-burbon"),
        ("Интерьерный спрей 50 мл — Яблоки + кленовый бурбон", "https://bathbasics.ru/tproduct/522437286142-interernii-sprei-50-ml-yabloki-klenovii"),
    ],
    "Карамельный попкорн": [
        ("Свеча в стекле 120 мл — Карамельный попкорн", "https://bathbasics.ru/tproduct/363271129392-svecha-karamelnii-popkorn"),
        ("Диффузор для дома 50/100 мл — Карамельный попкорн", "https://bathbasics.ru/tproduct/623161912322-diffuzor-karamelnii-popkorn"),
        ("Интерьерный спрей 50 мл — Карамельный попкорн", "https://bathbasics.ru/tproduct/888015344482-interernii-sprei-50-ml-karamelnii-popkor"),
        ("Лосьон для тела 300 мл — Карамельный попкорн", "https://bathbasics.ru/tproduct/124954135552-loson-dlya-tela-karamelnii-popkorn"),
        ("Мыло для рук 300 мл — Карамельный попкорн", "https://bathbasics.ru/tproduct/542358511812-zhidkoe-milo-karamelnii-popkorn"),
    ],
    "Тыквенный латте": [("Свеча в стекле 120 мл — Тыквенный латте", "https://bathbasics.ru/tproduct/281124913032-svecha-tikvennii-latte")],
    "Лепестки роз": [("Соль для ванны — Лепестки роз", "https://bathbasics.ru/tproduct/391350849282-sol-dlya-vanni-rose-petals-")],
    "Манговый сорбет": [
        ("Свеча в стекле 120 мл — Манговый сорбет", "https://bathbasics.ru/tproduct/176964868682-cvecha-mangovii-sorbet"),
        ("Диффузор для дома 50/100 мл — Манговый сорбет", "https://bathbasics.ru/tproduct/511871058092-diffuzor-mangovii-sorbet"),
        ("Интерьерный спрей 50 мл — Манговый сорбет", "https://bathbasics.ru/tproduct/225998064232-interernii-sprei-50-ml-mangovii-sorbet"),
        ("Крем для рук 50 мл — Манговый сорбет", "https://bathbasics.ru/tproduct/184448041762-krem-dlya-ruk-mangovii-sorbet"),
        ("Лосьон для тела 300 мл — Манговый сорбет", "https://bathbasics.ru/tproduct/646799116362-loson-dlya-tela-mangovii-sorbet"),
        ("Мыло для рук 300 мл — Манговый сорбет", "https://bathbasics.ru/tproduct/356161982152-zhidkoe-milo-mangovii-sorbet"),
    ],
    "Клюквенный лес": [
        ("Свеча в стекле 120 мл — Клюквенный лес", "https://bathbasics.ru/tproduct/646810893412-svecha-klyukvennii-les"),
        ("Диффузор для дома 50/100 мл — Клюквенный лес", "https://bathbasics.ru/tproduct/337662184122-diffuzor-klyukvennii-les"),
        ("Интерьерный спрей 50 мл — Клюквенный лес", "https://bathbasics.ru/tproduct/590899625732-interernii-sprei-50-ml-klyukvennii-les"),
        ("Соль для ванны — Клюквенный лес", "https://bathbasics.ru/tproduct/944380994792-sol-dlya-vanni-klyukvennii-les"),
    ],
    "Голубая ель": [
        ("Диффузор для дома 50/100 мл — Голубая ель", "https://bathbasics.ru/tproduct/398375391852-diffuzor-golubaya-el"),
        ("Интерьерный спрей 50 мл — Голубая ель", "https://bathbasics.ru/tproduct/117040601482-interernii-sprei-50-ml-golubaya-el"),
    ],
    "Морозный можжевельник": [("Свеча в стекле 120 мл — Морозный можжевельник", "https://bathbasics.ru/tproduct/938897949032-svecha-moroznii-mozhzhevelnik")],
}

PRODUCT_FLOW = {
    "product_root": {"reply": "Какая категория вас интересует?", "suggestions": ["Для дома", "Для тела", "Подарочные наборы"]},
    "Для дома": {"reply": "Какой продукт вас интересует?", "suggestions": ["Свечи", "Диффузоры", "Интерьерные спреи", "Саше для белья"]},
    "Для тела": {"reply": "Какой продукт вас интересует?", "suggestions": ["Жидкое мыло", "Лосьоны для тела", "Соль для ванны", "Кремы для рук"]},
    "Подарочные наборы": {"reply": "Вы можете посмотреть готовые подарочные решения или сразу перейти к подбору подарка с менеджером.", "links": [("Готовые подарочные наборы", "http://bathbasics.ru/page135471726.html"), ("Подобрать подарок", TELEGRAM_URL)]},
    "Свечи": {"reply": "Вот популярные ароматы для свечей", "links": [("Пачули + табак", "https://bathbasics.ru/tproduct/544821768482-svecha-pachuli-tabak"), ("Карамельный попкорн", "https://bathbasics.ru/tproduct/363271129392-svecha-karamelnii-popkorn"), ("Мох + амбра", "https://bathbasics.ru/tproduct/744620328512-svecha-moh-ambra"), ("Морская соль + орхидея", "https://bathbasics.ru/tproduct/349689568212-svecha-morskaya-sol-orhideya")]},
    "Диффузоры": {"reply": "Вот популярные ароматы для диффузоров", "links": [("Клюквенный лес", "https://bathbasics.ru/tproduct/337662184122-diffuzor-klyukvennii-les"), ("Пачули + табак", "https://bathbasics.ru/tproduct/177239159562-diffuzor-pachuli-tabak"), ("Хлопок + ирис", "https://bathbasics.ru/tproduct/426687082222-diffuzor-hlopok-iris"), ("Манговый сорбет", "https://bathbasics.ru/tproduct/511871058092-diffuzor-mangovii-sorbet")]},
    "Интерьерные спреи": {"reply": "Вот популярные ароматы для интерьерных спреев", "links": [("Манговый сорбет", "https://bathbasics.ru/tproduct/225998064232-interernii-sprei-50-ml-mangovii-sorbet"), ("Карамельный попкорн", "https://bathbasics.ru/tproduct/888015344482-interernii-sprei-50-ml-karamelnii-popkor"), ("Мох + амбра", "https://bathbasics.ru/tproduct/231116557522-interernii-sprei-50-ml-moh-ambra"), ("Хлопок + ирис", "https://bathbasics.ru/tproduct/985115124462-interernii-sprei-50-ml-hlopok-iris")]},
    "Саше для белья": {"reply": "Выберите формат саше для белья", "links": [("Лошадка", "https://bathbasics.ru/tproduct/172411195712-loshadka"), ("Щелкунчик", "https://bathbasics.ru/tproduct/866380938802-schelkuchnik")]},
    "Жидкое мыло": {"reply": "Вот популярные ароматы для жидкого мыла", "links": [("Пачули + табак", "https://bathbasics.ru/tproduct/623573831712-zhidkoe-milo-pachuli-tabak"), ("Перец + амбра", "https://bathbasics.ru/tproduct/956403805692-zhidkoe-milo-perets-ambra"), ("Жженая древесина", "https://bathbasics.ru/tproduct/882827290282-zhidkoe-milo-zhzhenaya-drevesina"), ("Анис + специи", "https://bathbasics.ru/tproduct/438408709162-zhidkoe-milo-anis-spetsii")]},
    "Лосьоны для тела": {"reply": "Вот популярные ароматы для лосьонов для тела", "links": [("Ваниль + сахар", "https://bathbasics.ru/tproduct/317575227672-loson-dlya-tela-vanil-sahar"), ("Анис + специи", "https://bathbasics.ru/tproduct/234147502032-loson-dlya-tela-anis-spetsii"), ("Пачули + табак", "https://bathbasics.ru/tproduct/936247085382-loson-dlya-tela-pachuli-tabak"), ("Манговый сорбет", "https://bathbasics.ru/tproduct/646799116362-loson-dlya-tela-mangovii-sorbet")]},
    "Соль для ванны": {"reply": "Вот популярные ароматы для соли для ванны", "links": [("Клюквенный лес", "https://bathbasics.ru/tproduct/944380994792-sol-dlya-vanni-klyukvennii-les"), ("Лепестки роз", "https://bathbasics.ru/tproduct/391350849282-sol-dlya-vanni-rose-petals-")]},
    "Кремы для рук": {"reply": "Вот популярные ароматы для кремов для рук", "links": [("Ваниль + сахар", "https://bathbasics.ru/tproduct/960076218692-krem-dlya-ruk-vanil-sahar"), ("Перец + амбра", "https://bathbasics.ru/tproduct/300783060912-krem-dlya-ruk-perets-ambra"), ("Пачули + табак", "https://bathbasics.ru/tproduct/426516668042-krem-dlya-ruk-pachuli-tabak"), ("Бергамот", "https://bathbasics.ru/tproduct/978920199882-krem-dlya-ruk-bergamot")]},
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
            links = [("Перейти в Telegram", TELEGRAM_URL)] if "Telegram" in answer or "менеджеру" in answer else []
            return make_response(answer, suggestions=[MAIN_MENU_LABEL], links=links, handoff=bool(links))

    if "аромат" in msg:
        return make_response("Выберите группу ароматов", list(AROMA_GROUPS.keys()) + [MAIN_MENU_LABEL])
    if any(x in msg for x in ["свеч", "диффуз", "спрей", "мыло", "лосьон", "крем", "соль"]):
        root = PRODUCT_FLOW["product_root"]
        return make_response(root["reply"], root["suggestions"] + [MAIN_MENU_LABEL])
    if "достав" in msg or "оплат" in msg or "самовывоз" in msg:
        root = DELIVERY_FLOW["root"]
        return make_response(root["reply"], root["suggestions"] + [MAIN_MENU_LABEL])
    if "подар" in msg:
        return make_response("Я помогу выбрать подарок. Вы можете посмотреть готовые подарочные наборы или сразу перейти к подбору подарка с менеджером.", suggestions=[MAIN_MENU_LABEL], links=[("Готовые подарочные наборы", "http://bathbasics.ru/page135471726.html"), ("Подобрать подарок", TELEGRAM_URL)])

    return make_response(START_REPLY, START_SUGGESTIONS)
