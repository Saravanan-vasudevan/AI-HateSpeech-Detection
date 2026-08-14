import React from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './rootpage.module.css'; // Using our CSS Module
import logo from '../assets/favicon.svg'; // Assuming logo is in assets
import HeroSection from '../components/HeroSection'; // Assuming these components exist
import RSSCards from '../components/RSSCards'; // Assuming these components exist
import { FaArrowRight } from 'react-icons/fa';

const RootPage = () => {
  const navigate = useNavigate();

  const handleLoginClick = () => {
    navigate('/login');
  };

  return (
    <div className={styles.pageContainer}>
      <nav className={styles.navbar}>
        <div className={styles.logoWrap}>
          <img src={logo} alt="Logo" className={styles.logoImg} />
        </div>
        <div className={styles.navLinks}>
          <button className={styles.active}>Home</button>
          <button>Blog</button>
          <button>About</button>
          <button>Help</button>
        </div>
        <button className={styles.loginBtn} onClick={handleLoginClick}>
          Login <span><FaArrowRight /></span>
        </button>
      </nav>
      <HeroSection />
      <RSSCards />
    </div>
  );
};

export default RootPage;