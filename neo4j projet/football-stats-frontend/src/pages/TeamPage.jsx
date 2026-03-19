import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getTeamDetails, getTeamPlayers, getTeamMatches, getTeamTopPlayers } from '../services/api';
import { Shield, Users, Calendar, TrendingUp } from 'lucide-react';

function TeamPage() {
  const { teamName } = useParams();
  const [teamInfo, setTeamInfo] = useState(null);
  const [players, setPlayers] = useState([]);
  const [matches, setMatches] = useState([]);
  const [topScorers, setTopScorers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [infoRes, playersRes, matchesRes, scorersRes] = await Promise.all([
          getTeamDetails(teamName),
          getTeamPlayers(teamName),
          getTeamMatches(teamName, 20),
          getTeamTopPlayers(teamName, 'goals', 5)
        ]);

        setTeamInfo(infoRes.data);
        setPlayers(playersRes.data.players);
        setMatches(matchesRes.data.matches);
        setTopScorers(scorersRes.data.players);
      } catch (error) {
        console.error('Error fetching team data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [teamName]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!teamInfo) {
    return <div className="text-center py-12">Team not found</div>;
  }

  const stats = teamInfo.stats || {};

  return (
    <div className="space-y-8">
      {/* Team Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-8 shadow-xl">
        <div className="flex items-center mb-4">
          <Shield className="h-12 w-12 mr-4" />
          <div>
            <h1 className="text-4xl font-bold">{teamInfo.info?.name || teamName}</h1>
            <p className="text-blue-100 text-lg">{teamInfo.info?.league}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mt-6">
          <StatBox label="Matches" value={stats.total_matches} />
          <StatBox label="Wins" value={stats.wins} color="green" />
          <StatBox label="Draws" value={stats.draws} color="yellow" />
          <StatBox label="Losses" value={stats.losses} color="red" />
          <StatBox label="Win Rate" value={`${((stats.win_rate || 0) * 100).toFixed(1)}%`} />
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Recent Matches */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center mb-6">
              <Calendar className="h-6 w-6 text-blue-500 mr-2" />
              <h2 className="text-2xl font-bold">Recent Matches</h2>
            </div>
            <div className="space-y-3">
              {matches.map((match, index) => (
                <div key={index} className="border rounded-lg p-4 hover:shadow-md transition">
                  <div className="text-xs text-gray-500 mb-2">
                    {match.competition_name} • {new Date(match.date).toLocaleDateString()}
                  </div>
                  <div className="flex items-center justify-between">
                    <Link
                      to={`/team/${encodeURIComponent(match.home_team_name)}`}
                      className={`text-sm font-semibold flex-1 ${
                        match.home_team_name === teamName ? 'text-blue-600' : 'hover:text-blue-600'
                      }`}
                    >
                      {match.home_team_name}
                    </Link>
                    <div className="mx-4 px-4 py-2 bg-gray-100 rounded font-bold">
                      {match.home_score} - {match.away_score}
                    </div>
                    <Link
                      to={`/team/${encodeURIComponent(match.away_team_name)}`}
                      className={`text-sm font-semibold flex-1 text-right ${
                        match.away_team_name === teamName ? 'text-blue-600' : 'hover:text-blue-600'
                      }`}
                    >
                      {match.away_team_name}
                    </Link>
                  </div>
                  {match.winner !== 'Draw' && (
                    <div className="text-xs text-gray-500 mt-2 text-center">
                      Winner: {match.winner}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Squad */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center mb-6">
              <Users className="h-6 w-6 text-purple-500 mr-2" />
              <h2 className="text-2xl font-bold">Squad</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Name</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Position</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Nation</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Age</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {players.map((player, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <Link
                          to={`/player/${encodeURIComponent(player.name)}`}
                          className="text-blue-600 hover:underline font-medium"
                        >
                          {player.name}
                        </Link>
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <span className={`px-2 py-1 rounded text-xs ${
                          player.position === 'FW' ? 'bg-red-100 text-red-800' :
                          player.position === 'MF' ? 'bg-green-100 text-green-800' :
                          player.position === 'DF' ? 'bg-blue-100 text-blue-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {player.position}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm">{player.nation}</td>
                      <td className="px-4 py-3 text-sm">{player.age}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Top Scorers */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center mb-4">
              <TrendingUp className="h-5 w-5 text-green-500 mr-2" />
              <h3 className="text-lg font-bold">Top Scorers</h3>
            </div>
            <div className="space-y-3">
              {topScorers.map((player, index) => (
                <Link
                  key={index}
                  to={`/player/${encodeURIComponent(player.name)}`}
                  className="flex justify-between items-center hover:bg-gray-50 p-2 rounded"
                >
                  <div>
                    <p className="font-semibold text-sm">{player.name}</p>
                    <p className="text-xs text-gray-500">{player.position}</p>
                  </div>
                  <span className="font-bold text-blue-600 text-lg">{player.value}</span>
                </Link>
              ))}
            </div>
          </div>

          {/* Team Statistics */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold mb-4">Statistics</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Goals Scored</span>
                <span className="font-semibold">{stats.goals_scored || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Goals Conceded</span>
                <span className="font-semibold">{stats.goals_conceded || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Goal Difference</span>
                <span className={`font-semibold ${
                  (stats.goals_scored || 0) - (stats.goals_conceded || 0) > 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {(stats.goals_scored || 0) - (stats.goals_conceded || 0)}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatBox({ label, value, color = 'blue' }) {
  const colors = {
    blue: 'bg-blue-100 text-blue-800',
    green: 'bg-green-100 text-green-800',
    yellow: 'bg-yellow-100 text-yellow-800',
    red: 'bg-red-100 text-red-800'
  };

  return (
    <div className={`${colors[color]} rounded-lg p-4 text-center`}>
      <p className="text-2xl font-bold">{value || 0}</p>
      <p className="text-xs mt-1">{label}</p>
    </div>
  );
}

export default TeamPage;