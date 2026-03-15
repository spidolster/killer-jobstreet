# Directive: Orchestration

**Goal:**
Coordinate the end-to-end execution of the job application assistant pipeline, from URL input to database and file output.

**Tools/Scripts:**
- `main.py`: The central orchestration script.
- `execution/db_manager.py`: For persistence.

**Pipeline Flow:**
1. **Fetch**: Scrape the job URL (`directives/scrape_job.md`).
2. **Research**: Research the company (`directives/research_company.md`).
3. **Analyze**: Perform fit analysis (`directives/analyze_fit.md`).
4. **Tailor**: If gaps are found, tailor the resume (`directives/tailor_resume.md`).
5. **Draft**: Generate the cover letter (`directives/generate_cover_letter.md`).
6. **Persist**: 
    - Save all data to the SQLite `jobs.db`.
    - Create an `output/` folder and save the tailored resume (`{Title}_{Company}_Resume.txt`) and cover letter (`{Title}_{Company}_CoverLetter.md`).

**Error Handling:**
- The orchestrator should catch exceptions in any single step (e.g., AI failure) and allow the pipeline to continue or fail gracefully without crashing.
- Logs all major events and warnings using the `logging` module.

**Maintenance:**
- Update this directive whenever a new major step is added to the CLI or the output format changes.
