import { useState } from 'react';
import { Link } from 'react-router-dom';
import '../holographic.css';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  return (
    <nav className="bg-transparent backdrop-blur-sm border-b border-white/30 shadow-lg sticky top-0 z-50">
      <div className="container mx-auto px-6 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <div className="holographic-card flex items-center">
              <Link to="/" className="flex items-center space-x-0 mx-4">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center">
                  <span className="text-white text-xl font-bold">🛖</span>
                </div>
                <span className="text-2xl font-bold text-gray-700 bg-clip-text text-transparent">
                  
                </span>
              </Link>
            </div>
          </div>

          {/* Menú para escritorio */}
          <div className="hidden md:flex space-x-2">
            <Link 
              to="/" 
              className="px-4 py-2 rounded-2xl text-slate-700 font-medium hover:bg-gradient-to-r hover:from-blue-50 hover:to-indigo-50 hover:text-blue-600 transition-all duration-200 flex items-center gap-2"
            >
        
              Inicio
            </Link>
            <Link 
              to="/capture" 
              className="px-4 py-2 rounded-2xl text-slate-700 font-medium hover:bg-gradient-to-r hover:from-emerald-50 hover:to-teal-50 hover:text-emerald-600 transition-all duration-200 flex items-center gap-2"
            >
             
              Captura
            </Link>
            <Link 
              to="/analysis" 
              className="px-4 py-2 rounded-2xl text-slate-700 font-medium hover:bg-gradient-to-r hover:from-purple-50 hover:to-pink-50 hover:text-purple-600 transition-all duration-200 flex items-center gap-2"
            >
            
              Análisis
            </Link>
          </div>

          {/* Botón para menú móvil */}
          <div className="md:hidden">            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="p-2 rounded-2xl bg-transparent backdrop-blur-sm border border-white/30 text-slate-700 hover:bg-gradient-to-r hover:from-slate-50 hover:to-slate-100 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-400"
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
          <div className="pt-4 pb-2 md:hidden bg-transparent backdrop-blur-sm rounded-2xl mt-4 border border-white/30">
            <Link
              to="/"
              className="flex items-center gap-2 px-4 py-3 text-slate-700 font-medium hover:bg-gradient-to-r hover:from-blue-50 hover:to-indigo-50 hover:text-blue-600 transition-all duration-200 rounded-2xl mx-2"
              onClick={() => setIsMenuOpen(false)}
            >
              <span>🏠</span>
              Inicio
            </Link>
            <Link
              to="/capture"
              className="flex items-center gap-2 px-4 py-3 text-slate-700 font-medium hover:bg-gradient-to-r hover:from-emerald-50 hover:to-teal-50 hover:text-emerald-600 transition-all duration-200 rounded-2xl mx-2"
              onClick={() => setIsMenuOpen(false)}
            >
              <span>📡</span>
              Captura
            </Link>
            <Link
              to="/analysis"
              className="flex items-center gap-2 px-4 py-3 text-slate-700 font-medium hover:bg-gradient-to-r hover:from-purple-50 hover:to-pink-50 hover:text-purple-600 transition-all duration-200 rounded-2xl mx-2"
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
