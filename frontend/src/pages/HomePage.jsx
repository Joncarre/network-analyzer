import { Link } from 'react-router-dom';

const HomePage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 py-12 px-6">
      <div className="max-w-6xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-16">

            <h1 className="text-5xl font-bold bg-gradient-to-r from-slate-300 via-slate-700 to-slate-300 bg-clip-text text-transparent mb-4">
              Network Analyzer
            </h1>

          <p className="text-xl text-slate-600 max-w-3xl mx-auto leading-relaxed mt-6">
            Analizador de tráfico de red con Inteligencia Artificial y consultas en lenguaje natural
          </p>
        </div>

        {/* Main Features Cards */}
              <div className="grid md:grid-cols-2 gap-8 mb-16">
              <div className="group bg-white/70 backdrop-blur-sm p-8 rounded-3xl shadow-lg border border-white/30 hover:shadow-xltransition-all duration-300">
                <div className="flex items-center mb-6">
                <h2 className="text-2xl font-bold bg-gradient-to-r from-green-400 to-emerald-500 bg-clip-text text-transparent">
              Captura de tráfico
                </h2>
                </div>
                <p className="text-slate-600 mb-8 leading-relaxed">
                Capture paquetes de red en tiempo real o cargue sus propios ficheros .pcap para análisis detallado
                </p>
                <Link
                to="/capture"
                className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-green-400 to-emerald-500 text-white font-semibold rounded-2xl shadow-md hover:shadow-lg hover:from-green-500 hover:to-emerald-600 transition-all duration-300 transform hover:-translate-y-1"
                >
                <span>Iniciar captura</span>
                <span className="ml-3 mt-1">⮞</span>
                </Link>
              </div>

              <div className="group bg-white/70 backdrop-blur-sm p-8 rounded-3xl shadow-lg border border-white/30 hover:shadow-xl transition-all duration-300">
                <div className="flex items-center mb-6">
                <h2 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">
              Análisis con IA
                </h2>
                </div>
                <p className="text-slate-600 mb-8 leading-relaxed">
                Utilice consultas en lenguaje natural para analizar su tráfico de red de forma inteligente
                </p>
                <Link
                to="/analysis"
                className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-purple-400 to-pink-500 text-white font-semibold rounded-2xl shadow-md hover:shadow-lg hover:from-purple-500 hover:to-pink-600 transition-all duration-300 transform hover:-translate-y-1"
                >
                <span>Analizar tráfico</span>
                <span className="ml-3 mt-1">⮞</span>
                </Link>
              </div>
              </div>

              {/* Features List */}
        <div className="bg-white/70 backdrop-blur-sm p-8 rounded-3xl shadow-lg border border-white/30">
          <h2 className="text-3xl font-bold text-slate-700 mb-8 text-center">
            Características principales
          </h2>
          <div className="grid md:grid-cols-1 gap-6">
            <div className="space-y-3">
              <div className="text-center group cursor-pointer">
                <p className="text-slate-600 group-hover:text-slate-800 transition-colors duration-200">
                  Análisis de tráfico en capa de Red y Transporte
                </p>
              </div>
              <div className="text-center group cursor-pointer">
                <p className="text-slate-600 group-hover:text-slate-800 transition-colors duration-200">
                  Captura de paquetes en tiempo real por cualquier interfaz disponible
                </p>
              </div>
              <div className="text-center group cursor-pointer">
                <p className="text-slate-600 group-hover:text-slate-800 transition-colors duration-200">
                  Procesamiento y almacenamiento eficiente en bases de datos SQLite
                </p>
              </div>
              <div className="text-center group cursor-pointer">
                <p className="text-slate-600 group-hover:text-slate-800 transition-colors duration-200">
                  Interfaz conversacional con IA para consultas en lenguaje natural
                </p>
              </div>
                            <div className="text-center group cursor-pointer">
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
