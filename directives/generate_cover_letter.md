# Directive: Generate Cover Letter

**Goal:**
Produce a professional, tailored cover letter for a specific job application.

**Inputs:**
- `job_title`: The role being applied for.
- `company_name`: The hiring company.
- `company_profile`: The research summary from the "Research Company" step.
- `job_description`: The full job posting.
- `resume_text`: The candidate's resume (use the **tailored** version if generated).

**Tools/Scripts:**
- `execution/generate_cover_letter.py`: Python script for AI text generation.
- `openai` (DeepSeek API).

**Outputs:**
- A professional cover letter formatted in plain text or Markdown.

**Edge Cases:**
- *Missing Company Info*: Use a generic professional opening if the company name or profile is unavailable.
- *Job Level*: Ensure the tone is appropriate for the job level (Entry, Senior, Lead, etc.).
- *Defaulting*: If tailoring failed, fall back to the original resume for generation.

**Execution Steps:**
1. Assemble all context (job, company, tailored resume).
2. Construct a prompt for a "Career Coach/Consultant" persona.
3. Generate the letter via the DeepSeek API.
4. Return the clean text of the cover letter.
