import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './TeacherLeaderboard.module.css'; // This component's specific CSS
import config from '../config'; // Import config for API_BASE_URL
import { FaArrowLeft, FaTrophy } from 'react-icons/fa';

const TeacherLeaderboard = () => { // Renamed component from TeacherStudentList
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

        const response = await fetch(`${config.API_BASE_URL}/scores/leaderboard`, { // Fetch from leaderboard endpoint
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            // 'Authorization': `Bearer ${accessToken}`, // Leaderboard API might not require auth, check backend
          },
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to fetch leaderboard data.');
        }

        const data = await response.json();
        // Assuming data is an array of objects: [{username, score}, ...]
        setLeaderboardData(data);

      } catch (error) {
        setErrorMessage(`Error loading leaderboard: ${error.message}.`);
        console.error('Error fetching leaderboard:', error);
        setLeaderboardData([]); // Clear list on error
      } finally {
        setIsLoading(false);
      }
    };

    fetchLeaderboard();
  }, []); // Run once on mount

  // No handleViewStudentHistory as this page is now pure leaderboard
  // If you need to click on a username here to view *their* history, we'd add that.

  const handleGoBack = () => {
    navigate('/teacher-menu'); // Go back to the Teacher Menu
  };

  return (
    <div className={styles.dashboardPageContainer}>
      <div className={styles.dashboardBox}>
        <div className={styles.dashboardTopBar}>
          <div className={styles.studentInfo}> {/* Reusing studentInfo styles */}
            <span className={`material-icons ${styles.identityIcon}`}>leaderboard</span> {/* Icon for leaderboard */}
            <div className={styles.studentText}>
              <span className={styles.studentName}>Global Leaderboard</span> {/* Changed text */}
              <span className={styles.studentNumber}>Top Student Scores</span> {/* Changed text */}
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