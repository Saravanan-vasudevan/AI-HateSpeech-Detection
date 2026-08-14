import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './TeacherLogin.module.css';
import animatedButtonStyles from '../styles/AnimatedButton.module.css'; // Import animated button styles
import config from '../config'; // Import config for API_BASE_URL
import { FaArrowLeft } from 'react-icons/fa';

const TeacherLogin = () => {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(''); // State for displaying error messages
  const navigate = useNavigate();

  const handleSubmit = async (e) => { // Accept event object to prevent default
    e.preventDefault(); // Prevent default form submission
    setErrorMessage(''); // Clear previous error messages
    
    if (!credentials.username.trim() || !credentials.password.trim()) {
      setErrorMessage('Please enter both username and password.');
      return;
    }

    setIsLoading(true);

    // Prepare data as x-www-form-urlencoded, as FastAPI's OAuth2PasswordRequestForm expects this
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    try {
        // --- Step 1: Authenticate and get token ---
        const response = await fetch(`${config.API_BASE_URL}/token`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData.toString(),
        });

        if (!response.ok) { // Check if login itself failed (e.g., wrong credentials)
            const errorData = await response.json();
            console.error('Teacher Login failed:', errorData);
            setErrorMessage(errorData.detail || 'Login failed. Please check your credentials.');
            setIsLoading(false);
            return;
        }
        
        const data = await response.json();
        console.log('Teacher Login successful, token received:', data);
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('token_type', data.token_type);
        
        // --- Step 2: Verify user's admin status ---
        const userMeResponse = await fetch(`${config.API_BASE_URL}/users/me`, {
            headers: { 'Authorization': `Bearer ${data.access_token}` }
        });
        const userData = await userMeResponse.json();

        if (userMeResponse.ok && userData.admin) { // Check if user is admin
            localStorage.setItem('teacherName', userData.first_name || userData.username);
            localStorage.setItem('teacherId', userData.username);
            alert('Teacher Login Successful! Navigating to Teacher Portal.');
            navigate('/teacher-menu'); // Navigate to teacher menu on successful admin login
        } else {
            // Not an admin or failed to get user info, revoke token and show error
            localStorage.removeItem('access_token');
            localStorage.removeItem('token_type');
            setErrorMessage('Access denied. Only administrators can access the Teacher Portal.');
        }
    } catch (error) {
        console.error('Network error during teacher login:', error);
        setErrorMessage('Network error. Could not connect to the server.');
    } finally {
        setIsLoading(false); // Ensure loading state is reset
    }
  };

  const handleBack = () => {
    navigate('/login'); // Navigate back to the dedicated login page (AuthLoginPage)
  };

  // Removed handleKeyPress as form onSubmit handles Enter key automatically

  return (
    <div className={styles.loginContainer}>
      <div className={styles.loginBox}>
        <h1 className={styles.loginTitle}>Teacher Login</h1>
        <form onSubmit={handleSubmit} className={styles.loginForm}> {/* Use onSubmit on form */}
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
            type="submit" // Set type to submit
            className={`${styles.loginButton} ${animatedButtonStyles.animatedButton}`} 
            disabled={isLoading}
          >
            {isLoading ? 'Logging in...' : 'Login'}
          </button>
          <button 
            type="button" // Set type to button to prevent form submission
            onClick={handleBack} 
            className={`${styles.backButton} ${animatedButtonStyles.animatedButton}`} 
            disabled={isLoading}
          >
            <FaArrowLeft /> Back to Main Login
          </button>
        </form>
        
        {/* Demo credentials helper */}
        <div className={styles.demoCredentials}>
          <p><strong>Demo Credentials:</strong></p>
          <p>Username: <code>Admin1234</code> | Password: <code>Admin1234!</code> (Ensure this user is registered as admin in your DB)</p>
        </div>
      </div>
    </div>
  );
};

export default TeacherLogin;