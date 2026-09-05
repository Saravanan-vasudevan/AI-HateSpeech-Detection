import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaArrowLeft, FaInbox } from 'react-icons/fa';
import styles from './studentpointshistory.module.css';
import config from '../config';

const StudentPointsHistory = () => {
    const navigate = useNavigate();

    const [historyData, setHistoryData] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [errorMessage, setErrorMessage] = useState('');

    useEffect(() => {
        const fetchHistory = async () => {
            setIsLoading(true);
            setErrorMessage('');
            try {
                const accessToken = localStorage.getItem('access_token');
                if (!accessToken) {
                    setErrorMessage('Not authenticated. Please log in again.');
                    setIsLoading(false);
                    return;
                }
                const response = await fetch(`${config.API_BASE_URL}/history/`, {
                    method: 'GET',
                    headers: { 'Accept': 'application/json', 'Authorization': `Bearer ${accessToken}` },
                });
                if (response.ok) {
                    const data = await response.json();
                    const formattedHistory = data.map(item => ({
                        activity: item.type === 'quiz' ? 'Quiz Completed' : `Text Analysis: "${item.text.substring(0, 30)}..."`,
                        pointsEarned: item.score || 0,
                        date: new Date(item.datetime).toLocaleDateString()
                    }));
                    setHistoryData(formattedHistory.reverse());
                } else {
                    const errorData = await response.json();
                    setErrorMessage(errorData.detail || 'Failed to fetch history.');
                    setHistoryData([]);
                }
            } catch (error) {
                setErrorMessage(`Network error: ${error.message}.`);
                setHistoryData([]);
            } finally {
                setIsLoading(false);
            }
        };
        fetchHistory();
    }, []);

    const handleGoBack = () => {
        navigate('/dashboard');
    };

    return (
        <div className={styles.historyPageContainer}>
            <div className={styles.historyBox}>
                <h1 className={styles.headerTitle}>Your Full Activity History</h1>
                <p className={styles.pageSubtitle}>Review your past analyses and earned points.</p>
                {errorMessage && <p className={styles.errorMessage}>{errorMessage}</p>}
                {isLoading ? (
                    <div className={styles.loadingState}>
                        <div className={styles.spinner}></div>
                        <p>Loading history...</p>
                    </div>
                ) : (
                    <div className={styles.historyContent}>
                        {historyData.length === 0 ? (
                            <div className={styles.noActivity}>
                                <p className={styles.noActivityIcon}><FaInbox /></p>
                                <p className={styles.noActivityMessage}>No activity recorded yet.</p>
                            </div>
                        ) : (
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
                                        {historyData.map((item, index) => (
                                            <tr key={index}>
                                                <td>{item.activity}</td>
                                                <td>{item.pointsEarned > 0 ? `+${item.pointsEarned}` : item.pointsEarned}</td>
                                                <td>{item.date}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                )}
                <button type="button" className={styles.backButton} onClick={handleGoBack}>
                    <FaArrowLeft /> Back to Dashboard
                </button>
            </div>
        </div>
    );
};

export default StudentPointsHistory;