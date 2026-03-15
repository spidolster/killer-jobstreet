import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class JobStreetScraper:
    def __init__(self, proxy: str | None = None):
        self.proxy = proxy
        self.stealth = Stealth()

    async def extract_job(self, url: str) -> dict | None:
        async with async_playwright() as p:
            browser_options = {
                "headless": True,
                "args": ["--no-sandbox", "--disable-setuid-sandbox"]
            }
            if self.proxy:
                browser_options["proxy"] = {"server": self.proxy}

            browser = await p.chromium.launch(**browser_options)
            
            # Use a realistic user agent
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            
            # Apply stealth evasions to avoid being blocked easily
            await self.stealth.apply_stealth_async(page)

            try:
                logging.info(f"Navigating to {url}")
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                
                # Wait for main content to load (title is usually a good indicator)
                await page.wait_for_selector('h1', timeout=15000)

                # Extract Job Title
                title_element = await page.query_selector('h1')
                title = await title_element.inner_text() if title_element else "Title Not Found"

                # Extract Company String
                # Usually jobstreet uses data-automation="advertiser-name" or similar.
                company_element = await page.query_selector('[data-automation="advertiser-name"]')
                if not company_element:
                    # Fallback if advertiser-name not found, let's try other common selectors
                    company_element = await page.query_selector('span[data-automation="company-name"]')
                company = await company_element.inner_text() if company_element else "Company Not Found"

                # Extract Description
                # The description is inside an element with data-automation="jobAdDetails"
                desc_element = await page.query_selector('[data-automation="jobAdDetails"]')

                if desc_element:
                    description = await desc_element.inner_text()
                else:
                    description = "Description Not Found"

                    
                return {
                    "url": url,
                    "title": title.strip(),
                    "company": company.strip(),
                    "description": description.strip()
                }

            except Exception as e:
                logging.error(f"Error extracting data from {url}: {e}")
                return None
            finally:
                await context.close()
                await browser.close()
