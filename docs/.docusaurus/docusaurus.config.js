export default {
  "title": "Tavily AI",
  "tagline": "Tavily AI is the leading search engine optimized for LLMs",
  "url": "https://docs.tavily.com",
  "baseUrl": "/",
  "onBrokenLinks": "ignore",
  "onBrokenMarkdownLinks": "warn",
  "favicon": "img/favicon.ico",
  "organizationName": "tavily-ai",
  "trailingSlash": false,
  "projectName": "tavily-ai.github.io",
  "themeConfig": {
    "navbar": {
      "logo": {
        "alt": "Tavily",
        "src": "img/tavily.png"
      },
      "items": [
        {
          "type": "doc",
          "docId": "welcome",
          "position": "left",
          "label": "Docs"
        },
        {
          "to": "blog",
          "label": "Blog",
          "position": "left"
        },
        {
          "type": "doc",
          "docId": "faq",
          "position": "left",
          "label": "FAQ"
        },
        {
          "href": "https://app.tavily.com",
          "position": "right",
          "label": "Get API Key"
        },
        {
          "href": "mailto:support@tavily.com",
          "position": "left",
          "label": "Contact"
        },
        {
          "href": "https://github.com/assafelovic/gpt-researcher",
          "label": "GitHub",
          "position": "right"
        }
      ],
      "hideOnScroll": false
    },
    "footer": {
      "style": "dark",
      "links": [
        {
          "title": "Community",
          "items": [
            {
              "label": "Discord",
              "href": "https://discord.gg/8YkBcCED5y"
            },
            {
              "label": "Twitter",
              "href": "https://twitter.com/tavilyai"
            },
            {
              "label": "LinkedIn",
              "href": "https://www.linkedin.com/company/tavily/"
            }
          ]
        },
        {
          "title": "Company",
          "items": [
            {
              "label": "Homepage",
              "href": "https://tavily.com"
            },
            {
              "label": "Tavily Platform",
              "href": "https://tavily.com"
            },
            {
              "label": "Contact",
              "href": "mailto:support@tavily.com"
            }
          ]
        }
      ],
      "copyright": "Copyright © 2024 Tavily."
    },
    "colorMode": {
      "defaultMode": "light",
      "disableSwitch": false,
      "respectPrefersColorScheme": false,
      "switchConfig": {
        "darkIcon": "🌜",
        "darkIconStyle": {},
        "lightIcon": "🌞",
        "lightIconStyle": {}
      }
    },
    "docs": {
      "versionPersistence": "localStorage"
    },
    "metadata": [],
    "prism": {
      "additionalLanguages": []
    },
    "hideableSidebar": false,
    "tableOfContents": {
      "minHeadingLevel": 2,
      "maxHeadingLevel": 3
    }
  },
  "presets": [
    [
      "@docusaurus/preset-classic",
      {
        "docs": {
          "sidebarPath": "/mnt/c/Users/carlv/Projects/tavily/tavily-python/docs/sidebars.js",
          "editUrl": "https://github.com/tavily-ai/tavily-python/tree/master/docs",
          "remarkPlugins": [
            null
          ],
          "rehypePlugins": [
            null
          ]
        },
        "theme": {
          "customCss": "/mnt/c/Users/carlv/Projects/tavily/tavily-python/docs/src/css/custom.css"
        }
      }
    ]
  ],
  "stylesheets": [
    {
      "href": "https://cdn.jsdelivr.net/npm/katex@0.13.11/dist/katex.min.css",
      "integrity": "sha384-Um5gpz1odJg5Z4HAmzPtgZKdTBHZdw8S29IecapCSB31ligYPhHQZMIlWLYQGVoc",
      "crossorigin": "anonymous"
    }
  ],
  "plugins": [
    [
      "/mnt/c/Users/carlv/Projects/tavily/tavily-python/docs/node_modules/@easyops-cn/docusaurus-search-local/dist/server/server/index.js",
      {
        "hashed": true,
        "blogDir": "./blog/"
      }
    ]
  ],
  "baseUrlIssueBanner": true,
  "i18n": {
    "defaultLocale": "en",
    "locales": [
      "en"
    ],
    "localeConfigs": {}
  },
  "onDuplicateRoutes": "warn",
  "customFields": {},
  "themes": [],
  "titleDelimiter": "|",
  "noIndex": false
};