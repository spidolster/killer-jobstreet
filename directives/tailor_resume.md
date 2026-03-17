# Directive: Tailor Resume

**Goal:**
Rewrite the candidate's base resume to better align with a specific job description, without fabricating any factual information.

**Inputs:**
- `resume_text`: The candidate's original base resume.
- `job_description`: The target job description.
- `fit_analysis`: The output from the "Analyze Fit" step (to focus on addressing gaps).

**Tools/Scripts:**
- `execution/tailor_resume.py`: Python script for AI-powered rewriting.
- `openai` (DeepSeek API).

**Outputs:**
- A Markdown-formatted string containing the rewritten, job-optimized resume.

**Edge Cases:**
- *Significant Gaps*: If the candidate is clearly unqualified, the AI should still attempt to highlight transferable skills without lying.
- *Base Resume Missing*: Return the original or an error if the base resume is empty.
- *Language Mismatch*: The tailored resume should be written in the same language as the job description.

**Execution Steps:**
1. Check if the "Analyze Fit" step identified meaningful gaps.
2. If gaps exist, call the `tailor_resume` script.
3. Instruct the AI to use the original resume as the *only* factual source.
4. Prompt the AI to rephrase, reorder, and emphasize relevant skills.
5. Save the resulting text for use in the cover letter step and file output.
