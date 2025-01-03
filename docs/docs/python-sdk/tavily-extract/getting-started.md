# Getting Started with Tavily Extract

> We’re excited to announce the release of the Tavily Extract feature in version 0.5.0 of our Python package! This feature is still in beta, so please report any bugs or send feedback to [support@tavily.com](mailto:support@tavily.com). 

The Tavily Extract API allows you to effortlessly retrieve raw content from a list of websites, making it ideal for data collection, content analysis, and research. You can also combine Tavily Extract with our Search method: first, obtain a list of relevant documents, then perform further processing on selected links to gather additional information and use it as context for your research tasks.

Please note that for every 5 successful URL extractions, 1 API credit is deducted from your account. We look forward to seeing what you build with it!

## 📦 Installing
```bash
pip install tavily-python
```

## 🛠️ Usage
Below are some code snippets demonstrating how to interact with the Tavily Extract API. The different steps and components of this code are explained in more detail on the Python [API Reference](/docs/python-sdk/tavily-extract/api-reference) page.

### Extracting Raw Content from Multiple URLs

```python
from tavily import TavilyClient

# Step 1. Instantiating your TavilyClient
tavily_client = TavilyClient(api_key="tvly-YOUR_API_KEY")

# Step 2. Defining the list of URLs to extract content from
urls = [
    "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "https://en.wikipedia.org/wiki/Machine_learning",
    "https://en.wikipedia.org/wiki/Data_science",
    "https://en.wikipedia.org/wiki/Quantum_computing",
    "https://en.wikipedia.org/wiki/Climate_change"
]

# Step 3. Executing the extract request
response = tavily_client.extract(urls=urls, include_images=True)

# Step 4. Printing the extracted raw content
for result in response["results"]:
    print(f"URL: {result['url']}")
    print(f"Raw Content: {result['raw_content']}")
    print(f"Images: {result['images']}\n")

# Note that URLs that could not be extracted will be stored in response["failed_results"]
```
This example demonstrates how to extract raw content from multiple URLs using the Tavily Extract API. You can retrieve content from up to 20 URLs simultaneously.

## 📝 License

This project is licensed under the terms of the MIT license.

## 💌 Contact

If you are encountering issues while using Tavily, please email us at [support@tavily.com](mailto:support@tavily.com). We'll be happy to help you.

If you want to stay updated on the latest Tavily news and releases, head to our [Developer Community](https://community.tavily.com) to learn more!