# Deployment (Google Cloud Run)

## Build

```bash
gcloud builds submit --tag europe-west2-docker.pkg.dev/<PROJECT_ID>/hate-backend/hate-backend \
  --machine-type=E2_HIGHCPU_32 .
```

## Deploy

```bash
gcloud run deploy hate-backend \
  --image europe-west2-docker.pkg.dev/<PROJECT_ID>/hate-backend/hate-backend:latest \
  --platform managed \
  --region europe-west2 \
  --allow-unauthenticated \
  --memory=8Gi --cpu=4 \
  --set-secrets="DB_PASSWORD=db-password:latest,GEMINI_API_KEY=gemini-api-key:latest,JWT_SECRET=jwt-secret:latest" \
  --set-env-vars="DB_STRING=<YOUR_MONGODB_CONNECTION_STRING>,OLLAMA_API_URL=<YOUR_OLLAMA_ENDPOINT>"
```

Replace `<PROJECT_ID>`, `<YOUR_MONGODB_CONNECTION_STRING>`, and
`<YOUR_OLLAMA_ENDPOINT>` with your own values. Store `DB_PASSWORD`,
`GEMINI_API_KEY`, and `JWT_SECRET` in Google Secret Manager (via
`--set-secrets`) rather than as plain environment variables -- never commit
real values for any of these to the repo. See `backend/.env.example` for the
full list of variables the app expects locally.
