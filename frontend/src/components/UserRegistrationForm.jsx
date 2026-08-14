import React, { useState } from 'react';
import styles from './UserRegistrationForm.module.css';
import animatedButtonStyles from '../styles/AnimatedButton.module.css';
import config from '../config';

const UserRegistrationForm = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [isAdmin, setIsAdmin] = useState(false); // State for the admin checkbox
    const [message, setMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    // New states for the Admin Confirmation Modal
    const [showAdminConfirmModal, setShowAdminConfirmModal] = useState(false);
    const [adminConfirmPassword, setAdminConfirmPassword] = useState('');
    const [adminConfirmError, setAdminConfirmError] = useState('');

    const API_BASE_URL = config.API_BASE_URL;

    // Function to handle the main registration form submission
    const handleRegister = async (e) => {
        e.preventDefault();
        setMessage(''); // Clear previous messages
        setAdminConfirmError(''); // Clear modal error
        setIsLoading(true);

        const requestBody = {
            username: username,
            password: password,
            first_name: firstName,
            last_name: lastName,
            admin: isAdmin // This reflects the checkbox state
        };

        try {
            const response = await fetch(`${API_BASE_URL}/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody)
            });

            setIsLoading(false);

            if (response.ok) {
                const data = await response.json();
                setMessage(`User '${data.username}' registered successfully!`);
                // Optionally clear form:
                setUsername('');
                setPassword('');
                setFirstName('');
                setLastName('');
                setIsAdmin(false); // Reset admin checkbox after successful registration
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

    // New: Handle the admin checkbox change
    const handleAdminCheckboxChange = (e) => {
        const isChecked = e.target.checked;
        if (isChecked) {
            // If checking "Make Admin User", show the confirmation modal
            setShowAdminConfirmModal(true);
            setAdminConfirmError(''); // Clear any previous modal errors
            setAdminConfirmPassword(''); // Clear password
        } else {
            // If unchecking, just set isAdmin to false directly
            setIsAdmin(false);
        }
    };

    // New: Handle confirmation in the modal
    const handleAdminConfirm = async () => {
        setAdminConfirmError('');
        setIsLoading(true);

        const loggedInUsername = localStorage.getItem('access_token'); // Get the username of the currently logged-in teacher
        if (!loggedInUsername || !adminConfirmPassword) {
            setAdminConfirmError('Username and password are required for confirmation.');
            setIsLoading(false);
            return;
        }

        // Make API call to re-authenticate the current admin user
        const formData = new URLSearchParams();
        formData.append('username', loggedInUsername);
        formData.append('password', adminConfirmPassword);

        try {
            const response = await fetch(`${API_BASE_URL}/token`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData.toString(),
            });

            setIsLoading(false);

            if (response.ok) {
                // If re-authentication successful, allow admin creation
                setIsAdmin(true);
                setShowAdminConfirmModal(false); // Close modal
                setAdminConfirmPassword(''); // Clear password
                setMessage('Admin privilege confirmed. Proceed with user registration.'); // Give feedback
            } else {
                const errorData = await response.json();
                setAdminConfirmError(errorData.detail || 'Incorrect password for admin confirmation.');
                setIsAdmin(false); // Keep checkbox unchecked on failed confirmation
            }
        } catch (error) {
            setIsLoading(false);
            setAdminConfirmError(`Network error: ${error.message}.`);
            console.error('Admin confirmation network error:', error);
            setIsAdmin(false);
        }
    };

    // New: Handle cancellation in the modal
    const handleAdminCancel = () => {
        setIsAdmin(false); // Uncheck the main checkbox
        setShowAdminConfirmModal(false); // Close modal
        setAdminConfirmPassword(''); // Clear password
        setAdminConfirmError(''); // Clear error
        setMessage('Admin user creation cancelled.');
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
                        onChange={handleAdminCheckboxChange} // Use new handler
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

            {/* Admin Confirmation Modal */}
            {showAdminConfirmModal && (
                <div className={styles.modalOverlay}>
                    <div className={styles.modalContent}>
                        <h3 className={styles.modalTitle}>Confirm Admin Creation</h3>
                        <p className={styles.modalText}>
                            To create an Admin user, please enter your own password to confirm.
                        </p>
                        {adminConfirmError && <p className={styles.modalErrorMessage}>{adminConfirmError}</p>}
                        <div className={styles.inputGroup}>
                            <label htmlFor="admin-confirm-password">Your Password:</label>
                            <input
                                type="password"
                                id="admin-confirm-password"
                                className={styles.inputField} // Reuse existing inputField style
                                value={adminConfirmPassword}
                                onChange={(e) => setAdminConfirmPassword(e.target.value)}
                                onKeyPress={(e) => { if (e.key === 'Enter') handleAdminConfirm(); }}
                                disabled={isLoading}
                                required
                            />
                        </div>
                        <div className={styles.modalActions}>
                            <button 
                                className={`${styles.modalConfirmButton} ${animatedButtonStyles.animatedButton}`} 
                                onClick={handleAdminConfirm}
                                disabled={isLoading}
                            >
                                {isLoading ? 'Confirming...' : 'Confirm'}
                            </button>
                            <button 
                                className={styles.modalCancelButton} 
                                onClick={handleAdminCancel}
                                disabled={isLoading}
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default UserRegistrationForm;