# OpenClaw Experiment

A FastAPI application deployed on Railway for testing purposes.

## Live URL

https://web-production-5d142.up.railway.app

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root - basic info and health |
| `/health` | GET | Health check with timestamp |
| `/api/info` | GET | Project information |
| `/api/time` | GET | Current server time (UTC) |
| `/api/headers` | GET | Echo request headers |
| `/api/metrics` | GET | System metrics (CPU, memory, disk) |
| `/api/echo` | POST | Echo message with transformation |
| `/api/random` | GET | Generate random UUIDs and tokens |
| `/api/hash/{data}` | GET | Generate hash of input data (sha256, sha512, md5, etc.) |
| `/api/ip` | GET | Get client IP and connection info |
| `/docs` | GET | Interactive API documentation |

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
