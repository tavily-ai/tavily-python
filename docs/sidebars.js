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
        'python-sdk/getting-started',
        'python-sdk/api-reference',
        'python-sdk/examples',
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
      label: 'Integrations',
      collapsible: true,
      collapsed: true,
      items: [
        'integrations/langchain',
        'integrations/llamaindex',
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
  referenceSideBar: [require("./docs/reference/sidebar.json")]
};
