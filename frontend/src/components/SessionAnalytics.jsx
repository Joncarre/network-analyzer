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
    <div className="mt-8">
      <div className="flex items-center mb-6">
        <div className="w-10 h-10 bg-gradient-to-r from-emerald-400 to-teal-500 rounded-2xl flex items-center justify-center mr-3">
          <span className="text-white text-lg">📊</span>
        </div>
        <h3 className="text-2xl font-bold text-gray-300">Análisis Estadístico</h3>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="flex items-center space-x-3">
            <div className="animate-spin w-8 h-8 bg-gradient-to-r from-emerald-400 to-teal-500 rounded-full flex items-center justify-center">
              <span className="text-white">⚙️</span>
            </div>
            <p className="text-gray-400 font-medium">Cargando análisis...</p>
          </div>
        </div>
      )}
      
      {error && (
        <div className="p-4 bg-gradient-to-r from-red-50 to-rose-50 border border-red-200 rounded-2xl shadow-sm mb-6">
          <p className="text-red-600 font-medium">{error}</p>
        </div>
      )}

      {!loading && !error && analytics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Resumen General */}
          <div className="bg-gray-800/70 backdrop-blur-sm p-6 rounded-3xl shadow-lg border border-gray-700/50 hover:shadow-xl transition-all duration-300">
            <div className="flex items-center mb-4">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-400 to-indigo-500 rounded-xl flex items-center justify-center mr-3">
                <span className="text-white text-sm">📋</span>
              </div>
              <h4 className="text-lg font-bold text-gray-300">Resumen General</h4>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center p-3 bg-gradient-to-r from-blue-900/30 to-indigo-900/30 rounded-2xl">
                <span className="text-gray-400 font-medium">Duración:</span>
                <span className="text-blue-300 font-semibold">{formatDuration(analytics.duration)}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gradient-to-r from-green-900/30 to-emerald-900/30 rounded-2xl">
                <span className="text-gray-400 font-medium">Total Paquetes:</span>
                <span className="text-emerald-300 font-semibold">{analytics.packet_count?.toLocaleString()}</span>
              </div>
            </div>
          </div>          {/* Protocolos */}
          <div className="bg-gray-800/70 backdrop-blur-sm p-6 rounded-3xl shadow-lg border border-gray-700/50 hover:shadow-xl transition-all duration-300">
            <div className="flex items-center mb-4">
              <div className="w-8 h-8 bg-gradient-to-r from-purple-400 to-pink-500 rounded-xl flex items-center justify-center mr-3">
                <span className="text-white text-sm">🌐</span>
              </div>
              <h4 className="text-lg font-bold text-gray-300">Protocolos</h4>
            </div>
            <div className="space-y-2">
              {analytics.protocols?.map((p, index) => (
                <div key={p.protocol} className="flex justify-between items-center p-3 bg-gradient-to-r from-purple-900/30 to-pink-900/30 rounded-2xl">
                  <span className="text-gray-400 font-medium">{p.protocol || 'Desconocido'}</span>
                  <span className="text-purple-300 font-semibold">{p.count?.toLocaleString()}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Top Comunicaciones */}
          <div className="bg-gray-800/70 backdrop-blur-sm p-6 rounded-3xl shadow-lg border border-gray-700/50 hover:shadow-xl transition-all duration-300 md:col-span-2 lg:col-span-3">
            <div className="flex items-center mb-4">
              <div className="w-8 h-8 bg-gradient-to-r from-orange-400 to-red-500 rounded-xl flex items-center justify-center mr-3">
                <span className="text-white text-sm">🔗</span>
              </div>
              <h4 className="text-lg font-bold text-gray-300">Top 10 Comunicaciones (IP Origen → IP Destino)</h4>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {analytics.top_communications?.map((comm, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gradient-to-r from-orange-900/30 to-red-900/30 rounded-2xl">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-bold text-orange-300 bg-orange-800/50 rounded-full w-6 h-6 flex items-center justify-center">
                      {index + 1}
                    </span>
                    <span className="font-mono text-sm text-gray-300">{comm.src_ip} → {comm.dst_ip}</span>
                  </div>
                  <span className="text-orange-300 font-semibold">{comm.count?.toLocaleString()} paquetes</span>
                </div>
              ))}
            </div>
          </div>

          {/* Puertos TCP */}
          <div className="bg-gray-800/70 backdrop-blur-sm p-6 rounded-3xl shadow-lg border border-gray-700/50 hover:shadow-xl transition-all duration-300">
            <div className="flex items-center mb-4">
              <div className="w-8 h-8 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-xl flex items-center justify-center mr-3">
                <span className="text-white text-sm">🔌</span>
              </div>
              <h4 className="text-lg font-bold text-gray-300">Top 10 Puertos TCP</h4>
            </div>
            {analytics.tcp_ports?.length > 0 ? (
              <div className="space-y-2">
                {analytics.tcp_ports.map((p, index) => (
                  <div key={p.port} className="flex justify-between items-center p-3 bg-gradient-to-r from-cyan-900/30 to-blue-900/30 rounded-2xl">
                    <span className="text-gray-400 font-medium">Puerto {p.port}</span>
                    <span className="text-cyan-300 font-semibold">{p.count?.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-gradient-to-r from-gray-700 to-gray-600 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-2xl">📭</span>
                </div>
                <p className="text-gray-400">No hay datos TCP</p>
              </div>
            )}
          </div>          {/* Puertos UDP */}
          <div className="bg-gray-800/70 backdrop-blur-sm p-6 rounded-3xl shadow-lg border border-gray-700/50 hover:shadow-xl transition-all duration-300">
            <div className="flex items-center mb-4">
              <div className="w-8 h-8 bg-gradient-to-r from-teal-400 to-emerald-500 rounded-xl flex items-center justify-center mr-3">
                <span className="text-white text-sm">🔗</span>
              </div>
              <h4 className="text-lg font-bold text-gray-300">Top 10 Puertos UDP</h4>
            </div>
            {analytics.udp_ports?.length > 0 ? (
              <div className="space-y-2">
                {analytics.udp_ports.map((p, index) => (
                  <div key={p.port} className="flex justify-between items-center p-3 bg-gradient-to-r from-teal-900/30 to-emerald-900/30 rounded-2xl">
                    <span className="text-gray-400 font-medium">Puerto {p.port}</span>
                    <span className="text-teal-300 font-semibold">{p.count?.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-gradient-to-r from-gray-700 to-gray-600 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-2xl">📭</span>
                </div>
                <p className="text-gray-400">No hay datos UDP</p>
              </div>
            )}
          </div>          
          {/* Tipos ICMP */}
          <div className="bg-gray-800/70 backdrop-blur-sm p-6 rounded-3xl shadow-lg border border-gray-700/50 hover:shadow-xl transition-all duration-300">
            <div className="flex items-center mb-4">
              <div className="w-8 h-8 bg-gradient-to-r from-indigo-400 to-purple-500 rounded-xl flex items-center justify-center mr-3">
                <span className="text-white text-sm">📡</span>
              </div>
              <h4 className="text-lg font-bold text-gray-300">Tipos ICMP</h4>
            </div>
            {analytics.icmp_types?.length > 0 ? (
              <div className="space-y-2">
                {analytics.icmp_types.map((t, index) => (
                  <div key={t.type} className="flex justify-between items-center p-3 bg-gradient-to-r from-indigo-900/30 to-purple-900/30 rounded-2xl">
                    <span className="text-gray-400 font-medium">Tipo {t.type}</span>
                    <span className="text-indigo-300 font-semibold">{t.count?.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-gradient-to-r from-gray-700 to-gray-600 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-2xl">📭</span>
                </div>
                <p className="text-gray-400">No hay datos ICMP</p>
              </div>
            )}
          </div>          {/* Resumen Anomalías */}
          <div className="bg-gray-800/70 backdrop-blur-sm p-6 rounded-3xl shadow-lg border border-gray-700/50 hover:shadow-xl transition-all duration-300 md:col-span-2 lg:col-span-3">
            <div className="flex items-center mb-4">
              <div className="w-8 h-8 bg-gradient-to-r from-red-400 to-rose-500 rounded-xl flex items-center justify-center mr-3">
                <span className="text-white text-sm">⚠️</span>
              </div>
              <h4 className="text-lg font-bold text-gray-300">Resumen de Anomalías</h4>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Por Tipo */}
              <div>
                <div className="flex items-center mb-3">
                  <div className="w-6 h-6 bg-gradient-to-r from-red-300 to-rose-400 rounded-lg flex items-center justify-center mr-2">
                    <span className="text-white text-xs">🔍</span>
                  </div>
                  <h5 className="text-md font-semibold text-gray-400">Por Tipo</h5>
                </div>
                {analytics.anomalies?.by_type?.length > 0 ? (
                  <div className="space-y-2">
                    {analytics.anomalies.by_type.map((a, index) => (
                      <div key={a.type} className="flex justify-between items-center p-3 bg-gradient-to-r from-red-900/30 to-rose-900/30 rounded-2xl">
                        <span className="text-gray-400 font-medium">{a.type}</span>
                        <span className="px-3 py-1 bg-red-800/50 text-red-300 font-semibold rounded-full text-sm">
                          {a.count?.toLocaleString()}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-6">
                    <div className="w-12 h-12 bg-gradient-to-r from-green-800/50 to-emerald-800/50 rounded-full flex items-center justify-center mx-auto mb-2">
                      <span className="text-lg">✅</span>
                    </div>
                    <p className="text-gray-400">Sin anomalías por tipo</p>
                  </div>
                )}
              </div>

              {/* Por Severidad */}
              <div>
                <div className="flex items-center mb-3">
                  <div className="w-6 h-6 bg-gradient-to-r from-orange-300 to-red-400 rounded-lg flex items-center justify-center mr-2">
                    <span className="text-white text-xs">📊</span>
                  </div>
                  <h5 className="text-md font-semibold text-gray-400">Por Severidad</h5>
                </div>
                {analytics.anomalies?.by_severity?.length > 0 ? (
                  <div className="space-y-2">
                    {analytics.anomalies.by_severity.map((a, index) => (
                      <div key={a.severity} className="flex justify-between items-center p-3 bg-gradient-to-r from-orange-900/30 to-red-900/30 rounded-2xl">
                        <span className="text-gray-400 font-medium capitalize">{a.severity}</span>
                        <span className={`px-3 py-1 font-semibold rounded-full text-sm ${
                          a.severity === 'high' || a.severity === 'alta' ? 'bg-red-800/50 text-red-300' :
                          a.severity === 'medium' || a.severity === 'media' ? 'bg-orange-800/50 text-orange-300' :
                          'bg-yellow-800/50 text-yellow-300'
                        }`}>
                          {a.count?.toLocaleString()}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-6">
                    <div className="w-12 h-12 bg-gradient-to-r from-green-800/50 to-emerald-800/50 rounded-full flex items-center justify-center mx-auto mb-2">
                      <span className="text-lg">✅</span>
                    </div>
                    <p className="text-gray-400">Sin anomalías por severidad</p>
                  </div>
                )}
              </div>
            </div>
          </div>

        </div>
      )}
    </div>
  );
}

export default SessionAnalytics;
