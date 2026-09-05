import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './GamifiedQuiz.module.css';
import animatedButtonStyles from '../Styles/AnimatedButton.module.css';
import config from '../config';
import { FaArrowLeft } from 'react-icons/fa';

const GamifiedQuiz = () => {
    const navigate = useNavigate();

    const [quizStarted, setQuizStarted] = useState(false);
    const [currentQuestion, setCurrentQuestion] = useState(null);
    const [selectedAnswerIndex, setSelectedAnswerIndex] = useState(null);
    const [feedbackMessage, setFeedbackMessage] = useState('');
    const [showFeedback, setShowFeedback] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [quizEnded, setQuizEnded] = useState(false);
    const [finalScore, setFinalScore] = useState(0);
    const [correctAnswerIndex, setCorrectAnswerIndex] = useState(null);
    const [difficulty, setDifficulty] = useState(0);

    const username = localStorage.getItem('access_token') || 'test_student';
    const numQuestions = 10;
    const QUIZ_API_BASE_URL = config.API_BASE_URL + '/quiz';

    const fetchQuestion = async () => {
        setIsLoading(true);
        setFeedbackMessage('');
        setShowFeedback(false);
        setSelectedAnswerIndex(null);
        setCorrectAnswerIndex(null);

        try {
            const accessToken = localStorage.getItem('access_token');
            if (!accessToken) {
                alert('You must be logged in to play the quiz.');
                setIsLoading(false);
                return;
            }
            const response = await fetch(`${QUIZ_API_BASE_URL}/next_question`, {
                method: 'GET',
                headers: { 'Accept': 'application/json', 'Authorization': `Bearer ${accessToken}` },
            });
            setIsLoading(false);
            if (response.ok) {
                if (response.status === 204) {
                    setQuizEnded(true);
                    return null;
                }
                const data = await response.json();
                setCurrentQuestion(data);
                return data;
            } else {
                const errorData = await response.json();
                alert(`Error fetching question: ${errorData.detail || 'Unknown error'}`);
                return null;
            }
        } catch (error) {
            setIsLoading(false);
            alert('Network error. Could not connect to quiz server.');
            return null;
        }
    };

    const submitAnswer = async () => {
        if (selectedAnswerIndex === null) {
            alert('Please select an answer!');
            return;
        }
        setIsLoading(true);
        setFeedbackMessage('');
        try {
            const accessToken = localStorage.getItem('access_token');
            if (!accessToken) {
                alert('You must be logged in to submit an answer.');
                setIsLoading(false);
                return;
            }
            const response = await fetch(`${QUIZ_API_BASE_URL}/submit_answer`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': `Bearer ${accessToken}` },
                body: JSON.stringify({ selected_answer_index: selectedAnswerIndex }),
            });
            setIsLoading(false);
            if (response.ok) {
                const data = await response.json();
                setFeedbackMessage(data.is_correct ? 'Correct!' : 'Incorrect!');
                setCorrectAnswerIndex(data.correct_answer_index);
                setShowFeedback(true);
                return data.is_correct;
            } else {
                const errorData = await response.json();
                alert(`Error submitting answer: ${errorData.detail || 'Unknown error'}`);
                return false;
            }
        } catch (error) {
            setIsLoading(false);
            alert('Network error. Could not connect to quiz server.');
            return false;
        }
    };

    const fetchScore = async () => {
        setIsLoading(true);
        try {
            const accessToken = localStorage.getItem('access_token');
            if (!accessToken) {
                alert('You must be logged in to fetch your score.');
                setIsLoading(false);
                return;
            }
            const response = await fetch(`${QUIZ_API_BASE_URL}/score`, {
                method: 'GET',
                headers: { 'Accept': 'application/json', 'Authorization': `Bearer ${accessToken}` },
            });
            setIsLoading(false);
            if (response.ok) {
                const data = await response.json();
                setFinalScore(data.score);
                setQuizEnded(true);
            } else {
                const errorData = await response.json();
                alert(`Error fetching score: ${errorData.detail || 'Unknown error'}`);
            }
        } catch (error) {
            setIsLoading(false);
            alert('Network error. Could not connect to quiz server.');
        }
    };

    const checkHasQuestion = async () => {
        try {
            const accessToken = localStorage.getItem('access_token');
            if (!accessToken) return false;
            const response = await fetch(`${QUIZ_API_BASE_URL}/has_question`, {
                method: 'GET',
                headers: { 'Accept': 'application/json', 'Authorization': `Bearer ${accessToken}` },
            });
            if (response.ok) {
                const data = await response.json();
                return data.has_more_questions;
            }
            return false;
        } catch (error) {
            console.error("Error checking has_question:", error);
            return false;
        }
    };

    const handleStartQuiz = async () => {
        setIsLoading(true);
        try {
            const accessToken = localStorage.getItem('access_token');
            if (!accessToken) {
                alert('You must be logged in to play the quiz.');
                setIsLoading(false);
                return;
            }
            const response = await fetch(`${QUIZ_API_BASE_URL}/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': `Bearer ${accessToken}` },
                body: JSON.stringify({ username, hardness: difficulty, num_questions: numQuestions }),
            });
            setIsLoading(false);
            if (response.ok) {
                const data = await response.json();
                setCurrentQuestion(data);
                setQuizStarted(true);
                setQuizEnded(false);
                setFinalScore(0);
                setFeedbackMessage('');
                setShowFeedback(false);
                setSelectedAnswerIndex(null);
                setCorrectAnswerIndex(null);
            } else {
                const errorData = await response.json();
                alert(`Error starting quiz: ${errorData.detail || 'Unknown error'}`);
            }
        } catch (error) {
            setIsLoading(false);
            alert('Network error. Could not connect to quiz server.');
        }
    };

    const handleAnswerAndAdvance = async () => {
        if (selectedAnswerIndex === null) return;

        await submitAnswer();
        setTimeout(async () => {
            const hasMore = await checkHasQuestion();
            if (hasMore) {
                fetchQuestion();
            } else {
                fetchScore();
            }
        }, 1500);
    };

    const handlePlayAgain = () => {
        setQuizStarted(false);
        setQuizEnded(false);
    };

    const handleGoToDashboard = () => navigate('/dashboard');

    return (
        <div className={styles.quizPageContainer}>
            <div className={styles.quizBox}>
                <h1 className={styles.headerTitle}>Gamified Quiz</h1>
                <p className={styles.pageSubtitle}>Test your knowledge on hate speech.</p>

                {isLoading ? (
                    <div className={styles.loadingState}>
                        <div className={styles.spinner}></div><p>Loading...</p>
                    </div>
                ) : quizEnded ? (
                    <div className={styles.quizEndScreen}>
                        <h2 className={styles.resultTitle}>Quiz Completed!</h2>
                        <p className={styles.finalScore}>Your Score: <span className={styles.pointsValue}>{finalScore}</span> points</p>
                        <button className={`${styles.submitButton} ${animatedButtonStyles.animatedButton}`} onClick={handlePlayAgain}>Play Again</button>
                        <button type="button" className={styles.backButton} onClick={handleGoToDashboard}><FaArrowLeft /> Back to Dashboard</button>
                    </div>
                ) : quizStarted && currentQuestion ? (
                    <div className={styles.quizActiveScreen}>
                        <div className={styles.questionDisplay}>
                            <p className={styles.questionText}>{currentQuestion.question_text}</p>
                            <div className={styles.optionsGroup}>
                                {currentQuestion.options.map((option, index) => (
                                    <button
                                        key={index}
                                        className={`${styles.optionButton} ${selectedAnswerIndex === index ? styles.selected : ''} ${showFeedback && index === correctAnswerIndex ? styles.correct : ''} ${showFeedback && selectedAnswerIndex === index && selectedAnswerIndex !== correctAnswerIndex ? styles.incorrect : ''}`}
                                        onClick={() => setSelectedAnswerIndex(index)}
                                        disabled={showFeedback || isLoading}
                                    >
                                        {`${String.fromCharCode(65 + index)}. ${option}`}
                                    </button>
                                ))}
                            </div>
                        </div>
                        {showFeedback && <p className={feedbackMessage === 'Correct!' ? styles.correctFeedback : styles.incorrectFeedback}>{feedbackMessage}</p>}
                        <button className={`${styles.submitButton} ${animatedButtonStyles.animatedButton}`} onClick={handleAnswerAndAdvance} disabled={isLoading || selectedAnswerIndex === null || showFeedback}>Submit Answer</button>
                        <button type="button" className={styles.backButton} onClick={handleGoToDashboard}><FaArrowLeft /> Back to Dashboard</button>
                    </div>
                ) : (
                    <div className={styles.quizStartScreen}>
                        <p className={styles.startInstruction}>Ready to test your knowledge?</p>
                        <div className={styles.difficultySelector}>
                            <label htmlFor="difficulty-select">Select Difficulty:</label>
                            <select id="difficulty-select" value={difficulty} onChange={(e) => setDifficulty(parseInt(e.target.value, 10))} className={styles.selectDropdown}>
                                <option value={0}>Easy</option>
                                <option value={1}>Medium</option>
                                <option value={2}>Hard</option>
                            </select>
                        </div>
                        <button className={`${styles.submitButton} ${animatedButtonStyles.animatedButton}`} onClick={handleStartQuiz} disabled={isLoading}>Start Quiz</button>
                        <button type="button" className={styles.backButton} onClick={handleGoToDashboard}><FaArrowLeft /> Back to Dashboard</button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default GamifiedQuiz;