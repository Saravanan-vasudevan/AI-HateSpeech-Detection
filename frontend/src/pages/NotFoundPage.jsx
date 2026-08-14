import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom'; // <--- NEW: Import useNavigate

const NotFoundPage = () => {
    const [countdown, setCountdown] = useState(10);
    const [autoRedirectEnabled, setAutoRedirectEnabled] = useState(true);
    const navigate = useNavigate(); // <--- NEW: Initialize useNavigate

    useEffect(() => {
        let countdownInterval;
        
        if (autoRedirectEnabled) {
            countdownInterval = setInterval(() => {
                setCountdown(prev => {
                    if (prev <= 1) {
                        clearInterval(countdownInterval);
                        navigate('/'); // <--- CORRECTED: Use navigate('/') for redirection
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
        navigate('/'); // <--- CORRECTED: Use navigate('/')
    };

    const handleGoBack = () => {
        navigate(-1); // <--- CORRECTED: Use navigate(-1) for going back in history
    };

    const handleNavigateTo = (path) => {
        navigate(path); // <--- CORRECTED: Use navigate(path)
    };

    return (
        <div className={styles.notFoundPageContainer}> {/* Use CSS Module Class */}
            <div className={styles.notFoundBox}> {/* Use CSS Module Class */}
                <div className={styles.iconContainer}> {/* Use CSS Module Class */}
                    <div className={styles.errorIcon}>404</div> {/* Use CSS Module Class */}
                </div>
                
                <h1 className={styles.title}>Page Not Found</h1> {/* Use CSS Module Class */}
                
                <p className={styles.subtitle}> {/* Use CSS Module Class */}
                    The page <code className={styles.pathCode}>/some-missing-page</code> doesn't exist. {/* Use CSS Module Class */}
                </p>

                <p className={styles.description}> {/* Use CSS Module Class */}
                    You might have mistyped the URL or the page may have been moved or deleted.
                </p>

                {autoRedirectEnabled && (
                    <div className={styles.autoRedirectBox}> {/* Use CSS Module Class */}
                        <p className={styles.autoRedirectText}> {/* Use CSS Module Class */}
                            Redirecting to home page in <span className={styles.countdown}>{countdown}</span> seconds
                        </p>
                        <button className={styles.cancelButton} onClick={cancelAutoRedirect}> {/* Use CSS Module Class */}
                            Cancel Auto-redirect
                        </button>
                    </div>
                )}

                <div className={styles.buttonContainer}> {/* Use CSS Module Class */}
                    <button 
                        className={`${styles.primaryButton} ${styles.animatedButton}`} // Use both local and potential shared animatedButton
                        onClick={handleGoHome}
                    >
                        Go to Home Page
                    </button>
                    
                    <button 
                        className={styles.secondaryButton} // Use CSS Module Class
                        onClick={handleGoBack}
                    >
                        Go Back
                    </button>
                </div>

                <div className={styles.suggestionsContainer}> {/* Use CSS Module Class */}
                    <h3 className={styles.suggestionsTitle}>Or try these pages:</h3> {/* Use CSS Module Class */}
                    <div className={styles.suggestionsList}> {/* Use CSS Module Class */}
                        <button 
                            className={styles.suggestionButton} // Use CSS Module Class
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

                <div className={styles.helpText}> {/* Use CSS Module Class */}
                    <p>If you believe this is an error, please contact the Speech Engine support team.</p>
                </div>
            </div>
        </div>
    );
};

export default NotFoundPage;