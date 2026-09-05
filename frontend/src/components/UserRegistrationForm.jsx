import React, { useState } from 'react';
import styles from './UserRegistrationForm.module.css';
import animatedButtonStyles from '../Styles/AnimatedButton.module.css';
import config from '../config';

const UserRegistrationForm = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [isAdmin, setIsAdmin] = useState(false);
    const [message, setMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const API_BASE_URL = config.API_BASE_URL;

    const handleRegister = async (e) => {
        e.preventDefault();
        setMessage('');
        setIsLoading(true);

        const requestBody = {
            username: username,
            password: password,
            first_name: firstName,
            last_name: lastName,
            admin: isAdmin
        };

        try {
            const response = await fetch(`${API_BASE_URL}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                },
                body: JSON.stringify(requestBody)
            });

            setIsLoading(false);

            if (response.ok) {
                const data = await response.json();
                setMessage(`User '${data.username}' registered successfully!`);
                setUsername('');
                setPassword('');
                setFirstName('');
                setLastName('');
                setIsAdmin(false);
            } else {
                const errorData = await response.json();
                setMessage(`Error: ${errorData.detail || 'Failed to register user.'}`);
            }
        } catch (error) {
            setIsLoading(false);
            setMessage(`Network error: ${error.message}. Could not connect to the server.`);
            console.error('Registration network error:', error);
        }
    };

    return (
        <div className={styles.registrationFormContainer}>
            <h2 className={styles.formTitle}>Register New User</h2>
            {message && <p className={`${styles.message} ${message.startsWith('User') ? styles.success : styles.error}`}>{message}</p>}

            <form onSubmit={handleRegister} className={styles.registrationForm}>
                <div className={styles.inputGroup}>
                    <label htmlFor="reg-username">Username:</label>
                    <input
                        type="text"
                        id="reg-username"
                        className={styles.inputField}
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                        disabled={isLoading}
                    />
                </div>
                <div className={styles.inputGroup}>
                    <label htmlFor="reg-password">Password:</label>
                    <input
                        type="password"
                        id="reg-password"
                        className={styles.inputField}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        disabled={isLoading}
                    />
                </div>
                <div className={styles.inputGroup}>
                    <label htmlFor="reg-first-name">First Name:</label>
                    <input
                        type="text"
                        id="reg-first-name"
                        className={styles.inputField}
                        value={firstName}
                        onChange={(e) => setFirstName(e.target.value)}
                        disabled={isLoading}
                    />
                </div>
                <div className={styles.inputGroup}>
                    <label htmlFor="reg-last-name">Last Name:</label>
                    <input
                        type="text"
                        id="reg-last-name"
                        className={styles.inputField}
                        value={lastName}
                        onChange={(e) => setLastName(e.target.value)}
                        disabled={isLoading}
                    />
                </div>
                <div className={styles.checkboxGroup}>
                    <input
                        type="checkbox"
                        id="reg-is-admin"
                        checked={isAdmin}
                        onChange={(e) => setIsAdmin(e.target.checked)}
                        disabled={isLoading}
                    />
                    <label htmlFor="reg-is-admin">Make Admin User</label>
                </div>

                <button
                    type="submit"
                    className={`${styles.submitButton} ${animatedButtonStyles.animatedButton}`}
                    disabled={isLoading}
                >
                    {isLoading ? 'Registering...' : 'Register User'}
                </button>
            </form>
        </div>
    );
};

export default UserRegistrationForm;
