# OpenClaw Experiment

A FastAPI application deployed on Railway for testing purposes.

## Live URL

https://web-production-5d142.up.railway.app

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Root - basic info and health |
| `GET /health` | Health check with timestamp |
| `GET /api/info` | Project information |
| `GET /api/time` | Current server time (UTC) |
| `GET /api/headers` | Echo request headers |
| `GET /docs` | Interactive API documentation |

## Local Development

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Deployment

Deployed automatically to Railway on push to main branch.

```bash
git add .
git commit -m "Your changes"
git push origin main
```
