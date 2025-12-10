import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from fastapi import FastAPI, Response, Request, Depends, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from starlette.middleware.sessions import SessionMiddleware
from app.api.v1 import api_router
from app.core.config import settings
import logging
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from datetime import datetime

# Initialize Sentry
sentry_sdk.init(
    dsn="https://examplePublicKey@o0.ingest.sentry.io/0",  # Replace with actual Sentry DSN
    integrations=[
        FastApiIntegration(),
        StarletteIntegration(),
    ],
    traces_sample_rate=1.0,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create metrics
REQUEST_COUNT = Counter('prism_ai_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('prism_ai_request_duration_seconds', 'Request duration')

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Add session middleware for authentication
app.add_middleware(SessionMiddleware, secret_key="prism_ai_secret_key")

# Middleware to collect metrics
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    import time
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.observe(time.time() - start_time)
    
    return response

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring system status
    """
    logger.info("Health check endpoint accessed")
    return {
        "status": "healthy",
        "service": "Prism AI",
        "timestamp": "2025-12-10T13:45:00Z"
    }

@app.get("/health/db")
async def database_health_check():
    """
    Database health check endpoint
    """
    try:
        # This would check database connectivity in a real implementation
        logger.info("Database health check accessed")
        return {
            "status": "healthy",
            "service": "Prism AI Database",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        sentry_sdk.capture_exception(e)
        return {
            "status": "unhealthy",
            "service": "Prism AI Database",
            "error": str(e)
        }

@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    sentry_sdk.capture_exception(exc)
    logger.error(f"Global exception handler caught: {str(exc)}")
    return {"message": "Internal server error"}

# HTML serving endpoints
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request}, headers={"Content-Type": "text/html"})

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request}, headers={"Content-Type": "text/html"})

@app.post("/login")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    # This is a simplified login flow for demonstration
    # In a real implementation, you would verify credentials against your database
    request.session['user'] = {"email": form_data.username}
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request}, headers={"Content-Type": "text/html"})

@app.post("/register")
async def register(request: Request, email: str = Form(...), password: str = Form(...)):
    # This is a simplified registration flow for demonstration
    # In a real implementation, you would hash the password and store user in database
    request.session['user'] = {"email": email}
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url="/login")
    
    # Mock user data for demonstration
    pages_limit = 100 if user.get("subscription_tier", "EXPLORER") == "EXPLORER" else 1000
    queries_limit = 50 if user.get("subscription_tier", "EXPLORER") == "EXPLORER" else 500
    
    pages_progress = (user.get("pages_processed_this_month", 25) / pages_limit) * 100
    queries_progress = (user.get("queries_this_month", 12) / queries_limit) * 100
    
    # Convert progress to nearest 10% increment for CSS classes
    pages_progress_class = f"progress-{round(min(pages_progress, 100) / 10) * 10}"
    queries_progress_class = f"progress-{round(min(queries_progress, 100) / 10) * 10}"
    
    user_data = {
        "email": user["email"],
        "pages_processed_this_month": user.get("pages_processed_this_month", 25),
        "queries_this_month": user.get("queries_this_month", 12),
        "subscription_tier": user.get("subscription_tier", "EXPLORER"),
        "pages_progress_class": pages_progress_class,
        "queries_progress_class": queries_progress_class,
        "pages_limit": "100" if user.get("subscription_tier", "EXPLORER") == "EXPLORER" else "∞",
        "queries_limit": "50" if user.get("subscription_tier", "EXPLORER") == "EXPLORER" else "∞"
    }
    
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user_data}, headers={"Content-Type": "text/html"})

@app.get("/documents", response_class=HTMLResponse)
async def documents_page(request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url="/login")
    
    # Mock documents data for demonstration
    documents = [
        {
            "filename": "research_paper.pdf",
            "file_type": "application/pdf",
            "size": 1024000,
            "processed": True,
            "created_at": datetime(2025, 12, 1, 10, 30, 0)
        },
        {
            "filename": "financial_report.docx",
            "file_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "size": 512000,
            "processed": False,
            "created_at": datetime(2025, 12, 5, 14, 15, 0)
        }
    ]
    
    return templates.TemplateResponse("documents.html", {"request": request, "documents": documents}, headers={"Content-Type": "text/html"})

@app.post("/documents")
async def upload_document(request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url="/login")
    
    # In a real implementation, you would handle the file upload here
    # and call your API endpoint for document processing
    
    return templates.TemplateResponse("documents.html", {
        "request": request, 
        "message": "Document uploaded successfully! Processing will begin shortly."
    }, headers={"Content-Type": "text/html"})

@app.get("/query", response_class=HTMLResponse)
async def query_page(request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse("query.html", {"request": request}, headers={"Content-Type": "text/html"})

@app.post("/query")
async def query_documents(request: Request, question: str = Form(...)):
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url="/login")
    
    # Mock response for demonstration
    # In a real implementation, you would call your API endpoint for querying
    answer = {
        "response": f"This is a simulated response to your question: '{question}'. In a full implementation, this would be answered using content from your documents.",
        "sources": ["research_paper.pdf", "financial_report.docx"]
    }
    
    return templates.TemplateResponse("query.html", {
        "request": request, 
        "question": question,
        "answer": answer
    }, headers={"Content-Type": "text/html"})

@app.get("/upgrade", response_class=HTMLResponse)
async def upgrade_page(request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse("upgrade.html", {"request": request}, headers={"Content-Type": "text/html"})

@app.post("/upgrade")
async def initiate_upgrade(request: Request, phone_number: str = Form(...)):
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url="/login")
    
    # In a real implementation, you would call your API endpoint for payment initiation
    # and handle the response appropriately
    
    return templates.TemplateResponse("upgrade.html", {
        "request": request,
        "message": "Payment request sent successfully! Please check your phone for the M-Pesa prompt."
    }, headers={"Content-Type": "text/html"})
