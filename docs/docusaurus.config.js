/** @type {import('@docusaurus/types').DocusaurusConfig} */
const math = require('remark-math');
const katex = require('rehype-katex');

module.exports = {
  title: 'Tavily AI',
  tagline: 'Tavily AI is the leading search engine optimized for LLMs',
  url: 'https://docs.tavily.com',
  baseUrl: '/',
  onBrokenLinks: 'ignore',
  //deploymentBranch: 'master',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',
  organizationName: 'tavily-ai',
  trailingSlash: false,
  projectName: 'tavily-python',
  themeConfig: {
    navbar: {
      //title: 'Tavily',
      logo: {
        alt: 'Tavily',
        src: 'img/tavily.png',
        srcDark: 'img/tavily-dark.png'
      },
      items: [
        {
          type: 'doc',
          docId: 'welcome',
          position: 'left',
          label: 'Docs',
        },

        // {to: 'blog', label: 'Blog', position: 'left'},
        {
          type: 'doc',
          docId: 'faq',
          position: 'left',
          label: 'FAQ',
        },
        {
          href: 'https://community.tavily.com',
          label: 'Developer Community',
          position: 'left',
        },
        {
          href: 'mailto:support@tavily.com',
          position: 'right',
          label: 'Contact',
        },
        {
            href: 'https://app.tavily.com',
            position: 'right',
            label: 'Get API Key',
        },

      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Community',
          items: [
            {
              label: 'Developer Community',
              href: 'https://community.tavily.com',
            },
            {
              label: 'Twitter',
              href: 'https://twitter.com/tavilyai',
            },
            {
              label: 'LinkedIn',
              href: 'https://www.linkedin.com/company/tavily/',
            },
          ],
        },
        {
          title: 'Company',
          items: [
            {
              label: 'Homepage',
              href: 'https://tavily.com',
            },
            {
              label: 'Tavily Platform',
              href: 'https://tavily.com',
            },
            {
              label: 'Contact',
              href: 'mailto:support@tavily.com',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Tavily.`,
    },
  },
  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          // Please change this to your repo.
          editUrl:
            'https://github.com/tavily-ai/tavily-python/tree/master/docs',
          remarkPlugins: [math],
          rehypePlugins: [katex],
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
  stylesheets: [
    {
        href: "https://cdn.jsdelivr.net/npm/katex@0.13.11/dist/katex.min.css",
        integrity: "sha384-Um5gpz1odJg5Z4HAmzPtgZKdTBHZdw8S29IecapCSB31ligYPhHQZMIlWLYQGVoc",
        crossorigin: "anonymous",
    },
  ],

  plugins: [
    // ... Your other plugins.
    [
      require.resolve("@easyops-cn/docusaurus-search-local"),
      {
        // ... Your options.
        // `hashed` is recommended as long-term-cache of index file is possible.
        hashed: true,
        blogDir:"./blog/"
        // For Docs using Chinese, The `language` is recommended to set to:
        // ```
        // language: ["en", "zh"],
        // ```
        // When applying `zh` in language, please install `nodejieba` in your project.
      },
    ],
  ],
};
