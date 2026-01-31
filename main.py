from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os

app = FastAPI(title="OpenClaw Experiment")

@app.get("/")
async def root():
    return {
        "message": "OpenClaw Experiment is running!",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/api/info")
async def info():
    return {
        "project": "openclaw-experiment",
        "description": "A test deployment for Railway",
        "environment": os.environ.get("RAILWAY_ENVIRONMENT", "development")
    }
