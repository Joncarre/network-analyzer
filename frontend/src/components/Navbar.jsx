import { useState } from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <nav className="bg-gray-800 text-white shadow-md">
      <div className="container mx-auto px-4 py-3">
        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <Link to="/" className="text-xl font-bold">
              Network Analyzer
            </Link>
          </div>

          {/* Menú para escritorio */}
          <div className="hidden md:flex space-x-6">
            <Link to="/" className="hover:text-gray-300">
              Inicio
            </Link>
            <Link to="/capture" className="hover:text-gray-300">
              Captura
            </Link>
            <Link to="/analysis" className="hover:text-gray-300">
              Análisis
            </Link>
          </div>

          {/* Botón para menú móvil */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="focus:outline-none"
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
        </div>

        {/* Menú móvil */}
        {isMenuOpen && (
          <div className="pt-4 pb-2 md:hidden">
            <Link
              to="/"
              className="block py-2 hover:text-gray-300"
              onClick={() => setIsMenuOpen(false)}
            >
              Inicio
            </Link>
            <Link
              to="/capture"
              className="block py-2 hover:text-gray-300"
              onClick={() => setIsMenuOpen(false)}
            >
              Captura
            </Link>
            <Link
              to="/analysis"
              className="block py-2 hover:text-gray-300"
              onClick={() => setIsMenuOpen(false)}
            >
              Análisis
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
