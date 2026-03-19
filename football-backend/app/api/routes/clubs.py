# app/api/routes/clubs.py
from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import Club, PlayerWithStats, Match
from app.database import neo4j_conn

router = APIRouter(prefix="/api/clubs", tags=["Clubs"])

@router.get("/{club_name}", response_model=Club)
async def get_club_details(club_name: str):
    """Détails d'un club"""
    query = """
    MATCH (c:Club {name: $club_name})
    OPTIONAL MATCH (c)-[:PLAYS_IN]->(l:League)
    OPTIONAL MATCH (c)-[:PARTICIPATES_IN]->(comp:Competition)
    OPTIONAL MATCH (p:Player)-[:PLAYS_FOR]->(c)
    RETURN c.name as name,
           l.name as league,
           collect(DISTINCT comp.name) as competitions,
           count(DISTINCT p) as players_count
    """
    try:
        results = neo4j_conn.execute_query(query, {"club_name": club_name})
        if not results:
            raise HTTPException(status_code=404, detail="Club not found")
        return results[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{club_name}/squad", response_model=List[PlayerWithStats])
async def get_club_squad(club_name: str):
    """Effectif complet du club avec statistiques"""
    query = """
    MATCH (p:Player)-[:PLAYS_FOR]->(c:Club {name: $club_name})
    OPTIONAL MATCH (p)-[:HAS_ADVANCED_STATS]->(ps:PlayerStats)
    RETURN p.name as name,
           p.nation as nation,
           p.position as position,
           p.age as age,
           p.born as born,
           c.name as club,
           {
               matches_played: COALESCE(ps.matches_played, 0),
               starts: COALESCE(ps.starts, 0),
               minutes: COALESCE(ps.minutes, 0),
               goals: COALESCE(ps.goals, 0),
               assists: COALESCE(ps.assists, 0),
               shots: COALESCE(ps.shots, 0),
               shots_on_target: COALESCE(ps.shots_on_target, 0),
               passes_completed: COALESCE(ps.passes_completed, 0),
               passes_attempted: COALESCE(ps.passes_attempted, 0),
               pass_completion_pct: COALESCE(ps.pass_completion_pct, 0),
               tackles: COALESCE(ps.tackles, 0),
               interceptions: COALESCE(ps.interceptions, 0),
               blocks: COALESCE(ps.blocks, 0),
               yellow_cards: COALESCE(ps.yellow_cards, 0),
               red_cards: COALESCE(ps.red_cards, 0)
           } as stats
    ORDER BY p.position, p.name
    """
    try:
        results = neo4j_conn.execute_query(query, {"club_name": club_name})
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{club_name}/matches", response_model=List[Match])
async def get_club_matches(club_name: str, limit: int = 50):
    """Matchs d'un club"""
    query = """
    MATCH (c:Club {name: $club_name})
    MATCH (m:Match)
    WHERE m.home_team_name = c.name OR m.away_team_name = c.name
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
        results = neo4j_conn.execute_query(query, {"club_name": club_name, "limit": limit})
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{club_name}/top-players")
async def get_club_top_players(club_name: str):
    """Meilleurs joueurs du club par catégorie"""
    query = """
    MATCH (p:Player)-[:PLAYS_FOR]->(c:Club {name: $club_name})
    MATCH (p)-[:HAS_ADVANCED_STATS]->(ps:PlayerStats)
    WITH c, 
         collect({name: p.name, goals: ps.goals})[0..5] as top_scorers,
         collect({name: p.name, assists: ps.assists})[0..5] as top_assisters
    MATCH (p2:Player)-[:PLAYS_FOR]->(c)
    MATCH (p2)-[:HAS_ADVANCED_STATS]->(ps2:PlayerStats)
    ORDER BY ps2.goals DESC
    WITH c, top_scorers, top_assisters, collect({name: p2.name, goals: ps2.goals})[0..5] as scorers
    MATCH (p3:Player)-[:PLAYS_FOR]->(c)
    MATCH (p3)-[:HAS_ADVANCED_STATS]->(ps3:PlayerStats)
    ORDER BY ps3.assists DESC
    WITH scorers, collect({name: p3.name, assists: ps3.assists})[0..5] as assisters
    RETURN {top_scorers: scorers, top_assisters: assisters} as top_players
    """
    try:
        results = neo4j_conn.execute_query(query, {"club_name": club_name})
        return results[0] if results else {"top_scorers": [], "top_assisters": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{club_name}/statistics")
async def get_club_statistics(club_name: str):
    """Statistiques du club"""
    query = """
    MATCH (c:Club {name: $club_name})
    OPTIONAL MATCH (c)-[:PLAYED_HOME]->(home:Match)
    OPTIONAL MATCH (c)-[:PLAYED_AWAY]->(away:Match)
    OPTIONAL MATCH (p:Player)-[:PLAYS_FOR]->(c)
    OPTIONAL MATCH (p)-[:HAS_ADVANCED_STATS]->(ps:PlayerStats)
    RETURN c.name as club_name,
           count(DISTINCT home) + count(DISTINCT away) as total_matches,
           sum(CASE WHEN home.winner = c.name OR away.winner = c.name THEN 1 ELSE 0 END) as wins,
           sum(CASE WHEN home.is_draw OR away.is_draw THEN 1 ELSE 0 END) as draws,
           sum(CASE WHEN (home.winner <> c.name AND NOT home.is_draw) OR 
                        (away.winner <> c.name AND NOT away.is_draw) THEN 1 ELSE 0 END) as losses,
           count(DISTINCT p) as squad_size,
           sum(ps.goals) as total_goals,
           sum(ps.assists) as total_assists
    """
    try:
        results = neo4j_conn.execute_query(query, {"club_name": club_name})
        return results[0] if results else {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{club_name}/league-position")
async def get_club_league_position(club_name: str):
    """Position du club dans son championnat"""
    query = """
    MATCH (c:Club {name: $club_name})-[:PLAYS_IN]->(l:League)
    MATCH (all_clubs:Club)-[:PLAYS_IN]->(l)
    OPTIONAL MATCH (all_clubs)-[:PLAYED_HOME]->(m:Match)-[:IN_LEAGUE]->(l)
    WITH all_clubs, l,
         count(m) as home_matches,
         sum(CASE WHEN m.winner = all_clubs.name THEN 1 ELSE 0 END) as home_wins,
         sum(CASE WHEN m.is_draw THEN 1 ELSE 0 END) as home_draws,
         sum(m.home_score) as home_goals_for,
         sum(m.away_score) as home_goals_against
    OPTIONAL MATCH (all_clubs)-[:PLAYED_AWAY]->(ma:Match)-[:IN_LEAGUE]->(l)
    WITH all_clubs,
         home_matches + count(ma) as matches_played,
         home_wins + sum(CASE WHEN ma.winner = all_clubs.name THEN 1 ELSE 0 END) as wins,
         home_draws + sum(CASE WHEN ma.is_draw THEN 1 ELSE 0 END) as draws,
         home_goals_for + sum(ma.away_score) as goals_for,
         home_goals_against + sum(ma.home_score) as goals_against
    WITH all_