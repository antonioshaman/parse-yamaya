# ✅ 1) Playwright официальный образ
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

# ✅ 2) Рабочая папка
WORKDIR /app

# ✅ 3) Копируем всё
COPY . .

# ✅ 4) Ставим Python-зависимости
RUN pip install -r requirements.txt

# ✅ 5) Ставим браузеры
RUN playwright install

# ✅ 6) Открываем порт
EXPOSE 8000

# ✅ 7) Стартуем FastAPI через Uvicorn
CMD ["uvicorn", "parse_yamaya:app", "--host", "0.0.0.0", "--port", "8000"]
