from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import prometheus_client
from sqlalchemy.orm import Session
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from prometheus_client import Counter, Histogram, Gauge, REGISTRY
from fastapi.responses import Response

from core.database import SessionLocal, engine, Base
from core.models.models import VaccinationType
import config

from routes import auth_routes, vaccination_routes, user_routes

# Create the FastAPI app
app = FastAPI(
    title="Cloud Vaccine Backend",
    description="Secure cloud-based vaccination record management system",
    version="1.0.0"
)

# Configure CORS
origins = [config.FRONTEND_URL]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth_routes.router, tags=["Authentication"])
app.include_router(user_routes.router, prefix="/api/user", tags=["User Management"])
app.include_router(vaccination_routes.router, prefix="/api/vaccinations", tags=["Vaccination Records"])


instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)


@app.get("/metrics")
async def metrics():
    return Response(
        prometheus_client.generate_latest(REGISTRY),
        media_type="text/plain"
    )

@app.get("/")
async def root():
    return {"message": "Server is running"}

# Seed initial data
def seed_vaccine_types(db: Session):
    vaccine_types = [
        {
            "vaccine_name": "Bacillus Calmette-Guérin (BCG)",
            "vaccine_code": "BCG",
            "max_doses": 5,
        },
        {
            "vaccine_name": "Pentavalent (DPT, Hepatitis B, Hib)",
            "vaccine_code": "PENTAVALENT",
            "max_doses": 5,
        },
        {
            "vaccine_name": "Oral Polio Vaccine",
            "vaccine_code": "OPV",
            "max_doses": 5,
        },
        {
            "vaccine_name": "Pneumococcal Conjugate Vaccine",
            "vaccine_code": "PCV",
            "max_doses": 5,
        },
        {
            "vaccine_name": "Inactivated Polio Vaccine",
            "vaccine_code": "IPV",
            "max_doses": 5,
        },
        {
            "vaccine_name": "Measles and Rubella Vaccine",
            "vaccine_code": "MR",
            "max_doses": 5,
        },
    ]

    for vaccine in vaccine_types:
        existing = (
            db.query(VaccinationType)
            .filter_by(vaccine_code=vaccine["vaccine_code"])
            .first()
        )
        if not existing:
            db_vaccine = VaccinationType(**vaccine)
            db.add(db_vaccine)

    db.commit()

# Initialize database with seed data
db = SessionLocal()
try:
    seed_vaccine_types(db)
finally:
    db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload in production
        workers=4,
        limit_concurrency=100,
        timeout_keep_alive=30,
        timeout_graceful_shutdown=30
    )