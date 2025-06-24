FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
# Если используешь playwright sync API:
RUN playwright install

CMD ["python3", "parse_yamaya.py"]
