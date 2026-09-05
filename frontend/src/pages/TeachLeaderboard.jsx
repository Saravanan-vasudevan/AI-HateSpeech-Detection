import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './TeachLeaderboard.module.css';
import config from '../config';
import { FaArrowLeft, FaTrophy } from 'react-icons/fa';

const TeacherLeaderboard = () => {
  const navigate = useNavigate();
  const [leaderboardData, setLeaderboardData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    const fetchLeaderboard = async () => {
      setIsLoading(true);
      setErrorMessage('');

      try {
        const accessToken = localStorage.getItem('access_token');
        if (!accessToken) {
          setErrorMessage('Authentication required. Please log in as an admin.');
          setIsLoading(false);
          return;
        }

        const response = await fetch(`${config.API_BASE_URL}/scores/leaderboard`, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          },
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to fetch leaderboard data.');
        }

        const data = await response.json();
        setLeaderboardData(data);

      } catch (error) {
        setErrorMessage(`Error loading leaderboard: ${error.message}.`);
        console.error('Error fetching leaderboard:', error);
        setLeaderboardData([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchLeaderboard();
  }, []);


  const handleGoBack = () => {
    navigate('/teacher-menu');
  };

  return (
    <div className={styles.dashboardPageContainer}>
      <div className={styles.dashboardBox}>
        <div className={styles.dashboardTopBar}>
          <div className={styles.studentInfo}>
            <span className={`material-icons ${styles.identityIcon}`}>leaderboard</span>
            <div className={styles.studentText}>
              <span className={styles.studentName}>Global Leaderboard</span>
              <span className={styles.studentNumber}>Top Student Scores</span>
            </div>
          </div>
          <button onClick={handleGoBack} className={styles.backButton}>
            <FaArrowLeft /> Back to Menu
          </button>
        </div>

        <h1 className={styles.dashboardTitle}>Current Leaderboard</h1>
        <p className={styles.dashboardSubtitle}>See the top scores across all students.</p>

        {errorMessage && <p className={styles.errorMessage}>{errorMessage}</p>}

        {isLoading ? (
          <div className={styles.loadingState}>
            <div className={styles.spinner}></div>
            <p>Loading leaderboard...</p>
          </div>
        ) : (
          <div className={styles.leaderboardContent}>
            {leaderboardData.length === 0 ? (
              <div className={styles.emptyContainer}>
                <div className={styles.emptyIcon}><FaTrophy /></div>
                <h2 className={styles.emptyTitle}>No Scores Yet</h2>
                <p className={styles.emptyMessage}>
                  No quiz scores have been recorded yet.
                  <br />
                  Encourage students to play the quiz!
                </p>
              </div>
            ) : (
              <div className={styles.leaderboardTableContainer}>
                <table className={styles.leaderboardTable}>
                  <thead>
                    <tr>
                      <th>Rank</th>
                      <th>Username</th>
                      <th>Total Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leaderboardData.map((entry, index) => (
                      <tr key={index}>
                        <td>{index + 1}</td>
                        <td>{entry.username}</td>
                        <td>{entry.score}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default TeacherLeaderboard;
