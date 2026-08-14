import React, { useEffect, useState } from 'react';
import styles from './SplashScreen.module.css'; // Import the new CSS module
import logoIcon from '../assets/favicon.svg'; // Assuming you have your new short logo icon in assets

// Placeholder for student avatars - these are external. Will keep as is for now.
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
    // Timers for fade-out and completion of splash screen
    const timer = setTimeout(() => setFade(true), 1400); // Start fade-out after 1.4s
    const finishTimer = setTimeout(() => onFinish && onFinish(), 2100); // Call onFinish after 2.1s (0.7s fade + 1.4s)
    return () => {
      clearTimeout(timer);
      clearTimeout(finishTimer);
    };
  }, [onFinish]);

  return (
    <div className={styles.splashScreenContainer}>
      {/* <div className={styles.avatarGroup}>
        {studentAvatars.map((src, idx) => (
          <img
            key={idx}
            src={src}
            alt={`Student ${idx + 1}`}
            className={styles.avatar}
          />
        ))}
      </div> */}
      <div className={styles.logoOrb}>
        <img
          // Assuming your main Speechalytics logo (the interconnected circles) is an SVG/PNG
          // You might need to place your actual logo file in frontend/src/assets/
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