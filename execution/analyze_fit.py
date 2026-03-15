import os
import logging
import json
from openai import AsyncOpenAI  # Using OpenAI SDK to interact with DeepSeek API

async def analyze_fit(job_description: str, resume_text: str) -> dict:
    """
    Analyzes the fit between a job description and a resume using DeepSeek AI.
    Returns a dictionary containing:
    - match_score: int (0-100)
    - fit_analysis: str (JSON string of matched_skills, gap_analysis, and pitch)
    """
    if not job_description or not resume_text:
        logging.warning("Missing job description or resume text for fit analysis.")
        return {"match_score": 0, "fit_analysis": '{"error": "Missing input data"}'}

    logging.info("Starting fit analysis...")
    
    try:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

        if not api_key:
            logging.error("DEEPSEEK_API_KEY is not set in .env")
            return {"match_score": 0, "fit_analysis": '{"error": "DeepSeek API key missing"}'}

        prompt = f"""
You are an expert technical recruiter and career coach.
Analyze the following Job Description against the provided Resume.

=== JOB DESCRIPTION ===
{job_description}

=== RESUME ===
{resume_text}

=== INSTRUCTIONS ===
Provide your analysis STRICTLY as a valid JSON object with the following keys exactly as written, and no other keys or markdown formatting:
"match_score": An integer from 0 to 100 representing how well the resume fits the job requirements.
"matched_skills": A brief bulleted list (as a single string) of skills in the resume that match the job requirements.
"gap_analysis": A brief bulleted list (as a single string) of critical job requirements missing from the resume.
"quick_pitch": A 2-3 sentence elevator pitch tailored to this specific job based on the resume.

Example JSON:
{{
  "match_score": 85,
  "matched_skills": "- Python\\n- SQL\\n- Data Analysis",
  "gap_analysis": "- Kubernetes (not mentioned)\\n- Scala",
  "quick_pitch": "As a Senior Data Analyst with over a decade of experience, I excel in SQL and Python. I have a proven track record of optimizing operations and would bring immediate value to this role."
}}
"""

        async with AsyncOpenAI(api_key=api_key, base_url=base_url) as client:
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a JSON-producing career analysis engine. Output only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={ "type": "json_object" }
            )
        
        result_content = response.choices[0].message.content.strip()
        
        try:
            analysis_dict = json.loads(result_content)
        except json.JSONDecodeError:
            logging.error("Failed to parse JSON from AI response: " + result_content)
            return {
                "match_score": 0, 
                "fit_analysis": json.dumps({"error": "Failed to parse AI response", "raw_response": result_content})
            }
            
        match_score = analysis_dict.get("match_score", 0)
        
        # Ensure match_score is an integer
        try:
            match_score = int(match_score)
        except (ValueError, TypeError):
            match_score = 0
            
        # Extract the text analysis parts
        fit_data = {
            "matched_skills": analysis_dict.get("matched_skills", "N/A"),
            "gap_analysis": analysis_dict.get("gap_analysis", "N/A"),
            "quick_pitch": analysis_dict.get("quick_pitch", "N/A")
        }

        return {
            "match_score": match_score,
            "fit_analysis": json.dumps(fit_data)
        }

    except Exception as e:
        logging.error(f"Error during AI fit analysis: {e}")
        return {"match_score": 0, "fit_analysis": json.dumps({"error": str(e)})}
