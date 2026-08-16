# ---- Hate Speech Detection Platform ----
# Assumes Python 3.11+ and Node 18+ are installed.

.PHONY: install install-backend install-frontend run run-backend run-frontend dev clean

# -- Setup --

install: install-backend install-frontend

install-backend:
	cd backend && python -m venv venv \
		&& . venv/bin/activate \
		&& pip install -r requirements.txt \
		&& python download_nltk.py
	@echo ""
	@echo "Backend deps installed. Copy .env.example -> credentials.env and fill it in:"
	@echo "  cp backend/.env.example backend/credentials.env"

install-frontend:
	cd frontend && npm install

# -- Run --

run: run-backend

run-backend:
	cd backend && . venv/bin/activate && uvicorn app.main:app --reload --port 8000

run-frontend:
	cd frontend && npm run dev

# Start both backend and frontend (requires two terminals, or use this with &)
dev:
	@echo "Starting backend on :8000 and frontend on :5173 ..."
	@echo "Press Ctrl-C to stop both."
	cd backend && . venv/bin/activate && uvicorn app.main:app --reload --port 8000 &
	cd frontend && npm run dev

# -- Misc --

clean:
	rm -rf backend/venv frontend/node_modules
