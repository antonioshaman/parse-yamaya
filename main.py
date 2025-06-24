from flask import Flask, request, jsonify
import asyncio
from playwright.async_api import async_playwright

app = Flask(__name__)

@app.route("/parse")
def parse():
    year = int(request.args.get("year"))
    month = int(request.args.get("month"))
    day = int(request.args.get("day"))
    result = asyncio.run(run_playwright(year, month, day))
    return jsonify(result)

async def run_playwright(year, month, day):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        # Твой код парсинга!
        await browser.close()
        return {"kin": "...", "tone": "...", "seal": "..."}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
