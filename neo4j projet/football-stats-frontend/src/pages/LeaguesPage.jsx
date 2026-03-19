import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getAllLeagues, getAllCompetitions } from '../services/api';
import { Trophy, Award } from 'lucide-react';

const leagueLogos = {
  'Premier League': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
  'La Liga': '🇪🇸',
  'Serie A': '🇮🇹',
  'Bundesliga': '🇩🇪',
  'Ligue 1': '🇫🇷'
};

const competitionLogos = {
  'Champions League': '⭐',
  'Europa League': '🌟',
  'Europa Conference League': '✨',
  'FA Cup': '🏆'
};

function LeaguesPage() {
  const [leagues, setLeagues] = useState([]);
  const [competitions, setCompetitions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [leaguesRes, competitionsRes] = await Promise.all([
          getAllLeagues(),
          getAllCompetitions()
        ]);
        setLeagues(leaguesRes.data.leagues);
        setCompetitions(competitionsRes.data.competitions);
      } catch (error) {
        console.error('Error fetching data:', error);
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

  return (
    <div className="space-y-12">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Leagues & Competitions</h1>
        <p className="text-gray-600">Explore Europe's top football leagues and competitions</p>
      </div>

      {/* Leagues Section */}
      <section>
        <div className="flex items-center mb-6">
          <Trophy className="h-8 w-8 text-blue-600 mr-3" />
          <h2 className="text-3xl font-bold">Top 5 Leagues</h2>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {leagues.map((league) => (
            <Link
              key={league.name}
              to={`/league/${encodeURIComponent(league.name)}`}
              className="bg-white rounded-lg shadow-lg p-8 hover:shadow-xl transition transform hover:-translate-y-1"
            >
              <div className="text-center">
                <div className="text-6xl mb-4">{leagueLogos[league.name] || '⚽'}</div>
                <h3 className="text-xl font-bold text-gray-800">{league.name}</h3>
                <p className="text-blue-600 mt-2 hover:underline">View Details →</p>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Competitions Section */}
      <section>
        <div className="flex items-center mb-6">
          <Award className="h-8 w-8 text-purple-600 mr-3" />
          <h2 className="text-3xl font-bold">European Competitions</h2>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {competitions.map((competition) => (
            <Link
              key={competition.name}
              to={`/competition/${encodeURIComponent(competition.name)}`}
              className="bg-gradient-to-br from-purple-500 to-blue-600 text-white rounded-lg shadow-lg p-8 hover:shadow-xl transition transform hover:-translate-y-1"
            >
              <div className="text-center">
                <div className="text-5xl mb-4">{competitionLogos[competition.name] || '🏆'}</div>
                <h3 className="text-lg font-bold">{competition.name}</h3>
                <p className="text-blue-100 mt-2 text-sm">View Matches →</p>
              </div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}

export default LeaguesPage;