from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="OpenClaw Experiment",
    description="A FastAPI application for testing Railway deployments",
    version="1.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
    return response

@app.get("/")
async def root():
    return {
        "message": "OpenClaw Experiment is running!",
        "status": "healthy",
        "version": "1.1.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "openclaw-experiment"
    }

@app.get("/api/info")
async def info():
    return {
        "project": "openclaw-experiment",
        "description": "A test deployment for Railway",
        "environment": os.environ.get("RAILWAY_ENVIRONMENT", "development"),
        "version": "1.1.0"
    }

@app.get("/api/time")
async def get_time():
    """Get current server time in various formats"""
    now = datetime.utcnow()
    return {
        "utc": now.isoformat(),
        "timestamp": int(now.timestamp()),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S")
    }

@app.get("/api/headers")
async def get_headers(request: Request):
    """Echo back request headers (useful for debugging)"""
    return {
        "headers": dict(request.headers),
        "client": request.client.host if request.client else None,
        "method": request.method,
        "url": str(request.url)
    }
