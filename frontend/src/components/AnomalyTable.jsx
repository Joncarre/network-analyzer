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
        return 'text-red-600 font-semibold';
      case 'media':
        return 'text-yellow-600 font-semibold';
      case 'baja':
        return 'text-blue-600 font-semibold';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="mt-6">
      <h3 className="text-lg font-semibold mb-3">Anomalías Detectadas ({totalAnomalies} total)</h3>

      {/* Controles de Filtro */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-4 p-2 border rounded bg-gray-50">
        <input
          type="text"
          name="severity"
          value={inputFilters.severity}
          onChange={handleFilterChange}
          placeholder="Filtrar Severidad (High, Medium, Low)..."
          className="border rounded p-1 text-sm"
        />
        <input
          type="text"
          name="type"
          value={inputFilters.type}
          onChange={handleFilterChange}
          placeholder="Filtrar Tipo de Anomalía..."
          className="border rounded p-1 text-sm"
        />
      </div>

      {loading && <p>Cargando anomalías...</p>}
      {error && <p className="text-red-500">{error}</p>}

      {!loading && !error && (
        <>
          {anomalies.length === 0 ? (
            <p>No se encontraron anomalías para esta sesión (o con los filtros aplicados).</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white border border-gray-200 text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 border-b text-left">Paquete #</th>
                    <th className="px-4 py-2 border-b text-left">Timestamp</th>
                    <th className="px-4 py-2 border-b text-left">Tipo</th>
                    <th className="px-4 py-2 border-b text-left">Descripción</th>
                    <th className="px-4 py-2 border-b text-left">Severidad</th>
                    <th className="px-4 py-2 border-b text-left">IP Origen</th>
                    <th className="px-4 py-2 border-b text-left">IP Destino</th>
                  </tr>
                </thead>
                <tbody>
                  {anomalies.map((anomaly) => (
                    <tr key={anomaly.id} className="hover:bg-gray-50">
                      <td className="px-4 py-2 border-b">{anomaly.packet?.id}</td>
                      <td className="px-4 py-2 border-b">{new Date(anomaly.packet?.timestamp * 1000).toISOString()}</td>
                      <td className="px-4 py-2 border-b">{anomaly.type}</td>
                      <td className="px-4 py-2 border-b">{anomaly.description}</td>
                      <td className={`px-4 py-2 border-b ${getSeverityClass(anomaly.severity)}`}>
                        {anomaly.severity || 'N/A'}
                      </td>
                      <td className="px-4 py-2 border-b">{anomaly.packet?.src_ip}</td>
                      <td className="px-4 py-2 border-b">{anomaly.packet?.dst_ip}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Paginación */}
          {totalPages > 1 && (
            <div className="mt-4 flex justify-between items-center">
              <button
                onClick={handlePreviousPage}
                disabled={currentPage === 0}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded disabled:opacity-50"
              >
                Anterior
              </button>
              <span>
                Página {currentPage + 1} de {totalPages}
              </span>
              <button
                onClick={handleNextPage}
                disabled={currentPage === totalPages - 1}
                className="px-4 py-2 bg-gray-300 text-gray-700 rounded disabled:opacity-50"
              >
                Siguiente
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default AnomalyTable;
