import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        c = await b.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = await c.new_page()
        await Stealth().apply_stealth_async(page)
        await page.goto("https://id.jobstreet.com/id/job/90616424", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        html = await page.content()
        with open("page.html", "w", encoding="utf-8") as f:
            f.write(html)
        await b.close()

asyncio.run(run())
