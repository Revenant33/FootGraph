import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getAllPlayers, searchPlayers } from '../services/api';
import { Search, Filter } from 'lucide-react';

function PlayerListPage() {
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    position: '',
    nation: '',
    minAge: '',
    maxAge: ''
  });

  useEffect(() => {
    fetchPlayers();
  }, [filters]);

  const fetchPlayers = async () => {
    setLoading(true);
    try {
      const params = {
        limit: 100,
        ...(filters.position && { position: filters.position }),
        ...(filters.nation && { nation: filters.nation }),
        ...(filters.minAge && { min_age: filters.minAge }),
        ...(filters.maxAge && { max_age: filters.maxAge })
      };
      const response = await getAllPlayers(params);
      setPlayers(response.data.players);
    } catch (error) {
      console.error('Error fetching players:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (searchTerm.length < 2) {
      fetchPlayers();
      return;
    }
    setLoading(true);
    try {
      const response = await searchPlayers(searchTerm);
      setPlayers(response.data.players);
    } catch (error) {
      console.error('Error searching players:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold mb-4">Players</h1>
        <p className="text-gray-600">Browse and search through all players</p>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <form onSubmit={handleSearch} className="mb-4">
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search players by name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Search
            </button>
          </div>
        </form>

        <div className="flex items-center gap-2 mb-4">
          <Filter className="h-5 w-5 text-gray-500" />
          <span className="font-semibold">Filters:</span>
        </div>

        <div className="grid md:grid-cols-4 gap-4">
          <select
            value={filters.position}
            onChange={(e) => setFilters({ ...filters, position: e.target.value })}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Positions</option>
            <option value="FW">Forward</option>
            <option value="MF">Midfielder</option>
            <option value="DF">Defender</option>
            <option value="GK">Goalkeeper</option>
          </select>

          <input
            type="text"
            placeholder="Nation (e.g., ENG)"
            value={filters.nation}
            onChange={(e) => setFilters({ ...filters, nation: e.target.value.toUpperCase() })}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />

          <input
            type="number"
            placeholder="Min Age"
            value={filters.minAge}
            onChange={(e) => setFilters({ ...filters, minAge: e.target.value })}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />

          <input
            type="number"
            placeholder="Max Age"
            value={filters.maxAge}
            onChange={(e) => setFilters({ ...filters, maxAge: e.target.value })}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <button
          onClick={() => {
            setFilters({ position: '', nation: '', minAge: '', maxAge: '' });
            setSearchTerm('');
          }}
          className="mt-4 text-sm text-blue-600 hover:underline"
        >
          Clear all filters
        </button>
      </div>

      {/* Players Table */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b-2 border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Name</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Position</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Nation</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Age</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase">Club</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {players.map((player, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <Link
                          to={`/player/${encodeURIComponent(player.name)}`}
                          className="text-blue-600 hover:underline font-medium"
                        >
                          {player.name}
                        </Link>
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <span className={`px-2 py-1 rounded ${
                          player.position === 'FW' ? 'bg-red-100 text-red-800' :
                          player.position === 'MF' ? 'bg-green-100 text-green-800' :
                          player.position === 'DF' ? 'bg-blue-100 text-blue-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {player.position}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm">{player.nation}</td>
                      <td className="px-6 py-4 text-sm">{player.age}</td>
                      <td className="px-6 py-4 text-sm">
                        <Link
                          to={`/team/${encodeURIComponent(player.club)}`}
                          className="text-gray-600 hover:text-blue-600"
                        >
                          {player.club}
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="px-6 py-4 bg-gray-50 text-sm text-gray-600">
              Showing {players.length} players
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default PlayerListPage;