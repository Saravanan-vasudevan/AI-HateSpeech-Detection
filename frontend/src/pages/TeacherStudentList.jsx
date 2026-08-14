import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './TeacherStudentList.module.css';
import config from '../config';
import { FaArrowLeft, FaTrophy } from 'react-icons/fa';

const TeacherStudentList = () => {
  const navigate = useNavigate();
  const [leaderboardData, setLeaderboardData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    const fetchLeaderboard = async () => {
      setIsLoading(true);
      setErrorMessage('');

      try {
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
        
        // --- UPDATED: Sorting by Quiz Score primarily ---
        data.sort((a, b) => (b.quiz_score || 0) - (a.quiz_score || 0));

        const topThree = data.slice(0, 3);

        // --- UPDATED: State format, removed totalScore ---
        const formattedList = topThree.map((user, index) => ({
            rank: index + 1,
            username: user.username,
            quizScore: user.quiz_score || 0,
            predictionScore: user.prediction_score || 0,
        }));

        setLeaderboardData(formattedList);

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
              <span className={styles.studentName}>Top 3 Leaderboard</span>
              <span className={styles.studentNumber}>Live Student Scores</span>
            </div>
          </div>
          <button onClick={handleGoBack} className={styles.backButton}>
            <FaArrowLeft /> Back to Menu
          </button>
        </div>

        <h1 className={styles.dashboardTitle}>Student Leaderboard</h1>
        <p className={styles.dashboardSubtitle}>Displaying the top 3 students, ranked by Quiz Score.</p>

        {errorMessage && <p className={styles.errorMessage}>{errorMessage}</p>}

        {isLoading ? (
          <div className={styles.loadingState}>
            <div className={styles.spinner}></div>
            <p>Loading leaderboard...</p>
          </div>
        ) : (
          <div className={styles.studentListContent}>
            {leaderboardData.length === 0 ? (
              <div className={styles.emptyContainer}>
                <div className={styles.emptyIcon}><FaTrophy /></div>
                <h2 className={styles.emptyTitle}>No Scores Yet</h2>
                <p className={styles.emptyMessage}>
                  The leaderboard is empty. Scores will appear here once students complete quizzes and analyses.
                </p>
              </div>
            ) : (
              <div className={styles.studentTableContainer}>
                <table className={styles.studentTable}>
                  {/* --- UPDATED: Table headers as requested --- */}
                  <thead>
                    <tr>
                      <th>Rank</th>
                      <th>Username</th>
                      <th>Prediction Score</th>
                      <th>Quiz Score</th>
                    </tr>
                  </thead>
                  {/* --- UPDATED: Table body to show separate scores --- */}
                  <tbody>
                    {leaderboardData.map((student) => (
                      <tr key={student.rank}>
                        <td>{student.rank}</td>
                        <td>{student.username}</td>
                        <td>{student.predictionScore}</td>
                        <td><strong>{student.quizScore}</strong></td>
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

export default TeacherStudentList;