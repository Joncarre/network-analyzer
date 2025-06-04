import React, { useState, useEffect, useCallback } from 'react';
import { getSessionPackets } from '../services/api';
import { debounce } from 'lodash'; // Necesitarás instalar lodash: npm install lodash

function PacketTable({ sessionId }) {
  const [packets, setPackets] = useState([]);
  const [totalPackets, setTotalPackets] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [limit, setLimit] = useState(20);

  // Estado para los filtros
  const [filters, setFilters] = useState({
    src_ip: '',
    dst_ip: '',
    protocol: '',
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

    const fetchPackets = async () => {
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
        
        const response = await getSessionPackets(sessionId, params);
        setPackets(response.data.packets || []);
        setTotalPackets(response.data.total || 0);
      } catch (err) {
        console.error(`Error fetching packets for session ${sessionId}:`, err);
        setError(`Error al cargar los paquetes.`);
        setPackets([]);
        setTotalPackets(0);
      } finally {
        setLoading(false);
      }
    };

    fetchPackets();
    // Incluir filters en las dependencias para recargar al cambiar filtros
  }, [sessionId, currentPage, limit, filters]); 

  const totalPages = Math.ceil(totalPackets / limit);

  const handlePreviousPage = () => {
    setCurrentPage((prev) => Math.max(0, prev - 1));
  };

  const handleNextPage = () => {
    setCurrentPage((prev) => Math.min(totalPages - 1, prev + 1));
  };
  return (
    <div className="mt-8">
      <div className="flex items-center mb-6">
        <div className="w-10 h-10 bg-gradient-to-r from-blue-400 to-indigo-500 rounded-2xl flex items-center justify-center mr-3">
          <span className="text-white text-lg">📦</span>
        </div>
        <h3 className="text-2xl font-bold text-slate-700">Paquetes de Red</h3>
        <span className="ml-3 px-3 py-1 bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-700 rounded-xl text-sm font-semibold">
          {totalPackets} total
        </span>
      </div>
      
      {/* Controles de Filtro */}
      <div className="bg-white/70 backdrop-blur-sm p-6 rounded-3xl shadow-lg border border-white/30 mb-6">
        <h4 className="text-lg font-semibold text-slate-700 mb-4 flex items-center">
          <span className="mr-2">🔍</span>
          Filtros de Búsqueda
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input
            type="text"
            name="src_ip"
            value={inputFilters.src_ip}
            onChange={handleFilterChange}
            placeholder="Filtrar IP Origen..."
            className="p-3 bg-white/80 backdrop-blur-sm border border-slate-200 rounded-2xl text-slate-700 focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition-all duration-200 shadow-sm hover:shadow-md"
          />
          <input
            type="text"
            name="dst_ip"
            value={inputFilters.dst_ip}
            onChange={handleFilterChange}
            placeholder="Filtrar IP Destino..."
            className="p-3 bg-white/80 backdrop-blur-sm border border-slate-200 rounded-2xl text-slate-700 focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition-all duration-200 shadow-sm hover:shadow-md"
          />
          <input
            type="text"
            name="protocol"
            value={inputFilters.protocol}
            onChange={handleFilterChange}
            placeholder="Filtrar Protocolo..."
            className="p-3 bg-white/80 backdrop-blur-sm border border-slate-200 rounded-2xl text-slate-700 focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition-all duration-200 shadow-sm hover:shadow-md"
          />
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="flex items-center space-x-3">
            <div className="animate-spin w-8 h-8 bg-gradient-to-r from-blue-400 to-indigo-500 rounded-full flex items-center justify-center">
              <span className="text-white">⚙️</span>
            </div>
            <p className="text-slate-600 font-medium">Cargando paquetes...</p>
          </div>
        </div>
      )}
      
      {error && (
        <div className="p-4 bg-gradient-to-r from-red-50 to-rose-50 border border-red-200 rounded-2xl shadow-sm mb-6">
          <p className="text-red-600 font-medium">{error}</p>
        </div>
      )}      {!loading && !error && (
        <>
          {packets.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-24 h-24 bg-gradient-to-r from-slate-100 to-slate-200 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-4xl">📋</span>
              </div>
              <h3 className="text-xl font-semibold text-slate-700 mb-2">No hay paquetes disponibles</h3>
              <p className="text-slate-500">No se encontraron paquetes para esta sesión o con los filtros aplicados</p>
            </div>
          ) : (
            <div className="bg-white/70 backdrop-blur-sm rounded-3xl shadow-lg border border-white/30 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead className="bg-gradient-to-r from-slate-50 to-slate-100 border-b border-slate-200">
                    <tr>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">#</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">Timestamp</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">IP Origen</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">IP Destino</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">Protocolo</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">Longitud</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">Detalles</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">Anomalías</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {packets.map((packet, index) => (
                      <tr key={packet.id} className="hover:bg-gradient-to-r hover:from-blue-50 hover:to-indigo-50 transition-all duration-200 group">
                        <td className="px-6 py-4 text-sm text-slate-600 font-medium">{packet.packet_number}</td>
                        <td className="px-6 py-4 text-sm text-slate-600 font-mono">{new Date(packet.timestamp * 1000).toISOString()}</td>
                        <td className="px-6 py-4 text-sm text-slate-700 font-mono">
                          <span className="bg-gradient-to-r from-emerald-100 to-teal-100 text-emerald-700 px-2 py-1 rounded-lg">
                            {packet.src_ip}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-700 font-mono">
                          <span className="bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-700 px-2 py-1 rounded-lg">
                            {packet.dst_ip}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm">
                          <span className="bg-gradient-to-r from-purple-100 to-pink-100 text-purple-700 px-3 py-1 rounded-xl font-semibold">
                            {packet.protocol || 'N/A'}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-600 font-mono">{packet.length} bytes</td>
                        <td className="px-6 py-4 text-sm text-slate-600 font-mono max-w-xs truncate">
                          {packet.protocol === 'TCP' && `Src:${packet.details?.src_port} Dst:${packet.details?.dst_port} Flags:${packet.details?.flags}`}
                          {packet.protocol === 'UDP' && `Src:${packet.details?.src_port} Dst:${packet.details?.dst_port}`}
                          {packet.protocol === 'ICMP' && `Tipo:${packet.details?.type_name} (${packet.details?.type}) Code:${packet.details?.code}`}
                          {packet.protocol === 'ICMPv6' && `Tipo:${packet.details?.type_name} (${packet.details?.type}) Code:${packet.details?.code}`}
                        </td>
                        <td className="px-6 py-4 text-sm">
                          {packet.anomalies && packet.anomalies.length > 0 ? (
                            <span className="bg-gradient-to-r from-red-100 to-rose-100 text-red-700 px-3 py-1 rounded-xl font-semibold flex items-center gap-1">
                              <span>⚠️</span>
                              Sí ({packet.anomalies.length})
                            </span>
                          ) : (
                            <span className="bg-gradient-to-r from-green-100 to-emerald-100 text-green-700 px-3 py-1 rounded-xl font-semibold flex items-center gap-1">
                              <span>✅</span>
                              No
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}          {/* Paginación */}
          {totalPages > 1 && (
            <div className="mt-6 flex justify-center">
              <div className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-lg border border-white/30 p-4">
                <div className="flex items-center space-x-4">
                  <button
                    onClick={handlePreviousPage}
                    disabled={currentPage === 0}
                    className={`px-4 py-2 rounded-xl font-semibold transition-all duration-200 ${
                      currentPage === 0
                        ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                        : 'bg-gradient-to-r from-blue-400 to-indigo-500 text-white hover:from-blue-500 hover:to-indigo-600 shadow-md hover:shadow-lg transform hover:-translate-y-0.5'
                    }`}
                  >
                    <span className="flex items-center gap-2">
                      <span>←</span>
                      Anterior
                    </span>
                  </button>
                  
                  <div className="flex items-center space-x-2">
                    <span className="text-slate-600 font-medium">Página</span>
                    <span className="px-3 py-1 bg-gradient-to-r from-slate-100 to-slate-200 text-slate-700 rounded-xl font-bold">
                      {currentPage + 1}
                    </span>
                    <span className="text-slate-600 font-medium">de</span>
                    <span className="px-3 py-1 bg-gradient-to-r from-slate-100 to-slate-200 text-slate-700 rounded-xl font-bold">
                      {totalPages}
                    </span>
                  </div>
                  
                  <button
                    onClick={handleNextPage}
                    disabled={currentPage === totalPages - 1}
                    className={`px-4 py-2 rounded-xl font-semibold transition-all duration-200 ${
                      currentPage === totalPages - 1
                        ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                        : 'bg-gradient-to-r from-blue-400 to-indigo-500 text-white hover:from-blue-500 hover:to-indigo-600 shadow-md hover:shadow-lg transform hover:-translate-y-0.5'
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

export default PacketTable;
