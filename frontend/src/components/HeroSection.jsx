import React from 'react';
import styles from './HeroSection.module.css';
import illustration from '../assets/Online-Social-Media-Interaction-Illustration.svg'; // Make sure illustration.svg is in your assets folder

const HeroSection = () => (
  <section className={styles.heroWrap}>
    <img src={illustration} alt="Illustration" className={styles.illustration} />
    <div className={styles.textWrap}>
      <h1 className={styles.mainHeading}>What is Hate Speech?</h1>
      <p className={styles.paragraph}>
        Hate speech is when someone uses really mean, unfair, or hateful words, pictures, or even actions against another person or group, just because of who they are – like their background, their religion, their gender, or who they love. It's often seen online in comments, posts, or games, and its goal is to spread bad vibes, make people feel unsafe or unwelcome, and can cause real hurt both online and offline. It's not just a "joke" if it's picking on someone's identity.
      </p>
      <h2 className={styles.subHeading}>What should you do if you see hate speech online?</h2>
      <p className={styles.paragraph}>
        If you spot hate speech online, the best thing to do is not engage with it directly or spread it further. Instead, report it using the platform's tools, as this helps get it removed. If someone you know is being targeted, reach out privately to support them. You can also block or mute the person sending it to protect yourself. Most importantly, always talk to a trusted adult like a parent or teacher, as they can help you figure out the next steps.
      </p>
      <div className={styles.buttonContainer}>
        <div className={styles.combinedButton}>
          <span className={styles.buttonText}>Find Out More</span>
        </div>
      </div>
    </div>
  </section>
);

export default HeroSection;