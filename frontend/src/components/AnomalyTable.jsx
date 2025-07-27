import React, { useState, useEffect, useCallback } from 'react';
import { getSessionAnomalies } from '../services/api';
import { debounce } from 'lodash'; // Asegúrate de tener lodash instalado

function AnomalyTable({ sessionId }) {
  const [anomalies, setAnomalies] = useState([]);
  const [totalAnomalies, setTotalAnomalies] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [limit, setLimit] = useState(10); // Menor límite por defecto para anomalías

  // Estado para los filtros
  const [filters, setFilters] = useState({
    severity: '',
    type: '',
  });
  // Estado intermedio para inputs (para debounce)
  const [inputFilters, setInputFilters] = useState(filters);

  // Debounce la actualización de los filtros principales
  const debouncedSetFilters = useCallback(debounce((newFilters) => {
    setFilters(newFilters);
    setCurrentPage(0); // Resetear a la primera página al aplicar filtros
  }, 500), []); // 500ms de debounce

  // Actualizar filtros intermedios y llamar al debounce
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    const updatedInputFilters = { ...inputFilters, [name]: value };
    setInputFilters(updatedInputFilters);
    debouncedSetFilters(updatedInputFilters);
  };

  useEffect(() => {
    if (!sessionId) return;

    const fetchAnomalies = async () => {
      setLoading(true);
      setError(null);
      try {
        // Construir parámetros incluyendo filtros no vacíos
        const params = {
          limit,
          offset: currentPage * limit,
        };
        for (const key in filters) {
          if (filters[key]) {
            params[key] = filters[key];
          }
        }

        const response = await getSessionAnomalies(sessionId, params);
        setAnomalies(response.data.anomalies || []);
        setTotalAnomalies(response.data.total || 0);
      } catch (err) {
        console.error(`Error fetching anomalies for session ${sessionId}:`, err);
        setError(`Error al cargar las anomalías.`);
        setAnomalies([]);
        setTotalAnomalies(0);
      } finally {
        setLoading(false);
      }
    };

    fetchAnomalies();
  }, [sessionId, currentPage, limit, filters]);

  const totalPages = Math.ceil(totalAnomalies / limit);

  const handlePreviousPage = () => {
    setCurrentPage((prev) => Math.max(0, prev - 1));
  };

  const handleNextPage = () => {
    setCurrentPage((prev) => Math.min(totalPages - 1, prev + 1));
  };

  // Helper para clases de severidad
  const getSeverityClass = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'alta':
      case 'crítica':
      case 'high':
        return 'bg-gradient-to-r from-red-100 to-rose-100 text-red-700';
      case 'media':
      case 'medium':
        return 'bg-gradient-to-r from-amber-100 to-orange-100 text-amber-700';
      case 'baja':
      case 'low':
        return 'bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-700';
      default:
        return 'bg-gradient-to-r from-gray-600 to-gray-500 text-gray-300';
    }
  };

  return (
    <div className="mt-8">
      <div className="flex items-center mb-6">
        <div className="w-10 h-10 bg-gradient-to-r from-red-400 to-rose-500 rounded-2xl flex items-center justify-center mr-3">
          <span className="text-white text-lg">⚠️</span>
        </div>
        <h3 className="text-2xl font-bold text-gray-300">Anomalías Detectadas</h3>
        <span className="ml-3 px-3 py-1 bg-gradient-to-r from-red-100 to-rose-100 text-red-700 rounded-xl text-sm font-semibold">
          {totalAnomalies} total
        </span>
      </div>

      {/* Controles de Filtro */}
      <div className="bg-gray-800/70 backdrop-blur-sm p-6 rounded-3xl shadow-lg border border-gray-700/50 mb-6">
        <h4 className="text-lg font-semibold text-gray-300 mb-4 flex items-center">
          <span className="mr-2">🔍</span>
          Filtros de Anomalías
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <input
            type="text"
            name="severity"
            value={inputFilters.severity}
            onChange={handleFilterChange}
            placeholder="Filtrar Severidad (High, Medium, Low)..."
            className="p-3 bg-gray-700/80 backdrop-blur-sm border border-gray-600 rounded-2xl text-gray-300 focus:ring-2 focus:ring-red-400 focus:border-red-400 transition-all duration-200 shadow-sm hover:shadow-md"
          />
          <input
            type="text"
            name="type"
            value={inputFilters.type}
            onChange={handleFilterChange}
            placeholder="Filtrar Tipo de Anomalía..."
            className="p-3 bg-gray-700/80 backdrop-blur-sm border border-gray-600 rounded-2xl text-gray-300 focus:ring-2 focus:ring-red-400 focus:border-red-400 transition-all duration-200 shadow-sm hover:shadow-md"
          />
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="flex items-center space-x-3">
            <div className="animate-spin w-8 h-8 bg-gradient-to-r from-red-400 to-rose-500 rounded-full flex items-center justify-center">
              <span className="text-white">⚙️</span>
            </div>
            <p className="text-gray-400 font-medium">Cargando anomalías...</p>
          </div>
        </div>
      )}
      
      {error && (
        <div className="p-4 bg-gradient-to-r from-red-900/50 to-red-800/50 border border-red-700/50 rounded-2xl shadow-sm mb-6">
          <p className="text-red-300 font-medium">{error}</p>
        </div>
      )}      {!loading && !error && (
        <>
          {anomalies.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-24 h-24 bg-gradient-to-r from-green-100 to-emerald-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-4xl">✅</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-300 mb-2">¡Excelente! No hay anomalías</h3>
              <p className="text-gray-400">No se encontraron anomalías para esta sesión o con los filtros aplicados</p>
            </div>
          ) : (
            <div className="bg-gray-800/70 backdrop-blur-sm rounded-3xl shadow-lg border border-gray-700/50 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead className="bg-gradient-to-r from-gray-700/80 to-gray-600/80 border-b border-gray-600">
                    <tr>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Paquete #</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Timestamp</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Tipo</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Descripción</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Severidad</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">IP Origen</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">IP Destino</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-600">
                    {anomalies.map((anomaly, index) => (
                      <tr key={anomaly.id} className="hover:bg-gradient-to-r hover:from-gray-700/50 hover:to-gray-600/50 transition-all duration-200 group">
                        <td className="px-6 py-4 text-sm text-gray-400 font-medium">
                          <span className="bg-gradient-to-r from-gray-700 to-gray-600 text-gray-300 px-2 py-1 rounded-lg">
                            #{anomaly.packet?.id}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-400 font-mono">{new Date(anomaly.packet?.timestamp * 1000).toISOString()}</td>
                        <td className="px-6 py-4 text-sm">
                          <span className="bg-gradient-to-r from-purple-100 to-pink-100 text-purple-700 px-3 py-1 rounded-xl font-semibold">
                            {anomaly.type}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-300 max-w-xs">
                          <div className="truncate">{anomaly.description}</div>
                        </td>
                        <td className="px-6 py-4 text-sm">
                          <span className={`px-3 py-1 rounded-xl font-semibold ${getSeverityClass(anomaly.severity)}`}>
                            {anomaly.severity || 'N/A'}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-300 font-mono">
                          <span className="bg-gradient-to-r from-emerald-100 to-teal-100 text-emerald-700 px-2 py-1 rounded-lg">
                            {anomaly.packet?.src_ip}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-300 font-mono">
                          <span className="bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-700 px-2 py-1 rounded-lg">
                            {anomaly.packet?.dst_ip}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Paginación */}
          {totalPages > 1 && (
            <div className="mt-6 flex justify-center">
              <div className="bg-gray-800/70 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-700/50 p-4">
                <div className="flex items-center space-x-4">
                  <button
                    onClick={handlePreviousPage}
                    disabled={currentPage === 0}
                    className={`px-4 py-2 rounded-xl font-semibold transition-all duration-200 ${
                      currentPage === 0
                        ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                        : 'bg-gradient-to-r from-red-400 to-rose-500 text-white hover:from-red-500 hover:to-rose-600 shadow-md hover:shadow-lg transform hover:-translate-y-0.5'
                    }`}
                  >
                    <span className="flex items-center gap-2">
                      <span>←</span>
                      Anterior
                    </span>
                  </button>
                  
                  <div className="flex items-center space-x-2">
                    <span className="text-gray-400 font-medium">Página</span>
                    <span className="px-3 py-1 bg-gradient-to-r from-gray-700 to-gray-600 text-gray-300 rounded-xl font-bold">
                      {currentPage + 1}
                    </span>
                    <span className="text-gray-400 font-medium">de</span>
                    <span className="px-3 py-1 bg-gradient-to-r from-gray-700 to-gray-600 text-gray-300 rounded-xl font-bold">
                      {totalPages}
                    </span>
                  </div>
                  
                  <button
                    onClick={handleNextPage}
                    disabled={currentPage === totalPages - 1}
                    className={`px-4 py-2 rounded-xl font-semibold transition-all duration-200 ${
                      currentPage === totalPages - 1
                        ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                        : 'bg-gradient-to-r from-red-400 to-rose-500 text-white hover:from-red-500 hover:to-rose-600 shadow-md hover:shadow-lg transform hover:-translate-y-0.5'
                    }`}
                  >
                    <span className="flex items-center gap-2">
                      Siguiente
                      <span>→</span>
                    </span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default AnomalyTable;
