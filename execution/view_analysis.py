import sqlite3
import json
import os

DB_PATH = 'jobs.db'


def normalize_score(raw_score, fallback=0):
    """Normalize match score into a safe integer for reporting logic."""
    try:
        if raw_score is None:
            raise ValueError("score is None")
        return int(float(raw_score))
    except (TypeError, ValueError):
        print(
            f"⚠️  Invalid match score value ({raw_score!r}). "
            f"Using fallback score {fallback}."
        )
        return fallback

def export_latest_analysis():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. Run a scrape first.")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Fetch the most recent job application
        cursor.execute('''
            SELECT job_title, company_name, job_url, match_score, fit_analysis,
                   tailored_resume, cover_letter 
            FROM job_applications 
            ORDER BY extracted_at DESC 
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        
        if not row:
            print("No jobs found in the database.")
            return

        print("="*60)
        print(f"JOB FIT ANALYSIS REPORT")
        print("="*60)
        print(f"Job Title : {row['job_title']}")
        print(f"Company   : {row['company_name']}")
        print(f"URL       : {row['job_url']}")
        print("-" * 60)
        
        raw_score = row['match_score']
        score = normalize_score(raw_score)
        print(f"Match Score: {score}/100")
        
        # Determine verbal match category
        if score >= 80:
            print("Verdict    : 🔥 EXCELLENT FIT")
        elif score >= 60:
            print("Verdict    : 👍 GOOD FIT")
        elif score >= 40:
            print("Verdict    : 🟡 MODERATE FIT")
        else:
            print("Verdict    : 🛑 POOR FIT")
            
        print("-" * 60)
        
        analysis_raw = row['fit_analysis']
        if not analysis_raw:
            print("No detailed fit analysis available.")
        else:
            try:
                analysis = json.loads(analysis_raw)

                print("\n✅ MATCHED SKILLS:")
                print(analysis.get('matched_skills', 'N/A'))

                print("\n⚠️ GAP ANALYSIS (What's Missing):")
                print(analysis.get('gap_analysis', 'N/A'))

                print("\n💬 QUICK PITCH:")
                print(analysis.get('quick_pitch', 'N/A'))

            except json.JSONDecodeError:
                print("Could not parse detailed analysis data.")
                print(f"Raw data: {analysis_raw}")
            
        print("="*60)
        
        # Display tailored resume
        tailored_resume = row['tailored_resume']
        if tailored_resume:
            print("\n" + "="*60)
            print("📄 TAILORED RESUME")
            print("="*60)
            print(tailored_resume)
            print("="*60)
        
        # Display cover letter
        cover_letter = row['cover_letter']
        if cover_letter:
            print("\n" + "="*60)
            print("📝 COVER LETTER")
            print("="*60)
            print(cover_letter)
            print("="*60)
        else:
            print("\nNo cover letter generated for this job.")

    except Exception as e:
        print(f"Error reading database: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    export_latest_analysis()
