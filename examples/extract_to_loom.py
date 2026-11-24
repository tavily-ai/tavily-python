"""Save Markdown from Tavily Extract as a cited document in Loom."""

import argparse
import os

import requests

from tavily import TavilyClient


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Public page to extract")
    args = parser.parse_args()

    loom_url = os.environ["LOOM_BASE_URL"].rstrip("/")
    org = os.environ["LOOM_ORG"]
    namespace = os.environ["LOOM_NAMESPACE"]
    token = os.environ["LOOM_WRITER_TOKEN"]

    result = TavilyClient(api_key=os.getenv("TAVILY_API_KEY")).extract(
        urls=[args.url], format="markdown"
    )
    pages = result["results"]
    if not pages or not (pages[0].get("raw_content") or "").strip():
        parser.exit(1, "Tavily returned no Markdown for that URL.\n")

    page = pages[0]
    response = requests.post(
        f"{loom_url}/v1/knowledge.upsert",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "org": org,
            "namespace": namespace,
            "source_uri": page["url"],
            "content": page["raw_content"],
            "source_class": "external",
        },
        timeout=60,
        allow_redirects=False,
    )
    if not 200 <= response.status_code < 300:
        parser.exit(1, f"Loom returned HTTP {response.status_code}.\n")
    receipt = response.json()
    print(f"Saved {receipt['source_uri']} ({receipt['chunks_created']} chunks)")


if __name__ == "__main__":
    main()
