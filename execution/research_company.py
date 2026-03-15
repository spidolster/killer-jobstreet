import os
import logging
from duckduckgo_search import DDGS
from openai import AsyncOpenAI  # Using OpenAI SDK to interact with DeepSeek API

async def research_company(company_name: str) -> str:
    """
    Researches a company using DuckDuckGo search and summarizes the findings using DeepSeek AI.
    """
    if not company_name or company_name.lower() in ["company not found", "unknown"]:
        return "Company information not available."

    logging.info(f"Starting research for company: {company_name}")
    
    # 1. Search with DuckDuckGo
    search_results_text = ""
    try:
        query = f"{company_name} company what they do products culture"
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=5)]
            if results:
                for idx, r in enumerate(results):
                    search_results_text += f"Result {idx+1}:\nTitle: {r.get('title', '')}\nSnippet: {r.get('body', '')}\n\n"
            else:
                logging.warning(f"DuckDuckGo returned no results for {company_name}")
    except Exception as e:
        logging.error(f"Error during DuckDuckGo search: {e}")

    if not search_results_text.strip():
        search_results_text = "No recent search results were found. Please describe this company based on your internal knowledge."

    # 2. Summarize with DeepSeek via OpenAI client
    try:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

        if not api_key:
            logging.error("DEEPSEEK_API_KEY is not set in .env")
            return "Error: DeepSeek API key is missing."

        client = AsyncOpenAI(api_key=api_key, base_url=base_url)

        prompt = f"""
Research results for the company '{company_name}':

{search_results_text}

Based on the above search results, provide a concise summary using bullet points about this company.
Focus on:
- What they are doing
- What they are known for
- Product/services they offer
- Company culture (if available)

Keep it very brief, objective, and strictly use bullet points.
"""

        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a concise business research assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=600
        )
        
        summary = response.choices[0].message.content.strip()
        return summary

    except Exception as e:
        logging.error(f"Error during AI summarization: {e}")
        return f"Error generating summary: {e}"
