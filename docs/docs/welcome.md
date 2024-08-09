# Introduction

Hey there! 👋

We're a team of AI researchers and developers who are passionate about helping you build the next generation of AI assistants. 
Our mission is to empower individuals and organizations with accurate, unbiased, and factual information.

## Tavily Search API
Building an AI agent that leverages realtime online information is not a simple task. Scraping doesn't scale and requires expertise to refine, current search engine APIs don't provide explicit information to queries but simply potential related articles (which are not always related), and are not very customziable for AI agent needs. This is why we're excited to introduce the first search engine for AI agents - **Tavily Search API**.

Tavily Search API is a search engine optimized for LLMs, aimed at efficient, quick and persistent search results. Unlike other search APIs such as Serp or Google, Tavily focuses on optimizing search for AI developers and autonomous AI agents. We take care of all the burden of searching, scraping, filtering and extracting the most relevant information from online sources. All in a single API call! 

To try the API in action, you can now use our hosted version on our [API Playground](https://app.tavily.com/playground).

If you're an AI developer looking to integrate your application with our API, or seek increased API limits, [please reach out!](mailto:support@tavily.com)


## Why choose the Tavily Search API?

1. **Purpose-Built**: Tailored just for LLM Agents, we ensure the search results are optimized for [RAG](https://towardsdatascience.com/retrieval-augmented-generation-intuitively-and-exhaustively-explain-6a39d6fe6fc9). We take care of all the burden in searching, scraping, filtering and extracting information from online sources. All in a single API call! Simply pass the returned search results as context to your LLM.
2. **Versatility**: Beyond just fetching results, Tavily Search API offers precision. With customizable search depths, domain management, and parsing HTML content controls, you're in the driver's seat.
3. **Performance**: Committed to speed and efficiency, our API guarantees real-time and trusted information. Our team works hard to improve Tavily's performance over time.
4. **Integration-friendly**: We appreciate the essence of adaptability. That's why integrating our API with your existing setup is a breeze. You can choose our Python library or a simple API call or any of our supported partners such as [Langchain](https://python.langchain.com/docs/integrations/tools/tavily_search) and [LLamaIndex](https://docs.llamaindex.ai/en/stable/api_reference/tools/tavily_research/).
5. **Transparent & Informative**: Our detailed documentation ensures you're never left in the dark. From setup basics to nuanced features, we've got you covered.

## How does the Search API work?
Current search APIs such as Google, Serp and Bing retrieve search results based on user query. However, the results are sometimes irrelevant to the goal of the search, and return simple site URLs and snippets of content which are not always relevant. Because of this, any developer would need to then scrape the sites to extract relevant content, filter irrelevant information, optimize the content to fit LLM context limits, and more. This task is a burden and requires a lot of time and effort to complete. The Tavily Search API takes care of all of this for you in a single API call.

Tavily Search API aggregates up to 20 sites per a single API call, and uses proprietary AI to score, filter and rank the top most relevant sources and content to your task, query or goal. 
In addition, Tavily allows developers to add custom fields such as context and limit response tokens to enable the optimal search experience for LLMs.

Tavily can also help your AI agent make better decisions by including a short answer for cross-agent communication.

Remember: With LLM hallucinations, it's crucial to optimize for RAG with the right context and information.

## Getting started
1. **Sign Up**: Begin by [signing up](https://app.tavily.com) on our platform.
2. **Obtain Your API Key**: Once registered, we will generate a Tavily API Key for you. You will also be able to generate additional keys.
3. **Test Drive in the API Playground**: Before diving in, familiarize yourself by testing out endpoints in our interactive [API playground](https://app.tavily.com/playground). 
4. **Explore & Learn**: Dive into our [Python SDK](/docs/python-sdk/getting-started) or [REST API](/docs/rest-api/api-reference) documentation to get familiar with the various features. The documentation offers a comprehensive rundown of functionalities, supplemented with practical sample inputs and outputs.
5. **Sample Use**: Check out our [Python examples](/docs/python-sdk/examples) page to see some code snippets showing you what you can accomplish with Tavily in only a few lines of code. Want a real-world application? Check out our [Research Assistant](https://app.tavily.com/chat) — a prime example that showcases how the API can optimize your AI content generation with factual and unbiased results.
6. **Stay up to date**: Join our [Community](https://community.tavily.com) to get latest updates on our continuous improvements and development

🙋‍♂️ Got questions? Stumbled upon an issue? Or simply intrigued? Don't hesitate! Our support team is always on standby, eager to assist. Join us, dive deep, and redefine your search experience! **[Contact us!](mailto:support@tavily.com)**


## GPT Researcher
In this digital age, quickly accessing relevant and trustworthy information is more crucial than ever. However, we've learned that none of today's search engines provide a suitable tool that provides factual, explicit and objective answers without the need to continuously click and explore multiple sites for a given research task. 

This is why we've built the trending open source **[GPT Researcher](https://github.com/assafelovic/gpt-researcher)**. GPT Researcher is an autonomous agent that takes care of the tedious task of research for you, by scraping, filtering and aggregating over 20+ web sources per a single research task. 

To learn more about GPT Researcher, check out the [documentation page](/docs/gpt-researcher/introduction).
