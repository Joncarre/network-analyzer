import React, { useState, useEffect } from 'react';
import { getSessionAnalytics } from '../services/api';

function SessionAnalytics({ sessionId }) {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!sessionId) return;

    const fetchAnalytics = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await getSessionAnalytics(sessionId);
        setAnalytics(response.data);
      } catch (err) {
        console.error(`Error fetching analytics for session ${sessionId}:`, err);
        setError(`Error al cargar los análisis.`);
        setAnalytics(null);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [sessionId]);

  // Helper para formatear duración
  const formatDuration = (seconds) => {
    if (seconds === null || seconds === undefined) return 'N/A';
    return `${seconds.toFixed(2)} segundos`;
  };

  return (
    <div className="mt-6">
      <h3 className="text-lg font-semibold mb-3">Análisis Estadístico</h3>

      {loading && <p>Cargando análisis...</p>}
      {error && <p className="text-red-500">{error}</p>}

      {!loading && !error && analytics && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          {/* Resumen General */}
          <div className="bg-gray-50 p-3 rounded">
            <h4 className="font-semibold mb-2">Resumen</h4>
            <p><strong>Duración:</strong> {formatDuration(analytics.duration)}</p>
            <p><strong>Total Paquetes:</strong> {analytics.packet_count}</p>
          </div>

          {/* Protocolos */}
          <div className="bg-gray-50 p-3 rounded">
            <h4 className="font-semibold mb-2">Protocolos</h4>
            <ul className="list-disc list-inside ml-4">
              {analytics.protocols?.map(p => (
                <li key={p.protocol}>{p.protocol || 'Desconocido'}: {p.count}</li>
              ))}
            </ul>
          </div>

          {/* Top Comunicaciones */}
          <div className="bg-gray-50 p-3 rounded md:col-span-2">
            <h4 className="font-semibold mb-2">Top 10 Comunicaciones (IP Origen -&gt; IP Destino)</h4>
            <ul className="list-decimal list-inside ml-4">
              {analytics.top_communications?.map((comm, index) => (
                <li key={index}>{comm.src_ip} -&gt; {comm.dst_ip} ({comm.count} paquetes)</li>
              ))}
            </ul>
          </div>

          {/* Puertos TCP */}
          <div className="bg-gray-50 p-3 rounded">
            <h4 className="font-semibold mb-2">Top 10 Puertos Destino TCP</h4>
            {analytics.tcp_ports?.length > 0 ? (
              <ul className="list-decimal list-inside ml-4">
                {analytics.tcp_ports.map(p => (
                  <li key={p.port}>Puerto {p.port} ({p.count} paquetes)</li>
                ))}
              </ul>
            ) : <p>No hay datos TCP.</p>}
          </div>

          {/* Puertos UDP */}
          <div className="bg-gray-50 p-3 rounded">
            <h4 className="font-semibold mb-2">Top 10 Puertos Destino UDP</h4>
            {analytics.udp_ports?.length > 0 ? (
              <ul className="list-decimal list-inside ml-4">
                {analytics.udp_ports.map(p => (
                  <li key={p.port}>Puerto {p.port} ({p.count} paquetes)</li>
                ))}
              </ul>
            ) : <p>No hay datos UDP.</p>}
          </div>
          
          {/* Tipos ICMP */}
          <div className="bg-gray-50 p-3 rounded">
            <h4 className="font-semibold mb-2">Tipos ICMP</h4>
            {analytics.icmp_types?.length > 0 ? (
              <ul className="list-disc list-inside ml-4">
                {analytics.icmp_types.map(t => (
                  <li key={t.type}>{t.type} ({t.count} paquetes)</li>
                ))}
              </ul>
            ) : <p>No hay datos ICMP.</p>}
          </div>

          {/* Resumen Anomalías */}
          <div className="bg-gray-50 p-3 rounded">
            <h4 className="font-semibold mb-2">Resumen Anomalías</h4>
            <p><strong>Por Tipo:</strong></p>
            {analytics.anomalies?.by_type?.length > 0 ? (
              <ul className="list-disc list-inside ml-4">
                {analytics.anomalies.by_type.map(a => (
                  <li key={a.type}>{a.type}: {a.count}</li>
                ))}
              </ul>
            ) : <p>Ninguna.</p>}
            <p className="mt-2"><strong>Por Severidad:</strong></p>
            {analytics.anomalies?.by_severity?.length > 0 ? (
              <ul className="list-disc list-inside ml-4">
                {analytics.anomalies.by_severity.map(a => (
                  <li key={a.severity}>{a.severity}: {a.count}</li>
                ))}
              </ul>
            ) : <p>Ninguna.</p>}
          </div>

        </div>
      )}
    </div>
  );
}

export default SessionAnalytics;
