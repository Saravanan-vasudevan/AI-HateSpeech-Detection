# Hate Speech Detection Platform

![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688)
![React](https://img.shields.io/badge/frontend-React%2019-61DAFB)
![License](https://img.shields.io/badge/license-MIT-green)

Multi-model hate speech detection API with a React frontend, built for a
university project. Online discourse has grown more polarized while human
moderation resources at major platforms have shrunk, and most existing
AI moderation tools are opaque about *why* they flag content and are
trained almost entirely on English-language data. This project explores
how different ML approaches (classical, fine-tuned transformer, cloud LLM)
compare on the same classification task, and pairs the predictions with a
plain-language explanation, aiming at a lightweight, explainable assistant
for moderators rather than an opaque black box.

The MVP was scoped and built within a four-week window, prioritizing
usability, explainability, and cost-efficiency over exhaustive model
coverage.

## What this is

![Main UI](assets/Screenshot%202026-08-16%20153826.png)

A FastAPI backend that exposes independent `/predict` endpoints for four
models — TF-IDF + Logistic Regression, a fine-tuned DistilBERT classifier
(via HuggingFace), Google Gemini, and a self-hosted Ollama/Llama 3 instance.
A fifth endpoint uses Gemini to generate natural-language feedback explaining
*why* text got flagged, which is the pedagogical angle of the project.

The frontend is a Vite + React SPA with student and teacher roles. Students
submit text, compare model outputs side-by-side, take a quiz on recognising
hate speech, and accumulate points. Teachers register students, view
class-wide prediction history, and check a leaderboard.

The stack was deliberately chosen over a simpler Python-only UI: an initial
Streamlit-based plan was dropped in favor of Vite + React because Streamlit
proved too restrictive for the interactive, component-heavy dashboards and
analysis tools the project needed, and React's component structure allowed
building a scalable, genuinely usable app within the four-week timeline.
The visual design follows WCAG accessibility guidelines to keep the
platform usable for a wider audience, using Red Hat Display and Red Hat
Text for improved readability.

Training data comes from Davidson, Jigsaw, HateSpeech18, ToxiGen, TweetEval,
and a few others. Per-dataset cleaning scripts and the DistilBERT fine-tuning
script live under `backend/ml/`.

## Architecture

```
frontend/          Vite + React 19 SPA
backend/
  app/
    main.py        FastAPI entrypoint, lifespan, CORS, router wiring
    models/        Model wrappers (sklearn, HF, Gemini, Ollama) + shared API router
    utils/         DB helpers, NLP preprocessing, auth (JWT + bcrypt)
    history/       Prediction logging and retrieval
    quiz/          Quiz game logic + question bank (JSON)
    points/        Scoring + leaderboard
  ml/
    data_prep/     Dataset download and cleaning scripts
    train/         Training scripts (TF-IDF, DistilBERT, BiLSTM)
    evaluate/      Evaluation scripts per model
  Dockerfile       Multi-stage build for Cloud Run
```

## How to Run

The fastest path from clone to running app:

```bash
# 1. Install everything
make install

# 2. Set up credentials (MongoDB, Gemini key, Ollama URL, JWT secret)
cp backend/.env.example backend/credentials.env
# ... edit credentials.env with your values

# 3. Start the backend (default port 8000)
make run-backend

# 4. In another terminal, start the frontend (port 5173)
make run-frontend
```

Or do it manually without the Makefile:

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pip install "bcrypt<4.0.0" # Required for passlib compatibility
python download_nltk.py
cp backend/.env.example backend/.env
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

The frontend hits the backend URL set in `frontend/src/config.js` — update it
if you changed the port or are running on a remote host.

### Docker

```bash
cd backend
docker build -t hate-backend .
docker run -p 8080:8080 --env-file credentials.env hate-backend
```

See `backend/deployment.md` for Cloud Run deploy commands.

### Prerequisites

- Python 3.11+, Node 18+
- A MongoDB instance (Atlas free tier works)
- Gemini API key (free tier: https://ai.google.dev)
- An Ollama endpoint if you want the Llama 3 model (otherwise the other three still work)

## Model Performance & Metrics

![Main UI](assets/Screenshot%202026-08-16%20155709.png)

Formal benchmarking (accuracy, precision, recall, F1) across the four
production models hasn't been run yet — see `backend/ml/evaluate/` to
produce it. The TF-IDF + Logistic Regression model is the fastest at
inference (~2ms/request). A fifth model, a BiLSTM + GloVe classifier, is
trained with evaluation scripts available but has not yet been
benchmarked head-to-head against the other four (see Future Work).

## DistilBERT Training Setup

- **Base model:** `facebook/roberta-hate-speech-dynabench-r4-target`
- **Framework:** HuggingFace Transformers + PyTorch

The fine-tuning script is at `backend/ml/train/train_distilbert.py`.
The generative explanation model (GPT-Neo 125M) is downloaded separately via
`python -m app.models.download_hf_generative`.

## Usage

1. Start backend + frontend (see above).
2. Register a student or teacher account through the login page.
3. Students: submit text on the "Hate Speech Identifier" page to get
   predictions from all models, or take the quiz to earn points.
4. Teachers: view the class leaderboard, drill into any student's history.
5. Creating the First Admin: Because a new database is empty, you must create the initial Teacher account via the backend API. Go to http://localhost:8000/docs, find the POST /register endpoint and execute a request with "role": "admin" to seed your first user.

To retrain or evaluate a model, see the scripts under `backend/ml/train/`
and `backend/ml/evaluate/`.

## Known Limitations

- Single-classroom only; there's no multi-tenancy for separate classes.
- The Teacher Dashboard supports adding users and viewing student
  histories, but doesn't yet have full CRUD (update/delete) for user
  management.
- English-language only, which limits applicability to the platform's
  broader goal of addressing global moderation challenges.

## Future Work

- **BiLSTM + GloVe integration.** A BiLSTM classifier using GloVe 300d
  embeddings is trained and has evaluation scripts (`backend/ml/train/train_bilstm_glove.py`,
  `backend/ml/evaluate/Evaluate_BiLSTM_Glove.py`), but it hasn't been
  benchmarked head-to-head against the other four models yet. The model
  wrapper exists at `backend/app/models/bilstm_glove_model.py` — wiring it
  into the API is straightforward once the benchmarks justify adding a fifth
  prediction card to the frontend.
- Multi-tenancy to support multiple, distinct classrooms.
- Full CRUD functionality for user management in the Teacher Dashboard.
- Multilingual support for the AI models.
- A more immersive "tell-tale" style, turn-based scenario game to simulate
  real-life moderation challenges more accurately.
- Batch prediction endpoint for bulk CSV analysis.
- Confidence calibration across models (Platt scaling or similar).
- Frontend accessibility audit.
- User testing with local schools to validate the feature set and surface
  new use cases.

## License

MIT. See `LICENSE`.
