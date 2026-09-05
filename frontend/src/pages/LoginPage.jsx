import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './LoginPage.module.css';
import animatedButtonStyles from '../Styles/AnimatedButton.module.css';
import config from '../config';
import { FaArrowLeft } from 'react-icons/fa';

const LoginPage = () => {
    const navigate = useNavigate();
    const [loginMode, setLoginMode] = useState('initial');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleLoginSubmit = async (e) => {
        e.preventDefault();
        setErrorMessage('');
        setIsLoading(true);

        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        try {
            const response = await fetch(`${config.API_BASE_URL}/token`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData.toString(),
            });

            setIsLoading(false);

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('token_type', data.token_type);

                alert('Login Successful! Navigating to dashboard.');
                navigate('/dashboard');
            } else {
                const errorData = await response.json();
                console.error('Login failed:', errorData);
                setErrorMessage(errorData.detail || 'Login failed. Please check your credentials.');
            }
        } catch (error) {
            setIsLoading(false);
            console.error('Network error during login:', error);
            setErrorMessage('Network error. Could not connect to the server.');
        }
    };

    const handleStudentLoginClick = () => {
        setLoginMode('student');
        setUsername('');
        setPassword('');
        setErrorMessage('');
    };

    const handleTeacherLoginClick = () => {
        navigate('/teacher-login');
    };

    return (
        <div className={styles.loginPageContainer}>
            <div className={styles.loginBox}>
                <h1 className={styles.title}>Welcome to Speech Engine</h1>
                <p className={styles.subtitle}>Choose your login type:</p>

                {loginMode === 'initial' ? (
                    <div className={styles.roleSelection}>
                        <button
                            className={`${styles.roleButton} ${animatedButtonStyles.animatedButton}`}
                            onClick={handleStudentLoginClick}
                        >
                            Student Login
                        </button>
                        <button
                            className={`${styles.roleButton} ${animatedButtonStyles.animatedButton}`}
                            onClick={handleTeacherLoginClick}
                        >
                            Teacher Login
                        </button>
                    </div>
                ) : (
                    <form onSubmit={handleLoginSubmit} className={styles.loginForm}>
                        <p className={styles.formInstruction}>
                            Please enter your credentials as a {loginMode}:
                        </p>

                        {errorMessage && <p className={styles.errorMessage}>{errorMessage}</p>}

                        <div className={styles.inputGroup}>
                            <label htmlFor="username">Username:</label>
                            <input
                                type="text"
                                id="username"
                                className={styles.inputField}
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                                disabled={isLoading}
                            />
                        </div>
                        <div className={styles.inputGroup}>
                            <label htmlFor="password">Password:</label>
                            <input
                                type="password"
                                id="password"
                                className={styles.inputField}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                disabled={isLoading}
                            />
                        </div>
                        <button
                            type="submit"
                            className={`${styles.submitButton} ${animatedButtonStyles.animatedButton}`}
                            disabled={isLoading}
                        >
                            {isLoading ? 'Logging In...' : 'Login'}
                        </button>
                        <button
                            type="button"
                            className={styles.backButton}
                            onClick={() => {
                                setLoginMode('initial');
                                setUsername('');
                                setPassword('');
                                setErrorMessage('');
                            }}
                            disabled={isLoading}
                        >
                            <FaArrowLeft /> Back to Role Selection
                        </button>
                    </form>
                )}
            </div>
        </div>
    );
};

export default LoginPage;
