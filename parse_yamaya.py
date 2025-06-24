import asyncio
from datetime import datetime
import random
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from playwright.async_api import async_playwright

app = FastAPI()

# 📌 Твои юзер-агенты
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
]

# 🔑 Безопасный XPath-захват
async def extract_label(page, label):
    handle = await page.evaluate_handle(f"""
        () => {{
            const el = document.evaluate(
                '//b[contains(text(), "{label}")]',
                document,
                null,
                XPathResult.FIRST_ORDERED_NODE_TYPE,
                null
            ).singleNodeValue;
            return el && el.nextSibling ? el.nextSibling.textContent.trim() : "";
        }}
    """)
    return await handle.json_value()

async def get_kin_data(year: int, month: int, day: int):
    async with async_playwright() as p:
        user_agent = random.choice(USER_AGENTS)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=user_agent)
        page = await context.new_page()

        date = datetime(year, month, day)
        url = f"https://yamaya.ru/maya/choosedate/?action=setOwnDate&formday={date.day}&formmonth={date.month}&formyear={date.year}"
        print(f"🌐 Открываю: {url}")

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            await page.wait_for_function("""
                () => {
                    const el = document.evaluate('//b[contains(text(), "Кин:")]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    return el && el.nextSibling && el.nextSibling.textContent.trim() !== "";
                }
            """, timeout=10000)

            kin = await extract_label(page, "Кин:")
            tone = await extract_label(page, "Тон")
            seal = await extract_label(page, "Печать")
            portal = await extract_label(page, "Портал Галактической Активации:")
            color = await extract_label(page, "Сила цвета:")

            oracle = {
                "Ведущая Печать": await extract_label(page, "Ведущая Печать"),
                "Аналог": await extract_label(page, "Аналог"),
                "Антипод": await extract_label(page, "Антипод"),
                "Оккультный Учитель": await extract_label(page, "Оккультный Учитель")
            }

            data = {
                "date": date.strftime("%Y-%m-%d"),
                "kin": kin,
                "tone": tone,
                "seal": seal,
                "portal": portal,
                "color": color,
                "oracle": oracle
            }

            print(f"✅ {data['date']} → {data}")
            await browser.close()
            return data

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            await browser.close()
            return {"error": str(e)}

# === FastAPI route ===
@app.get("/parse-yamaya")
async def parse_yamaya(date: str = Query(..., example="1992-07-30")):
    try:
        year, month, day = map(int, date.split("-"))
        result = await get_kin_data(year, month, day)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)})
