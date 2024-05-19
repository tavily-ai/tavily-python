
import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/blog',
    component: ComponentCreator('/blog','30c'),
    exact: true
  },
  {
    path: '/blog/archive',
    component: ComponentCreator('/blog/archive','f4c'),
    exact: true
  },
  {
    path: '/blog/building-gpt-researcher',
    component: ComponentCreator('/blog/building-gpt-researcher','dcf'),
    exact: true
  },
  {
    path: '/blog/building-openai-assistant',
    component: ComponentCreator('/blog/building-openai-assistant','7ba'),
    exact: true
  },
  {
    path: '/blog/tags',
    component: ComponentCreator('/blog/tags','e13'),
    exact: true
  },
  {
    path: '/blog/tags/assistant-api',
    component: ComponentCreator('/blog/tags/assistant-api','3c8'),
    exact: true
  },
  {
    path: '/blog/tags/autonomous-agent',
    component: ComponentCreator('/blog/tags/autonomous-agent','093'),
    exact: true
  },
  {
    path: '/blog/tags/github',
    component: ComponentCreator('/blog/tags/github','e38'),
    exact: true
  },
  {
    path: '/blog/tags/gpt-researcher',
    component: ComponentCreator('/blog/tags/gpt-researcher','d45'),
    exact: true
  },
  {
    path: '/blog/tags/openai',
    component: ComponentCreator('/blog/tags/openai','4e6'),
    exact: true
  },
  {
    path: '/blog/tags/opensource',
    component: ComponentCreator('/blog/tags/opensource','43b'),
    exact: true
  },
  {
    path: '/blog/tags/search-api',
    component: ComponentCreator('/blog/tags/search-api','cd3'),
    exact: true
  },
  {
    path: '/blog/tags/tavily',
    component: ComponentCreator('/blog/tags/tavily','ddb'),
    exact: true
  },
  {
    path: '/search',
    component: ComponentCreator('/search','79a'),
    exact: true
  },
  {
    path: '/docs',
    component: ComponentCreator('/docs','764'),
    routes: [
      {
        path: '/docs/contribute',
        component: ComponentCreator('/docs/contribute','e6a'),
        exact: true,
        'sidebar': "docsSidebar"
      },
      {
        path: '/docs/examples/examples',
        component: ComponentCreator('/docs/examples/examples','8df'),
        exact: true,
        'sidebar': "docsSidebar"
      },
      {
        path: '/docs/faq',
        component: ComponentCreator('/docs/faq','e60'),
        exact: true
      },
      {
        path: '/docs/gpt-researcher/agent_frameworks',
        component: ComponentCreator('/docs/gpt-researcher/agent_frameworks','774'),
        exact: true,
        'sidebar': "docsSidebar"
      },
      {
        path: '/docs/gpt-researcher/config',
        component: ComponentCreator('/docs/gpt-researcher/config','fdc'),
        exact: true,
        'sidebar': "docsSidebar"
      },
      {
        path: '/docs/gpt-researcher/example',
        component: ComponentCreator('/docs/gpt-researcher/example','b99'),
        exact: true,
        'sidebar': "docsSidebar"
      },
      {
        path: '/docs/gpt-researcher/getting-started',
        component: ComponentCreator('/docs/gpt-researcher/getting-started','e85'),
        exact: true,
        'sidebar': "docsSidebar"
      },
      {
        path: '/docs/gpt-researcher/introduction',
        component: ComponentCreator('/docs/gpt-researcher/introduction','18c'),
        exact: true,
        'sidebar': "docsSidebar"
      },
      {
        path: '/docs/gpt-researcher/pip-package',
        component: ComponentCreator('/docs/gpt-researcher/pip-package','47d'),
        exact: true,
        'sidebar': "docsSidebar"
      },
      {
        path: '/docs/gpt-researcher/roadmap',
        component: ComponentCreator('/docs/gpt-researcher/roadmap','1db'),
        exact: true
      },
      {
        path: '/docs/gpt-researcher/tailored-research',
        component: ComponentCreator('/docs/gpt-researcher/tailored-research','713'),
        exact: true,
        'sidebar': "docsSidebar"
      },
      {
        path: '/docs/gpt-researcher/troubleshooting',
        component: ComponentCreator('/docs/gpt-researcher/troubleshooting','261'),
        exact: true,
        'sidebar': "docsSidebar"
      },
      {
        path: '/docs/reference/config/config',
        component: ComponentCreator('/docs/reference/config/config','0fa'),
        exact: true,
        'sidebar': "referenceSideBar"
      },
      {
        path: '/docs/reference/config/singleton',
        component: ComponentCreator('/docs/reference/config/singleton','dd1'),
        exact: true,
        'sidebar': "referenceSideBar"
      },
      {
        path: '/docs/reference/processing/html',
        component: ComponentCreator('/docs/reference/processing/html','84d'),
        exact: true,
        'sidebar': "referenceSideBar"
      },
      {
        path: '/docs/reference/processing/text',
        component: ComponentCreator('/docs/reference/processing/text','dda'),
        exact: true,
        'sidebar': "referenceSideBar"
      },
      {
        path: '/docs/tavily-api/introduction',
        component: ComponentCreator('/docs/tavily-api/introduction','203'),
        exact: true,
        'sidebar': "docsSidebar"
      },
      {
        path: '/docs/tavily-api/langchain',
        component: ComponentCreator('/docs/tavily-api/langchain','907'),
        exact: true,
        'sidebar': "docsSidebar"
      },
      {
        path: '/docs/tavily-api/llamaindex',
        component: ComponentCreator('/docs/tavily-api/llamaindex','387'),
        exact: true,
        'sidebar': "docsSidebar"
      },
      {
        path: '/docs/tavily-api/python-sdk',
        component: ComponentCreator('/docs/tavily-api/python-sdk','76f'),
        exact: true,
        'sidebar': "docsSidebar"
      },
      {
        path: '/docs/tavily-api/rest_api',
        component: ComponentCreator('/docs/tavily-api/rest_api','83b'),
        exact: true,
        'sidebar': "docsSidebar"
      },
      {
        path: '/docs/welcome',
        component: ComponentCreator('/docs/welcome','177'),
        exact: true,
        'sidebar': "docsSidebar"
      }
    ]
  },
  {
    path: '/',
    component: ComponentCreator('/','deb'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*')
  }
];
