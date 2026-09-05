import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './HateSpeechIdentifier.module.css';
import animatedButtonStyles from '../Styles/AnimatedButton.module.css';
import config from '../config';
import { FaArrowLeft } from 'react-icons/fa';

const HateSpeechIdentifier = () => {
    const navigate = useNavigate();
    const [inputText, setInputText] = useState(
        "Some people are just naturally inferior due to their background."
    );
    const [isHateSpeech, setIsHateSpeech] = useState(null);
    const [reasoning, setReasoning] = useState('');

    const [showResults, setShowResults] = useState(false);
    const [aiClassification, setAiClassification] = useState(null);
    const [aiExplanation, setAiExplanation] = useState('');
    const [feedbackMessage, setFeedbackMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');

const handleSubmit = async (e) => {
    e.preventDefault();

    if (isHateSpeech === null) {
        setErrorMessage("Please select whether you think the text is hate speech or not.");
        return;
    }
    if (!reasoning.trim()) {
        setErrorMessage("Please provide your reasoning.");
        return;
    }

    setIsLoading(true);
    setErrorMessage('');

    try {
        const accessToken = localStorage.getItem('access_token');
        if (!accessToken) {
            setErrorMessage('Authentication error. Please log in again.');
            setIsLoading(false);
            return;
        }

        const predictionResponse = await fetch(`${config.API_BASE_URL}/gemini/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({ text: inputText })
        });

        const predictionData = await predictionResponse.json();
        if (!predictionResponse.ok) {
            throw new Error(predictionData.detail || 'Failed to get a prediction from the AI model.');
        }

        const feedbackResponse = await fetch(`${config.API_BASE_URL}/feedback/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({
                student_prediction: isHateSpeech === 'yes',
                student_explanation: reasoning,
                ai_prediction: predictionData.is_hate_speech,
                ai_explanation: predictionData.explanation
            })
        });

        const feedbackData = await feedbackResponse.json();
        if (!feedbackResponse.ok) {
            throw new Error(feedbackData.detail || 'Failed to generate feedback.');
        }

        await fetch(`${config.API_BASE_URL}/history/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({
                text: inputText,
                human_prediction: isHateSpeech === 'yes',
                ai_prediction: predictionData.is_hate_speech,
                human_explanation: reasoning,
                ai_explanation: predictionData.explanation,
                probability: predictionData.hate_speech_probability
            })
        });

        setAiClassification(predictionData.is_hate_speech ? 'yes' : 'no');
        setAiExplanation(predictionData.explanation);
        setFeedbackMessage(feedbackData.feedback_text);
        setShowResults(true);

    } catch (error) {
        console.error('API call error:', error);
        setErrorMessage(`Error during analysis: ${error.message}`);
        setShowResults(false);
    } finally {
        setIsLoading(false);
    }
};

    const handleGoBack = () => {
        navigate('/dashboard');
    };

    const handleAnalyzeAnother = () => {
        setInputText("Some people are just naturally inferior due to their background.");
        setIsHateSpeech(null);
        setReasoning('');
        setShowResults(false);
        setAiClassification(null);
        setAiExplanation('');
        setFeedbackMessage('');
        setErrorMessage('');
    };

    return (
        <div className={styles.identifierPageContainer}>
            <div className={styles.identifierBox}>
                <h1 className={styles.headerTitle}>Analyze Your Hate Speech</h1>
                <p className={styles.pageSubtitle}>
                    Evaluate the provided text and explain your reasoning.
                </p>

                {errorMessage && <p className={styles.errorMessage}>{errorMessage}</p>}

                {isLoading ? (
                    <div className={styles.loadingState}>
                        <div className={styles.spinner}></div>
                        <p>Analyzing your text...</p>
                    </div>
                ) : showResults ? (
                    <div className={styles.resultsSection}>
                        <div className={styles.resultGroup}>
                            <h3 className={styles.resultTitle}>Text Analyzed:</h3>
                            <p className={styles.resultTextAnalyzed}>{inputText}</p>
                        </div>

                        <div className={styles.comparisonGrid}>
                            <div className={styles.studentColumn}>
                                <h3 className={styles.resultTitle}>Your Analysis:</h3>
                                <p><strong>Classification:</strong> <span className={isHateSpeech === 'yes' ? styles.hateSpeechClass : styles.notHateSpeechClass}>
                                    {isHateSpeech === 'yes' ? 'Yes, it is hate speech' : 'No, it is not hate speech'}
                                </span></p>
                                <p><strong>Your Reasoning:</strong></p>
                                <p className={styles.reasoningText}>{reasoning}</p>
                            </div>

                            <div className={styles.aiColumn}>
                                <h3 className={styles.resultTitle}>AI's Analysis:</h3>
                                <p><strong>Classification:</strong> <span className={aiClassification === 'yes' ? styles.hateSpeechClass : styles.notHateSpeechClass}>
                                    {aiClassification === 'yes' ? 'Yes, it is hate speech' : 'No, it is not hate speech'}
                                </span></p>
                                <p><strong>AI's Explanation:</strong></p>
                                <p className={styles.reasoningText}>{aiExplanation}</p>
                            </div>
                        </div>

                        <div className={styles.feedbackSection}>
                            <h3 className={styles.resultTitle}>Feedback:</h3>
                            <p className={styles.feedbackMessage}>{feedbackMessage}</p>
                        </div>

                        <button
                            className={`${styles.submitButton} ${animatedButtonStyles.animatedButton}`}
                            onClick={handleAnalyzeAnother}
                        >
                            Analyze Another Text
                        </button>
                        <button type="button" className={styles.backButton} onClick={handleGoBack}>
                            <FaArrowLeft /> Back to Dashboard
                        </button>
                    </div>
                ) : (
                    <form onSubmit={handleSubmit} className={styles.analysisForm}>
                        <div className={styles.inputGroup}>
                            <label htmlFor="inputText" className={styles.label}>Text to Analyze:</label>
                            <textarea
                                id="inputText"
                                className={styles.textAreaInput}
                                value={inputText}
                                onChange={(e) => setInputText(e.target.value)}
                                rows="8"
                                required
                            ></textarea>
                        </div>

                        <div className={styles.inputGroup}>
                            <label className={styles.label}>Do you think this is Hate Speech?</label>
                            <div className={styles.radioGroup}>
                                <label className={styles.radioLabel}>
                                    <input
                                        type="radio"
                                        name="isHateSpeech"
                                        value="yes"
                                        checked={isHateSpeech === 'yes'}
                                        onChange={(e) => setIsHateSpeech(e.target.value)}
                                        className={styles.radioInput}
                                    />
                                    Yes, it is hate speech
                                </label>
                                <label className={styles.radioLabel}>
                                    <input
                                        type="radio"
                                        name="isHateSpeech"
                                        value="no"
                                        checked={isHateSpeech === 'no'}
                                        onChange={(e) => setIsHateSpeech(e.target.value)}
                                        className={styles.radioInput}
                                    />
                                    No, it is not hate speech
                                </label>
                            </div>
                        </div>

                        <div className={styles.inputGroup}>
                            <label htmlFor="reasoning" className={styles.label}>Your Reasoning:</label>
                            <textarea
                                id="reasoning"
                                className={styles.textAreaInput}
                                value={reasoning}
                                onChange={(e) => setReasoning(e.target.value)}
                                rows="5"
                                placeholder="Explain why you think it is or isn't hate speech..."
                                required
                            ></textarea>
                        </div>

                        <button type="submit" className={`${styles.submitButton} ${animatedButtonStyles.animatedButton}`}>
                            Submit Analysis
                        </button>
                        <button type="button" className={styles.backButton} onClick={handleGoBack}>
                            <FaArrowLeft /> Back to Dashboard
                        </button>
                    </form>
                )}
            </div>
        </div>
    );
};

export default HateSpeechIdentifier;