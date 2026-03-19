import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Home Page
export const getHomePageData = () => api.get('/home');

// Leagues
export const getAllLeagues = () => api.get('/leagues/');
export const getLeagueDetails = (leagueName) => api.get(`/leagues/${encodeURIComponent(leagueName)}`);
export const getLeagueStandings = (leagueName) => api.get(`/leagues/${encodeURIComponent(leagueName)}/standings`);
export const getLeagueClubs = (leagueName) => api.get(`/leagues/${encodeURIComponent(leagueName)}/clubs`);
export const getLeagueTopScorers = (leagueName, limit = 20) => api.get(`/leagues/${encodeURIComponent(leagueName)}/top-scorers`, { params: { limit } });

// Competitions
export const getAllCompetitions = () => api.get('/competitions/');
export const getCompetitionDetails = (competitionName) => api.get(`/competitions/${encodeURIComponent(competitionName)}`);
export const getCompetitionMatches = (competitionName) => api.get(`/competitions/${encodeURIComponent(competitionName)}/matches`);
export const getCompetitionParticipants = (competitionName) => api.get(`/competitions/${encodeURIComponent(competitionName)}/participants`);

// Teams
export const getTeamDetails = (teamName) => api.get(`/teams/${encodeURIComponent(teamName)}`);
export const getTeamPlayers = (teamName) => api.get(`/teams/${encodeURIComponent(teamName)}/players`);
export const getTeamMatches = (teamName, limit = 50) => api.get(`/teams/${encodeURIComponent(teamName)}/matches`, { params: { limit } });
export const getTeamTopPlayers = (teamName, metric = 'goals', limit = 5) => api.get(`/teams/${encodeURIComponent(teamName)}/top-players`, { params: { metric, limit } });
export const getTeamStats = (teamName) => api.get(`/teams/${encodeURIComponent(teamName)}/stats`);

// Players
export const getAllPlayers = (params = {}) => api.get('/players/', { params });
export const searchPlayers = (query, limit = 20) => api.get('/players/search', { params: { q: query, limit } });
export const getPlayerProfile = (playerName) => api.get(`/players/${encodeURIComponent(playerName)}`);
export const getTopScorers = (limit = 20, league = null) => api.get('/players/top-scorers', { params: { limit, league } });
export const getTopAssisters = (limit = 20, league = null) => api.get('/players/top-assisters', { params: { limit, league } });
export const comparePlayers = (playerNames) => api.post('/players/compare', playerNames);

// Matches
export const getRecentMatches = (limit = 20) => api.get('/matches/recent', { params: { limit } });

// Analysis
export const getTopByMetric = (metric, limit = 20, position = null) => api.get('/analysis/top-by-metric', { params: { metric, limit, position } });
export const getStatsByNationality = (nation = null) => api.get('/analysis/by-nationality', { params: { nation } });
export const getStatsByPosition = () => api.get('/analysis/by-position');
export const getStatsByAgeGroup = () => api.get('/analysis/by-age-group');
export const comparePlayersAnalysis = (playerNames) => api.post('/analysis/compare-players', playerNames);

export default api;