# Hate Speech Detection Platform

![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688)
![React](https://img.shields.io/badge/frontend-React%2019-61DAFB)
![License](https://img.shields.io/badge/license-MIT-green)

A full-stack platform for detecting and explaining hate speech in text,
combining multiple machine learning backends (a classical TF-IDF/Logistic
Regression model, a fine-tuned Hugging Face classifier, and cloud LLMs via
Gemini and Ollama) behind a single FastAPI service, with a React frontend
that includes a gamified quiz for learning to recognize harmful content and
a leaderboard to track progress.

## Description

The backend exposes independent endpoints for each detection model so
predictions can be compared side by side, along with supporting services for
user accounts, prediction history, a points/leaderboard system, and an
LLM-generated feedback explainer that describes *why* a piece of text was
flagged. The frontend is a Vite + React single-page app with dedicated
student and teacher views: students can run text through the models, take a
gamified quiz, and review their prediction history; teachers can register
students, review class-wide activity, and manage the leaderboard.

Models are trained against a combination of public hate speech datasets
(Davidson, Jigsaw, HateSpeech18, ToxiGen, TweetEval, Ethos, Dynabench, and
others) with per-dataset cleaning scripts and DistilBERT fine-tuning scripts
included under `backend/ml/`.

## Features

- Multi-model prediction comparison (Logistic Regression, Hugging Face
  classifier, Gemini, Ollama/Llama 3) behind a unified API
- LLM-generated natural-language explanations for why text was flagged
- User authentication and role-based access (student vs. teacher)
- Prediction history per user, with teacher visibility into any student's
  history
- Gamified quiz mode with a points system and class leaderboard
- Dataset preparation and DistilBERT fine-tuning scripts for six public hate
  speech datasets
- Dockerized backend, ready for Cloud Run deployment

## Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- A MongoDB instance (Atlas or self-hosted)
- API keys for Gemini (and optionally a hosted Ollama endpoint)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python download_nltk.py         # fetches required NLTK corpora
cp .env.example credentials.env # then fill in your own DB/API credentials
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend expects the backend at the URL configured in
`frontend/src/config.js`; update it if you're not running both locally on
default ports.

## Usage

1. Start the backend and frontend as above.
2. Register a student or teacher account through the app's login flow.
3. From the student dashboard, submit text to the "Hate Speech Identifier"
   page to get predictions and explanations from all available models, or
   launch the gamified quiz to earn points.
4. Teachers can view the class leaderboard and drill into any individual
   student's prediction history from the teacher menu.

To train or re-evaluate a model against the bundled datasets, see the
scripts in `backend/ml/train/` and `backend/ml/evaluate/`.

## License

Released under the MIT License. See `LICENSE` for details.
