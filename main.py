from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pydantic import BaseModel
import os
import time
import logging
import psutil
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Request/Response models
class EchoRequest(BaseModel):
    message: str
    delay: float = 0.0
    uppercase: bool = False

class EchoResponse(BaseModel):
    original: str
    echoed: str
    timestamp: str
    processing_time_ms: float

app = FastAPI(
    title="OpenClaw Experiment",
    description="A FastAPI application for testing Railway deployments",
    version="1.2.0"
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
        "version": "1.2.0",
        "docs": "/docs",
        "endpoints": [
            "/health",
            "/api/info",
            "/api/time",
            "/api/headers",
            "/api/metrics",
            "/api/echo (POST)",
            "/api/random"
        ]
    }

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "openclaw-experiment",
        "version": "1.2.0"
    }

@app.get("/api/info")
async def info():
    return {
        "project": "openclaw-experiment",
        "description": "A test deployment for Railway",
        "environment": os.environ.get("RAILWAY_ENVIRONMENT", "development"),
        "version": "1.2.0",
        "python_version": os.sys.version,
        "features": [
            "Health checks",
            "Request header echo",
            "System metrics",
            "Message echo with transformation",
            "Random token generation"
        ]
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

@app.get("/api/metrics")
async def get_metrics():
    """Get system metrics and application stats"""
    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "system": {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory": {
                    "total_mb": round(memory.total / (1024 * 1024), 2),
                    "available_mb": round(memory.available / (1024 * 1024), 2),
                    "percent_used": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "percent_used": round(disk.used / disk.total * 100, 2)
                }
            },
            "app": {
                "version": "1.2.0",
                "environment": os.environ.get("RAILWAY_ENVIRONMENT", "development"),
                "service_name": os.environ.get("RAILWAY_SERVICE_NAME", "unknown")
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")

@app.post("/api/echo", response_model=EchoResponse)
async def echo_message(request: EchoRequest):
    """Echo back a message with optional transformation"""
    start_time = time.time()
    
    # Simulate processing delay if requested
    if request.delay > 0:
        await asyncio.sleep(request.delay)
    
    # Transform message
    echoed = request.message
    if request.uppercase:
        echoed = echoed.upper()
    else:
        echoed = echoed.lower()
    
    processing_time = (time.time() - start_time) * 1000
    
    return EchoResponse(
        original=request.message,
        echoed=echoed,
        timestamp=datetime.utcnow().isoformat(),
        processing_time_ms=round(processing_time, 2)
    )

@app.get("/api/random")
async def get_random():
    """Generate a random UUID and token"""
    import uuid
    import secrets
    
    return {
        "uuid": str(uuid.uuid4()),
        "uuidv4": str(uuid.uuid4()),
        "token": secrets.token_urlsafe(32),
        "hex": secrets.token_hex(16),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if os.environ.get("DEBUG") else "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
