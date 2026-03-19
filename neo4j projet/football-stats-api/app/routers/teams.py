from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.services.neo4j_service import Neo4jService

router = APIRouter()


@router.get("/{team_name}")
async def get_team_details(team_name: str):
    """Get complete team information"""
    team_info = Neo4jService.get_team_info(team_name=team_name)
    
    if not team_info:
        raise HTTPException(status_code=404, detail=f"Team '{team_name}' not found")
    
    team_stats = Neo4jService.get_team_stats(team_name=team_name)
    
    return {
        "info": team_info,
        "stats": team_stats
    }


@router.get("/{team_name}/players")
async def get_team_players(team_name: str):
    """Get all players in a team"""
    players = Neo4jService.get_team_players(team_name=team_name)
    
    if not players:
        raise HTTPException(status_code=404, detail=f"Team '{team_name}' not found or has no players")
    
    return {
        "team": team_name,
        "players": players,
        "count": len(players)
    }


@router.get("/{team_name}/matches")
async def get_team_matches(
    team_name: str,
    limit: int = Query(50, ge=1, le=200)
):
    """Get team's matches"""
    matches = Neo4jService.get_team_matches(team_name=team_name, limit=limit)
    
    if not matches:
        raise HTTPException(status_code=404, detail=f"No matches found for team '{team_name}'")
    
    return {
        "team": team_name,
        "matches": matches,
        "count": len(matches)
    }


@router.get("/{team_name}/top-players")
async def get_team_top_players(
    team_name: str,
    metric: str = Query("goals", description="Metric to rank by (goals, assists, etc.)"),
    limit: int = Query(5, ge=1, le=20)
):
    """Get team's top players by a specific metric"""
    try:
        players = Neo4jService.get_team_top_players(
            team_name=team_name,
            metric=metric,
            limit=limit
        )
        
        if not players:
            return {
                "team": team_name,
                "metric": metric,
                "players": [],
                "message": f"No players found with {metric} data"
            }
        
        return {
            "team": team_name,
            "metric": metric,
            "players": players
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid metric or query error: {str(e)}")


@router.get("/{team_name}/stats")
async def get_team_stats(team_name: str):
    """Get team statistics"""
    stats = Neo4jService.get_team_stats(team_name=team_name)
    
    if not stats:
        raise HTTPException(status_code=404, detail=f"Team '{team_name}' not found")
    
    return stats