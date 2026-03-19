# app/api/routes/competitions.py
from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import Competition, Match, TopScorer, Club
from app.database import neo4j_conn

router = APIRouter(prefix="/api/competitions", tags=["Competitions"])

@router.get("/", response_model=List[Competition])
async def get_all_competitions():
    """Liste toutes les compétitions avec statistiques"""
    query = """
    MATCH (comp:Competition)
    OPTIONAL MATCH (c:Club)-[:PARTICIPATES_IN]->(comp)
    OPTIONAL MATCH (m:Match)-[:IN_COMPETITION]->(comp)
    RETURN comp.name as name,
           count(DISTINCT c) as participants_count,
           count(DISTINCT m) as matches_count
    ORDER BY comp.name
    """
    try:
        results = neo4j_conn.execute_query(query)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{competition_name}/matches", response_model=List[Match])
async def get_competition_matches(competition_name: str, round: str = None):
    """Récupère les matchs d'une compétition, optionnellement filtrés par round"""
    if round:
        query = """
        MATCH (m:Match)-[:IN_COMPETITION]->(comp:Competition {name: $competition_name})
        WHERE m.round = $round
        RETURN m.date as date,
               m.home_team_name as home_team_name,
               m.away_team_name as away_team_name,
               m.home_score as home_score,
               m.away_score as away_score,
               m.competition_name as competition_name,
               m.attendance as attendance,
               m.round as round,
               m.winner as winner,
               m.is_draw as is_draw,
               m.total_goals as total_goals,
               m.goal_difference as goal_difference
        ORDER BY m.date DESC
        """
        params = {"competition_name": competition_name, "round": round}
    else:
        query = """
        MATCH (m:Match)-[:IN_COMPETITION]->(comp:Competition {name: $competition_name})
        RETURN m.date as date,
               m.home_team_name as home_team_name,
               m.away_team_name as away_team_name,
               m.home_score as home_score,
               m.away_score as away_score,
               m.competition_name as competition_name,
               m.attendance as attendance,
               m.round as round,
               m.winner as winner,
               m.is_draw as is_draw,
               m.total_goals as total_goals,
               m.goal_difference as goal_difference
        ORDER BY m.date DESC
        """
        params = {"competition_name": competition_name}
    
    try:
        results = neo4j_conn.execute_query(query, params)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{competition_name}/rounds")
async def get_competition_rounds(competition_name: str):
    """Liste des rounds disponibles pour une compétition"""
    query = """
    MATCH (m:Match)-[:IN_COMPETITION]->(comp:Competition {name: $competition_name})
    WHERE m.round IS NOT NULL AND m.round <> ''
    RETURN DISTINCT m.round as round
    ORDER BY m.round
    """
    try:
        results = neo4j_conn.execute_query(query, {"competition_name": competition_name})
        return [r['round'] for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{competition_name}/top-scorers", response_model=List[TopScorer])
async def get_competition_top_scorers(competition_name: str, limit: int = 20):
    """Meilleurs buteurs d'une compétition (basé sur les clubs participants)"""
    query = """
    MATCH (p:Player)-[:PLAYS_FOR]->(c:Club)-[:PARTICIPATES_IN]->(comp:Competition {name: $competition_name})
    MATCH (p)-[:HAS_ADVANCED_STATS]->(ps:PlayerStats)
    WHERE ps.goals > 0
    RETURN p.name as player_name,
           c.name as club_name,
           ps.goals as goals,
           ps.matches_played as matches_played,
           ps.minutes as minutes
    ORDER BY ps.goals DESC
    LIMIT $limit
    """
    try:
        results = neo4j_conn.execute_query(query, {"competition_name": competition_name, "limit": limit})
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{competition_name}/participants", response_model=List[Club])
async def get_competition_participants(competition_name: str):
    """Liste des clubs participants à une compétition"""
    query = """
    MATCH (c:Club)-[:PARTICIPATES_IN]->(comp:Competition {name: $competition_name})
    OPTIONAL MATCH (c)-[:PLAYS_IN]->(l:League)
    OPTIONAL MATCH (p:Player)-[:PLAYS_FOR]->(c)
    RETURN c.name as name,
           l.name as league,
           [] as competitions,
           count(DISTINCT p) as players_count
    ORDER BY c.name
    """
    try:
        results = neo4j_conn.execute_query(query, {"competition_name": competition_name})
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{competition_name}/statistics")
async def get_competition_statistics(competition_name: str):
    """Statistiques globales d'une compétition"""
    query = """
    MATCH (comp:Competition {name: $competition_name})
    OPTIONAL MATCH (c:Club)-[:PARTICIPATES_IN]->(comp)
    OPTIONAL MATCH (m:Match)-[:IN_COMPETITION]->(comp)
    RETURN comp.name as competition_name,
           count(DISTINCT c) as total_participants,
           count(DISTINCT m) as total_matches,
           sum(m.total_goals) as total_goals,
           toFloat(sum(m.total_goals)) / CASE WHEN count(m) > 0 THEN count(m) ELSE 1 END as avg_goals_per_match,
           avg(m.attendance) as avg_attendance
    """
    try:
        results = neo4j_conn.execute_query(query, {"competition_name": competition_name})
        return results[0] if results else {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))