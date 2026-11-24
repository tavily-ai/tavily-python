# Save a page to Loom

[ClickHouse Loom](https://github.com/ClickHouse/loom) indexes extracted text for later search. This example extracts a public page with Tavily and saves its Markdown under the source URL so search results can cite the page. Running it again with the same returned URL updates the document in that namespace.

Set `LOOM_BASE_URL` to your Loom server's HTTPS origin, `LOOM_ORG` and `LOOM_NAMESPACE` to the destination, and `LOOM_WRITER_TOKEN` to a writer token scoped to that namespace. Set `TAVILY_API_KEY` to use your Tavily account or leave it unset for keyless extraction.

Install the SDK and run the example from the repository root.

```sh
pip install tavily-python
python examples/extract_to_loom.py https://docs.tavily.com/documentation/api-reference/endpoint/extract
```

The script prints the saved source URL and the number of chunks. Search the destination namespace in Loom for a phrase from the page and check that the result cites that URL.
