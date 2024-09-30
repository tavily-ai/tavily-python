# Getting Started with Tavily Search
Tavily.js allows for easy interaction with the Tavily API, offering the full range of our search and extract functionalities directly from your JavaScript and TypeScript programs. Easily integrate smart search and content extraction capabilities into your applications, harnessing Tavily's powerful search and extract features.

## Installing
```bash
npm i @tavily/core
```

# Tavily Search
Connect your LLM to the web using the Tavily Search API.

## Usage
Below are some code snippets that show you how to interact with our search API. The different steps and components of this code are explained in more detail on the JavaScript [API Reference](/docs/javascript-sdk/tavily-search/api-reference) page.

### Getting and printing the full Search API response

```javascript
const { tavily } = require("@tavily/core");

// Step 1. Instantiating your Tavily client
const tvly = tavily({ apiKey: "tvly-YOUR_API_KEY" });

// Step 2. Executing a simple search query
const response = await tvly.search("Who is Leo Messi?");

// Step 3. That's it! You've done a Tavily Search!
console.log(response);
```
This is equivalent to directly querying our REST API.


### Generating context for a RAG Application

```javascript
const { tavily } = require("@tavily/core");

// Step 1. Instantiating your Tavily client
const tvly = tavily({ apiKey: "tvly-YOUR_API_KEY" });

// Step 2. Executing a context search query
const context = tvly.searchContext("What happened during the Burning Man floods?");

// Step 3. That's it! You now have a context string that you can feed directly into your RAG Application
console.log(response);
```
This is how you can generate precise and fact-based context for your RAG application in one line of code.

### Getting a quick answer to a question
```javascript
const { tavily } = require("@tavily/core");

// Step 1. Instantiating your Tavily client
const tvly = tavily({ apiKey: "tvly-YOUR_API_KEY" });

// Step 2. Executing a Q&A search query
const answer = tvly.searchQNA("Who is Leo Messi?");

// Step 3. That's it! Your question has been answered!
console.log(answer);
```
This is how you get accurate and concise answers to questions, in one line of code. Perfect for usage by LLMs!