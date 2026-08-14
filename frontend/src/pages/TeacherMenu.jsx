import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './TeacherMenu.module.css';
import animatedButtonStyles from '../styles/AnimatedButton.module.css';
import config from '../config';
import { FaSignOutAlt } from 'react-icons/fa';

const TeacherMenu = () => {
    const navigate = useNavigate();
    const [teacherName, setTeacherName] = useState('Teacher');
    const [teacherId, setTeacherId] = useState('N/A');

    useEffect(() => {
        const fetchTeacherInfo = async () => {
            const accessToken = localStorage.getItem('access_token');
            if (!accessToken) {
                console.warn('No access token found for teacher menu. Redirecting to login.');
                navigate('/login');
                return;
            }
            try {
                const response = await fetch(`${config.API_BASE_URL}/users/me`, {
                    headers: { 'Authorization': `Bearer ${accessToken}` }
                });
                if (response.ok) {
                    const userData = await response.json();
                    if (userData.admin) {
                        setTeacherName(userData.first_name || userData.username);
                        setTeacherId(userData.username);
                        localStorage.setItem('teacherName', userData.first_name || userData.username);
                        localStorage.setItem('teacherId', userData.username);
                    } else {
                        alert('Access Denied: Only administrators can view the Teacher Portal.');
                        localStorage.removeItem('access_token');
                        localStorage.removeItem('token_type');
                        navigate('/');
                    }
                } else {
                    alert('Failed to load teacher info. Please log in again.');
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('token_type');
                    navigate('/');
                }
            } catch (error) {
                console.error('Error fetching teacher info:', error);
                alert('Network error fetching teacher info. Please try again.');
                localStorage.removeItem('access_token');
                localStorage.removeItem('token_type');
                navigate('/');
            }
        };

        fetchTeacherInfo();
    }, [navigate]);

    const handleRegisterUser = () => {
        navigate('/teacher-dashboard'); // This is where the registration form is
    };

    const handleViewStudentHistory = () => {
        navigate('/teacher-students'); // <--- UPDATED: Navigate to the new TeacherStudentList page
    };

    const handleLogout = () => {
        alert("Logging out from Teacher Portal!");
        localStorage.removeItem('access_token');
        localStorage.removeItem('token_type');
        localStorage.removeItem('teacherName');
        localStorage.removeItem('teacherId');
        navigate('/');
    };

    return (
        <div className={styles.dashboardPageContainer}>
            <div className={styles.dashboardBox}>
                <div className={styles.dashboardTopBar}>
                    <div className={styles.studentInfo} onClick={handleLogout}>
                        <span className={`material-icons ${styles.identityIcon}`}>admin_panel_settings</span>
                        <div className={styles.studentText}>
                            <span className={styles.studentName}>Welcome, {teacherName}</span>
                            <span className={styles.studentNumber}>ID: {teacherId}</span>
                        </div>
                    </div>
                    <div className={styles.totalPoints}>
                        Status: <span className={styles.pointsValue}>Online</span>
                    </div>
                </div>

                <h1 className={styles.dashboardTitle}>Teacher Portal</h1>
                <p className={styles.dashboardSubtitle}>Manage users and monitor educational progress.</p>

                <div className={styles.dashboardActions}>
                    <button 
                        className={`${styles.actionButton} ${animatedButtonStyles.animatedButton}`} 
                        onClick={handleRegisterUser}
                    >
                        <div className={styles.actionButtonTitle}>Register New Students</div>
                        <div className={styles.actionButtonDescription}>Create new accounts for students.</div>
                    </button>
                    <button 
                        className={`${styles.actionButton} ${animatedButtonStyles.animatedButton}`} 
                        onClick={handleViewStudentHistory}
                    >
                        <div className={styles.actionButtonTitle}>View All Students</div>
                        <div className={styles.actionButtonDescription}>Access a list of all students and their detailed history.</div>
                    </button>
                </div>

                <button type="button" className={styles.backButton} onClick={handleLogout}>
                    <FaSignOutAlt /> Logout
                </button>
            </div>
        </div>
    );
};

export default TeacherMenu;