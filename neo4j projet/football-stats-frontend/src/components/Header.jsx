import { Link } from 'react-router-dom';
import { Trophy, Users, BarChart3 } from 'lucide-react';

function Header() {
  return (
    <header className="bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between py-4">
          <Link to="/" className="flex items-center space-x-2">
            <Trophy className="h-8 w-8" />
            <span className="text-2xl font-bold">FootStats</span>
          </Link>
          
          <nav className="hidden md:flex space-x-8">
            <Link to="/" className="hover:text-blue-200 transition">
              Home
            </Link>
            <Link to="/leagues" className="hover:text-blue-200 transition">
              Leagues & Competitions
            </Link>
            <Link to="/players" className="hover:text-blue-200 transition">
              Players
            </Link>
            <Link to="/analysis" className="hover:text-blue-200 transition">
              Analysis
            </Link>
          </nav>

          <div className="md:hidden">
            <button className="text-white">
              <svg className="h-6 w-6" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                <path d="M4 6h16M4 12h16M4 18h16"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;