# app/api/routes/players.py
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.schemas import PlayerWithStats
from app.database import neo4j_conn

router = APIRouter(prefix="/api/players", tags=["Players"])

@router.get("/", response_model=List[PlayerWithStats])
async def get_players(
    position: Optional[str] = None,
    nation: Optional[str] = None,
    club: Optional[str] = None,
    min_goals: Optional[int] = None,
    min_assists: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Liste des joueurs avec filtres multiples"""
    
    filters = []
    params = {"limit": limit, "offset": offset}
    
    if position:
        filters.append("p.position = $position")
        params["position"] = position
    
    if nation:
        filters.append("p.nation = $nation")
        params["nation"] = nation
    
    if club:
        filters.append("c.name = $club")
        params["club"] = club
    
    if min_goals is not None:
        filters.append("ps.goals >= $min_goals")
        params["min_goals"] = min_goals
    
    if min_assists is not None:
        filters.append("ps.assists >= $min_assists")
        params["min_assists"] = min_assists
    
    if search:
        filters.append("toLower(p.name) CONTAINS toLower($search)")
        params["search"] = search
    
    where_clause = "WHERE " + " AND ".join(filters) if filters else ""
    
    query = f"""
    MATCH (p:Player)-[:PLAYS_FOR]->(c:Club)
    OPTIONAL MATCH (p)-[:HAS_ADVANCED_STATS]->(ps:PlayerStats)
    {where_clause}
    RETURN p.name as name,
           p.nation as nation,
           p.position as position,
           p.age as age,
           p.born as born,
           c.name as club,
           {{
               matches_played: COALESCE(ps.matches_played, 0),
               starts: COALESCE(ps.starts, 0),
               minutes: COALESCE(ps.minutes, 0),
               ninety_mins: COALESCE(ps.ninety_mins, 0),
               goals: COALESCE(ps.goals, 0),
               assists: COALESCE(ps.assists, 0),
               shots: COALESCE(ps.shots, 0),
               shots_on_target: COALESCE(ps.shots_on_target, 0),
               shot_on_target_pct: COALESCE(ps.shot_on_target_pct, 0),
               passes_completed: COALESCE(ps.passes_completed, 0),
               passes_attempted: COALESCE(ps.passes_attempted, 0),
               pass_completion_pct: COALESCE(ps.pass_completion_pct, 0),
               tackles: COALESCE(ps.tackles, 0),
               interceptions: COALESCE(ps.interceptions, 0),
               blocks: COALESCE(ps.blocks, 0),
               yellow_cards: COALESCE(ps.yellow_cards, 0),
               red_cards: COALESCE(ps.red_cards, 0)
           }} as stats
    ORDER BY p.name
    SKIP $offset
    LIMIT $limit
    """
    
    try:
        results = neo4j_conn.execute_query(query, params)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{player_name}", response_model=PlayerWithStats)
async def get_player_profile(player_name: str):
    """Profil complet d'un joueur avec toutes ses statistiques"""
    query = """
    MATCH (p:Player {name: $player_name})-[:PLAYS_FOR]->(c:Club)
    MATCH (p)-[:HAS_ADVANCED_STATS]->(ps:PlayerStats)
    RETURN p.name as name,
           p.nation as nation,
           p.position as position,
           p.age as age,
           p.born as born,
           c.name as club,
           {
               matches_played: ps.matches_played,
               starts: ps.starts,
               minutes: ps.minutes,
               ninety_mins: ps.ninety_mins,
               goals: ps.goals,
               shots: ps.shots,
               shots_on_target: ps.shots_on_target,
               shot_on_target_pct: ps.shot_on_target_pct,
               assists: ps.assists,
               passes_completed: ps.passes_completed,
               passes_attempted: ps.passes_attempted,
               pass_completion_pct: ps.pass_completion_pct,
               tackles: ps.tackles,
               interceptions: ps.interceptions,
               blocks: ps.blocks,
               yellow_cards: ps.yellow_cards,
               red_cards: ps.red_cards
           } as stats
    """
    try:
        results = neo4j_conn.execute_query(query, {"player_name": player_name})
        if not results:
            raise HTTPException(status_code=404, detail="Player not found")
        return results[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/autocomplete")
async def search_players_autocomplete(q: str, limit: int = 10):
    """Recherche autocomplete pour les joueurs"""
    query = """
    MATCH (p:Player)-[:PLAYS_FOR]->(c:Club)
    WHERE toLower(p.name) CONTAINS toLower($q)
    RETURN p.name as name, c.name as club, p.position as position
    ORDER BY p.name
    LIMIT $limit
    """
    try:
        results = neo4j_conn.execute_query(query, {"q": q, "limit": limit})
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/positions/list")
async def get_positions():
    """Liste des positions disponibles"""
    query = """
    MATCH (p:Player)
    RETURN DISTINCT p.position as position
    ORDER BY p.position
    """
    try:
        results = neo4j_conn.execute_query(query)
        return [r['position'] for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nations/list")
async def get_nations():
    """Liste des nationalités disponibles"""
    query = """
    MATCH (p:Player)
    RETURN DISTINCT p.nation as nation
    ORDER BY p.nation
    """
    try:
        results = neo4j_conn.execute_query(query)
        return [r['nation'] for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))