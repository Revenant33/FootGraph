import { useState, useEffect } from 'react';
import { getTopByMetric, getStatsByPosition, getStatsByAgeGroup, comparePlayersAnalysis, searchPlayers } from '../services/api';
import { BarChart3, Users, TrendingUp } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function AnalysisPage() {
  const [activeTab, setActiveTab] = useState('metrics');
  const [metric, setMetric] = useState('goals');
  const [position, setPosition] = useState('');
  const [topPlayers, setTopPlayers] = useState([]);
  const [positionStats, setPositionStats] = useState([]);
  const [ageGroupStats, setAgeGroupStats] = useState([]);
  const [comparisonPlayers, setComparisonPlayers] = useState(['', '']);
  const [comparisonResults, setComparisonResults] = useState(null);
  const [searchResults, setSearchResults] = useState([[], []]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (activeTab === 'metrics') {
      fetchTopPlayers();
    } else if (activeTab === 'demographics') {
      fetchDemographics();
    }
  }, [activeTab, metric, position]);

  const fetchTopPlayers = async () => {
    setLoading(true);
    try {
      const response = await getTopByMetric(metric, 20, position || null);
      setTopPlayers(response.data.players || []);
    } catch (error) {
      console.error('Error fetching top players:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDemographics = async () => {
    setLoading(true);
    try {
      const [posRes, ageRes] = await Promise.all([
        getStatsByPosition(),
        getStatsByAgeGroup()
      ]);
      setPositionStats(posRes.data.stats);
      setAgeGroupStats(ageRes.data.stats);
    } catch (error) {
      console.error('Error fetching demographics:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchPlayer = async (searchTerm, index) => {
    if (searchTerm.length < 2) {
      const newResults = [...searchResults];
      newResults[index] = [];
      setSearchResults(newResults);
      return;
    }

    try {
      const response = await searchPlayers(searchTerm, 10);
      const newResults = [...searchResults];
      newResults[index] = response.data.players;
      setSearchResults(newResults);
    } catch (error) {
      console.error('Error searching players:', error);
    }
  };

  const handleCompare = async () => {
    if (!comparisonPlayers[0] || !comparisonPlayers[1]) {
      alert('Please select two players to compare');
      return;
    }

    setLoading(true);
    try {
      const response = await comparePlayersAnalysis(comparisonPlayers);
      setComparisonResults(response.data);
    } catch (error) {
      console.error('Error comparing players:', error);
      alert('Error comparing players. Make sure both players exist.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold mb-4">Analysis</h1>
        <p className="text-gray-600">Deep dive into player and team statistics</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          <button
            onClick={() => setActiveTab('metrics')}
            className={`pb-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'metrics'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <BarChart3 className="inline h-5 w-5 mr-2" />
            Top by Metric
          </button>
          <button
            onClick={() => setActiveTab('comparison')}
            className={`pb-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'comparison'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <Users className="inline h-5 w-5 mr-2" />
            Player Comparison
          </button>
          <button
            onClick={() => setActiveTab('demographics')}
            className={`pb-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'demographics'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <TrendingUp className="inline h-5 w-5 mr-2" />
            Demographics
          </button>
        </nav>
      </div>

      {/* Top by Metric Tab */}
      {activeTab === 'metrics' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-4">Filter Players by Metric</h2>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Metric</label>
                <select
                  value={metric}
                  onChange={(e) => setMetric(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="goals">Goals</option>
                  <option value="assists">Assists</option>
                  <option value="shots">Shots</option>
                  <option value="tackles">Tackles</option>
                  <option value="interceptions">Interceptions</option>
                  <option value="passes_completed">Passes Completed</option>
                  <option value="pass_completion_pct">Pass Completion %</option>
                  <option value="aerials_won">Aerials Won</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Position (Optional)</label>
                <select
                  value={position}
                  onChange={(e) => setPosition(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Positions</option>
                  <option value="FW">Forward</option>
                  <option value="MF">Midfielder</option>
                  <option value="DF">Defender</option>
                  <option value="GK">Goalkeeper</option>
                </select>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-bold mb-4">Top Players - {metric}</h3>
            {loading ? (
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Rank</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Player</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Club</th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Position</th>
                      <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">Value</th>
                      <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase">Matches</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {topPlayers.map((player, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm font-bold">{index + 1}</td>
                        <td className="px-4 py-3 text-sm font-semibold text-blue-600">{player.name}</td>
                        <td className="px-4 py-3 text-sm">{player.club}</td>
                        <td className="px-4 py-3 text-sm">{player.position}</td>
                        <td className="px-4 py-3 text-center text-sm font-bold">{player.value}</td>
                        <td className="px-4 py-3 text-center text-sm">{player.matches_played}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Player Comparison Tab */}
      {activeTab === 'comparison' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-4">Compare Players</h2>
            <div className="grid md:grid-cols-2 gap-4 mb-4">
              {[0, 1].map((index) => (
                <div key={index} className="relative">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Player {index + 1}
                  </label>
                  <input
                    type="text"
                    placeholder="Search for player..."
                    onChange={(e) => handleSearchPlayer(e.target.value, index)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                  {searchResults[index]?.length > 0 && (
                    <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                      {searchResults[index].map((player, i) => (
                        <button
                          key={i}
                          onClick={() => {
                            const newPlayers = [...comparisonPlayers];
                            newPlayers[index] = player.name;
                            setComparisonPlayers(newPlayers);
                            const newResults = [...searchResults];
                            newResults[index] = [];
                            setSearchResults(newResults);
                          }}
                          className="w-full px-4 py-2 text-left hover:bg-gray-50 text-sm"
                        >
                          {player.name} - {player.club}
                        </button>
                      ))}
                    </div>
                  )}
                  {comparisonPlayers[index] && (
                    <div className="mt-2 px-3 py-2 bg-blue-50 text-blue-800 rounded text-sm">
                      Selected: {comparisonPlayers[index]}
                    </div>
                  )}
                </div>
              ))}
            </div>
            <button
              onClick={handleCompare}
              disabled={loading}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
            >
              {loading ? 'Comparing...' : 'Compare Players'}
            </button>
          </div>

          {comparisonResults && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-bold mb-6">Comparison Results</h3>
              <div className="grid md:grid-cols-2 gap-6">
                {comparisonResults.players?.map((player, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <h4 className="text-lg font-bold mb-2">{player.name}</h4>
                    <p className="text-sm text-gray-600 mb-4">
                      {player.club} • {player.position} • Age {player.age}
                    </p>
                    <div className="space-y-2">
                      {player.stats && Object.entries(player.stats).slice(0, 10).map(([key, value]) => (
                        <div key={key} className="flex justify-between text-sm">
                          <span className="text-gray-600">{key.replace(/_/g, ' ')}</span>
                          <span className="font-semibold">{value || 0}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Demographics Tab */}
      {activeTab === 'demographics' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-6">Statistics by Position</h2>
            {loading ? (
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={positionStats}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="position" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="total_players" fill="#3B82F6" name="Total Players" />
                  <Bar dataKey="avg_goals" fill="#10B981" name="Avg Goals" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-6">Statistics by Age Group</h2>
            {loading ? (
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={ageGroupStats}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="age_group" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="total_players" fill="#8B5CF6" name="Total Players" />
                  <Bar dataKey="avg_goals" fill="#F59E0B" name="Avg Goals" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default AnalysisPage;