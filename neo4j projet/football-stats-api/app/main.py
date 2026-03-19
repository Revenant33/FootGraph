from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import neo4j_conn
from app.routers import players, teams, leagues, competitions, matches, analysis
import os
from dotenv import load_dotenv

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    neo4j_conn.connect()
    yield
    # Shutdown
    neo4j_conn.close()


app = FastAPI(
    title="Football Stats API",
    description="API for football statistics from top 5 leagues and European competitions",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(players.router, prefix="/api/players", tags=["Players"])
app.include_router(teams.router, prefix="/api/teams", tags=["Teams"])
app.include_router(leagues.router, prefix="/api/leagues", tags=["Leagues"])
app.include_router(competitions.router, prefix="/api/competitions", tags=["Competitions"])
app.include_router(matches.router, prefix="/api/matches", tags=["Matches"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])


@app.get("/")
async def root():
    return {
        "message": "Football Stats API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/home")
async def get_home_page_data():
    """Get all data needed for the home page"""
    from app.services.neo4j_service import Neo4jService
    
    top_scorers = Neo4jService.get_top_scorers(limit=10)
    top_assisters = Neo4jService.get_top_assisters(limit=10)
    recent_matches = Neo4jService.get_recent_matches(limit=20)
    league_standings_preview = Neo4jService.get_league_standings_preview()
    
    return {
        "top_scorers": top_scorers,
        "top_assisters": top_assisters,
        "recent_matches": recent_matches,
        "league_standings_preview": league_standings_preview
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run("app.main:app", host=host, port=port, reload=True)