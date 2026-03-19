from fastapi import APIRouter, HTTPException
from collections import defaultdict
from app.services.neo4j_service import Neo4jService

router = APIRouter()


@router.get("/")
async def get_all_competitions():
    """Get all competitions"""
    competitions = Neo4jService.get_all_competitions()
    return {"competitions": competitions}


@router.get("/{competition_name}")
async def get_competition_details(competition_name: str):
    """Get complete competition information"""
    matches = Neo4jService.get_competition_matches(competition_name=competition_name)
    
    if not matches:
        raise HTTPException(status_code=404, detail=f"Competition '{competition_name}' not found")
    
    participants = Neo4jService.get_competition_participants(competition_name=competition_name)
    
    # Group matches by round
    matches_by_round = defaultdict(list)
    for match in matches:
        round_name = match.get('round', 'League Stage')
        matches_by_round[round_name].append(match)
    
    # Get top scorers for this competition
    # Note: This gets all top scorers, ideally you'd want competition-specific stats
    top_scorers = Neo4jService.get_top_scorers(limit=10)
    
    return {
        "competition_name": competition_name,
        "matches_by_round": dict(matches_by_round),
        "participating_clubs": [p['name'] for p in participants],
        "top_scorers": top_scorers,
        "total_matches": len(matches)
    }


@router.get("/{competition_name}/matches")
async def get_competition_matches(competition_name: str):
    """Get all matches in a competition"""
    matches = Neo4jService.get_competition_matches(competition_name=competition_name)
    
    if not matches:
        raise HTTPException(status_code=404, detail=f"Competition '{competition_name}' not found")
    
    return {
        "competition": competition_name,
        "matches": matches,
        "count": len(matches)
    }


@router.get("/{competition_name}/participants")
async def get_competition_participants(competition_name: str):
    """Get clubs that participated in a competition"""
    participants = Neo4jService.get_competition_participants(competition_name=competition_name)
    
    if not participants:
        raise HTTPException(status_code=404, detail=f"Competition '{competition_name}' not found")
    
    return {
        "competition": competition_name,
        "participants": participants
    }