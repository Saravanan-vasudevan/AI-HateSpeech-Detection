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

A FastAPI backend with independent `/predict` endpoints for four approaches:
TF-IDF + Logistic Regression, a RoBERTa hate-speech classifier with a local
explanation model, Google Gemini, and a self-hosted Ollama/Llama 3 instance.
A fifth endpoint uses Gemini to generate natural-language feedback explaining
*why* text got flagged, which is the pedagogical angle of the project.

The frontend is a Vite + React SPA with student and teacher roles. Students
submit text, compare model outputs side-by-side, take a quiz on recognising
hate speech, and accumulate points. Teachers register students, view
class-wide prediction history, and check a leaderboard.

An early Streamlit version was replaced with Vite and React because the
student and teacher screens needed more control over navigation and state.
The interface uses readable type, clear labels and keyboard-friendly native
controls, but it has not had a formal WCAG audit.

Training data comes from Davidson, Jigsaw, HateSpeech18, ToxiGen, TweetEval,
and a few others. Per-dataset cleaning scripts and the Hugging Face RoBERTa classifier
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
    train/         Experimental transformer and BiLSTM training scripts
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
cp .env.example credentials.env
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
- A local sklearn artifact if you want the Logistic Regression endpoint; model binaries are not stored in Git
- Gemini and Ollama are optional. Their endpoints return 503 when the related configuration is absent

## Model Performance & Metrics

![Main UI](assets/Screenshot%202026-08-16%20155709.png)

## Hugging Face model setup

- **Base model:** `facebook/roberta-hate-speech-dynabench-r4-target`
- **Framework:** HuggingFace Transformers + PyTorch

The application uses `facebook/roberta-hate-speech-dynabench-r4-target` as
the classifier. The repository contains experimental per-dataset DistilBERT
training scripts, but it does not claim that those scripts produced the
application's RoBERTa checkpoint. Download the application models with
`python -m app.models.download_hf_generative` from the `backend` directory.

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
- English-language only.
- Model binaries and the full training datasets are not committed, so model
  training and the application setup are separate steps.

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
