import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getLeagueDetails } from '../services/api';
import { Trophy, TrendingUp, Users } from 'lucide-react';

function LeagueDetailPage() {
  const { leagueName } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await getLeagueDetails(leagueName);
        setData(response.data);
      } catch (error) {
        console.error('Error fetching league details:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [leagueName]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!data) {
    return <div className="text-center py-12">League not found</div>;
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-8 shadow-xl">
        <h1 className="text-4xl font-bold mb-4">{data.league_name}</h1>
        <div className="flex flex-wrap gap-6 text-blue-100">
          <div>
            <p className="text-sm">Total Matches</p>
            <p className="text-2xl font-bold">{data.stats?.total_matches || 0}</p>
          </div>
          <div>
            <p className="text-sm">Total Goals</p>
            <p className="text-2xl font-bold">{data.stats?.total_goals || 0}</p>
          </div>
          <div>
            <p className="text-sm">Avg Goals/Match</p>
            <p className="text-2xl font-bold">{data.stats?.avg_goals_per_match || 0}</p>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Standings Table */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center mb-6">
            <Trophy className="h-6 w-6 text-yellow-500 mr-2" />
            <h2 className="text-2xl font-bold">Standings</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b-2 border-gray-200">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Pos</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Club</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">MP</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">W</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">D</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">L</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">GF</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">GA</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">GD</th>
                  <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">Pts</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {data.standings?.map((team, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-semibold">{index + 1}</td>
                    <td className="px-4 py-3">
                      <Link
                        to={`/team/${encodeURIComponent(team.club_name)}`}
                        className="text-blue-600 hover:underline font-medium"
                      >
                        {team.club_name}
                      </Link>
                    </td>
                    <td className="px-4 py-3 text-center text-sm">{team.matches_played}</td>
                    <td className="px-4 py-3 text-center text-sm text-green-600">{team.wins}</td>
                    <td className="px-4 py-3 text-center text-sm text-gray-600">{team.draws}</td>
                    <td className="px-4 py-3 text-center text-sm text-red-600">{team.losses}</td>
                    <td className="px-4 py-3 text-center text-sm">{team.goals_for}</td>
                    <td className="px-4 py-3 text-center text-sm">{team.goals_against}</td>
                    <td className="px-4 py-3 text-center text-sm font-semibold">{team.goal_difference}</td>
                    <td className="px-4 py-3 text-center text-sm font-bold text-blue-600">{team.points}</td>
                  </tr>
                ))}
              </tbody>
            </table>
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
              {data.top_scorers?.slice(0, 10).map((player, index) => (
                <Link
                  key={index}
                  to={`/player/${encodeURIComponent(player.name)}`}
                  className="flex justify-between items-center hover:bg-gray-50 p-2 rounded"
                >
                  <div>
                    <p className="font-semibold text-sm">{player.name}</p>
                    <p className="text-xs text-gray-500">{player.club}</p>
                  </div>
                  <span className="font-bold text-blue-600">{player.goals}</span>
                </Link>
              ))}
            </div>
          </div>

          {/* Clubs */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center mb-4">
              <Users className="h-5 w-5 text-purple-500 mr-2" />
              <h3 className="text-lg font-bold">All Clubs</h3>
            </div>
            <div className="space-y-2">
              {data.clubs?.map((club, index) => (
                <Link
                  key={index}
                  to={`/team/${encodeURIComponent(club)}`}
                  className="block text-sm text-blue-600 hover:underline"
                >
                  {club}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LeagueDetailPage;