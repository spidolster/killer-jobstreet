# JobStreet Scraper CLI

A Python CLI application that automates scraping job details (title, company, description) from JobStreet URLs. It uses Playwright with the `playwright-stealth` plugin to bypass basic bot detections and outputs the extracted data into a well-formatted Markdown file. Additionally, it integrates an AI-powered company research feature to append a summary of the hiring company to your job log.

## Features

- **Automated Scraping:** Extracts job title, company name, and full description from a JobStreet posting.
- **Stealth Mode:** Utilizes `playwright-stealth` to reduce the likelihood of being blocked.
- **Company Research:** Automatically fetches a brief research summary (business, products/services, and culture) on the company using an AI provider.
- **SQLite Database:** Saves all job and company information into a centralized local `jobs.db` SQLite database.
- **Proxy Support:** Supports custom proxy configurations via CLI arguments.
- **Continuous Mode:** Optional polling interval to run the scraper repeatedly.

## Structure

Following the 3-Layer Agentic Architecture defined in `AGENTS.md`:
- **`main.py`**: The CLI entry point and orchestration script ([Orchestration Directive](directives/orchestration.md)).
- **`execution/scraper.py`**: The Playwright automation script ([Scrape Job Directive](directives/scrape_job.md)).
- **`execution/db_manager.py`**: SQLite database manager for structured tracking.
- **`directives/research_company.md`**: Instruction set/SOP for company research.
- **`execution/research_company.py`**: Deterministic script fetching company info using tools and AI.
- **`directives/analyze_fit.md`**: SOP for AI-powered resume fit/gap analysis.
- **`directives/tailor_resume.md`**: SOP for AI-powered resume tailoring.
- **`directives/generate_cover_letter.md`**: SOP for professional cover letter generation.
- **`.tmp/`**: Local directory where intermediate processing files are saved (if any).

## Prerequisites

- Python 3.10+
- [Playwright](https://playwright.dev/python/) dependencies

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/spidolster/job-assistant.git
   cd jobstreet-helper
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright Chromium browser:**
   ```bash
   playwright install chromium
   ```

5. **Configure Environment Variables:**
   Create a `.env` file in the root directory and add any required API keys for the company research tool (e.g., `OPENAI_API_KEY`).
   ```env
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

Run the scraper using `main.py` and provide the target JobStreet job URL.

```bash
python main.py "https://www.jobstreet.co.id/job/..."
```

### Optional Arguments

- `--interval <minutes>`: Set an interval to run the extraction continuously (e.g., `--interval 60` runs every hour).
- `--proxy <proxy_url>`: Use a proxy server (format: `http://username:password@ip:port`).

**Example with arguments:**
```bash
python main.py "https://www.jobstreet.co.id/job/..." --interval 30 --proxy "http://user:pass@127.0.0.1:8080"
```

## Output

Extracted job applications are saved automatically to a local SQLite database named `jobs.db` in the root directory.

The table `job_applications` contains:
- `id`: Unique identifier
- `job_title`: The title of the job
- `company_name`: The company name
- `job_url`: The original JobStreet URL
- `description`: The full job description
- `research_summary`: AI-generated company research summary
- `extracted_at`: Timestamp of extraction
