import { Link } from 'react-router-dom';

const HomePage = () => {
  return (
    <div className="max-w-5xl mx-auto p-6" style={{ background: '#222831', borderRadius: '1.5rem' }}>
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-4" style={{ color: '#e9d7a5' }}>
          Analizador de tráfico de red con Inteligencia Artificial
        </h1>
        <p className="text-xl" style={{ color: '#DFD0B8' }}>
          Analiza el tráfico de red y detecta posibles amenazas con consultas en lenguaje natural
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        <div className="p-6 rounded-2xl shadow-md" style={{ background: '#393E46' }}>
          <h2 className="text-2xl font-semibold mb-4" style={{ color: '#DFD0B8' }}>
            Captura de tráfico
          </h2>
          <p className="mb-6" style={{ color: '#DFD0B8' }}>
            Capture paquetes de red en tiempo real o cargue sus propios ficheros .pcap para su análisis
          </p>
          <Link
            to="/capture"
            className="px-4 py-2 rounded bg-[#948979] text-[#222831] font-semibold shadow hover:bg-[#e9d7a5] transition-colors duration-200 inline-block"
          >
            Iniciar captura
          </Link>
        </div>

        <div className="p-6 rounded-2xl shadow-md" style={{ background: '#393E46' }}>
          <h2 className="text-2xl font-semibold mb-4" style={{ color: '#DFD0B8' }}>
            Análisis con IA
          </h2>
          <p className="mb-6" style={{ color: '#DFD0B8' }}>
            Utilice consultas en lenguaje natural para analizar su tráfico de red
          </p>
          <Link
            to="/analysis"
            className="px-4 py-2 rounded bg-[#948979] text-[#222831] font-semibold shadow hover:bg-[#e9d7a5] transition-colors duration-200 inline-block"
          >
            Analizar tráfico
          </Link>
        </div>
      </div>

      <div className="mt-12 p-6 rounded-2xl shadow-md" style={{ background: '#393E46' }}>
        <h2 className="text-2xl font-semibold mb-4" style={{ color: '#DFD0B8' }}>
          Características principales de la aplicación
        </h2>
        <ul className="list-disc pl-6 space-y-2" style={{ color: '#DFD0B8' }}>
          <li className="hover:text-[#e9d7a5] transition-colors">Análisis de tráfico en capa de Red y Transporte</li>
          <li className="hover:text-[#e9d7a5] transition-colors">Captura de paquetes en tiempo real por cualquier interfaz de red disponibles</li>
          <li className="hover:text-[#e9d7a5] transition-colors">Procesamiento y almacenamiento eficiente en bases de datos SQLite</li>
          <li className="hover:text-[#e9d7a5] transition-colors">Interfaz conversacional con IA para consultas en lenguaje natural</li>
          <li className="hover:text-[#e9d7a5] transition-colors">Detección automática de anomalías y patrones sospechosos</li>
        </ul>
      </div>
    </div>
  );
};

export default HomePage;
