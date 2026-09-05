import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './TeacherLogin.module.css';
import animatedButtonStyles from '../Styles/AnimatedButton.module.css';
import config from '../config';
import { FaArrowLeft } from 'react-icons/fa';

const TeacherLogin = () => {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');

    if (!credentials.username.trim() || !credentials.password.trim()) {
      setErrorMessage('Please enter both username and password.');
      return;
    }

    setIsLoading(true);

    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    try {
        const response = await fetch(`${config.API_BASE_URL}/token`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData.toString(),
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Teacher Login failed:', errorData);
            setErrorMessage(errorData.detail || 'Login failed. Please check your credentials.');
            setIsLoading(false);
            return;
        }

        const data = await response.json();
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('token_type', data.token_type);

        const userMeResponse = await fetch(`${config.API_BASE_URL}/users/me`, {
            headers: { 'Authorization': `Bearer ${data.access_token}` }
        });
        const userData = await userMeResponse.json();

        if (userMeResponse.ok && userData.admin) {
            localStorage.setItem('teacherName', userData.first_name || userData.username);
            localStorage.setItem('teacherId', userData.username);
            alert('Teacher Login Successful! Navigating to Teacher Portal.');
            navigate('/teacher-menu');
        } else {
            localStorage.removeItem('access_token');
            localStorage.removeItem('token_type');
            setErrorMessage('Access denied. Only administrators can access the Teacher Portal.');
        }
    } catch (error) {
        console.error('Network error during teacher login:', error);
        setErrorMessage('Network error. Could not connect to the server.');
    } finally {
        setIsLoading(false);
    }
  };

  const handleBack = () => {
    navigate('/login');
  };


  return (
    <div className={styles.loginContainer}>
      <div className={styles.loginBox}>
        <h1 className={styles.loginTitle}>Teacher Login</h1>
        <form onSubmit={handleSubmit} className={styles.loginForm}>
          {errorMessage && <p className={styles.errorMessage}>{errorMessage}</p>}
          <div className={styles.formGroup}>
            <div className={styles.formLabel}>Username</div>
            <input
              type="text"
              className={styles.formInput}
              value={credentials.username}
              onChange={(e) => setCredentials({...credentials, username: e.target.value})}
              placeholder="Enter your username"
              disabled={isLoading}
              required
            />
          </div>
          <div className={styles.formGroup}>
            <div className={styles.formLabel}>Password</div>
            <input
              type="password"
              className={styles.formInput}
              value={credentials.password}
              onChange={(e) => setCredentials({...credentials, password: e.target.value})}
              placeholder="Enter your password"
              disabled={isLoading}
              required
            />
          </div>
          <button
            type="submit"
            className={`${styles.loginButton} ${animatedButtonStyles.animatedButton}`}
            disabled={isLoading}
          >
            {isLoading ? 'Logging in...' : 'Login'}
          </button>
          <button
            type="button"
            onClick={handleBack}
            className={`${styles.backButton} ${animatedButtonStyles.animatedButton}`}
            disabled={isLoading}
          >
            <FaArrowLeft /> Back to Main Login
          </button>
        </form>
      </div>
    </div>
  );
};

export default TeacherLogin;
