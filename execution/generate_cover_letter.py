import os
import logging
from openai import AsyncOpenAI

async def generate_cover_letter(job_title: str, company_name: str, company_profile: str, job_description: str, resume_text: str) -> str:
    """
    Generates a tailored cover letter using DeepSeek AI.
    Returns the generated cover letter as a string.
    """
    if not job_description or not resume_text:
        logging.warning("Missing job description or resume text for cover letter generation.")
        return "Error: Missing input data for cover letter generation."

    logging.info("Starting cover letter generation...")
    
    try:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

        if not api_key:
            logging.error("DEEPSEEK_API_KEY is not set in .env")
            return "Error: DeepSeek API key missing in environment variables."

        client = AsyncOpenAI(api_key=api_key, base_url=base_url)

        prompt = f"""
You are a very competent career coach, CV and resume consultant. You help people get their dream job.
You will help me with my job application.

Company Name:
{company_name}

Company profile(based on research):
{company_profile}

Applied Position:
{job_title}

Job description:
{job_description}

this is my resume:
{resume_text}

Please help me with this task:
Create a cover letter for this job, suitable for the applied job level, in language of the job description.
Do not wrap it in markdown block quotes or prepend unnecessary text; output just the cover letter content.
"""

        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a professional cover letter writer. Output only the final cover letter text without additional commentary."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # Slightly higher than fit_analysis for natural text wording
            response_format={ "type": "text" }
        )
        
        result_content = response.choices[0].message.content.strip()
        return result_content

    except Exception as e:
        logging.error(f"Error during AI cover letter generation: {e}")
        return f"Error generation cover letter: {str(e)}"
