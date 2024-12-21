/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

 module.exports = {
  docsSidebar: [
    'welcome',
    {
      type: 'category',
      label: 'Python SDK',
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: 'category',
          label: 'Tavily Search',
          items: [
            {
              type: 'doc',
              id: 'python-sdk/tavily-search/getting-started',
              label: 'Getting Started',
            },
            'python-sdk/tavily-search/api-reference',
            'python-sdk/tavily-search/examples',
          ],
        },
        {
          type: 'category',
          label: 'Tavily Extract (beta)',
          items: [
             {
              type: 'doc',
              id: 'python-sdk/tavily-extract/getting-started',
              label: 'Getting Started',
             },
            'python-sdk/tavily-extract/api-reference',
            'python-sdk/tavily-extract/examples',
          ],
        },
        {
          type: 'category',
          label: 'Tavily Hybrid RAG (beta)',
          items: [
             {
              type: 'doc',
              id: 'python-sdk/tavily-hybrid-rag/getting-started',
              label: 'Getting Started',
             },
            'python-sdk/tavily-hybrid-rag/api-reference',
            'python-sdk/tavily-hybrid-rag/examples',
          ],
        }
      ],
    },
    {
      type: 'category',
      label: 'REST API',
      collapsible: true,
      collapsed: true,
      items: [
        'rest-api/api-reference',
        'rest-api/examples',
      ],
    },
    {
      type: 'category',
      label: 'JavaScript SDK (Beta)',
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: 'category',
          label: 'Tavily Search',
          items: [
            {
              type: 'doc',
              id: 'javascript-sdk/tavily-search/getting-started',
              label: 'Getting Started',
            },
            'javascript-sdk/tavily-search/api-reference',
            // 'javascript-sdk/tavily-search/examples',
          ],
        },
        {
          type: 'category',
          label: 'Tavily Extract',
          items: [
            {
              type: 'doc',
              id: 'javascript-sdk/tavily-extract/getting-started',
              label: 'Getting Started',
            },
            'javascript-sdk/tavily-extract/api-reference',
            // 'javascript-sdk/tavily-extract/examples',
          ],
        },
      ],
    },
    {
      type: 'category',
      label: 'Integrations',
      collapsible: true,
      collapsed: true,
      items: [
        'integrations/langchain',
        'integrations/llamaindex',
        'integrations/zapier',

      ],
    },
    {
      type: 'category',
      label: 'Use Cases',
      collapsible: true,
      collapsed: true,
      items: [
        'use-cases/data-enrichment/data-enrichment',
        'use-cases/company-research/company-research',
      ],
    },
    {
      type: 'category',
      label: 'GPT Researcher',
      collapsible: true,
      collapsed: true,
      items: [
        'gpt-researcher/introduction',
        'gpt-researcher/getting-started',
        'gpt-researcher/config',
        'gpt-researcher/example',
        'gpt-researcher/tailored-research',
        'gpt-researcher/agent_frameworks',
        'gpt-researcher/pip-package',
        'gpt-researcher/troubleshooting',
      ],
    },
  ],
  // pydoc-markdown auto-generated markdowns from docstrings
  // referenceSideBar: [require("./docs/reference/sidebar.json")]
};