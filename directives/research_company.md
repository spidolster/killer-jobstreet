# Directive: Research Company

**Goal:**
Automatically research a company's background, products/services, and culture based on its name, and provide a concise bullet-point summary.

**Inputs:**
- `company_name`: The name of the company to research (extacted from JobStreet).

**Tools/Scripts:**
- `execution/research_company.py`: Python script containing the logic.
- `duckduckgo-search`: For fetching text snippets about the company from the web.
- `openai` (DeepSeek API): For summarizing the text snippets into a structured bulleted list.

**Outputs:**
- A Markdown-formatted string containing bullet points summarizing the company.

**Edge Cases:**
- *Company not found/Unknown*: If the extracted company name is invalid, skip the research and return a default message.
- *Search fails*: If DuckDuckGo search errors out or returns no results, return a message indicating no information could be retrieved.
- *AI API limits/errors*: If DeepSeek rate limits or fails, return the error message gracefully.

**Execution Steps (for Orchestrator):**
1. Extract the `company` name from the job source.
2. Call `research_company(company_name)` from `execution.research_company`.
3. Append the resulting Markdown output to the final Job document.
