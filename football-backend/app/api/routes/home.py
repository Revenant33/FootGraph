# app/api/routes/home.py
from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import TopScorer, TopAssister, Match, ClubStandings
from app.database import neo4j_conn

router = APIRouter(prefix="/api/home", tags=["Home"])

@router.get("/top-scorers", response_model=List[TopScorer])
async def get_top_scorers(limit: int = 10):
    """Récupère les meilleurs buteurs toutes compétitions confondues"""
    query = """
    MATCH (p:Player)-[:PLAYS_FOR]->(c:Club)
    MATCH (p)-[:HAS_ADVANCED_STATS]->(ps:PlayerStats)
    WHERE ps.goals > 0
    RETURN p.name as player_name, 
           c.name as club_name,
           ps.goals as goals,
           ps.matches_played as matches_played,
           ps.minutes as minutes
    ORDER BY ps.goals DESC, ps.matches_played ASC
    LIMIT $limit
    """
    try:
        results = neo4j_conn.execute_query(query, {"limit": limit})
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-assisters", response_model=List[TopAssister])
async def get_top_assisters(limit: int = 10):
    """Récupère les meilleurs passeurs"""
    query = """
    MATCH (p:Player)-[:PLAYS_FOR]->(c:Club)
    MATCH (p)-[:HAS_ADVANCED_STATS]->(ps:PlayerStats)
    WHERE ps.assists > 0
    RETURN p.name as player_name,
           c.name as club_name,
           ps.assists as assists,
           ps.matches_played as matches_played,
           ps.minutes as minutes
    ORDER BY ps.assists DESC, ps.matches_played ASC
    LIMIT $limit
    """
    try:
        results = neo4j_conn.execute_query(query, {"limit": limit})
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent-matches", response_model=List[Match])
async def get_recent_matches(limit: int = 20):
    """Récupère les matchs récents"""
    query = """
    MATCH (m:Match)
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
    LIMIT $limit
    """
    try:
        results = neo4j_conn.execute_query(query, {"limit": limit})
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/league-preview/{league_name}", response_model=List[ClubStandings])
async def get_league_preview(league_name: str, limit: int = 5):
    """Aperçu du classement d'une league (top 5)"""
    query = """
    MATCH (c:Club)-[:PLAYS_IN]->(l:League {name: $league_name})
    MATCH (c)-[:PLAYED_HOME]->(m:Match)-[:IN_LEAGUE]->(l)
    WITH c, 
         count(m) as home_matches,
         sum(CASE WHEN m.winner = c.name THEN 1 ELSE 0 END) as home_wins,
         sum(CASE WHEN m.is_draw THEN 1 ELSE 0 END) as home_draws,
         sum(CASE WHEN m.winner <> c.name AND NOT m.is_draw THEN 1 ELSE 0 END) as home_losses,
         sum(m.home_score) as home_goals_for,
         sum(m.away_score) as home_goals_against
    MATCH (c)-[:PLAYED_AWAY]->(ma:Match)-[:IN_LEAGUE]->(l)
    WITH c,
         home_matches + count(ma) as matches_played,
         home_wins + sum(CASE WHEN ma.winner = c.name THEN 1 ELSE 0 END) as wins,
         home_draws + sum(CASE WHEN ma.is_draw THEN 1 ELSE 0 END) as draws,
         home_losses + sum(CASE WHEN ma.winner <> c.name AND NOT ma.is_draw THEN 1 ELSE 0 END) as losses,
         home_goals_for + sum(ma.away_score) as goals_for,
         home_goals_against + sum(ma.home_score) as goals_against
    WITH c.name as club_name,
         matches_played,
         wins, draws, losses,
         goals_for, goals_against,
         goals_for - goals_against as goal_difference,
         wins * 3 + draws as points
    ORDER BY points DESC, goal_difference DESC, goals_for DESC
    LIMIT $limit
    WITH collect({club_name: club_name, matches_played: matches_played, wins: wins, 
                  draws: draws, losses: losses, goals_for: goals_for, 
                  goals_against: goals_against, goal_difference: goal_difference, 
                  points: points}) as standings
    UNWIND range(0, size(standings)-1) as idx
    RETURN idx + 1 as position,
           standings[idx].club_name as club_name,
           standings[idx].matches_played as matches_played,
           standings[idx].wins as wins,
           standings[idx].draws as draws,
           standings[idx].losses as losses,
           standings[idx].goals_for as goals_for,
           standings[idx].goals_against as goals_against,
           standings[idx].goal_difference as goal_difference,
           standings[idx].points as points
    """
    try:
        results = neo4j_conn.execute_query(query, {"league_name": league_name, "limit": limit})
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))