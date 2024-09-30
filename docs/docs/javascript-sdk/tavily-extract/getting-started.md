# Getting Started with Tavily Extract

> We’re excited to announce the release of the Tavily Extract feature! This feature is still in beta, so please report any bugs or send feedback to [support@tavily.com](mailto:support@tavily.com). 

The Tavily Extract API allows you to effortlessly retrieve raw content from a list of websites, making it ideal for data collection, content analysis, and research. You can also combine Tavily Extract with our Search method: first, obtain a list of relevant documents, then perform further processing on selected links to gather additional information and use it as context for your research tasks.

Please note that for every 5 successful URL extractions, 1 API credit is deducted from your account. We look forward to seeing what you build with it!

## 📦 Installing
```bash
npm i @tavily/core
```


## 🛠️ Usage
Below are some code snippets demonstrating how to interact with the Tavily Extract API. The different steps and components of this code are explained in more detail on the JavaScript [API Reference](/docs/javascript-sdk/tavily-extract/api-reference) page.

### Extracting Raw Content from Multiple URLs using Tavily Extract API

```javascript
const { tavily } = require("@tavily/core");

// Step 1. Instantiating your TavilyClient
const tvly = tavily({ apiKey: "tvly-YOUR_API_KEY" });

// Step 2. Defining the list of URLs to extract content from
const urls = [
    "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "https://en.wikipedia.org/wiki/Machine_learning",
    "https://en.wikipedia.org/wiki/Data_science",
    "https://en.wikipedia.org/wiki/Quantum_computing",
    "https://en.wikipedia.org/wiki/Climate_change"
] // You can provide up to 20 URLs simultaneously

// Step 3. Executing the extract request
response = await tvly.extract(urls)

// Step 4. Printing the extracted raw content
for (let result of response.results) {
    console.log(`URL: ${result['url']}`)
    console.log(`Raw Content: ${result['raw_content']}\n`)
}
// Note that URLs that could not be extracted will be stored in response.failedResults
```

## 📝 License

This project is licensed under the terms of the MIT license.

## 💌 Contact

If you are encountering issues while using Tavily, please email us at [support@tavily.com](mailto:support@tavily.com). We'll be happy to help you.

If you want to stay updated on the latest Tavily news and releases, head to our [Developer Community](https://community.tavily.com) to learn more!