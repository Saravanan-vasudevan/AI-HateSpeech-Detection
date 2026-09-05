import React, { useEffect, useState } from 'react';
import styles from './rsscards.module.css';
import { FaArrowRight } from 'react-icons/fa';

const cardImages = [
  'https://images.unsplash.com/photo-1497366216548-37526070297c?w=400&h=400&fit=crop&crop=center',
  'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=400&h=400&fit=crop&crop=center',
  'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=400&h=400&fit=crop&crop=center',
  'https://images.unsplash.com/photo-1509062522246-3755977927d7?w=400&h=400&fit=crop&crop=center'
];

const articles = [
  { title: "BBC News - Hate Speech Coverage", description: "Latest news and analysis on hate speech from BBC News...", image: cardImages[0], link: "https://www.bbc.co.uk/news/topics/cvjpvzj0p3vt" },
  { title: "UN News - Hate Speech Resources", description: "United Nations coverage of hate speech issues...", image: cardImages[1], link: "https://news.un.org/en/tags/hate-speech" },
  { title: "The Independent - Hate Speech Analysis", description: "In-depth reporting and analysis on hate speech...", image: cardImages[2], link: "https://www.independent.co.uk/topic/hate-speech" },
  { title: "The Conversation - Academic Perspectives", description: "Academic research and expert analysis on hate speech...", image: cardImages[3], link: "https://theconversation.com/topics/hate-speech-10323" }
];

const RSSCards = () => {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 1000);
    return () => clearTimeout(timer);
  }, []);

  const handleCardClick = (link) => window.open(link, '_blank', 'noopener,noreferrer');
  const handleReadMoreClick = (e, link) => {
    e.stopPropagation();
    window.open(link, '_blank', 'noopener,noreferrer');
  };

  return (
    <div className={styles.cardGrid}>
      {loading ? (
        Array(4).fill(0).map((_, i) => (
          <div key={i} className={styles.card}>
            <img src={cardImages[i]} alt="Loading" className={styles.cardImg} />
            <div className={styles.cardOverlay} />
            <div className={styles.cardContent}>
              <h3 className={styles.cardTitle}>Loading...</h3>
              <p className={styles.cardDesc}>Loading article...</p>
              <button className={styles.readMoreBtn}>Read More <FaArrowRight /></button>
            </div>
          </div>
        ))
      ) : (
        articles.map((item, i) => (
          <div key={i} className={styles.card} onClick={() => handleCardClick(item.link)}>
            <img src={item.image} alt={item.title} className={styles.cardImg} />
            <div className={styles.cardOverlay} />
            <div className={styles.cardContent}>
              <h3 className={styles.cardTitle}>{item.title}</h3>
              <p className={styles.cardDesc}>{item.description}</p>
              <button className={styles.readMoreBtn} onClick={(e) => handleReadMoreClick(e, item.link)}>
                Read More <FaArrowRight />
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  );
};

export default RSSCards;
