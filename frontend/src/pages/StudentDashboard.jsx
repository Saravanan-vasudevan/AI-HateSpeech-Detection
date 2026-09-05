import React,{ useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './StudentDashboard.module.css';
import animatedButtonStyles from '../Styles/AnimatedButton.module.css';
import config from '../config';

const StudentDashboard = () => {
    const navigate = useNavigate();

    const [recentHistory, setRecentHistory] = useState([]);
    const [historyLoading, setHistoryLoading] = useState(true);
    const [historyError, setHistoryError] = useState('');
    const [totalScore, setTotalScore] = useState(0);

    useEffect(() => {
        const fetchData = async () => {
            setHistoryLoading(true);
            setHistoryError('');

            try {
                const accessToken = localStorage.getItem('access_token');
                if (!accessToken) {
                    setHistoryError('Not authenticated.');
                    return;
                }

                const historyResponse = await fetch(`${config.API_BASE_URL}/history/?limit=3`, {
                    headers: { 'Authorization': `Bearer ${accessToken}` }
                });
                if (historyResponse.ok) {
                    const historyData = await historyResponse.json();
                    const formattedHistory = historyData.map(item => ({
                        activity: item.type === 'quiz' ? 'Quiz Completed' : `Text Analysis: "${item.text.substring(0, 25)}..."`,
                        pointsEarned: item.score || 0,
                        date: new Date(item.datetime).toLocaleDateString()
                    }));
                    setRecentHistory(formattedHistory);
                } else {
                    setHistoryError('Failed to load recent history.');
                }

                const scoreResponse = await fetch(`${config.API_BASE_URL}/scores/users/me/score`, {
                    headers: { 'Authorization': `Bearer ${accessToken}` }
                });
                if (scoreResponse.ok) {
                    const scoreData = await scoreResponse.json();
                    setTotalScore(scoreData.score);
                } else {
                    console.error("Failed to fetch total score.");
                }

            } catch (error) {
                setHistoryError('A network error occurred.');
            } finally {
                setHistoryLoading(false);
            }
        };

        fetchData();
    }, []);

    const handleHateSpeechIdentifierClick = () => navigate('/hate-speech-identifier');
    const handleMultiModelAnalysisClick = () => navigate('/multi-model-comparison');
    const handleGamifiedQuizClick = () => navigate('/gamified-quiz');
    const handleViewFullHistory = () => navigate('/history');
    const handleLogout = () => {
        alert("Logging out!");
        navigate('/');
    };

    return (
        <div className={styles.dashboardPageContainer}>
            <div className={styles.dashboardBox}>
                <div className={styles.dashboardTopBar}>
                    <div className={styles.studentInfo} onClick={handleLogout}>
                        <span className={`material-icons ${styles.identityIcon}`}>account_circle</span>
                        <div className={styles.studentText}>
                            <span className={styles.studentName}>John Doe</span>
                            <span className={styles.studentNumber}>C25018409</span>
                        </div>
                    </div>
                    <div className={styles.totalPoints}>
                        Total Points: <span className={styles.pointsValue}>{totalScore}</span>
                    </div>
                </div>
                <h1 className={styles.dashboardTitle}>Student Dashboard</h1>
                <p className={styles.dashboardSubtitle}>Your hub for learning and identifying hate speech.</p>
                <div className={styles.dashboardActions}>
                    <button className={`${styles.actionButton} ${animatedButtonStyles.animatedButton}`} onClick={handleHateSpeechIdentifierClick}>
                        Single Model Analysis
                        <span>Analyze text with our primary AI model</span>
                    </button>
                    <button className={`${styles.actionButton} ${animatedButtonStyles.animatedButton}`} onClick={handleMultiModelAnalysisClick}>
                        Multi-Model Analysis
                        <span>Compare predictions from multiple AI models</span>
                    </button>
                    <button className={`${styles.actionButton} ${animatedButtonStyles.animatedButton}`} onClick={handleGamifiedQuizClick}>
                        Gamified Quiz
                        <span>Test your knowledge with real scenarios</span>
                    </button>
                </div>
                <div className={styles.historySection}>
                    <div className={styles.historyHeader}>
                        <h2 className={styles.historyTitle}>Your Activity History</h2>
                        <button className={styles.viewFullHistoryButton} onClick={handleViewFullHistory}>
                            View Full History
                        </button>
                    </div>
                    <div className={styles.historyTableContainer}>
                        <table className={styles.historyTable}>
                            <thead>
                                <tr>
                                    <th>Activity</th>
                                    <th>Points Earned</th>
                                    <th>Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                {historyLoading ? (
                                    <tr><td colSpan="3">Loading recent activity...</td></tr>
                                ) : historyError ? (
                                    <tr><td colSpan="3">{historyError}</td></tr>
                                ) : recentHistory.length > 0 ? (
                                    recentHistory.map((item, index) => (
                                        <tr key={index}>
                                            <td>{item.activity}</td>
                                            <td>{item.pointsEarned > 0 ? `+${item.pointsEarned}` : item.pointsEarned}</td>
                                            <td>{item.date}</td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr><td colSpan="3">No recent activity to display.</td></tr>
                                )}
                            </tbody>
                        </table>
                        <p className={styles.historyNote}>
                            *Points are awarded for correctly identifying hate speech.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default StudentDashboard;