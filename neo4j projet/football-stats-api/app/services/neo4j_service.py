from typing import List, Dict, Optional
from app.database import neo4j_conn


class Neo4jService:
    
    # ==================== HOME PAGE ====================
    
    @staticmethod
    def get_top_scorers(limit: int = 10, league: Optional[str] = None):
        """Get top scorers across all leagues or specific league"""
        league_filter = ""
        if league:
            league_filter = f"AND (c)-[:PLAYS_IN]->(:League {{name: '{league}'}})"
        
        query = f"""
        MATCH (p:Player)-[:PLAYS_FOR]->(c:Club)
        MATCH (p)-[:HAS_ADVANCED_STATS]->(ps:PlayerStats)
        WHERE ps.goals IS NOT NULL AND ps.goals > 0 {league_filter}
        RETURN p.name as name, c.name as club, 
               ps.goals as goals, ps.matches_played as matches_played
        ORDER BY ps.goals DESC, ps.matches_played ASC
        LIMIT {limit}
        """
        return neo4j_conn.execute_query(query)
    
    @staticmethod
    def get_top_assisters(limit: int = 10, league: Optional[str] = None):
        """Get top assist providers"""
        league_filter = ""
        if league:
            league_filter = f"AND (c)-[:PLAYS_IN]->(:League {{name: '{league}'}})"
        
        query = f"""
        MATCH (p:Player)-[:PLAYS_FOR]->(c:Club)
        MATCH (p)-[:HAS_ADVANCED_STATS]->(ps:PlayerStats)
        WHERE ps.assists IS NOT NULL AND ps.assists > 0 {league_filter}
        RETURN p.name as name, c.name as club, 
               ps.assists as assists, ps.matches_played as matches_played
        ORDER BY ps.assists DESC, ps.matches_played ASC
        LIMIT {limit}
        """
        return neo4j_conn.execute_query(query)
    
    @staticmethod
    def get_recent_matches(limit: int = 20):
        """Get most recent matches"""
        query = f"""
        MATCH (m:Match)
        RETURN m.date as date, m.home_team_name as home_team_name,
               m.away_team_name as away_team_name, m.home_score as home_score,
               m.away_score as away_score, m.competition_name as competition_name,
               m.winner as winner, m.is_draw as is_draw, m.attendance as attendance,
               m.round as round, m.total_goals as total_goals,
               m.goal_difference as goal_difference
        ORDER BY m.date DESC
        LIMIT {limit}
        """
        return neo4j_conn.execute_query(query)
    
    @staticmethod
    def get_league_standings_preview():
        """Get top 5 teams from each league for homepage preview"""
        query = """
        MATCH (c:Club)-[:PLAYS_IN]->(l:League)
        OPTIONAL MATCH (m:Match)-[:IN_LEAGUE]->(l)
        WHERE m.home_team_name = c.name OR m.away_team_name = c.name
        WITH l.name as league, c.name as club,
             collect(CASE 
                WHEN m.home_team_name = c.name THEN {
                    winner: m.winner,
                    is_draw: m.is_draw,
                    goals_for: m.home_score,
                    goals_against: m.away_score
                }
                WHEN m.away_team_name = c.name THEN {
                    winner: m.winner,
                    is_draw: m.is_draw,
                    goals_for: m.away_score,
                    goals_against: m.home_score
                }
                ELSE null
             END) as matches
        WITH league, club,
             [m IN matches WHERE m IS NOT NULL] as valid_matches
        WITH league, club,
             size(valid_matches) as matches_played,
             size([m IN valid_matches WHERE m.winner = club]) as wins,
             size([m IN valid_matches WHERE m.is_draw = true]) as draws,
             size([m IN valid_matches WHERE m.winner <> club AND m.is_draw = false]) as losses,
             reduce(s = 0, m IN valid_matches | s + m.goals_for) as goals_for,
             reduce(s = 0, m IN valid_matches | s + m.goals_against) as goals_against
        WITH league, club, matches_played, wins, draws, losses, 
             goals_for, goals_against,
             goals_for - goals_against as goal_difference,
             wins * 3 + draws as points
        ORDER BY league, points DESC, goal_difference DESC, goals_for DESC
        WITH league, collect({
            club_name: club,
            matches_played: matches_played,
            wins: wins,
            draws: draws,
            losses: losses,
            goals_for: goals_for,
            goals_against: goals_against,
            goal_difference: goal_difference,
            points: points
        })[0..5] as top_teams
        RETURN league, top_teams
        """
        results = neo4j_conn.execute_query(query)
        return {r['league']: r['top_teams'] for r in results}
    
    # ==================== LEAGUES ====================
    
    @staticmethod
    def get_all_leagues():
        """Get all leagues"""
        query = "MATCH (l:League) RETURN l.name as name"
        return neo4j_conn.execute_query(query)
    
    @staticmethod
    def get_league_standings(league_name: str):
        """Get complete standings for a league"""
        query = """
        MATCH (c:Club)-[:PLAYS_IN]->(l:League {name: $league_name})
        OPTIONAL MATCH (m:Match)-[:IN_LEAGUE]->(l)
        WHERE m.home_team_name = c.name OR m.away_team_name = c.name
        WITH c.name as club,
             collect(CASE 
                WHEN m.home_team_name = c.name THEN {
                    type: 'home',
                    winner: m.winner,
                    is_draw: m.is_draw,
                    goals_for: m.home_score,
                    goals_against: m.away_score
                }
                WHEN m.away_team_name = c.name THEN {
                    type: 'away',
                    winner: m.winner,
                    is_draw: m.is_draw,
                    goals_for: m.away_score,
                    goals_against: m.home_score
                }
                ELSE null
             END) as matches
        WITH club,
             [m IN matches WHERE m IS NOT NULL] as valid_matches
        WITH club,
             size(valid_matches) as matches_played,
             size([m IN valid_matches WHERE m.winner = club]) as wins,
             size([m IN valid_matches WHERE m.is_draw = true]) as draws,
             size([m IN valid_matches WHERE m.winner <> club AND m.is_draw = false]) as losses,
             reduce(s = 0, m IN valid_matches | s + m.goals_for) as goals_for,
             reduce(s = 0, m IN valid_matches | s + m.goals_against) as goals_against
        WITH club, matches_played, wins, draws, losses, 
             goals_for, goals_against,
             goals_for - goals_against as goal_difference,
             wins * 3 + draws as points
        RETURN club as club_name, 
               matches_played, 
               wins, 
               draws, 
               losses,
               goals_for, 
               goals_against, 
               goal_difference, 
               points
        ORDER BY points DESC, goal_difference DESC, goals_for DESC
        """
        return neo4j_conn.execute_query(query, {'league_name': league_name})
    
    @staticmethod
    def get_league_clubs(league_name: str):
        """Get all clubs in a league"""
        query = f"""
        MATCH (c:Club)-[:PLAYS_IN]->(l:League {{name: '{league_name}'}})
        RETURN c.name as name
        ORDER BY c.name
        """
        return neo4j_conn.execute_query(query)
    
    @staticmethod
    def get_league_stats(league_name: str):
        """Get aggregate statistics for a league"""
        query = f"""
        MATCH (m:Match)-[:IN_LEAGUE]->(l:League {{name: '{league_name}'}})
        RETURN count(m) as total_matches,
               sum(m.total_goals) as total_goals,
               avg(m.total_goals) as avg_goals_per_match
        """
        return neo4j_conn.execute_query(query)
    
    # ==================== COMPETITIONS ====================
    
    @staticmethod
    def get_all_competitions():
        """Get all competitions"""
        query = "MATCH (c:Competition) RETURN c.name as name"
        return neo4j_conn.execute_query(query)
    
    @staticmethod
    def get_competition_matches(competition_name: str):
        """Get all matches in a competition grouped by round"""
        query = f"""
        MATCH (m:Match)-[:IN_COMPETITION]->(c:Competition {{name: '{competition_name}'}})
        RETURN m.date as date, m.home_team_name as home_team_name,
               m.away_team_name as away_team_name, m.home_score as home_score,
               m.away_score as away_score, m.winner as winner,
               m.is_draw as is_draw, m.round as round, m.attendance as attendance,
               m.total_goals as total_goals, m.goal_difference as goal_difference,
               m.competition_name as competition_name
        ORDER BY m.date DESC
        """
        return neo4j_conn.execute_query(query)
    
    @staticmethod
    def get_competition_participants(competition_name: str):
        """Get clubs that participated in a competition"""
        query = f"""
        MATCH (c:Club)-[:PARTICIPATES_IN]->(comp:Competition {{name: '{competition_name}'}})
        RETURN c.name as name
        ORDER BY c.name
        """
        return neo4j_conn.execute_query(query)
    
    # ==================== TEAMS ====================
    
    @staticmethod
    def get_team_info(team_name: str):
        """Get team basic information"""
        query = f"""
        MATCH (c:Club {{name: '{team_name}'}})
        OPTIONAL MATCH (c)-[:PLAYS_IN]->(l:League)
        OPTIONAL MATCH (c)-[:PARTICIPATES_IN]->(comp:Competition)
        RETURN c.name as name, l.name as league, 
               collect(DISTINCT comp.name) as competitions
        """
        results = neo4j_conn.execute_query(query)
        return results[0] if results else None
    
    @staticmethod
    def get_team_stats(team_name: str):
        """Get team match statistics"""
        query = """
        MATCH (c:Club {name: $team_name})
        OPTIONAL MATCH (m:Match)
        WHERE m.home_team_name = c.name OR m.away_team_name = c.name
        WITH c,
             collect(CASE 
                WHEN m.home_team_name = c.name THEN {
                    winner: m.winner,
                    is_draw: m.is_draw,
                    goals_for: m.home_score,
                    goals_against: m.away_score
                }
                WHEN m.away_team_name = c.name THEN {
                    winner: m.winner,
                    is_draw: m.is_draw,
                    goals_for: m.away_score,
                    goals_against: m.home_score
                }
                ELSE null
             END) as matches
        WITH c,
             [m IN matches WHERE m IS NOT NULL] as valid_matches
        WITH c,
             size(valid_matches) as total_matches,
             size([m IN valid_matches WHERE m.winner = c.name]) as wins,
             size([m IN valid_matches WHERE m.is_draw = true]) as draws,
             size([m IN valid_matches WHERE m.winner <> c.name AND m.is_draw = false]) as losses,
             reduce(s = 0, m IN valid_matches | s + m.goals_for) as goals_scored,
             reduce(s = 0, m IN valid_matches | s + m.goals_against) as goals_conceded
        RETURN c.name as club_name, 
               total_matches, 
               wins, 
               draws, 
               losses,
               goals_scored, 
               goals_conceded,
               CASE WHEN total_matches > 0 THEN toFloat(wins) / total_matches ELSE 0.0 END as win_rate
        """
        results = neo4j_conn.execute_query(query, {'team_name': team_name})
        return results[0] if results else None
    
    @staticmethod
    def get_team_players(team_name: str):
        """Get all players in a team"""
        query = f"""
        MATCH (p:Player)-[:PLAYS_FOR]->(c:Club {{name: '{team_name}'}})
        RETURN p.name as name, p.nation as nation, p.position as position,
               p.age as age, p.born as born
        ORDER BY p.position, p.name
        """
        return neo4j_conn.execute_query(query)
    
    @staticmethod
    def get_team_matches(team_name: str, limit: int = 50):
        """Get team's matches"""
        query = """
        MATCH (c:Club {name: $team_name})
        MATCH (m:Match)
        WHERE m.home_team_name = c.name OR m.away_team_name = c.name
        WITH DISTINCT m
        RETURN m.date as date, m.home_team_name as home_team_name,
               m.away_team_name as away_team_name, 
               m.home_score as home_score, m.away_score as away_score,
               m.competition_name as competition_name, m.winner as winner,
               m.is_draw as is_draw, m.round as round
        ORDER BY m.date DESC
        LIMIT $limit
        """
        return neo4j_conn.execute_query(query, {'team_name': team_name, 'limit': limit})
    
    @staticmethod
    def get_team_top_players(team_name: str, metric: str = "goals", limit: int = 5):
        """Get team's top players by a specific metric"""
        query = f"""
        MATCH (p:Player)-[:PLAYS_FOR]->(c:Club {{name: '{team_name}'}})
        MATCH (p)-[:HAS_ADVANCED_STATS]->(ps:PlayerStats)
        WHERE ps.{metric} IS NOT NULL AND ps.{metric} > 0
        RETURN p.name as name, p.position as position,
               ps.{metric} as value, ps.matches_played as matches_played
        ORDER BY ps.{metric} DESC
        LIMIT {limit}
        """
        return neo4j_conn.execute_query(query)
    
    # ==================== PLAYERS ====================
    
    @staticmethod
    def get_all_players(
        limit: int = 100, 
        offset: int = 0,
        position: Optional[str] = None,
        nation: Optional[str] = None,
        club: Optional[str] = None,
        min_age: Optional[int] = None,
        max_age: Optional[int] = None
    ):
        """Get players with filters and pagination"""
        filters = []
        if position:
            filters.append(f"p.position = '{position}'")
        if nation:
            filters.append(f"p.nation = '{nation}'")
        if club:
            filters.append(f"c.name = '{club}'")
        if min_age:
            filters.append(f"p.age >= {min_age}")
        if max_age:
            filters.append(f"p.age <= {max_age}")
        
        where_clause = "WHERE " + " AND ".join(filters) if filters else ""
        
        query = f"""
        MATCH (p:Player)-[:PLAYS_FOR]->(c:Club)
        {where_clause}
        RETURN p.name as name, p.nation as nation, p.position as position,
               p.age as age, p.born as born, c.name as club
        ORDER BY p.name
        SKIP {offset}
        LIMIT {limit}
        """
        return neo4j_conn.execute_query(query)
    
    @staticmethod
    def get_player_profile(player_name: str):
        """Get complete player profile with stats"""
        query = f"""
        MATCH (p:Player {{name: '{player_name}'}})-[:PLAYS_FOR]->(c:Club)
        OPTIONAL MATCH (p)-[:HAS_ADVANCED_STATS]->(ps:PlayerStats)
        RETURN p.name as name, p.nation as nation, p.position as position,
               p.age as age, p.born as born, c.name as club, properties(ps) as stats
        """
        results = neo4j_conn.execute_query(query)
        return results[0] if results else None
    
    @staticmethod
    def search_players(search_term: str, limit: int = 20):
        """Search players by name"""
        query = f"""
        MATCH (p:Player)-[:PLAYS_FOR]->(c:Club)
        WHERE toLower(p.name) CONTAINS toLower('{search_term}')
        RETURN p.name as name, p.nation as nation, p.position as position,
               p.age as age, c.name as club
        ORDER BY p.name
        LIMIT {limit}
        """
        return neo4j_conn.execute_query(query)
    
    # ==================== ANALYSIS ====================
    
    @staticmethod
    def compare_players(player_names: List[str]):
        """Compare multiple players"""
        names_str = "', '".join(player_names)
        query = f"""
        MATCH (p:Player)-[:PLAYS_FOR]->(c:Club)
        WHERE p.name IN ['{names_str}']
        OPTIONAL MATCH (p)-[:HAS_ADVANCED_STATS]->(ps:PlayerStats)
        RETURN p.name as name, p.nation as nation, p.position as position,
               p.age as age, c.name as club, properties(ps) as stats
        """
        return neo4j_conn.execute_query(query)
    
    @staticmethod
    def get_top_players_by_metric(metric: str, limit: int = 20, position: Optional[str] = None):
        """Get top players by any statistical metric"""
        position_filter = f"AND p.position = '{position}'" if position else ""
        
        query = f"""
        MATCH (p:Player)-[:PLAYS_FOR]->(c:Club)
        MATCH (p)-[:HAS_ADVANCED_STATS]->(ps:PlayerStats)
        WHERE ps.{metric} IS NOT NULL AND ps.{metric} > 0 {position_filter}
        RETURN p.name as name, c.name as club, p.position as position,
               ps.{metric} as value, ps.matches_played as matches_played
        ORDER BY ps.{metric} DESC
        LIMIT {limit}
        """
        return neo4j_conn.execute_query(query)
    
    @staticmethod
    def get_stats_by_nationality(nation: Optional[str] = None):
        """Get aggregate statistics by nationality"""
        nation_filter = f"WHERE p.nation = '{nation}'" if nation else ""
        
        query = f"""
        MATCH (p:Player)
        {nation_filter}
        OPTIONAL MATCH (p)-[:HAS_ADVANCED_STATS]->(ps:PlayerStats)
        WITH p.nation as nation, 
             count(p) as total_players,
             sum(ps.goals) as total_goals,
             sum(ps.assists) as total_assists,
             avg(p.age) as avg_age
        RETURN nation, total_players, total_goals, total_assists, avg_age
        ORDER BY total_players DESC
        """
        return neo4j_conn.execute_query(query)
    
    @staticmethod
    def get_stats_by_position():
        """Get aggregate statistics by position"""
        query = """
        MATCH (p:Player)-[:HAS_ADVANCED_STATS]->(ps:PlayerStats)
        WITH p.position as position,
             count(p) as total_players,
             avg(p.age) as avg_age,
             avg(ps.goals) as avg_goals,
             avg(ps.assists) as avg_assists,
             avg(ps.matches_played) as avg_matches
        RETURN position, total_players, avg_age, avg_goals, avg_assists, avg_matches
        ORDER BY position
        """
        return neo4j_conn.execute_query(query)
    
    @staticmethod
    def get_stats_by_age_group():
        """Get statistics grouped by age ranges"""
        query = """
        MATCH (p:Player)-[:HAS_ADVANCED_STATS]->(ps:PlayerStats)
        WITH CASE
            WHEN p.age < 21 THEN 'U21'
            WHEN p.age >= 21 AND p.age < 25 THEN '21-24'
            WHEN p.age >= 25 AND p.age < 30 THEN '25-29'
            WHEN p.age >= 30 THEN '30+'
        END as age_group,
        count(p) as total_players,
        avg(ps.goals) as avg_goals,
        avg(ps.assists) as avg_assists,
        avg(ps.matches_played) as avg_matches
        RETURN age_group, total_players, avg_goals, avg_assists, avg_matches
        ORDER BY age_group
        """
        return neo4j_conn.execute_query(query)