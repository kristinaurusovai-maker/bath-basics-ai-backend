# BATH BASICS — готовый пакет

Внутри:
- app.py
- requirements.txt
- google_apps_script.gs
- env_example.txt

Что уже настроено:
- ИИ без звездочек и markdown
- ИИ только для открытых вопросов
- ИИ опирается только на встроенный контекст сайта
- подбор товара идет по готовым сценариям и ссылкам
- диалоги логируются в Google Sheets

## Render
Build Command:
pip install -r requirements.txt

Start Command:
python -m uvicorn app:app --host 0.0.0.0 --port $PORT

## Переменные окружения
OPENAI_API_KEY
OPENAI_MODEL=gpt-5.4
GOOGLE_SHEETS_WEBHOOK_URL=ссылка на Apps Script Web App

## Google Sheets
1. Создай таблицу
2. Заголовки:
timestamp | session_id | role | message | page_url | source | response_type | matched_intent | matched_aroma | matched_category
3. Extensions → Apps Script
4. Вставь код из google_apps_script.gs
5. Deploy → New deployment → Web app
6. Скопируй URL и вставь в GOOGLE_SHEETS_WEBHOOK_URL

## Проверка
/health
/test-openai
