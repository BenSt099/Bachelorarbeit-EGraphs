import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Installation',
    Svg: require('@site/static/img/arrow-down-circle.svg').default,
    description: (
      <>
       Learn how to install the required dependencies and how to start the software.
      </>
    ),
  },
  {
    title: 'Usage',
    Svg: require('@site/static/img/alphabet.svg').default,
    description: (
      <>
        This documentation explains everything you need to know about managing the software, creating EGraphs and Rewrite Rules,
        manipulating EGraphs and go through the Equality Saturation process step for step.
      </>
    ),
  },
  {
    title: 'Tests',
    Svg: require('@site/static/img/bookmark-check.svg').default,
    description: (
      <>
        This software is covered by Unit-Tests. Learn how to run them.
      </>
    ),
  },
];

function Feature({Svg, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}
        </Heading>
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
