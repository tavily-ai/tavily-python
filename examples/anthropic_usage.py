"""
Minimal example showing how to forward Tavily credit usage data into an Anthropic workflow.

Requires: pip install anthropic tavily-python
"""

import os
from anthropic import Anthropic
from tavily import TavilyClient


anthropic_client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


def tavily_search_with_usage(query: str) -> dict:
    """
    Runs a Tavily search with include_usage enabled so we can forward credit data.
    """
    return tavily_client.search(
        query=query,
        search_depth="advanced",
        include_usage=True,
        max_results=6,
        include_answer="advanced",
    )


def build_prompt(question: str, tavily_response: dict) -> str:
    usage = tavily_response.get("usage", {})
    usage_note = (
        f"Tavily usage may still read 0 until thresholds hit. Current usage payload: {usage}"
    )
    snippets = []
    for result in tavily_response.get("results", []):
        snippets.append(f"- {result['title']}: {result['content'][:200]}...")
    snippets_text = "\n".join(snippets)

    return (
        f"Answer the following question with the provided Tavily snippets only.\n"
        f"Question: {question}\n\n"
        f"Tavily snippets:\n{snippets_text}\n\n"
        f"{usage_note}"
    )


def ask_claude(question: str):
    tavily_payload = tavily_search_with_usage(question)
    prompt = build_prompt(question, tavily_payload)

    response = anthropic_client.messages.create(
        model="claude-3-sonnet-20240229",
        max_output_tokens=400,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    print("Claude answer:")
    print(response.content[0].text)
    print("\nTavily credit usage payload:", tavily_payload.get("usage"))


if __name__ == "__main__":
    ask_claude("Summarize the latest AI regulation updates in the EU.")
