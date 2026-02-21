# src/app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

# --- Integration Placeholders for Optimization/Expansion ---
# langchain: Plan to add LLM workflow chains as endpoints/services
# haystack: Plan to add semantic search/RAG endpoints
# celery/redis: Plan to offload heavy tasks and cache responses
# openai: Plan to enhance OpenAI compatibility and error handling
# playwright: Plan to automate browser-based LLMs if needed

from app.services.gemini_client import get_gemini_client, init_gemini_client, GeminiClientNotInitializedError
from app.services.session_manager import init_session_managers
from app.logger import logger

# Import endpoint routers
from app.endpoints import gemini, chat, google_generative, langchain

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Initializes services on startup.
    """
    # Try to get the existing client first
    client_initialized = False
    try:
        get_gemini_client()
        client_initialized = True
        logger.info("Gemini client found (initialized in main process).")
    except GeminiClientNotInitializedError:
        logger.info("Gemini client not initialized in worker process, attempting reinitialization...")

    # If client is not available, try to initialize it (for multiprocessing support)
    if not client_initialized:
        try:
            init_result = await init_gemini_client()
            if init_result:
                logger.info("Gemini client successfully initialized in worker process.")
            else:
                logger.error("Failed to initialize Gemini client in worker process.")
        except Exception as e:
            logger.error(f"Error initializing Gemini client in worker process: {e}")

    # Initialize session managers only if the client is available
    try:
        get_gemini_client()
        init_session_managers()
        logger.info("Session managers initialized for WebAI-to-API.")
    except GeminiClientNotInitializedError as e:
        logger.warning(f"Session managers not initialized: {e}")

    yield

    # Shutdown logic: No explicit client closing is needed anymore.
    # The underlying HTTPX client manages its connection pool automatically.
    logger.info("Application shutdown complete.")

from fastapi import Depends, Request
from fastapi.openapi.utils import get_openapi

# Dependency injection example: Provide config or logger
def get_config():
    from app.config import CONFIG
    return CONFIG

def get_logger():
    from app.logger import logger
    return logger

app = FastAPI(lifespan=lifespan)

# Custom OpenAPI schema with branding and version
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="WebAI-to-API",
        version="0.4.0",
        description="Modular FastAPI server for browser-based LLMs (Gemini, g4f, etc).",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "/assets/logo.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema
app.openapi = custom_openapi

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Example event hook: log every request
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger = get_logger()
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")

    return response

# Register the endpoint routers for WebAI-to-API
app.include_router(gemini.router)
app.include_router(chat.router)
app.include_router(google_generative.router)
app.include_router(langchain.router)
