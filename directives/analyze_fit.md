# Directive: Analyze Fit

**Goal:**
Compare a candidate's resume against a job description to determine match quality and identify specific gaps.

**Inputs:**
- `job_description`: Full text of the job posting.
- `resume_text`: Full text of the candidate's resume.

**Tools/Scripts:**
- `execution/analyze_fit.py`: Python script orchestrating the AI call.
- `openai` (DeepSeek API): For qualitative analysis and scoring.

**Official Output Contract (single source of truth):**
Return a Python object (dict) with exactly these top-level fields:
- `match_score`: Integer (0-100).
- `fit_analysis`: JSON-formatted string that contains:
  - `matched_skills`: Bullet points of skills found in the resume.
  - `gap_analysis`: Bullet points of required skills missing from the resume.
  - `quick_pitch`: A short elevator pitch for the role.

> Note: `matched_skills`, `gap_analysis`, and `quick_pitch` are intentionally nested inside the `fit_analysis` JSON string, not returned as flat top-level fields.

**Final Output Payload Example:**
```json
{
  "match_score": 82,
  "fit_analysis": "{\"matched_skills\":\"- Python\\n- SQL\\n- Dashboarding\",\"gap_analysis\":\"- Kubernetes (not mentioned)\\n- Team leadership examples\",\"quick_pitch\":\"I bring strong analytics execution with Python and SQL, plus proven reporting impact. With minor upskilling in container tooling, I can ramp quickly and contribute to data-driven delivery from day one.\"}"
}
```

**Edge Cases:**
- *Empty inputs*: If either description or resume is missing, return `{"match_score": 0, "fit_analysis": "{\"error\": \"Missing input data\"}"}`.
- *AI failure*: Handle API errors gracefully, returning `match_score = 0` with an error object encoded in `fit_analysis`.
- *Large text*: Ensure input text fits within AI context limits (truncate if necessary, though unlikely for single resumes).

**Execution Steps:**
1. Receive job description and resume text.
2. Construct a prompt for the AI recruiter persona.
3. Call the DeepSeek API with `json_object` response format.
4. Parse AI JSON response.
5. Return top-level `match_score` plus serialized `fit_analysis` JSON string.
