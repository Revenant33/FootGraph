from fastapi import APIRouter, HTTPException
from app.services.neo4j_service import Neo4jService

router = APIRouter()


@router.get("/")
async def get_all_leagues():
    """Get all leagues"""
    leagues = Neo4jService.get_all_leagues()
    return {"leagues": leagues}


@router.get("/{league_name}")
async def get_league_details(league_name: str):
    """Get complete league information"""
    standings = Neo4jService.get_league_standings(league_name=league_name)
    
    if not standings:
        raise HTTPException(status_code=404, detail=f"League '{league_name}' not found")
    
    clubs = Neo4jService.get_league_clubs(league_name=league_name)
    stats = Neo4jService.get_league_stats(league_name=league_name)
    top_scorers = Neo4jService.get_top_scorers(limit=10, league=league_name)
    
    stats_data = stats[0] if stats else {}
    
    return {
        "league_name": league_name,
        "standings": standings,
        "clubs": [c['name'] for c in clubs],
        "top_scorers": top_scorers,
        "stats": {
            "total_matches": stats_data.get('total_matches', 0),
            "total_goals": stats_data.get('total_goals', 0),
            "avg_goals_per_match": round(stats_data.get('avg_goals_per_match', 0), 2)
        }
    }


@router.get("/{league_name}/standings")
async def get_league_standings(league_name: str):
    """Get league standings table"""
    standings = Neo4jService.get_league_standings(league_name=league_name)
    
    if not standings:
        raise HTTPException(status_code=404, detail=f"League '{league_name}' not found")
    
    return {
        "league": league_name,
        "standings": standings
    }


@router.get("/{league_name}/clubs")
async def get_league_clubs(league_name: str):
    """Get all clubs in a league"""
    clubs = Neo4jService.get_league_clubs(league_name=league_name)
    
    if not clubs:
        raise HTTPException(status_code=404, detail=f"League '{league_name}' not found")
    
    return {
        "league": league_name,
        "clubs": clubs
    }


@router.get("/{league_name}/top-scorers")
async def get_league_top_scorers(league_name: str, limit: int = 20):
    """Get top scorers in a league"""
    scorers = Neo4jService.get_top_scorers(limit=limit, league=league_name)
    
    return {
        "league": league_name,
        "top_scorers": scorers
    }