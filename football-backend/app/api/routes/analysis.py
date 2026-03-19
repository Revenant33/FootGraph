# app/api/routes/analysis.py
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.database import neo4j_conn

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])

@router.get("/compare/players")
async def compare_players(player1: str, player2: str):
    """Compare deux joueurs statistiquement"""
    query = """
    MATCH (p1:Player {name: $player1})-[:PLAYS_FOR]->(c1:Club)
    MATCH (p1)-[:HAS_ADVANCED_STATS]->(ps1:PlayerStats)
    MATCH (p2:Player {name: $player2})-[:PLAYS_FOR]->(c2:Club)
    MATCH (p2)-[:HAS_ADVANCED_STATS]->(ps2:PlayerStats)
    RETURN {
        player1: {
            name: p1.name, club: c1.name, position: p1.position, age: p1.age,
            stats: {
                matches_played: ps1.matches_played, goals: ps1.goals, assists: ps1.assists,
                shots: ps1.shots, shot_on_target_pct: ps1.shot_on_target_pct,
                pass_completion_pct: ps1.pass_completion_pct, tackles: ps1.tackles,
                interceptions: ps1.interceptions, aerials_won: ps1.aerials_won
            }
        },
        player2: {
            name: p2.name, club: c2.name, position: p2.position, age: p2.age,
            stats: {
                matches_played: ps2.matches_played, goals: ps2.goals, assists: ps2.assists,
                shots: ps2.shots, shot_on_target_pct: ps2.shot_on_target_pct,
                pass_completion_pct: ps2.pass_completion_pct, tackles: ps2.tackles,
                interceptions: ps2.interceptions, aerials_won: ps2.aerials_won
            }
        }
    } as comparison
    """
    try:
        results = neo4j_conn.execute_query(query, {"player1": player1, "player2": player2})
        if not results:
            raise HTTPException(status_code=404, detail="One or both players not found")
        return results[0]['comparison']
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compare/teams")
async def compare_teams(team1: str, team2: str):
    """Compare deux équipes statistiquement"""
    query = """
    MATCH (c1:Club {name: $team1})
    OPTIONAL MATCH (c1)-[:PLAYED_HOME]->(home1:Match)
    OPTIONAL MATCH (c1)-[:PLAYED_AWAY]->(away1:Match)
    OPTIONAL MATCH (p1:Player)-[:PLAYS_FOR]->(c1)
    OPTIONAL MATCH (p1)-[:HAS_ADVANCED_STATS]->(ps1:PlayerStats)
    
    WITH c1,
         count(DISTINCT home1) + count(DISTINCT away1) as matches1,
         sum(CASE WHEN home1.winner = c1.name OR away1.winner = c1.name THEN 1 ELSE 0 END) as wins1,
         sum(ps1.goals) as goals1,
         count(DISTINCT p1) as squad1
    
    MATCH (c2:Club {name: $team2})
    OPTIONAL MATCH (c2)-[:PLAYED_HOME]->(home2:Match)
    OPTIONAL MATCH (c2)-[:PLAYED_AWAY]->(away2:Match)
    OPTIONAL MATCH (p2:Player)-[:PLAYS_FOR]->(c2)
    OPTIONAL MATCH (p2)-[:HAS_ADVANCED_STATS]->(ps2:PlayerStats)
    
    RETURN {
        team1: {
            name: c1.name,
            matches: matches1,
            wins: wins1,
            total_goals: goals1,
            squad_size: squad1
        },
        team2: {
            name: c2.name,
            matches: count(DISTINCT home2) + count(DISTINCT away2),
            wins: sum(CASE WHEN home2.winner = c2.name OR away2.winner = c2.name THEN 1 ELSE 0 END),
            total_goals: sum(ps2.goals),
            squad_size: count(DISTINCT p2)
        }
    } as comparison
    """
    try:
        results = neo4j_conn.execute_query(query, {"team1": team1, "team2": team2})
        if not results:
            raise HTTPException(status_code=404, detail="One or both teams not found")
        return results[0]['comparison']
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-by-metric")
async def get_top_by_metric(
    metric: str,
    position: Optional[str] = None,
    league: Optional[str] = None,
    limit: int = 20
):
    """Meilleurs joueurs par métrique spécifique"""
    
    valid_metrics = [
        'goals', 'assists', 'shots', 'shots_on_target', 'pass_completion_pct',
        'tackles', 'interceptions', 'blocks', 'aerials_won', 'progressive_carries'
    ]
    
    if metric not in valid_metrics:
        raise HTTPException(status_code=400, detail=f"Invalid metric. Choose from: {valid_metrics}")
    
    filters = []
    params = {"limit": limit}
    
    if position:
        filters.append("p.position = $position")
        params["position"] = position
    
    if league:
        filters.append("l.name = $league")
        params["league"] = league
        league_match = "MATCH (c)-[:PLAYS_IN]->(l:League)"
    else:
        league_match = ""
    
    where_clause = "WHERE " + " AND ".join(filters) if filters else ""
    
    query = f"""
    MATCH (p:Player)-[:PLAYS_FOR]->(c:Club)
    {league_match}
    MATCH (p)-[:HAS_ADVANCED_STATS]->(ps:PlayerStats)
    {where_clause}
    RETURN p.name as player_name,
           c.name as club_name,
           p.position as position,
           ps.{metric} as value,
           ps.matches_played as matches_played
    ORDER BY ps.{metric} DESC
    LIMIT $limit
    """
    
    try:
        results = neo4j_conn.execute_query(query, params)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics/by-nationality")
async def get_stats_by_nationality(limit: int = 20):
    """Statistiques agrégées par nationalité"""
    query = """
    MATCH (p:Player)-[:HAS_ADVANCED_STATS]->(ps:PlayerStats)
    WITH p.nation as nation,
         count(p) as player_count,
         sum(ps.goals) as total_goals,
         sum(ps.assists) as total_assists,
         avg(ps.pass_completion_pct) as avg_pass_completion
    WHERE player_count > 5
    RETURN nation,
           player_count,
           total_goals,
           total_assists,
           round(avg_pass_completion * 100) / 100 as avg_pass_completion
    ORDER BY total_goals DESC
    LIMIT $limit
    """
    try:
        results = neo4j_conn.execute_query(query, {"limit": limit})
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics/by-age-group")
async def get_stats_by_age_group():
    """Statistiques par tranche d'âge"""
    query = """
    MATCH (p:Player)-[:HAS_ADVANCED_STATS]->(ps:PlayerStats)
    WITH CASE
        WHEN p.age < 21 THEN 'U21'
        WHEN p.age >= 21 AND p.age < 25 THEN '21-24'
        WHEN p.age >= 25 AND p.age < 30 THEN '25-29'
        WHEN p.age >= 30 THEN '30+'
    END as age_group,
    p, ps
    RETURN age_group,
           count(p) as player_count,
           avg(ps.goals) as avg_goals,
           avg(ps.assists) as avg_assists,
           avg(ps.minutes) as avg_minutes,
           avg(ps.pass_completion_pct) as avg_pass_completion
    ORDER BY age_group
    """
    try:
        results = neo4j_conn.execute_query(query)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics/by-position")
async def get_stats_by_position():
    """Statistiques moyennes par position"""
    query = """
    MATCH (p:Player)-[:HAS_ADVANCED_STATS]->(ps:PlayerStats)
    WITH p.position as position,
         count(p) as player_count,
         avg(ps.goals) as avg_goals,
         avg(ps.assists) as a