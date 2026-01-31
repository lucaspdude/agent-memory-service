# OpenClaw Experiment Tests

Simple tests for the FastAPI application.

## Running Tests

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest test_main.py -v
```

## Manual Testing

```bash
# Start the server
uvicorn main:app --reload

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/info
curl http://localhost:8000/api/random
curl "http://localhost:8000/api/hash/hello?algorithm=sha256"
curl http://localhost:8000/api/ip
```
