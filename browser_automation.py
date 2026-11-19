import asyncio
from playwright.async_api import async_playwright, Playwright  # type: ignore

async def apply(playwright: Playwright, url: str = "http://google.com"):
    chromium = playwright.chromium # or "firefox" or "webkit".
    browser = await chromium.launch()
    page = await browser.new_page()
    await page.goto(url)
    # other actions...
    await page.screenshot(path="google.png")
    await browser.close()

async def main():
    async with async_playwright() as playwright:
        await apply(playwright)
asyncio.run(main())