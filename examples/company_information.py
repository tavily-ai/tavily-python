import os
import json
import time
from openai import OpenAI
from tavily import TavilyClient

# Initialize clients with API keys
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

query = "Information about Nvidia (nvidia.com)"
context = tavily_client.get_company_info(query=query, search_depth="advanced", max_results=5)
print(context)

PROMPT = f"""
You are a business analyst tasked with collecting and summarizing company information and insights.
Anything between the following `context` html blocks is retrieved from a knowledge bank, and you MUST only use it to extract information.

<context>
    {context}
<context/>

Given the context above only, please extract and answer based on the following params:
- company_name: What is the company name?
- company_domain: What is the company's site domain?
- description: What does this company do?
- business_model: How does this company make money?
- financials: If company is public, information from recent reports
- recent_news: Recent news about the company
- leadership_team: The leadership team (C-levels eg, CEO CFO CTO etc).
- general_information: Any valuable or insightful information found in the context not yet mentioned.

REMEMBER: If there is no relevant information within the context for a given param, just return "None". For example: company_name: None.
"""

chat_completion = openai_client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": PROMPT,
        }
    ],
    model="gpt-4-1106-preview",
)
print(chat_completion.choices[0].message.content)
