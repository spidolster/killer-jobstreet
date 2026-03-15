import os
import logging
from openai import AsyncOpenAI  # Using OpenAI SDK to interact with DeepSeek API


async def tailor_resume(resume_text: str, job_description: str, fit_analysis: str) -> str:
    """
    Generates a tailored resume based on the original resume, the target job description,
    and the gap analysis from the fit analysis step.
    
    The original resume is used as the factual basis — no experience is fabricated.
    Returns the tailored resume as a plain text string.
    """
    if not resume_text or not job_description:
        logging.warning("Missing resume or job description for tailoring.")
        return resume_text  # Return original if inputs are missing

    logging.info("Starting resume tailoring...")

    try:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

        if not api_key:
            logging.error("DEEPSEEK_API_KEY is not set in .env")
            return resume_text

        client = AsyncOpenAI(api_key=api_key, base_url=base_url)

        prompt = f"""
You are a very competent career coach, CV and resume consultant. You help people get their dream job.

Here is the candidate's ORIGINAL RESUME (this is the factual basis — do NOT invent or fabricate any new experience, education, or certifications):
{resume_text}

Here is the TARGET JOB DESCRIPTION the candidate is applying for:
{job_description}

Here is the FIT / GAP ANALYSIS showing what matches and what's missing:
{fit_analysis}

=== YOUR TASK ===
Rewrite the resume to be optimally tailored for this specific job. Follow these rules strictly:

1. DO NOT fabricate any experience, skills, education, or certifications that are not in the original resume.
2. Reorder sections and bullet points to lead with the most relevant experience for this role.
3. Rephrase existing bullet points to use keywords and terminology from the job description where truthful.
4. For skills identified as gaps, highlight any transferable skills or adjacent experience from the original resume.
5. Add a tailored Professional Summary / Objective at the top, customized for this position.
6. Keep the resume professional, concise, and well-structured.
7. Write the resume in the same language as the job description.
8. Output ONLY the final resume text. No commentary, no explanations, no markdown formatting.
"""

        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert resume writer. Output only the final tailored resume text without any commentary or formatting markers."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            response_format={"type": "text"}
        )

        result_content = response.choices[0].message.content.strip()
        logging.info("Resume tailoring completed successfully.")
        return result_content

    except Exception as e:
        logging.error(f"Error during AI resume tailoring: {e}")
        return resume_text  # Fall back to original resume on error
