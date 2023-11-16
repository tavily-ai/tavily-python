import os
from openai import OpenAI
from tavily import TavilyClient

# Initialize clients with API keys
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

query = "Information about Nvidia (nvidia.com)"

print(f"Calling Tavily company retrieval with query: {query}...\n[Note]: Using 'advanced' may take up to 10 seconds.")
context = tavily_client.get_company_info(query=query, search_depth="advanced", max_results=7)

PROMPT = f"""
You are a business analyst tasked with collecting and summarizing company information and insights from a given context.
Anything between the following `context` html blocks is retrieved from a knowledge bank, and you MUST only use it to extract information.

<context>
    {context}
<context/>

Given the context above only, please extract and answer based on the following params:
- company_name: What is the company name?
- company_domain: What is the company's root site domain name?
- description: What does this company do?
- business_model: How does this company make money?
- financials: If company is public, information from recent reports and stock performance.
- recent_news: Recent news about the company
- leadership_team: The leadership team (C-levels eg, CEO CFO CTO etc).
- general_information: Any valuable or insightful information found in the context not yet mentioned.

You must answer short and concise without opening remarks.
REMEMBER: If there is no relevant information within the context for a given param, you must answer with "None". For example: company_name: None.
"""

print(f"Calling OpenAI to extract information...")
chat_completion = openai_client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": PROMPT,
        }
    ],
    temperature=0.4,
    max_tokens=4000,
    model="gpt-4-1106-preview",
)
print(chat_completion.choices[0].message.content)
