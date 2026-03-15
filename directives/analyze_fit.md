# Directive: Analyze Fit

**Goal:**
Compare a candidate's resume against a job description to determine match quality and identify specific gaps.

**Inputs:**
- `job_description`: Full text of the job posting.
- `resume_text`: Full text of the candidate's resume.

**Tools/Scripts:**
- `execution/analyze_fit.py`: Python script orchestrating the AI call.
- `openai` (DeepSeek API): For qualitative analysis and scoring.

**Outputs:**
- A JSON-formatted string containing:
    - `match_score`: Integer (0-100).
    - `matched_skills`: Bullet points of skills found in the resume.
    - `gap_analysis`: Bullet points of required skills missing from the resume.
    - `quick_pitch`: A short elevator pitch for the role.

**Edge Cases:**
- *Empty inputs*: If either description or resume is missing, return a score of 0 and an error message.
- *AI failure*: Handle API errors gracefully, returning a default "analysis unavailable" structure.
- *Large text*: Ensure input text fits within AI context limits (truncate if necessary, though unlikely for single resumes).

**Execution Steps:**
1. Receive job description and resume text.
2. Construct a prompt for the AI recruiter persona.
3. Call the DeepSeek API with `json_object` response format.
4. Parse and return the resulting JSON.
