from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from app.services.neo4j_service import Neo4jService

router = APIRouter()


@router.get("/top-by-metric")
async def get_top_by_metric(
    metric: str = Query(..., description="Statistical metric (goals, assists, tackles, etc.)"),
    limit: int = Query(20, ge=1, le=100),
    position: Optional[str] = Query(None, description="Filter by position")
):
    """Get top players by any statistical metric"""
    try:
        players = Neo4jService.get_top_players_by_metric(
            metric=metric,
            limit=limit,
            position=position
        )
        
        if not players:
            return {
                "metric": metric,
                "position": position,
                "players": [],
                "message": f"No players found with {metric} data"
            }
        
        return {
            "metric": metric,
            "position": position,
            "players": players
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid metric or query error: {str(e)}")


@router.get("/by-nationality")
async def get_stats_by_nationality(nation: Optional[str] = Query(None)):
    """Get aggregate statistics by nationality"""
    stats = Neo4jService.get_stats_by_nationality(nation=nation)
    
    return {
        "nationality": nation,
        "stats": stats
    }


@router.get("/by-position")
async def get_stats_by_position():
    """Get aggregate statistics by position"""
    stats = Neo4jService.get_stats_by_position()
    
    return {
        "stats": stats
    }


@router.get("/by-age-group")
async def get_stats_by_age_group():
    """Get statistics grouped by age ranges"""
    stats = Neo4jService.get_stats_by_age_group()
    
    return {
        "stats": stats
    }


@router.post("/compare-players")
async def compare_players_analysis(player_names: List[str]):
    """Detailed player comparison for analysis page"""
    if len(player_names) < 2:
        raise HTTPException(status_code=400, detail="At least 2 players required")
    
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
    
    # Calculate comparison metrics
    comparison_metrics = {}
    if players and players[0].get('stats'):
        # Get all available metrics from the first player
        available_metrics = [k for k, v in players[0]['stats'].items() if v is not None]
        
        for metric in available_metrics:
            comparison_metrics[metric] = {
                p['name']: p['stats'].get(metric, 0) 
                for p in players if p.get('stats')
            }
    
    return {
        "players": players,
        "comparison_metrics": comparison_metrics
    }