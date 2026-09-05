import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FaArrowLeft } from 'react-icons/fa';
import styles from './TeacherDashboard.module.css';
import UserRegistrationForm from '../components/UserRegistrationForm';

const TeacherDashboard = () => {
    const navigate = useNavigate();

    const handleGoBack = () => {
        navigate('/teacher-menu');
    };

    return (
        <div className={styles.teacherDashboardPageContainer}>
            <div className={styles.teacherDashboardBox}>
                <h1 className={styles.headerTitle}>User Registration</h1>
                <p className={styles.pageSubtitle}>Create new student or admin accounts.</p>


                <div className={styles.registrationSection}>
                    <UserRegistrationForm />
                </div>

                <button type="button" className={styles.backButton} onClick={handleGoBack}>
                    <FaArrowLeft /> Back to Teacher Menu
                </button>
            </div>
        </div>
    );
};

export default TeacherDashboard;