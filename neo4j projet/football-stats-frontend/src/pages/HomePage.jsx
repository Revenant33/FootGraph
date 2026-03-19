import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getHomePageData } from '../services/api';
import { Trophy, Target, Calendar } from 'lucide-react';

function HomePage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await getHomePageData();
        setData(response.data);
      } catch (error) {
        console.error('Error fetching home page data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!data) {
    return <div className="text-center py-12">Error loading data</div>;
  }

  return (
    <div className="space-y-12">
      {/* Hero Section */}

      <section className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-8 shadow-xl">
        <h1 className="text-4xl font-bold mb-4">Football Statistics Hub</h1>
        
        <p className="text-xl text-blue-100">
          Explore comprehensive stats from Europe's top 5 leagues and competitions
        </p>
      </section>

      {/* Top Scorers & Assisters */}
      <section className="grid md:grid-cols-2 gap-8">
        {/* Top Scorers */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center mb-6">
            <Trophy className="h-6 w-6 text-yellow-500 mr-2" />
            <h2 className="text-2xl font-bold">Top Scorers</h2>
          </div>
          <div className="space-y-3">
            {data.top_scorers?.slice(0, 10).map((player, index) => (
              <Link
                key={index}
                to={`/player/${encodeURIComponent(player.name)}`}
                className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition"
              >
                <div className="flex items-center space-x-3">
                  <span className="text-2xl font-bold text-gray-300 w-8">
                    {index + 1}
                  </span>
                  <div>
                    <p className="font-semibold">{player.name}</p>
                    <p className="text-sm text-gray-500">{player.club}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-blue-600">{player.goals}</p>
                  <p className="text-xs text-gray-500">{player.matches_played} matches</p>
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Top Assisters */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center mb-6">
            <Target className="h-6 w-6 text-green-500 mr-2" />
            <h2 className="text-2xl font-bold">Top Assisters</h2>
          </div>
          <div className="space-y-3">
            {data.top_assisters?.slice(0, 10).map((player, index) => (
              <Link
                key={index}
                to={`/player/${encodeURIComponent(player.name)}`}
                className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition"
              >
                <div className="flex items-center space-x-3">
                  <span className="text-2xl font-bold text-gray-300 w-8">
                    {index + 1}
                  </span>
                  <div>
                    <p className="font-semibold">{player.name}</p>
                    <p className="text-sm text-gray-500">{player.club}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-green-600">{player.assists}</p>
                  <p className="text-xs text-gray-500">{player.matches_played} matches</p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* League Standings Preview */}
      <section className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-6">League Standings</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Object.entries(data.league_standings_preview || {}).map(([league, standings]) => (
            <div key={league} className="border rounded-lg p-4">
              <Link
                to={`/league/${encodeURIComponent(league)}`}
                className="text-lg font-bold text-blue-600 hover:text-blue-800 mb-3 block"
              >
                {league}
              </Link>
              <div className="space-y-2">
                {standings.slice(0, 5).map((team, index) => (
                  <div key={index} className="flex justify-between text-sm">
                    <span className="flex items-center">
                      <span className="w-6 text-gray-500">{index + 1}</span>
                      <Link
                        to={`/team/${encodeURIComponent(team.club_name)}`}
                        className="hover:text-blue-600 truncate"
                      >
                        {team.club_name}
                      </Link>
                    </span>
                    <span className="font-semibold">{team.points} pts</span>
                  </div>
                ))}
              </div>
              <Link
                to={`/league/${encodeURIComponent(league)}`}
                className="text-sm text-blue-600 hover:text-blue-800 mt-3 inline-block"
              >
                View full table →
              </Link>
            </div>
          ))}
        </div>
      </section>

      {/* Recent Matches */}
      <section className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center mb-6">
          <Calendar className="h-6 w-6 text-blue-500 mr-2" />
          <h2 className="text-2xl font-bold">Recent Matches</h2>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.recent_matches?.slice(0, 12).map((match, index) => (
            <div key={index} className="border rounded-lg p-4 hover:shadow-md transition">
              <div className="text-xs text-gray-500 mb-2">
                {match.competition_name} • {new Date(match.date).toLocaleDateString()}
              </div>
              <div className="flex items-center justify-between">
                <Link
                  to={`/team/${encodeURIComponent(match.home_team_name)}`}
                  className="text-sm font-semibold hover:text-blue-600 flex-1 truncate"
                >
                  {match.home_team_name}
                </Link>
                <div className="mx-4 text-lg font-bold">
                  {match.home_score} - {match.away_score}
                </div>
                <Link
                  to={`/team/${encodeURIComponent(match.away_team_name)}`}
                  className="text-sm font-semibold hover:text-blue-600 flex-1 truncate text-right"
                >
                  {match.away_team_name}
                </Link>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default HomePage;