# app/models/schemas.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class LeagueBase(BaseModel):
    name: str

class League(LeagueBase):
    clubs_count: Optional[int] = 0
    matches_count: Optional[int] = 0

class CompetitionBase(BaseModel):
    name: str

class Competition(CompetitionBase):
    participants_count: Optional[int] = 0
    matches_count: Optional[int] = 0

class ClubBase(BaseModel):
    name: str

class Club(ClubBase):
    league: Optional[str] = None
    competitions: Optional[List[str]] = []
    players_count: Optional[int] = 0
    
class ClubStandings(BaseModel):
    position: int
    club_name: str
    matches_played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int

class PlayerBase(BaseModel):
    name: str
    nation: str
    position: str
    age: int
    born: int

class Player(PlayerBase):
    club: Optional[str] = None

class PlayerStats(BaseModel):
    # Basic
    matches_played: Optional[int] = 0
    starts: Optional[int] = 0
    minutes: Optional[int] = 0
    ninety_mins: Optional[float] = 0
    # Shooting
    goals: Optional[int] = 0
    shots: Optional[int] = 0
    shots_on_target: Optional[int] = 0
    shot_on_target_pct: Optional[float] = 0
    # Passing
    assists: Optional[int] = 0
    passes_completed: Optional[int] = 0
    passes_attempted: Optional[int] = 0
    pass_completion_pct: Optional[float] = 0
    # Defensive
    tackles: Optional[int] = 0
    interceptions: Optional[int] = 0
    blocks: Optional[int] = 0
    # Discipline
    yellow_cards: Optional[int] = 0
    red_cards: Optional[int] = 0

class PlayerWithStats(Player):
    stats: Optional[PlayerStats] = None

class MatchBase(BaseModel):
    date: str
    home_team_name: str
    away_team_name: str
    home_score: int
    away_score: int
    competition_name: str
    
class Match(MatchBase):
    attendance: Optional[float] = None
    round: Optional[str] = None
    winner: Optional[str] = None
    is_draw: bool
    total_goals: int
    goal_difference: int

class TopScorer(BaseModel):
    player_name: str
    club_name: str
    goals: int
    matches_played: int
    minutes: int

class TopAssister(BaseModel):
    player_name: str
    club_name: str
    assists: int
    mat