# Getting Started

> We're excited to announce the release of the Tavily Hybrid RAG feature in version 0.3.7 of our Python package! We're looking forward to seeing what you build with it! Please note that this feature is still in beta. If you encounter any bugs, please report them to support@tavily.com.

Tavily Hybrid RAG is an extension of the Tavily Search API built to retrieve relevant data from both the web and an existing database collection. This way, a RAG agent can combine web sources and locally available data to perform its tasks. Additionally, data queried from the web that is not yet in the database can optionally be inserted into it. This will allow similar searches in the future to be answered faster, without the need to query the web again.

## 📦 Installing
You'll need to [install our Python package](/docs/python-sdk/getting-started), as well as a Python database client. Currently, we only support MongoDB through [PyMongo](https://pypi.org/project/pymongo/).

## 🛠️ Setup

### MongoDB setup
You will need to have a MongoDB collection with a vector search index. You can follow the [MongoDB Documentation](https://www.mongodb.com/docs/atlas/atlas-vector-search/vector-search-type/) to learn how to set this up.

### Cohere API Key
By default, embedding and ranking use the Cohere API, our recommended option. Unless you want to provide a custom embedding and ranking function, you'll need to get an API key from [Cohere](https://cohere.ai/) and set it as an environment variable named `CO_API_KEY`.

If you decide to stick with Cohere, please note that you'll need to install the Cohere Python package as well:
```bash
pip install cohere
```

### Tavily Hybrid RAG Client setup
Once you are done setting up your database, you'll need to create a MongoDB Client as well as a Tavily Hybrid RAG Client.

A minimal setup would look like this:
```python
from pymongo import MongoClient
from tavily import TavilyHybridClient

db = MongoClient("mongodb+srv://YOUR_MONGO_URI")["YOUR_DB"]

hybrid_rag = TavilyHybridClient(
    api_key="tvly-YOUR_API_KEY",
    db_provider="mongodb",
    collection=db.get_collection("YOUR_COLLECTION"),
    index="YOUR_VECTOR_SEARCH_INDEX",
    embeddings_field="YOUR_EMBEDDINGS_FIELD",
    content_field="YOUR_CONTENT_FIELD"
)
```

Each of these parameters are explained more in detail in the [Tavily Hybrid RAG API Reference](/docs/python-sdk/tavily-hybrid-rag/api-reference)


##  Usage

Once you create the proper clients, you can easily start searching. A few simple examples are shown below. They assume you've followed earlier steps. You can use most of the Tavily Search parameters with Tavily Hybrid RAG as well.

### Simple Tavily Hybrid RAG example
This example will look for context about Leo Messi on the web and in the local database.

Here, we get 5 sources, both from our database and from the web, but we want to exclude `unwanted-domain.com` from our web search results:
```python
results = hybrid_rag.search("Who is Leo Messi?", max_results=5, exclude_domains=['unwanted-domain.com'])
```

Here, we want to prioritize the number of local sources, so we will get 2 foreign (web) sources, and 5 sources from our database:
```python
results = hybrid_rag.search("Who is Leo Messi?",  max_local=5, max_foreign=2)
```
Note: The sum of `max_local` and `max_foreign` can exceed `max_results`, but only the top `max_results` results will be returned.


### Adding retrieved data to the database
If you want to add the retrieved data to the database, you can do so by setting the `save_foreign` parameter to `True`:
```python
results = hybrid_rag.search("Who is Leo Messi?", save_foreign=True)
```
This will use our default saving function, which stores the content and its embedding.
