import React from 'react';
import styles from './StudentHistory.module.css';
import { FaChartBar } from 'react-icons/fa';

const StudentHistory = ({ onBack }) => {
  return (
    <div className={styles.dashboardPageContainer}>
      <div className={styles.dashboardBox}>
        <div className={styles.dashboardTopBar}>
          <div className={styles.studentInfo}>
            <span className={`material-icons ${styles.identityIcon}`}>history</span>
            <div className={styles.studentText}>
              <span className={styles.studentName}>Student History</span>
              <span className={styles.studentNumber}>All Student Activities</span>
            </div>
          </div>
          <button onClick={onBack} className={styles.backButton}>
            Back
          </button>
        </div>

        <h1 className={styles.dashboardTitle}>Student Activity History</h1>
        <p className={styles.dashboardSubtitle}>Comprehensive view of all student interactions and progress.</p>

        <div className={styles.emptyContainer}>
          <div className={styles.emptyIcon}><FaChartBar /></div>
          <h2 className={styles.emptyTitle}>Student History Page</h2>
          <p className={styles.emptyMessage}>
            This page will display detailed student activity history and analytics.
            <br />
            Feature coming soon!
          </p>
        </div>
      </div>
    </div>
  );
};

export default StudentHistory;