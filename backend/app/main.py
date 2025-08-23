from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="APEX Asia Property Exchange API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене замените на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes probes"""
    return {"status": "healthy", "environment": os.getenv("ENVIRONMENT", "development")}

@app.get("/")
async def root():
    return {"message": "APEX Asia Property Exchange API"}

# Подключаем webhook роутер
from app.api import webhooks
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
