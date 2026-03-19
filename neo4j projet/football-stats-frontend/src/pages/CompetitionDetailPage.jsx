import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getCompetitionDetails } from '../services/api';
import { Trophy, Calendar, Users } from 'lucide-react';

function CompetitionDetailPage() {
  const { competitionName } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedRound, setSelectedRound] = useState('all');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await getCompetitionDetails(competitionName);
        setData(response.data);
        // Set first round as default if available
        if (response.data.matches_by_round) {
          const rounds = Object.keys(response.data.matches_by_round);
          if (rounds.length > 0) {
            setSelectedRound(rounds[0]);
          }
        }
      } catch (error) {
        console.error('Error fetching competition details:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [competitionName]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!data) {
    return <div className="text-center py-12">Competition not found</div>;
  }

  const rounds = Object.keys(data.matches_by_round || {});
  const displayMatches = selectedRound === 'all' 
    ? Object.values(data.matches_by_round || {}).flat()
    : data.matches_by_round[selectedRound] || [];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg p-8 shadow-xl">
        <div className="flex items-center mb-4">
          <Trophy className="h-12 w-12 mr-4" />
          <div>
            <h1 className="text-4xl font-bold">{data.competition_name}</h1>
            <p className="text-purple-100 text-lg mt-2">
              {data.total_matches} matches • {data.participating_clubs?.length} clubs
            </p>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Matches Section */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center">
                <Calendar className="h-6 w-6 text-blue-500 mr-2" />
                <h2 className="text-2xl font-bold">Matches</h2>
              </div>
              <select
                value={selectedRound}
                onChange={(e) => setSelectedRound(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Rounds</option>
                {rounds.map((round) => (
                  <option key={round} value={round}>
                    {round}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-3">
              {displayMatches.map((match, index) => (
                <div key={index} className="border rounded-lg p-4 hover:shadow-md transition">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-xs text-gray-500">
                      {new Date(match.date).toLocaleDateString()}
                    </span>
                    {match.round && (
                      <span className="text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded">
                        {match.round}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center justify-between">
                    <Link
                      to={`/team/${encodeURIComponent(match.home_team_name)}`}
                      className="text-sm font-semibold hover:text-blue-600 flex-1 truncate"
                    >
                      {match.home_team_name}
                    </Link>
                    <div className="mx-4 px-4 py-2 bg-gray-100 rounded font-bold">
                      {match.home_score} - {match.away_score}
                    </div>
                    <Link
                      to={`/team/${encodeURIComponent(match.away_team_name)}`}
                      className="text-sm font-semibold hover:text-blue-600 flex-1 truncate text-right"
                    >
                      {match.away_team_name}
                    </Link>
                  </div>
                  {match.attendance && (
                    <div className="text-xs text-gray-500 mt-2 text-center">
                      Attendance: {match.attendance.toLocaleString()}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Top Scorers */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold mb-4">Top Scorers</h3>
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

          {/* Participating Clubs */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center mb-4">
              <Users className="h-5 w-5 text-purple-500 mr-2" />
              <h3 className="text-lg font-bold">Participating Clubs</h3>
            </div>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {data.participating_clubs?.map((club, index) => (
                <Link
                  key={index}
                  to={`/team/${encodeURIComponent(club)}`}
                  className="block text-sm text-blue-600 hover:underline py-1"
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

export default CompetitionDetailPage;