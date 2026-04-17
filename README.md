# BATH BASICS FastAPI backend

## Что внутри
- `app.py` — backend для AI-ассистента
- `requirements.txt` — зависимости
- `BATH_BASICS_AI_final_package.xlsx` — база знаний

## Как запустить локально

```bash
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
# или .venv\Scripts\activate для Windows

pip install -r requirements.txt
uvicorn app:app --reload
```

Backend откроется на:
- `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`

## Основной endpoint

`POST /api/chat`

Пример JSON:
```json
{
  "session_id": "bb_test_1",
  "message": "Хочу подарок до 3000",
  "page_url": "https://bathbasics.ru/",
  "source": "tilda_widget"
}
```

## Как подключить к Tilda

В Tilda-коде замени:
```js
const API_URL = "https://YOUR-DOMAIN.COM/api/chat";
```

на адрес backend, например:
```js
const API_URL = "https://your-backend.onrender.com/api/chat";
```

## Environment variables

- `BB_DATA_PATH` — путь к xlsx с листами
- `BB_TELEGRAM_URL` — ссылка на Telegram
- `BB_CORS_ORIGINS` — список origins через запятую

Пример:
```bash
export BB_DATA_PATH=/path/to/BATH_BASICS_AI_final_package.xlsx
export BB_TELEGRAM_URL=https://t.me/bath_basics
export BB_CORS_ORIGINS=https://bathbasics.ru,https://www.bathbasics.ru
```

## Деплой на Render

Start command:
```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```

Build command:
```bash
pip install -r requirements.txt
```
