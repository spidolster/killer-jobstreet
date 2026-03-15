import argparse
import asyncio
import json
import re
import time
import os
from execution.scraper import JobStreetScraper
import logging
from execution.research_company import research_company
from execution.analyze_fit import analyze_fit
from execution.tailor_resume import tailor_resume
from execution.generate_cover_letter import generate_cover_letter
from execution.db_manager import init_db, insert_job
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def _sanitize_filename(name: str) -> str:
    """Remove characters that are not safe for file/directory names."""
    return re.sub(r'[\\/*?:"<>|]', '_', name).strip()


def _save_output_files(job_data: dict):
    """Save tailored resume and cover letter to the output/ directory."""
    title = _sanitize_filename(job_data.get('title', 'Unknown'))
    company = _sanitize_filename(job_data.get('company', 'Unknown'))
    folder_name = f"{title}_{company}"
    output_dir = os.path.join("output", folder_name)
    os.makedirs(output_dir, exist_ok=True)

    tailored = job_data.get('tailored_resume', '')
    if tailored:
        filename = f"{title}_{company}_Resume.txt"
        path = os.path.join(output_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(tailored)
        logging.info(f"Tailored resume saved to {path}")

    cover = job_data.get('cover_letter', '')
    if cover:
        filename = f"{title}_{company}_CoverLetter.md"
        path = os.path.join(output_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(cover)
        logging.info(f"Cover letter saved to {path}")


async def run_scraper(url: str, interval_minutes: int | None, proxy: str | None):
    scraper = JobStreetScraper(proxy=proxy)
    
    # Read resume content once at startup (this file is NEVER modified)
    resume_path = "documents/my-resume.txt"
    resume_text = ""
    try:
        with open(resume_path, 'r', encoding='utf-8') as f:
            resume_text = f.read()
    except Exception as e:
        logging.warning(f"Failed to read resume at {resume_path}: {e}")
        
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
                
            if resume_text and job_data.get('description'):
                # --- Step 1: Fit Analysis ---
                logging.info("Analyzing fit for your resume...")
                fit_results = await analyze_fit(job_data['description'], resume_text)
                job_data['match_score'] = fit_results.get('match_score', 0)
                job_data['fit_analysis'] = fit_results.get('fit_analysis', '')

                # --- Step 2: Tailor Resume (if gaps found) ---
                resume_for_cover_letter = resume_text  # default: original
                fit_analysis_str = job_data.get('fit_analysis', '')
                has_gaps = False
                try:
                    fit_json = json.loads(fit_analysis_str)
                    gap = fit_json.get('gap_analysis', '')
                    # Consider gaps exist if gap_analysis is non-empty and not just "N/A" / "None"
                    has_gaps = bool(gap) and gap.strip().lower() not in ('n/a', 'none', '-', '')
                except (json.JSONDecodeError, AttributeError):
                    has_gaps = False

                if has_gaps:
                    logging.info("Gaps detected — generating tailored resume...")
                    tailored = await tailor_resume(resume_text, job_data['description'], fit_analysis_str)
                    job_data['tailored_resume'] = tailored
                    resume_for_cover_letter = tailored
                else:
                    logging.info("No significant gaps — using original resume for cover letter.")
                    job_data['tailored_resume'] = ''

                # --- Step 3: Cover Letter (uses tailored resume if available) ---
                logging.info("Generating cover letter...")
                cover_letter = await generate_cover_letter(
                    job_title=job_data.get('title', ''),
                    company_name=company_name or '',
                    company_profile=job_data.get('research_summary', ''),
                    job_description=job_data['description'],
                    resume_text=resume_for_cover_letter
                )
                job_data['cover_letter'] = cover_letter

                # --- Step 4: Save files to output/ ---
                _save_output_files(job_data)
            else:
                logging.warning("Skipping fit analysis and cover letter because resume or job description is missing.")
                
            insert_job(job_data)
        else:
            logging.warning("Failed to extract job data.")
        
        if not interval_minutes:
            logging.info("Single extraction completed.")
            break
            
        logging.info(f"Waiting for {interval_minutes} minutes before the next extraction...")
        await asyncio.sleep(interval_minutes * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JobStreet Scraper CLI with Stealth")
    parser.add_argument("--interval", type=int, help="Interval in minutes to run the scraper repeatedly (optional)")
    parser.add_argument("--proxy", type=str, help="Proxy server in the format http://username:password@ip:port (optional)")

    args = parser.parse_args()

    print("=" * 50)
    print("  JobStreet Job Scraper")
    print("=" * 50)
    url = input("Masukkan URL JobStreet: ").strip()

    if not url:
        print("Error: URL tidak boleh kosong.")
        exit(1)

    init_db()

    try:
        asyncio.run(run_scraper(url, args.interval, args.proxy))
    except KeyboardInterrupt:
        logging.info("Scraper stopped by user.")
