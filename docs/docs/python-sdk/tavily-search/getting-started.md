# Getting Started with Tavily Search
The Python SDK allows for easy interaction with the Tavily API, offering the full range of our search functionality directly from your Python programs. Easily integrate smart search capabilities into your applications, harnessing Tavily's powerful search features.

## 📦 Installing

```bash
pip install tavily-python
```

## 🛠️ Usage
Below are some code snippets that show you how to interact with our API. The different steps and components of this code are explained in more detail on the Python [API Reference](/docs/python-sdk/tavily-search/api-reference) page.

### Getting and printing the full Search API response

```python
from tavily import TavilyClient

# Step 1. Instantiating your TavilyClient
tavily_client = TavilyClient(api_key="tvly-YOUR_API_KEY")

# Step 2. Executing a simple search query
response = tavily_client.search("Who is Leo Messi?")

# Step 3. That's it! You've done a Tavily Search!
print(result)
```
This is equivalent to directly querying our REST API.

### Generating context for a RAG Application

```python
from tavily import TavilyClient

# Step 1. Instantiating your TavilyClient
tavily_client = TavilyClient(api_key="tvly-YOUR_API_KEY")

# Step 2. Executing a context search query
context = tavily_client.get_search_context(query="What happened during the Burning Man floods?")

# Step 3. That's it! You now have a context string that you can feed directly into your RAG Application
print(context)
```
This is how you can generate precise and fact-based context for your RAG application in one line of code.

### Getting a quick answer to a question

```python
from tavily import TavilyClient

# Step 1. Instantiating your TavilyClient
tavily_client = TavilyClient(api_key="tvly-YOUR_API_KEY")

# Step 2. Executing a Q&A search query
answer = tavily_client.qna_search(query="Who is Leo Messi?")

# Step 3. That's it! Your question has been answered!
print(answer)
```
This is how you get accurate and concise answers to questions, in one line of code. Perfect for usage by LLMs!

This snippet shows you how to set up a Tavily Hybrid RAG Client and connect it to a MongoDB database to perform a simple Hybrid RAG query! For more information on how to set up your

## 📝 License

This project is licensed under the terms of the MIT license.

## 💌 Contact

If you are encountering issues while using Tavily, please email us at [support@tavily.com](mailto:support@tavily.com). We'll be happy to help you.

If you want to stay updated on the latest Tavily news and releases, head to our [Developer Community](https://community.tavily.com) to learn more!