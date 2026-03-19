from fastapi import APIRouter, Query
from app.services.neo4j_service import Neo4jService

router = APIRouter()


@router.get("/recent")
async def get_recent_matches(limit: int = Query(20, ge=1, le=100)):
    """Get most recent matches"""
    matches = Neo4jService.get_recent_matches(limit=limit)
    
    return {
        "matches": matches,
        "count": len(matches)
    }