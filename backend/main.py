from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from routers import health, transactions, budgets, bills, ai_chat, auth
from core.database import init_db
from core.security import get_audit_logger
from middleware.security import (
    SecurityHeadersMiddleware,
    RequestValidationMiddleware,
    APIVersionMiddleware,
    ComplianceLoggingMiddleware,
    ErrorHandlingMiddleware
)

# Create FastAPI app
app = FastAPI(
    title="AI Budget Assistant API",
    description="A comprehensive AI-powered household budgeting application with CrewAI multi-agent system",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add security middleware (order matters - first added is outermost)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(ComplianceLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestValidationMiddleware)
app.add_middleware(APIVersionMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Restrict origins for security
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-API-Version", "X-Request-ID", "X-Client-Version"],
)

# Initialize database
@app.on_event("startup")
async def startup_event():
    """Initialize database and AI systems on startup."""
    await init_db()
    
    # Initialize CrewAI system
    from ai.crew_setup import initialize_crew
    await initialize_crew()

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(transactions.router, prefix="/api/v1", tags=["transactions"])
app.include_router(budgets.router, prefix="/api/v1", tags=["budgets"])
app.include_router(bills.router, prefix="/api/v1", tags=["bills"])
app.include_router(ai_chat.router, prefix="/api/v1", tags=["ai-chat"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    # Log security events for audit
    audit_logger = get_audit_logger()
    audit_logger.log_security_event(
        event_type="UNHANDLED_EXCEPTION",
        severity="ERROR",
        details={
            "error": str(exc),
            "path": str(request.url.path),
            "method": request.method,
            "client_ip": request.client.host
        }
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}  # Don't expose error details
    )

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "AI Budget Assistant API",
        "version": "2.0.0",
        "features": [
            "Secure Authentication (PIN/Biometric)",
            "Encrypted Data Storage (SQLCipher)",
            "Transaction Management",
            "Budget Planning",
            "Bill Tracking",
            "AI-Powered Insights with Security Controls",
            "Simplified AI Architecture",
            "Natural Language Processing",
            "Voice Integration",
            "PCI-DSS/GDPR/CCPA Compliance",
            "Security Audit Logging"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
