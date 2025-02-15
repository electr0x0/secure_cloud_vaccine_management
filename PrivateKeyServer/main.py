# app/main.py
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware 
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session
import ipaddress

from core.database import engine, Base
from routes import key_routes

# List of allowed IPs
ALLOWED_IPS = [
    "100.114.11.98",  # CloudBackend
    "127.0.0.1",
    "100.127.99.47"   # Monitoring Server
]

class TailscaleMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        
        # Check if the client IP is in the allowed list
        if client_ip not in ALLOWED_IPS:
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "Access denied. Only Tailscale connections are allowed."
                }
            )
        
        response = await call_next(request)
        return response

# Create the FastAPI app
app = FastAPI(
    title="Private Key Management Server",
    description="Secure on-premises key management server for cloud-based vaccination system",
    version="1.0.0"
)

# Add the Tailscale middleware
app.add_middleware(TailscaleMiddleware)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(key_routes.router, tags=["Key Management"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=False,  # Disable reload in production
        workers=4,     # Multiple workers for better performance
        log_level="info",
        proxy_headers=True,  # Trust proxy headers for proper IP handling
        forwarded_allow_ips='*'  # Allow forwarded IPs since we're behind a proxy
    )