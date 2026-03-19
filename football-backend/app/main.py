# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import neo4j_conn
from app.config import settings

# Import des routes
from app.api.routes import home, leagues, competitions, clubs, players, analysis

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connexion à Neo4j
    neo4j_conn.connect()
    print("✅ Connected to Neo4j")
    yield
    # Shutdown: Fermeture de la connexion
    neo4j_conn.close()
    print("❌ Disconnected from Neo4j")

# Initialisation de l'application
app = FastAPI(
    title=settings.APP_NAME,
    description="API Backend pour l'analyse de données football avec Neo4j",
    version="1.0.0",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À modifier en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes
app.include_router(home.router)
app.include_router(leagues.router)
app.include_router(competitions.router)
app.include_router(clubs.router)
app.include_router(players.router)
app.include_router(analysis.router)

@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "message": "Football Analytics API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Vérification de santé de l'API"""
    try:
        # Test de connexion à Neo4j
        neo4j_conn.execute_query("RETURN 1")
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
    )