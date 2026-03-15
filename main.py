import argparse
import asyncio
import time
import os
from scraper import JobStreetScraper
import logging
from execution.research_company import research_company
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def save_to_markdown(job_data: dict, output_dir: str = "output"):
    if not job_data:
        return

    os.makedirs(output_dir, exist_ok=True)
    
    # Create safe filename based on title
    safe_title = "".join([c for c in job_data['title'] if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    if not safe_title:
        safe_title = "job_post"
        
    filename = f"{safe_title.replace(' ', '_')}_{int(time.time())}.md"
    filepath = os.path.join(output_dir, filename)

    markdown_content = f"""# {job_data['title']}

**Company:** {job_data['company']}
**URL:** {job_data['url']}
**Extracted At:** {time.strftime('%Y-%m-%d %H:%M:%S')}

## Job Description
{job_data['description']}

## Company Research
{job_data.get('research_summary', 'No research data available.')}
"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    logging.info(f"Saved extracted job data to: {filepath}")


async def run_scraper(url: str, interval_minutes: int | None, proxy: str | None):
    scraper = JobStreetScraper(proxy=proxy)
    
    # Loop execution. If interval is None, runs only once.
    while True:
        logging.info(f"Starting extraction for {url} ...")
        job_data = await scraper.extract_job(url)
        
        if job_data:
            company_name = job_data.get('company')
            if company_name and company_name != "Company Not Found":
                logging.info(f"Researching company: {company_name}")
                research_summary = await research_company(company_name)
                job_data['research_summary'] = research_summary
            else:
                job_data['research_summary'] = "Company name not found; skipping research."
                
            save_to_markdown(job_data)
        else:
            logging.warning("Failed to extract job data.")
        
        if not interval_minutes:
            logging.info("Single extraction completed.")
            break
            
        logging.info(f"Waiting for {interval_minutes} minutes before the next extraction...")
        await asyncio.sleep(interval_minutes * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JobStreet Scraper CLI with Stealth")
    parser.add_argument("url", help="JobStreet URL to scrape")
    parser.add_argument("--interval", type=int, help="Interval in minutes to run the scraper repeatedly (optional)")
    parser.add_argument("--proxy", type=str, help="Proxy server in the format http://username:password@ip:port (optional)")
    
    args = parser.parse_args()
    
    try:
        asyncio.run(run_scraper(args.url, args.interval, args.proxy))
    except KeyboardInterrupt:
        logging.info("Scraper stopped by user.")
