from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from app.services.neo4j_service import Neo4jService

router = APIRouter()


@router.get("/")
async def get_players(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    position: Optional[str] = Query(None, description="Filter by position (FW, MF, DF, GK)"),
    nation: Optional[str] = Query(None, description="Filter by nationality"),
    club: Optional[str] = Query(None, description="Filter by club name"),
    min_age: Optional[int] = Query(None, ge=15, le=50),
    max_age: Optional[int] = Query(None, ge=15, le=50)
):
    """Get all players with optional filters and pagination"""
    players = Neo4jService.get_all_players(
        limit=limit,
        offset=offset,
        position=position,
        nation=nation,
        club=club,
        min_age=min_age,
        max_age=max_age
    )
    return {
        "players": players,
        "count": len(players),
        "offset": offset,
        "limit": limit
    }


@router.get("/search")
async def search_players(
    q: str = Query(..., min_length=2, description="Search term"),
    limit: int = Query(20, ge=1, le=100)
):
    """Search players by name"""
    players = Neo4jService.search_players(search_term=q, limit=limit)
    return {
        "players": players,
        "count": len(players),
        "search_term": q
    }


@router.get("/top-scorers")
async def get_top_scorers(
    limit: int = Query(20, ge=1, le=100),
    league: Optional[str] = Query(None, description="Filter by league")
):
    """Get top goal scorers"""
    scorers = Neo4jService.get_top_scorers(limit=limit, league=league)
    return {"top_scorers": scorers}


@router.get("/top-assisters")
async def get_top_assisters(
    limit: int = Query(20, ge=1, le=100),
    league: Optional[str] = Query(None, description="Filter by league")
):
    """Get top assist providers"""
    assisters = Neo4jService.get_top_assisters(limit=limit, league=league)
    return {"top_assisters": assisters}


@router.get("/{player_name}")
async def get_player_profile(player_name: str):
    """Get complete player profile with all statistics"""
    player = Neo4jService.get_player_profile(player_name=player_name)
    
    if not player:
        raise HTTPException(status_code=404, detail=f"Player '{player_name}' not found")
    
    return player


@router.post("/compare")
async def compare_players(player_names: List[str]):
    """Compare multiple players"""
    if len(player_names) < 2:
        raise HTTPException(status_code=400, detail="At least 2 players required for comparison")
    
    if len(player_names) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 players can be compared")
    
    players = Neo4jService.compare_players(player_names=player_names)
    
    if len(players) != len(player_names):
        found_names = [p['name'] for p in players]
        missing = [name for name in player_names if name not in found_names]
        raise HTTPException(
            status_code=404, 
            detail=f"Players not found: {', '.join(missing)}"
        )
    
    return {"players": players}