# Directive: Scrape Job

**Goal:**
Automatically extract job details (title, company, description) from a JobStreet job URL while avoiding bot detection.

**Inputs:**
- `url`: The JobStreet job posting URL.

**Tools/Scripts:**
- `execution/scraper.py`: Python script using Playwright.
- `playwright-stealth`: Plugin to bypass basic bot detection scripts.

**Outputs:**
- A dictionary containing:
    - `title`: Job title.
    - `company`: Company name.
    - `description`: Full job description text.
    - `url`: The original URL.

**Edge Cases:**
- *URL invalid/404*: Return `None` if the page cannot be loaded.
- *Selector change*: If JobStreet updates their DOM, the scraper may fail to find elements. Return default strings like "Not Found".
- *Bot blocking*: If blocked, consider using a proxy (supported via CLI arguments).

**Execution Steps:**
1. Initialize a Playwright browser instance with stealth settings.
2. Navigate to the job URL.
3. Wait for the job description container to load.
4. Extract the title, company name, and description text.
5. Close the browser and return the data dictionary.
