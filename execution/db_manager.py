import sqlite3
import os
import logging
import time

DB_PATH = 'jobs.db'

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS job_applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_title TEXT NOT NULL,
                    company_name TEXT NOT NULL,
                    job_url TEXT NOT NULL UNIQUE,
                    description TEXT,
                    research_summary TEXT,
                    match_score INTEGER,
                    fit_analysis TEXT,
                    tailored_resume TEXT,
                    cover_letter TEXT,
                    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Migrations: add columns if missing (existing databases)
            for col in ['cover_letter', 'tailored_resume']:
                try:
                    cursor.execute(f'ALTER TABLE job_applications ADD COLUMN {col} TEXT')
                except Exception:
                    pass  # Column already exists
            conn.commit()
            logging.info(f"Database initialized at {DB_PATH}")
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")

def insert_job(job_data: dict) -> bool:
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO job_applications (
                    job_title, company_name, job_url, description, research_summary,
                    match_score, fit_analysis, tailored_resume, cover_letter
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(job_url) DO UPDATE SET
                    job_title=excluded.job_title,
                    company_name=excluded.company_name,
                    description=excluded.description,
                    research_summary=excluded.research_summary,
                    match_score=excluded.match_score,
                    fit_analysis=excluded.fit_analysis,
                    tailored_resume=excluded.tailored_resume,
                    cover_letter=excluded.cover_letter,
                    extracted_at=CURRENT_TIMESTAMP
            ''', (
                job_data.get('title', 'Unknown Title'),
                job_data.get('company', 'Unknown Company'),
                job_data.get('url', ''),
                job_data.get('description', ''),
                job_data.get('research_summary', ''),
                job_data.get('match_score', 0),
                job_data.get('fit_analysis', ''),
                job_data.get('tailored_resume', ''),
                job_data.get('cover_letter', '')
            ))
            conn.commit()
            logging.info(f"Successfully saved job '{job_data.get('title')}' to database.")
            return True
    except Exception as e:
        logging.error(f"Failed to insert job into database: {e}")
        return False
