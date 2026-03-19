from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Base Models
class League(BaseModel):
    name: str


class Competition(BaseModel):
    name: str


class Club(BaseModel):
    name: str
    league: Optional[str] = None
    competitions: Optional[List[str]] = None


class Player(BaseModel):
    name: str
    nation: str
    position: str
    age: int
    born: int
    club: Optional[str] = None


class PlayerStats(BaseModel):
    # Basic
    matches_played: Optional[int] = None
    starts: Optional[int] = None
    minutes: Optional[int] = None
    ninety_mins: Optional[float] = None
    
    # Shooting
    goals: Optional[int] = None
    shots: Optional[int] = None
    shots_on_target: Optional[int] = None
    shot_on_target_pct: Optional[float] = None
    goals_per_shot: Optional[float] = None
    goals_per_shot_on_target: Optional[float] = None
    shot_distance: Optional[float] = None
    shot_free_kicks: Optional[int] = None
    shot_penalty_kicks: Optional[int] = None
    penalty_kicks_attempted: Optional[int] = None
    
    # Passing
    passes_completed: Optional[int] = None
    passes_attempted: Optional[int] = None
    pass_completion_pct: Optional[float] = None
    total_pass_distance: Optional[float] = None
    progressive_pass_distance: Optional[float] = None
    assists: Optional[int] = None
    assist_passes: Optional[int] = None
    passes_into_final_third: Optional[int] = None
    passes_into_penalty_area: Optional[int] = None
    crosses_into_penalty_area: Optional[int] = None
    progressive_passes: Optional[int] = None
    
    # Defensive
    tackles: Optional[int] = None
    tackles_won: Optional[int] = None
    tackles_def_3rd: Optional[int] = None
    tackles_mid_3rd: Optional[int] = None
    tackles_att_3rd: Optional[int] = None
    blocks: Optional[int] = None
    blocked_shots: Optional[int] = None
    blocked_passes: Optional[int] = None
    interceptions: Optional[int] = None
    clearances: Optional[int] = None
    
    # Possession
    touches: Optional[int] = None
    take_ons_attempted: Optional[int] = None
    take_ons_successful: Optional[int] = None
    take_on_success_pct: Optional[float] = None
    carries: Optional[int] = None
    total_carry_distance: Optional[float] = None
    progressive_carry_distance: Optional[float] = None
    progressive_carries: Optional[int] = None
    
    # Discipline
    yellow_cards: Optional[int] = None
    red_cards: Optional[int] = None
    fouls_committed: Optional[int] = None
    fouls_drawn: Optional[int] = None
    
    # Aerial
    aerials_won: Optional[int] = None
    aerials_lost: Optional[int] = None
    aerial_win_pct: Optional[float] = None


class PlayerWithStats(Player):
    stats: Optional[PlayerStats] = None


class Match(BaseModel):
    date: str
    home_team_name: str
    away_team_name: str
    home_score: int
    away_score: int
    attendance: Optional[float] = None
    round: Optional[str] = None
    competition_name: str
    winner: str
    is_draw: bool
    total_goals: int
    goal_difference: int


# Response Models
class TopScorer(BaseModel):
    name: str
    club: str
    goals: int
    matches_played: int


class TopAssister(BaseModel):
    name: str
    club: str
    assists: int
    matches_played: int


class LeagueStanding(BaseModel):
    club_name: str
    matches_played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int


class TeamStats(BaseModel):
    club_name: str
    total_matches: int
    wins: int
    draws: int
    losses: int
    goals_scored: int
    goals_conceded: int
    win_rate: float
    league: Optional[str] = None
    position: Optional[int] = None


class HomePageData(BaseModel):
    top_scorers: List[TopScorer]
    top_assisters: List[TopAssister]
    recent_matches: List[Match]
    league_standings_preview: dict  # Dict[league_name, List[LeagueStanding]]


class LeagueDetailData(BaseModel):
    league_name: str
    standings: List[LeagueStanding]
    top_scorers: List[TopScorer]
    clubs: List[str]
    total_goals: int
    total_matches: int
    avg_goals_per_match: float


class CompetitionDetailData(BaseModel):
    competition_name: str
    matches_by_round: dict  # Dict[round, List[Match]]
    top_scorers: List[TopScorer]
    participating_clubs: List[str]


class PlayerComparison(BaseModel):
    players: List[PlayerWithStats]
    comparison_metrics: dict


class TeamComparison(BaseModel):
    teams: List[TeamStats]
    head_to_head: Optional[List[Match]] = None