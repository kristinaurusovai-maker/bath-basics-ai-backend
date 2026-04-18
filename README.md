[README.md](https://github.com/user-attachments/files/26858876/README.md)
# BATH BASICS Assistant v2 — версия с main.py

## 1. Что внутри
- `main.py` — backend FastAPI
- `requirements.txt`
- `t123_widget.html` — код для блока T123
- `README.md`

---

## 2. Как запустить локально

Открой Terminal в папке проекта и выполни:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Проверка:
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

Если удобнее, можно так:

```bash
python -m uvicorn main:app --reload
```

---

## 3. Что поменять на Render

В Render укажи:

### Build Command
```bash
pip install -r requirements.txt
```

### Start Command
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Если нужен фикс версии Python, оставь файл `.python-version` со строкой:
```text
3.12.8
```

---

## 4. Что вставлять в Tilda

Открой файл `t123_widget.html`, скопируй весь код и вставь его в блок **T123**.

Если адрес backend другой, замени строку:
```js
const API_URL = "https://bath-basics-ai.onrender.com/api/chat";
```

на свой Render URL.

---

## 5. Логика, которая уже есть
- первый экран
- подобрать аромат
- подобрать товар
- подарок
- доставка и оплата
- связаться с менеджером
- расширенный FAQ
