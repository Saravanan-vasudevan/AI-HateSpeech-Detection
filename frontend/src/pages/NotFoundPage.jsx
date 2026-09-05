import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const NotFoundPage = () => {
    const [countdown, setCountdown] = useState(10);
    const [autoRedirectEnabled, setAutoRedirectEnabled] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        let countdownInterval;

        if (autoRedirectEnabled) {
            countdownInterval = setInterval(() => {
                setCountdown(prev => {
                    if (prev <= 1) {
                        clearInterval(countdownInterval);
                        navigate('/');
                        return 0;
                    }
                    return prev - 1;
                });
            }, 1000);
        }

        return () => clearInterval(countdownInterval);
    }, [autoRedirectEnabled]);

    const cancelAutoRedirect = () => {
        setAutoRedirectEnabled(false);
    };

    const handleGoHome = () => {
        navigate('/');
    };

    const handleGoBack = () => {
        navigate(-1);
    };

    const handleNavigateTo = (path) => {
        navigate(path);
    };

    return (
        <div className={styles.notFoundPageContainer}>
            <div className={styles.notFoundBox}>
                <div className={styles.iconContainer}>
                    <div className={styles.errorIcon}>404</div>
                </div>

                <h1 className={styles.title}>Page Not Found</h1>

                <p className={styles.subtitle}>
                    The page <code className={styles.pathCode}>/some-missing-page</code> doesn't exist.
                </p>

                <p className={styles.description}>
                    You might have mistyped the URL or the page may have been moved or deleted.
                </p>

                {autoRedirectEnabled && (
                    <div className={styles.autoRedirectBox}>
                        <p className={styles.autoRedirectText}>
                            Redirecting to home page in <span className={styles.countdown}>{countdown}</span> seconds
                        </p>
                        <button className={styles.cancelButton} onClick={cancelAutoRedirect}>
                            Cancel Auto-redirect
                        </button>
                    </div>
                )}

                <div className={styles.buttonContainer}>
                    <button
                        className={`${styles.primaryButton} ${styles.animatedButton}`}
                        onClick={handleGoHome}
                    >
                        Go to Home Page
                    </button>

                    <button
                        className={styles.secondaryButton}
                        onClick={handleGoBack}
                    >
                        Go Back
                    </button>
                </div>

                <div className={styles.suggestionsContainer}>
                    <h3 className={styles.suggestionsTitle}>Or try these pages:</h3>
                    <div className={styles.suggestionsList}>
                        <button
                            className={styles.suggestionButton}
                            onClick={() => handleNavigateTo('/')}
                        >
                            Home / Login
                        </button>
                        <button
                            className={styles.suggestionButton}
                            onClick={() => handleNavigateTo('/dashboard')}
                        >
                            Student Dashboard
                        </button>
                        <button
                            className={styles.suggestionButton}
                            onClick={() => handleNavigateTo('/hate-speech-identifier')}
                        >
                            Hate Speech Identifier
                        </button>
                    </div>
                </div>

                <div className={styles.helpText}>
                    <p>If you believe this is an error, please contact the Speech Engine support team.</p>
                </div>
            </div>
        </div>
    );
};

export default NotFoundPage;