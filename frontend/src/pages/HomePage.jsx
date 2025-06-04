import { Link } from 'react-router-dom';

const HomePage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 py-12 px-6">
      <div className="max-w-6xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <div className="inline-block p-4 mb-6 bg-white/60 backdrop-blur-sm rounded-3xl shadow-lg border border-white/30">
            <h1 className="text-5xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-4">
              Analizador de Tráfico de Red
            </h1>
            <h2 className="text-2xl font-semibold text-indigo-700 mb-2">
              con Inteligencia Artificial
            </h2>
          </div>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
            Analiza el tráfico de red y detecta posibles amenazas con consultas en lenguaje natural.
            Una herramienta moderna y potente para la seguridad de redes.
          </p>
        </div>

        {/* Main Features Cards */}
        <div className="grid md:grid-cols-2 gap-8 mb-16">
          <div className="group bg-white/70 backdrop-blur-sm p-8 rounded-3xl shadow-lg border border-white/30 hover:shadow-xl hover:scale-105 transition-all duration-300">
            <div className="flex items-center mb-6">
              <div className="w-12 h-12 bg-gradient-to-r from-green-400 to-emerald-500 rounded-2xl flex items-center justify-center mr-4">
                <span className="text-white text-xl">📡</span>
              </div>
              <h2 className="text-2xl font-bold text-slate-700">
                Captura de Tráfico
              </h2>
            </div>
            <p className="text-slate-600 mb-8 leading-relaxed">
              Capture paquetes de red en tiempo real o cargue sus propios ficheros .pcap para análisis detallado
            </p>
            <Link
              to="/capture"
              className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-green-400 to-emerald-500 text-white font-semibold rounded-2xl shadow-md hover:shadow-lg hover:from-green-500 hover:to-emerald-600 transition-all duration-300 transform hover:-translate-y-1"
            >
              <span>Iniciar Captura</span>
              <span className="ml-2">→</span>
            </Link>
          </div>

          <div className="group bg-white/70 backdrop-blur-sm p-8 rounded-3xl shadow-lg border border-white/30 hover:shadow-xl hover:scale-105 transition-all duration-300">
            <div className="flex items-center mb-6">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-400 to-indigo-500 rounded-2xl flex items-center justify-center mr-4">
                <span className="text-white text-xl">🤖</span>
              </div>
              <h2 className="text-2xl font-bold text-slate-700">
                Análisis con IA
              </h2>
            </div>
            <p className="text-slate-600 mb-8 leading-relaxed">
              Utilice consultas en lenguaje natural para analizar su tráfico de red de forma inteligente
            </p>
            <Link
              to="/analysis"
              className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-400 to-indigo-500 text-white font-semibold rounded-2xl shadow-md hover:shadow-lg hover:from-blue-500 hover:to-indigo-600 transition-all duration-300 transform hover:-translate-y-1"
            >
              <span>Analizar Tráfico</span>
              <span className="ml-2">→</span>
            </Link>
          </div>
        </div>

        {/* Features List */}
        <div className="bg-white/70 backdrop-blur-sm p-8 rounded-3xl shadow-lg border border-white/30">
          <h2 className="text-3xl font-bold text-slate-700 mb-8 text-center">
            Características Principales
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="flex items-start group cursor-pointer">
                <div className="w-6 h-6 bg-gradient-to-r from-pink-400 to-rose-500 rounded-full flex-shrink-0 mt-1 mr-4 group-hover:scale-110 transition-transform duration-200"></div>
                <p className="text-slate-600 group-hover:text-slate-800 transition-colors duration-200">
                  Análisis de tráfico en capa de Red y Transporte
                </p>
              </div>
              <div className="flex items-start group cursor-pointer">
                <div className="w-6 h-6 bg-gradient-to-r from-cyan-400 to-teal-500 rounded-full flex-shrink-0 mt-1 mr-4 group-hover:scale-110 transition-transform duration-200"></div>
                <p className="text-slate-600 group-hover:text-slate-800 transition-colors duration-200">
                  Captura de paquetes en tiempo real por cualquier interfaz disponible
                </p>
              </div>
              <div className="flex items-start group cursor-pointer">
                <div className="w-6 h-6 bg-gradient-to-r from-amber-400 to-orange-500 rounded-full flex-shrink-0 mt-1 mr-4 group-hover:scale-110 transition-transform duration-200"></div>
                <p className="text-slate-600 group-hover:text-slate-800 transition-colors duration-200">
                  Procesamiento y almacenamiento eficiente en bases de datos SQLite
                </p>
              </div>
            </div>
            <div className="space-y-4">
              <div className="flex items-start group cursor-pointer">
                <div className="w-6 h-6 bg-gradient-to-r from-purple-400 to-violet-500 rounded-full flex-shrink-0 mt-1 mr-4 group-hover:scale-110 transition-transform duration-200"></div>
                <p className="text-slate-600 group-hover:text-slate-800 transition-colors duration-200">
                  Interfaz conversacional con IA para consultas en lenguaje natural
                </p>
              </div>
              <div className="flex items-start group cursor-pointer">
                <div className="w-6 h-6 bg-gradient-to-r from-red-400 to-pink-500 rounded-full flex-shrink-0 mt-1 mr-4 group-hover:scale-110 transition-transform duration-200"></div>
                <p className="text-slate-600 group-hover:text-slate-800 transition-colors duration-200">
                  Detección automática de anomalías y patrones sospechosos
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
