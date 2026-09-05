import React, { useEffect, useState } from 'react';
import styles from './splashscreen.module.css';
import logoIcon from '../assets/favicon.svg';

const studentAvatars = [
  'https://api.dicebear.com/7.x/adventurer/svg?seed=student1',
  'https://api.dicebear.com/7.x/adventurer/svg?seed=student2',
  'https://api.dicebear.com/7.x/adventurer/svg?seed=student3',
  'https://api.dicebear.com/7.x/adventurer/svg?seed=student4',
  'https://api.dicebear.com/7.x/adventurer/svg?seed=student5',
];

const SplashScreen = ({ onFinish }) => {
  const [fade, setFade] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setFade(true), 1400);
    const finishTimer = setTimeout(() => onFinish && onFinish(), 2100);
    return () => {
      clearTimeout(timer);
      clearTimeout(finishTimer);
    };
  }, [onFinish]);

  return (
    <div className={styles.splashScreenContainer}>

      <div className={styles.logoOrb}>
        <img
          src={logoIcon}
          alt="Speechalytics App Logo"
          className={styles.appLogo}
        />
      </div>
      <h1 className={styles.mainTitle}>
        SPEECHALYTICS
      </h1>
      <h2 className={styles.subtitle}>

      </h2>
    </div>
  );
};

export default SplashScreen;
