from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import aiohttp
import asyncio
from .api.endpoints import flashcards

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Notes Generator API",
    description="API for generating flashcards from PDF documents",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    flashcards.router,
    prefix="/api/v1/flashcards",
    tags=["flashcards"]
)

@app.get("/")
async def root():
    return {"message": "AI Notes Generator API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.exception_handler(aiohttp.ClientError)
async def client_error_handler(request: Request, exc: aiohttp.ClientError):
    logger.error(f"Network error occurred: {str(exc)}")
    return JSONResponse(
        status_code=503,
        content={"detail": "Service temporarily unavailable. Please try again later."}
    )

@app.exception_handler(asyncio.TimeoutError)
async def timeout_error_handler(request: Request, exc: asyncio.TimeoutError):
    logger.error(f"Request timed out: {str(exc)}")
    return JSONResponse(
        status_code=504,
        content={"detail": "Request timed out. Please try again later."}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error occurred: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."}
    ) 