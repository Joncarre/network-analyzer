import { Link } from 'react-router-dom';

const HomePage = () => {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">
          Analizador de Tráfico de Red con IA
        </h1>
        <p className="text-xl text-gray-600">
          Capture, analice y visualice su tráfico de red con consultas en lenguaje natural.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            Captura de Tráfico
          </h2>
          <p className="text-gray-600 mb-6">
            Capture paquetes de red en tiempo real o cargue archivos PCAP existentes para su análisis.
          </p>
          <Link
            to="/capture"
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded inline-block"
          >
            Iniciar Captura
          </Link>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            Análisis con IA
          </h2>
          <p className="text-gray-600 mb-6">
            Utilice consultas en lenguaje natural para analizar su tráfico de red y detectar posibles amenazas.
          </p>
          <Link
            to="/analysis"
            className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded inline-block"
          >
            Analizar Tráfico
          </Link>
        </div>
      </div>

      <div className="mt-12 bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">
          Características Principales
        </h2>
        <ul className="list-disc pl-6 space-y-2 text-gray-600">
          <li>Captura de paquetes en tiempo real de cualquier interfaz de red</li>
          <li>Procesamiento y almacenamiento eficiente en base de datos SQLite</li>
          <li>Análisis de tráfico en capas 3 (Red) y 4 (Transporte)</li>
          <li>Interfaz conversacional con IA para consultas en lenguaje natural</li>
          <li>Detección automática de anomalías y patrones sospechosos</li>
        </ul>
      </div>
    </div>
  );
};

export default HomePage;
