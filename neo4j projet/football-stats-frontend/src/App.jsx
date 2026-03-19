import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import HomePage from './pages/HomePage';
import LeaguesPage from './pages/LeaguesPage';
import LeagueDetailPage from './pages/LeagueDetailPage';
import CompetitionDetailPage from './pages/CompetitionDetailPage';
import TeamPage from './pages/TeamPage';
import PlayerListPage from './pages/PlayerListPage';
import PlayerProfilePage from './pages/PlayerProfilePage';
import AnalysisPage from './pages/AnalysisPage';

function App() {
  return (
    <Router>
      <div className="min-h-screen flex flex-col bg-gray-50">
        <Header />
        <main className="flex-grow container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/leagues" element={<LeaguesPage />} />
            <Route path="/league/:leagueName" element={<LeagueDetailPage />} />
            <Route path="/competition/:competitionName" element={<CompetitionDetailPage />} />
            <Route path="/team/:teamName" element={<TeamPage />} />
            <Route path="/players" element={<PlayerListPage />} />
            <Route path="/player/:playerName" element={<PlayerProfilePage />} />
            <Route path="/analysis" element={<AnalysisPage />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;