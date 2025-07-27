import { useState } from 'react';
import { Link } from 'react-router-dom';
import '../holographic.css';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  return (
    <nav className="bg-gray-800/80 backdrop-blur-sm border-b border-gray-700/50 shadow-lg sticky top-0 z-50">
      <div className="container mx-auto px-6 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <div className="holographic-card flex items-center">
              <Link to="/" className="flex items-center space-x-0 mx-4">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center">
                  <span className="text-white text-xl font-bold">🛖</span>
                </div>
                <span className="text-2xl font-bold text-gray-300 bg-clip-text text-transparent">
                  
                </span>
              </Link>
            </div>
          </div>

          {/* Menú para escritorio */}
          <div className="hidden md:flex space-x-2">
            <Link 
              to="/" 
              className="px-4 py-2 rounded-2xl text-gray-300 font-medium hover:bg-gradient-to-r hover:from-blue-900/30 hover:to-indigo-900/30 hover:text-blue-400 transition-all duration-200 flex items-center gap-2"
            >
        
              Inicio
            </Link>
            <Link 
              to="/capture" 
              className="px-4 py-2 rounded-2xl text-gray-300 font-medium hover:bg-gradient-to-r hover:from-emerald-900/30 hover:to-teal-900/30 hover:text-emerald-400 transition-all duration-200 flex items-center gap-2"
            >
             
              Captura
            </Link>
            <Link 
              to="/analysis" 
              className="px-4 py-2 rounded-2xl text-gray-300 font-medium hover:bg-gradient-to-r hover:from-purple-900/30 hover:to-pink-900/30 hover:text-purple-400 transition-all duration-200 flex items-center gap-2"
            >
            
              Análisis
            </Link>
          </div>

          {/* Botón para menú móvil */}
          <div className="md:hidden">            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="p-2 rounded-2xl bg-gray-800/50 backdrop-blur-sm border border-gray-600/50 text-gray-300 hover:bg-gradient-to-r hover:from-gray-700/50 hover:to-gray-600/50 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-400"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                {isMenuOpen ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                )}
              </svg>
            </button>
          </div>
        </div>        {/* Menú móvil */}
        {isMenuOpen && (
          <div className="pt-4 pb-2 md:hidden bg-gray-800/80 backdrop-blur-sm rounded-2xl mt-4 border border-gray-600/50">
            <Link
              to="/"
              className="flex items-center gap-2 px-4 py-3 text-gray-300 font-medium hover:bg-gradient-to-r hover:from-blue-900/30 hover:to-indigo-900/30 hover:text-blue-400 transition-all duration-200 rounded-2xl mx-2"
              onClick={() => setIsMenuOpen(false)}
            >
              <span>🏠</span>
              Inicio
            </Link>
            <Link
              to="/capture"
              className="flex items-center gap-2 px-4 py-3 text-gray-300 font-medium hover:bg-gradient-to-r hover:from-emerald-900/30 hover:to-teal-900/30 hover:text-emerald-400 transition-all duration-200 rounded-2xl mx-2"
              onClick={() => setIsMenuOpen(false)}
            >
              <span>📡</span>
              Captura
            </Link>
            <Link
              to="/analysis"
              className="flex items-center gap-2 px-4 py-3 text-gray-300 font-medium hover:bg-gradient-to-r hover:from-purple-900/30 hover:to-pink-900/30 hover:text-purple-400 transition-all duration-200 rounded-2xl mx-2"
              onClick={() => setIsMenuOpen(false)}
            >
              <span>📊</span>
              Análisis
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
