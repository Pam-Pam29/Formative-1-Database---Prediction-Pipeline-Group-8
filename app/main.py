"""
FastAPI main application
"""
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import postgres, mongodb
from app.database import close_postgres_pool, close_mongo_clients


load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
   
    yield

    close_postgres_pool()
    close_mongo_clients()


app = FastAPI(
    title="AgroYield API",
    description="CRUD API for crop yield records - PostgreSQL and MongoDB",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(postgres.router)
app.include_router(mongodb.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AgroYield API",
        "version": "1.0.0",
        "endpoints": {
            "postgres": "/api/postgres/records/",
            "mongodb": "/api/mongodb/records/",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
