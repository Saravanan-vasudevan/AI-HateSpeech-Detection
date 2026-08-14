import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './MultiModelPrediction.module.css';
import config from '../config';
import animatedButtonStyles from '../styles/AnimatedButton.module.css';
import { FaChartBar, FaBrain, FaMagic, FaRobot, FaQuestion, FaExclamationTriangle, FaCheck, FaArrowLeft } from 'react-icons/fa';

const MultiModelPrediction = () => {
    const navigate = useNavigate();
    const [inputText, setInputText] = useState(
        "Some people are just naturally inferior due to their background."
    );
    const [userClassification, setUserClassification] = useState(null);
    const [userReasoning, setUserReasoning] = useState('');
    const [selectedAIModel, setSelectedAIModel] = useState('all'); // State for AI model selection ('all' or specific ID)
    const [isLoading, setIsLoading] = useState(false);
    const [showResults, setShowResults] = useState(false);
    const [modelPredictions, setModelPredictions] = useState([]); // Stores results from backend
    const [selectedModel, setSelectedModel] = useState(null); // The AI model the user prefers
    const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
    const [errorMessage, setErrorMessage] = useState(''); // To display API errors

    // Define available AI models and their corresponding backend paths/display info
    // Colors and icons are defined here, styles map these to CSS classes
    const aiModels = [
        {
            id: 'sklearn',
            name: 'Scikit-learn Model',
            description: 'Fast, traditional ML model',
            endpoint: '/sklearn/predict',
            icon: FaChartBar,
            className: styles.modelColorSklearn // CSS class for specific model color
        },
        {
            id: 'hf_generative',
            name: 'HuggingFace Generative',
            description: 'Contextual analysis from HuggingFace',
            endpoint: '/hf_generative/predict',
            icon: FaBrain,
            className: styles.modelColorHF // CSS class for specific model color
        },
        {
            id: 'gemini',
            name: 'Gemini Model',
            description: 'Google\'s advanced generative AI',
            endpoint: '/gemini/predict',
            icon: FaMagic,
            className: styles.modelColorGemini // CSS class for specific model color
        },
        {
            id: 'ollama',
            name: 'Ollama Llama 3',
            description: 'Local large language model',
            endpoint: '/ollama/predict',
            icon: FaRobot,
            className: styles.modelColorOllama // CSS class for specific model color
        }
    ];

    const handleSubmit = async () => {
        if (userClassification === null) {
            setErrorMessage("Please select whether you think the text is hate speech or not.");
            return;
        }
        if (!userReasoning.trim()) {
            setErrorMessage("Please provide your reasoning.");
            return;
        }

        setErrorMessage(''); // Clear previous errors
        setIsLoading(true);
        setShowResults(false);
        setModelPredictions([]);
        setSelectedModel(null);
        setFeedbackSubmitted(false);

        try {
            const accessToken = localStorage.getItem('access_token');
            if (!accessToken) {
                setErrorMessage('You must be logged in to analyze text.');
                setIsLoading(false);
                return;
            }

            let modelsToAnalyze = [];
            if (selectedAIModel === 'all') {
                modelsToAnalyze = aiModels;
            } else {
                const selected = aiModels.find(model => model.id === selectedAIModel);
                if (selected) {
                    modelsToAnalyze = [selected];
                } else {
                    setErrorMessage('Selected AI model not found. Please choose a valid model.');
                    setIsLoading(false);
                    return;
                }
            }

            // Create an array of promises for concurrent API calls
            const predictionPromises = modelsToAnalyze.map(async (model) => {
                const startTime = performance.now();
                try {
                    const response = await fetch(`${config.API_BASE_URL}${model.endpoint}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${accessToken}` // Add Authorization header
                        },
                        body: JSON.stringify({ text: inputText })
                    });

                    const data = await response.json();
                    
                    if (!response.ok) {
                        throw new Error(data.detail || `Model '${model.name}' failed with status ${response.status}`);
                    }
                    const endTime = performance.now();
                    return {
                        modelId: model.id,
                        isHateSpeech: data.is_hate_speech,
                        confidence: Math.round(data.hate_speech_probability * 100), // Assuming probability is 0-1
                        explanation: data.explanation,
                        processingTime: endTime - startTime
                    };
                } catch (error) {
                    console.error(`Error with model ${model.name}:`, error);
                    return {
                        modelId: model.id,
                        error: error.message || 'Analysis failed',
                        isHateSpeech: false, // Default for error display
                        confidence: 0,
                        explanation: 'Failed to get prediction for this model.',
                        processingTime: performance.now() - startTime
                    };
                }
            });

            // Use Promise.allSettled to wait for all requests to complete, even if some fail
            const results = await Promise.allSettled(predictionPromises);

            // Extract fulfilled values or reasons, filtering out reasons (errors) for successful predictions
            const successfulPredictions = results
                .filter(result => result.status === 'fulfilled')
                .map(result => result.value);
            
            // Log errors from rejected promises separately if needed, or display a general error summary
            const rejectedReasons = results
                .filter(result => result.status === 'rejected')
                .map(result => result.reason);

            if (successfulPredictions.length === 0 && rejectedReasons.length > 0) {
                setErrorMessage(`All model analyses failed: ${rejectedReasons.map(r => r.message || r).join('; ')}`);
            } else if (rejectedReasons.length > 0) {
                setErrorMessage(`Some models failed: ${rejectedReasons.map(r => r.message || r).join('; ')}`);
            }
            
            setModelPredictions(successfulPredictions);
            setShowResults(true);

        } catch (error) {
            console.error('Submission error:', error);
            setErrorMessage(`An unexpected error occurred during submission: ${error.message}.`);
        } finally {
            setIsLoading(false);
        }
    };

    const handleModelSelection = (modelId) => {
        setSelectedModel(modelId);
        setFeedbackSubmitted(false); // Reset feedback status when new model selected
    };

    const handleSubmitFeedback = async () => {
        if (!selectedModel) {
            setErrorMessage("Please select your preferred model prediction first.");
            return;
        }

        setIsLoading(true);
        setErrorMessage('');

        try {
            const accessToken = localStorage.getItem('access_token');
            if (!accessToken) {
                setErrorMessage('You must be logged in to submit feedback.');
                setIsLoading(false);
                return;
            }

            const selectedPrediction = modelPredictions.find(p => p.modelId === selectedModel);
            if (!selectedPrediction) {
                throw new Error("Selected model prediction data not found for feedback submission.");
            }

            // --- Log prediction to history (backend /history/ endpoint) ---
            const logResponse = await fetch(`${config.API_BASE_URL}/history/`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${accessToken}`
                },
                body: JSON.stringify({
                    text: inputText,
                    human_prediction: userClassification === 'yes',
                    ai_prediction: selectedPrediction.isHateSpeech,
                    human_explanation: userReasoning,
                    ai_explanation: selectedPrediction.explanation,
                    probability: selectedPrediction.confidence / 100 // Convert percentage back to float (0-1)
                })
            });

            if (!logResponse.ok) {
                const errorData = await logResponse.json();
                throw new Error(errorData.detail || "Failed to log history.");
            }

            setFeedbackSubmitted(true);
        } catch (error) {
            console.error('Feedback submission error:', error);
            setErrorMessage(`Error submitting feedback: ${error.message}.`);
        } finally {
            setIsLoading(false);
        }
    };

    const handleAnalyzeAnother = () => {
        setInputText("Some people are just naturally inferior due to their background.");
        setUserClassification(null);
        setUserReasoning('');
        setSelectedAIModel('all');
        setShowResults(false);
        setModelPredictions([]);
        setSelectedModel(null);
        setFeedbackSubmitted(false);
        setErrorMessage('');
    };

    const handleGoBack = () => {
        navigate('/dashboard');
    };

    // Helper function to find model details by ID (used for display)
    const getModelById = (id) => aiModels.find(m => m.id === id);

    // Function to determine if we should show single model results (original hate speech detector style)
    const shouldShowSingleModelResults = () => {
        return selectedAIModel !== 'all' && modelPredictions.length === 1 && !modelPredictions[0].error;
    };

    // Generate feedback message for single model results (reusing logic from HateSpeechIdentifier)
    const generateFeedbackMessage = () => {
        if (!shouldShowSingleModelResults() || modelPredictions.length === 0) return ''; // Only for single valid results

        const aiPrediction = modelPredictions[0];
        const userPredictionBool = userClassification === 'yes';
        
        if (userPredictionBool === aiPrediction.isHateSpeech) {
            let message = "Excellent! Your understanding aligns with the AI's analysis.";
            if (aiPrediction.isHateSpeech) {
                message += " This phrase often targets individuals based on their origins.";
            } else {
                message += " You correctly identified that this isn't hate speech as per current classification standards.";
            }
            return message;
        } else {
            return "Interesting! Your classification differs from the AI's. Let's look closer.";
        }
    };

    return (
        <div className={styles.predictionPageContainer}>
            <div className={styles.predictionBox}>
                <h1 className={styles.headerTitle}>Multi-Model Hate Speech Analysis</h1>
                <p className={styles.pageSubtitle}>
                    Compare predictions from multiple AI models and choose the most accurate result.
                </p>

                {errorMessage && <p className={styles.errorMessage}>{errorMessage}</p>}

                {isLoading ? (
                    <div className={styles.loadingState}>
                        <div className={styles.spinner}></div>
                        <p>{showResults ? 'Submitting your feedback...' : 'Analyzing text with selected AI models...'}</p>
                    </div>
                ) : showResults ? (
                    <div className={styles.resultsSection}>
                        <div className={styles.resultGroup}>
                            <h3 className={styles.resultTitle}>Text Analyzed:</h3>
                            <p className={styles.resultTextAnalyzed}>{inputText}</p>
                        </div>

                        <div className={styles.userAnalysisSection}>
                            <h3 className={styles.resultTitle}>Your Analysis:</h3>
                            <div className={styles.userAnalysisContent}>
                                <p><strong>Classification:</strong> 
                                    <span className={userClassification === 'yes' ? styles.hateSpeechClass : styles.notHateSpeechClass}>
                                        {userClassification === 'yes' ? 'Yes, it is hate speech' : 'No, it is not hate speech'}
                                    </span>
                                </p>
                                <p><strong>Your Reasoning:</strong></p>
                                <p className={styles.reasoningText}>{userReasoning}</p>
                            </div>
                        </div>

                        {shouldShowSingleModelResults() ? (
                            <div className={styles.singleModelResults}>
                                <div className={styles.comparisonGrid}>
                                    <div className={styles.studentColumn}>
                                        <h3>Your Analysis:</h3>
                                        <p><strong>Classification:</strong> 
                                            <span className={userClassification === 'yes' ? styles.hateSpeechClass : styles.notHateSpeechClass}>
                                                {userClassification === 'yes' ? 'Yes, it is hate speech' : 'No, it is not hate speech'}
                                            </span>
                                        </p>
                                        <p><strong>Your Reasoning:</strong></p>
                                        <p className={styles.reasoningText}>{userReasoning}</p>
                                    </div>

                                    <div className={styles.aiColumn}>
                                        <h3>AI's Analysis:</h3>
                                        <p><strong>Classification:</strong> 
                                            <span className={modelPredictions[0].isHateSpeech ? styles.hateSpeechClass : styles.notHateSpeechClass}>
                                                {modelPredictions[0].isHateSpeech ? 'Yes, it is hate speech' : 'No, it is not hate speech'}
                                            </span>
                                        </p>
                                        <p><strong>AI's Explanation:</strong></p>
                                        <p className={styles.reasoningText}>{modelPredictions[0].explanation}</p>
                                    </div>
                                </div>
                                
                                <div className={styles.feedbackSection}>
                                    <h3 className={styles.resultTitle}>Feedback:</h3>
                                    <p className={styles.feedbackMessage}>{generateFeedbackMessage()}</p>
                                </div>
                            </div>
                        ) : (
                            <div className={styles.modelsSection}>
                                <h3 className={styles.resultTitle}>AI Model Predictions:</h3>
                                <div className={styles.modelsGrid}>
                                    {modelPredictions.map(prediction => {
                                        // Handle errors from Promise.allSettled (rejected promises)
                                        if (prediction && prediction.error) {
                                            const model = aiModels.find(m => prediction.modelId === m.id) || { name: 'Unknown Model', icon: FaQuestion };
                                            return (
                                                <div key={model.id || prediction.modelId || Math.random()} className={`${styles.modelCard} ${styles.errorCard}`}>
                                                    <div className={styles.modelHeader}>
                                                        <span className={styles.modelIcon}><FaExclamationTriangle /></span>
                                                        <div className={styles.modelInfo}>
                                                            <h4 className={styles.modelName}>{model.name}</h4>
                                                            <p className={styles.modelDescription}>Error during prediction.</p>
                                                        </div>
                                                    </div>
                                                    <p className={styles.predictionExplanation} style={{ color: 'var(--error-color)' }}>
                                                        {prediction.error || 'An error occurred.'}
                                                    </p>
                                                </div>
                                            );
                                        }

                                        const model = getModelById(prediction.modelId);
                                        const isSelected = selectedModel === prediction.modelId;
                                        
                                        return (
                                            <div 
                                                key={prediction.modelId}
                                                className={`${styles.modelCard} ${isSelected ? styles.selected : ''} ${model.className}`} // Apply model-specific color class
                                                onClick={() => handleModelSelection(prediction.modelId)}
                                            >
                                                <div className={styles.modelHeader}>
                                                    <span className={styles.modelIcon}><model.icon /></span>
                                                    <div className={styles.modelInfo}>
                                                        <h4 className={styles.modelName}>{model.name}</h4>
                                                        <p className={styles.modelDescription}>{model.description}</p>
                                                    </div>
                                                    <div className={styles.confidenceScore}>
                                                        {prediction.confidence}%
                                                    </div>
                                                </div>
                                                
                                                <div className={styles.modelPrediction}>
                                                    <p className={styles.predictionResult}>
                                                        <strong>Classification:</strong>
                                                        <span className={prediction.isHateSpeech ? styles.hateSpeechClass : styles.notHateSpeechClass}>
                                                            {prediction.isHateSpeech ? 'Hate Speech' : 'Not Hate Speech'}
                                                        </span>
                                                    </p>
                                                    <p className={styles.predictionExplanation}>
                                                        <strong>Explanation:</strong> {prediction.explanation}
                                                    </p>
                                                    <p className={styles.processingTime}>
                                                        Processing time: {Math.round(prediction.processingTime)}ms
                                                    </p>
                                                </div>
                                                
                                                {isSelected && (
                                                    <div className={styles.selectionIndicator}>
                                                        <span><FaCheck /> Selected as preferred prediction</span>
                                                    </div>
                                                )}
                                            </div>
                                        );
                                    })}
                                </div>

                                {selectedModel && !feedbackSubmitted && (
                                    <div className={styles.feedbackSection}>
                                        <h3 className={styles.resultTitle}>Submit Your Preference:</h3>
                                        <p className={styles.feedbackMessage}>
                                            You've selected <strong>{getModelById(selectedModel).name}</strong> as the most accurate prediction.
                                        </p>
                                        <button 
                                            className={`${styles.submitFeedbackButton} ${animatedButtonStyles.animatedButton}`}
                                            onClick={handleSubmitFeedback}
                                            disabled={isLoading}
                                        >
                                            Submit Feedback
                                        </button>
                                    </div>
                                )}

                                {feedbackSubmitted && (
                                    <div className={styles.successMessage}>
                                        <h3 className={styles.resultTitle}>Thank You!</h3>
                                        <p>Your feedback has been recorded. This helps improve our AI models' accuracy.</p>
                                    </div>
                                )}
                            </div>
                        )}

                        <div className={styles.actionButtons}>
                            <button 
                                className={`${styles.analyzeAnotherButton} ${animatedButtonStyles.animatedButton}`}
                                onClick={handleAnalyzeAnother}
                            >
                                Analyze Another Text
                            </button>
                            <button 
                                className={`${styles.backButton} ${animatedButtonStyles.animatedButton}`} 
                                onClick={handleGoBack}
                            >
                                <FaArrowLeft /> Back to Dashboard
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className={styles.analysisForm}>
                        <div className={styles.inputGroup}>
                            <label htmlFor="inputText" className={styles.label}>Text to Analyze:</label>
                            <textarea
                                id="inputText"
                                className={styles.textAreaInput}
                                value={inputText}
                                onChange={(e) => setInputText(e.target.value)}
                                rows="8"
                                required
                            />
                        </div>

                        <div className={styles.inputGroup}>
                            <label className={styles.label}>Do you think this is Hate Speech?</label>
                            <div className={styles.radioGroup}>
                                <label className={styles.radioLabel}>
                                    <input
                                        type="radio"
                                        name="isHateSpeech"
                                        value="yes"
                                        checked={userClassification === 'yes'}
                                        onChange={(e) => setUserClassification(e.target.value)}
                                        className={styles.radioInput}
                                    />
                                    Yes, it is hate speech
                                </label>
                                <label className={styles.radioLabel}>
                                    <input
                                        type="radio"
                                        name="isHateSpeech"
                                        value="no"
                                        checked={userClassification === 'no'}
                                        onChange={(e) => setUserClassification(e.target.value)}
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
                                value={userReasoning}
                                onChange={(e) => setUserReasoning(e.target.value)}
                                rows="5"
                                placeholder="Explain why you think it is or isn't hate speech..."
                                required
                            />
                        </div>

                        <div className={styles.inputGroup}>
                            <div className={styles.aiModelSelect}>
                                <label htmlFor="aiModelSelect" className={styles.label}>Choose AI Model(s) for Analysis:</label>
                                <select
                                    id="aiModelSelect"
                                    className={styles.aiModelDropdown}
                                    value={selectedAIModel}
                                    onChange={(e) => setSelectedAIModel(e.target.value)}
                                >
                                    <option value="all">All Models (Compare Multiple)</option>
                                    {aiModels.map(model => (
                                        <option key={model.id} value={model.id}>
                                            {model.name} - {model.description}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        <button 
                            className={`${styles.submitButton} ${animatedButtonStyles.animatedButton}`}
                            onClick={handleSubmit}
                        >
                            {selectedAIModel === 'all' ? 'Analyze with Multiple Models' : 'Analyze with Selected Model'}
                        </button>
                        <button 
                            className={`${styles.backButton} ${animatedButtonStyles.animatedButton}`} 
                            onClick={handleGoBack}
                        >
                            <FaArrowLeft /> Back to Dashboard
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default MultiModelPrediction;