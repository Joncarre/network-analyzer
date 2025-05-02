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
    <div className="mt-6">
      <h3 className="text-lg font-semibold mb-3">Paquetes ({totalPackets} total)</h3>
      
      {/* Controles de Filtro */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-2 mb-4 p-2 border rounded bg-gray-50">
        <input
          type="text"
          name="src_ip"
          value={inputFilters.src_ip}
          onChange={handleFilterChange}
          placeholder="Filtrar IP Origen..."
          className="border rounded p-1 text-sm"
        />
        <input
          type="text"
          name="dst_ip"
          value={inputFilters.dst_ip}
          onChange={handleFilterChange}
          placeholder="Filtrar IP Destino..."
          className="border rounded p-1 text-sm"
        />
        <input
          type="text"
          name="protocol"
          value={inputFilters.protocol}
          onChange={handleFilterChange}
          placeholder="Filtrar Protocolo..."
          className="border rounded p-1 text-sm"
        />
      </div>

      {loading && <p>Cargando paquetes...</p>}
      {error && <p className="text-red-500">{error}</p>}

      {!loading && !error && (
        <>
          {packets.length === 0 ? (
            <p>No se encontraron paquetes para esta sesión (o con los filtros aplicados).</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white border border-gray-200 text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 border-b text-left">#</th>
                    <th className="px-4 py-2 border-b text-left">Timestamp</th>
                    <th className="px-4 py-2 border-b text-left">Origen IP</th>
                    <th className="px-4 py-2 border-b text-left">Destino IP</th>
                    <th className="px-4 py-2 border-b text-left">Proto</th>
                    <th className="px-4 py-2 border-b text-left">Longitud</th>
                    <th className="px-4 py-2 border-b text-left">Detalles</th>
                    <th className="px-4 py-2 border-b text-left">Anomalías</th>
                  </tr>
                </thead>
                <tbody>
                  {packets.map((packet) => (
                    <tr key={packet.id} className="hover:bg-gray-50">
                      <td className="px-4 py-2 border-b">{packet.packet_number}</td>
                      <td className="px-4 py-2 border-b">{new Date(packet.timestamp * 1000).toISOString()}</td>
                      <td className="px-4 py-2 border-b">{packet.src_ip}</td>
                      <td className="px-4 py-2 border-b">{packet.dst_ip}</td>
                      <td className="px-4 py-2 border-b">{packet.protocol || 'N/A'}</td>
                      <td className="px-4 py-2 border-b">{packet.length}</td>
                      <td className="px-4 py-2 border-b">
                        {packet.protocol === 'TCP' && `Src:${packet.details?.src_port} Dst:${packet.details?.dst_port} Flags:${packet.details?.flags}`}
                        {packet.protocol === 'UDP' && `Src:${packet.details?.src_port} Dst:${packet.details?.dst_port}`}
                        {packet.protocol === 'ICMP' && `Tipo:${packet.details?.type_name} (${packet.details?.type}) Code:${packet.details?.code}`}
                        {packet.protocol === 'ICMPv6' && `Tipo:${packet.details?.type_name} (${packet.details?.type}) Code:${packet.details?.code}`}
                      </td>
                      <td className="px-4 py-2 border-b">
                        {packet.anomalies && packet.anomalies.length > 0 ? (
                          <span className="text-red-600 font-semibold">Sí ({packet.anomalies.length})</span>
                        ) : (
                          'No'
                        )}
                      </td>
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

export default PacketTable;
