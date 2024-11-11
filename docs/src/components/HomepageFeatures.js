import clsx from 'clsx';
import { Link } from 'react-router-dom';
import React from 'react';
import styles from './HomepageFeatures.module.css';
const FeatureList = [
  {
    title: 'Tavily Search API',
    Svg: require('../../static/img/logo.png').default,
    docLink: './docs/python-sdk/tavily-search/getting-started',
    description: (
      <>
        Tavily Search API is a search engine optimized for LLMs, optimized for a factual, efficient, and persistent search experience
      </>
    ),
  },
  {
    title: 'Examples and Demos',
    Svg: require('../../static/img/idea.png').default,
    docLink: './docs/python-sdk/tavily-search/examples',
    description: (
      <>
          Check out Tavily API in action across multiple frameworks and use cases
      </>
    ),
  },
  {
    title: 'GPT Researcher',
    Svg: require('../../static/img/gptresearcher.png').default,
    docLink: './docs/gpt-researcher/getting-started',
    description: (
      <>
        GPT Researcher is an open source autonomous agent designed for comprehensive online research on a variety of tasks.
      </>
    ),
  },
];

function Feature({Svg, title, description, docLink}) {
    return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        {/*<Svg className={styles.featureSvg} alt={title} />*/}
          <img src={Svg} alt={title} height="60"/>
      </div>
        <div className="text--center padding-horiz--md">
        <Link to={docLink}>
            <h3>{title}</h3>
        </Link>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
