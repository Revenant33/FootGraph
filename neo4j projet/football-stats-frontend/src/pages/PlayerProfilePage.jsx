import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getPlayerProfile } from '../services/api';
import { User, MapPin, Calendar, Shield } from 'lucide-react';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer } from 'recharts';

function PlayerProfilePage() {
  const { playerName } = useParams();
  const [player, setPlayer] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await getPlayerProfile(playerName);
        setPlayer(response.data);
      } catch (error) {
        console.error('Error fetching player profile:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [playerName]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!player) {
    return <div className="text-center py-12">Player not found</div>;
  }

  const stats = player.stats || {};

  // Prepare radar chart data with scaled values (max 40 instead of 100)
  const radarData = [
    { category: 'Goals', value: Math.min((stats.goals || 0) * 1.5, 40), fullMark: 40 },
    { category: 'Assists', value: Math.min((stats.assists || 0) * 2, 40), fullMark: 40 },
    { category: 'Passes', value: Math.min((stats.passes_completed || 0) / 80, 40), fullMark: 40 },
    { category: 'Tackles', value: Math.min((stats.tackles || 0) * 1.5, 40), fullMark: 40 },
    { category: 'Shots', value: Math.min((stats.shots || 0) / 3, 40), fullMark: 40 },
    { category: 'Aerials', value: Math.min((stats.aerials_won || 0) / 2, 40), fullMark: 40 }
  ];

  return (
    <div className="space-y-8">
      {/* Player Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-8 shadow-xl">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-4">{player.name}</h1>
            <div className="flex flex-wrap gap-4 text-blue-100">
              <div className="flex items-center">
                <Shield className="h-5 w-5 mr-2" />
                <span>{player.position}</span>
              </div>
              <div className="flex items-center">
                <MapPin className="h-5 w-5 mr-2" />
                <span>{player.nation}</span>
              </div>
              <div className="flex items-center">
                <Calendar className="h-5 w-5 mr-2" />
                <span>{player.age} years old</span>
              </div>
            </div>
            <Link
              to={`/team/${encodeURIComponent(player.club)}`}
              className="inline-block mt-4 text-lg font-semibold text-blue-100 hover:text-white"
            >
              {player.club} →
            </Link>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Main Stats */}
        <div className="lg:col-span-2 space-y-6">
          {/* Key Stats */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold mb-6">Season Statistics</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <p className="text-3xl font-bold text-blue-600">{stats.matches_played || 0}</p>
                <p className="text-sm text-gray-600 mt-1">Matches</p>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <p className="text-3xl font-bold text-green-600">{stats.goals || 0}</p>
                <p className="text-sm text-gray-600 mt-1">Goals</p>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <p className="text-3xl font-bold text-purple-600">{stats.assists || 0}</p>
                <p className="text-sm text-gray-600 mt-1">Assists</p>
              </div>
              <div className="text-center p-4 bg-yellow-50 rounded-lg">
                <p className="text-3xl font-bold text-yellow-600">{stats.minutes || 0}</p>
                <p className="text-sm text-gray-600 mt-1">Minutes</p>
              </div>
            </div>
          </div>

          {/* Shooting Stats */}
          {stats.shots > 0 && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-bold mb-4">Shooting</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <StatItem label="Shots" value={stats.shots} />
                <StatItem label="Shots on Target" value={stats.shots_on_target} />
                <StatItem label="Shot Accuracy" value={`${(stats.shot_on_target_pct || 0).toFixed(1)}%`} />
                <StatItem label="Goals per Shot" value={(stats.goals_per_shot || 0).toFixed(2)} />
                <StatItem label="Shot Distance" value={`${(stats.shot_distance || 0).toFixed(1)}m`} />
                <StatItem label="Penalties" value={stats.shot_penalty_kicks} />
              </div>
            </div>
          )}

          {/* Passing Stats */}
          {stats.passes_completed > 0 && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-bold mb-4">Passing</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <StatItem label="Passes Completed" value={stats.passes_completed} />
                <StatItem label="Pass Accuracy" value={`${(stats.pass_completion_pct || 0).toFixed(1)}%`} />
                <StatItem label="Key Passes" value={stats.assist_passes} />
                <StatItem label="Passes to Final 3rd" value={stats.passes_into_final_third} />
                <StatItem label="Passes to Penalty Area" value={stats.passes_into_penalty_area} />
                <StatItem label="Progressive Passes" value={stats.progressive_passes} />
              </div>
            </div>
          )}

          {/* Defensive Stats */}
          {stats.tackles > 0 && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-bold mb-4">Defensive</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <StatItem label="Tackles" value={stats.tackles} />
                <StatItem label="Tackles Won" value={stats.tackles_won} />
                <StatItem label="Interceptions" value={stats.interceptions} />
                <StatItem label="Blocks" value={stats.blocks} />
                <StatItem label="Clearances" value={stats.clearances} />
                <StatItem label="Aerials Won" value={stats.aerials_won} />
              </div>
            </div>
          )}

          {/* Possession Stats */}
          {stats.touches > 0 && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-bold mb-4">Possession</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <StatItem label="Touches" value={stats.touches} />
                <StatItem label="Carries" value={stats.carries} />
                <StatItem label="Progressive Carries" value={stats.progressive_carries} />
                <StatItem label="Take-Ons Attempted" value={stats.take_ons_attempted} />
                <StatItem label="Take-Ons Success" value={`${(stats.take_on_success_pct || 0).toFixed(1)}%`} />
                <StatItem label="Dispossessed" value={stats.dispossessed} />
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Radar Chart */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-bold mb-4">Performance Radar</h3>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="category" />
                <PolarRadiusAxis angle={90} domain={[0, 40]} />
                <Radar name="Player" dataKey="value" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.6} />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Discipline */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-bold mb-4">Discipline</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Yellow Cards</span>
                <span className="font-semibold">{stats.yellow_cards || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Red Cards</span>
                <span className="font-semibold">{stats.red_cards || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Fouls Committed</span>
                <span className="font-semibold">{stats.fouls_committed || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Fouls Drawn</span>
                <span className="font-semibold">{stats.fouls_drawn || 0}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatItem({ label, value }) {
  return (
    <div className="text-center p-3 bg-gray-50 rounded">
      <p className="text-2xl font-bold text-gray-800">{value || 0}</p>
      <p className="text-xs text-gray-600 mt-1">{label}</p>
    </div>
  );
}

export default PlayerProfilePage;