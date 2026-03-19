# app/api/routes/leagues.py
from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import League, ClubStandings, TopScorer, Club
from app.database import neo4j_conn

router = APIRouter(prefix="/api/leagues", tags=["Leagues"])

@router.get("/", response_model=List[League])
async def get_all_leagues():
    """Liste toutes les leagues avec statistiques de base"""
    query = """
    MATCH (l:League)
    OPTIONAL MATCH (c:Club)-[:PLAYS_IN]->(l)
    OPTIONAL MATCH (m:Match)-[:IN_LEAGUE]->(l)
    RETURN l.name as name,
           count(DISTINCT c) as clubs_count,
           count(DISTINCT m) as matches_count
    ORDER BY l.name
    """
    try:
        results = neo4j_conn.execute_query(query)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{league_name}/standings", response_model=List[ClubStandings])
async def get_league_standings(league_name: str):
    """Classement complet d'une league"""
    query = """
    MATCH (c:Club)-[:PLAYS_IN]->(l:League {name: $league_name})
    OPTIONAL MATCH (c)-[:PLAYED_HOME]->(m:Match)-[:IN_LEAGUE]->(l)
    WITH c, l,
         count(m) as home_matches,
         sum(CASE WHEN m.winner = c.name THEN 1 ELSE 0 END) as home_wins,
         sum(CASE WHEN m.is_draw THEN 1 ELSE 0 END) as home_draws,
         sum(CASE WHEN m.winner <> c.name AND NOT m.is_draw THEN 1 ELSE 0 END) as home_losses,
         sum(m.home_score) as home_goals_for,
         sum(m.away_score) as home_goals_against
    OPTIONAL MATCH (c)-[:PLAYED_AWAY]->(ma:Match)-[:IN_LEAGUE]->(l)
    WITH c,
         COALESCE(home_matches, 0) + count(ma) as matches_played,
         COALESCE(home_wins, 0) + sum(CASE WHEN ma.winner = c.name THEN 1 ELSE 0 END) as wins,
         COALESCE(home_draws, 0) + sum(CASE WHEN ma.is_draw THEN 1 ELSE 0 END) as draws,
         COALESCE(home_losses, 0) + sum(CASE WHEN ma.winner <> c.name AND NOT ma.is_draw THEN 1 ELSE 0 END) as losses,
         COALESCE(home_goals_for, 0) + sum(ma.away_score) as goals_for,
         COALESCE(home_goals_against, 0) + sum(ma.home_score) as goals_against
    WITH c.name as club_name,
         matches_played, wins, draws, losses,
         goals_for, goals_against,
         goals_for - goals_against as goal_difference,
         wins * 3 + draws as points
    ORDER BY points DESC, goal_difference DESC, goals_for DESC
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
        results = neo4j_conn.execute_query(query, {"league_name": league_name})
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{league_name}/top-scorers", response_model=List[TopScorer])
async def get_league_top_scorers(league_name: str, limit: int = 20):
    """Meilleurs buteurs d'une league"""
    query = """
    MATCH (p:Player)-[:PLAYS_FOR]->(c:Club)-[:PLAYS_IN]->(l:League {name: $league_name})
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
        results = neo4j_conn.execute_query(query, {"league_name": league_name, "limit": limit})
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{league_name}/clubs", response_model=List[Club])
async def get_league_clubs(league_name: str):
    """Liste des clubs d'une league"""
    query = """
    MATCH (c:Club)-[:PLAYS_IN]->(l:League {name: $league_name})
    OPTIONAL MATCH (p:Player)-[:PLAYS_FOR]->(c)
    OPTIONAL MATCH (c)-[:PARTICIPATES_IN]->(comp:Competition)
    RETURN c.name as name,
           l.name as league,
           collect(DISTINCT comp.name) as competitions,
           count(DISTINCT p) as players_count
    ORDER BY c.name
    """
    try:
        results = neo4j_conn.execute_query(query, {"league_name": league_name})
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{league_name}/statistics")
async def get_league_statistics(league_name: str):
    """Statistiques globales d'une league"""
    query = """
    MATCH (l:League {name: $league_name})
    OPTIONAL MATCH (c:Club)-[:PLAYS_IN]->(l)
    OPTIONAL MATCH (m:Match)-[:IN_LEAGUE]->(l)
    OPTIONAL MATCH (p:Player)-[:PLAYS_FOR]->(c)
    RETURN l.name as league_name,
           count(DISTINCT c) as total_clubs,
           count(DISTINCT m) as total_matches,
           count(DISTINCT p) as total_players,
           sum(m.total_goals) as total_goals,
           toFloat(sum(m.total_goals)) / count(DISTINCT m) as avg_goals_per_match
    """
    try:
        results = neo4j_conn.execute_query(query, {"league_name": league_name})
        return results[0] if results else {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))