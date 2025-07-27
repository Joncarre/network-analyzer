import React, { useState, useEffect } from 'react';
import { getSessions, getSessionDetails, listDbFiles } from '../services/api';
import ChatInterface from '../components/ChatInterface'; // Importar ChatInterface

function AnalysisPage() {
  const [sessions, setSessions] = useState([]);
  const [loadingSessions, setLoadingSessions] = useState(true);
  const [errorSessions, setErrorSessions] = useState(null);

  const [selectedSessionId, setSelectedSessionId] = useState(null);
  const [selectedSessionDetails, setSelectedSessionDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [errorDetails, setErrorDetails] = useState(null);

  const [dbFiles, setDbFiles] = useState([]);
  const [selectedDbFile, setSelectedDbFile] = useState(null);

  // Efecto para cargar la lista de bases de datos al montar
  useEffect(() => {
    const fetchDbFiles = async () => {
      try {
        const response = await listDbFiles();
        setDbFiles(response.data);
      } catch (err) {
        setDbFiles([]);
      }
    };
    fetchDbFiles();
  }, []);

  // Efecto para cargar la lista de sesiones cuando cambia la base de datos seleccionada
  useEffect(() => {
    if (!selectedDbFile) {
      setSessions([]);
      return;
    }
    const fetchSessions = async () => {
      try {
        setLoadingSessions(true);
        const response = await getSessions(selectedDbFile);
        setSessions(Array.isArray(response.data.sessions) ? response.data.sessions : []);
        setErrorSessions(null);
      } catch (err) {
        setErrorSessions("Error al cargar las sesiones. Asegúrate de que el backend está funcionando.");
        setSessions([]);
      } finally {
        setLoadingSessions(false);
      }
    };
    fetchSessions();
  }, [selectedDbFile]);

  // Función para manejar la selección de una sesión
  const handleSelectSession = async (sessionId) => {
    if (selectedSessionId === sessionId) {
      setSelectedSessionId(null);
      setSelectedSessionDetails(null);
      setErrorDetails(null);
      return;
    }
    setSelectedSessionId(sessionId);
    setSelectedSessionDetails(null); // Limpiar detalles anteriores
    setErrorDetails(null);
    setLoadingDetails(true);
    try {
      const response = await getSessionDetails(sessionId, selectedDbFile);
      setSelectedSessionDetails(response.data);
    } catch (err) {
      console.error(`Error fetching details for session ${sessionId}:`, err);
      setErrorDetails(`Error al cargar los detalles de la sesión ${sessionId}.`);
    } finally {
      setLoadingDetails(false);
    }
  };
  return (
    <div className="min-h-screen bg-gray-900 py-8 px-4">
      <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
         
              <h1 className="text-4xl mb-8 font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-rose-400 bg-clip-text text-transparent">
                Análisis de sesiones
              </h1>

            <p className="text-lg text-gray-400 max-w-2xl mx-auto">
              Explora y analiza sesiones de captura con la ayuda del asistente inteligente
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 min-h-[80vh]">
            {/* Selector de base de datos */}
          <div className="lg:col-span-1 bg-gray-800/70 backdrop-blur-sm p-8 rounded-3xl shadow-lg border border-gray-700/50 hover:shadow-xl transition-all duration-300">
            <div className="flex items-center mb-6">
              <div className="w-12 h-12 bg-gradient-to-r from-purple-400 to-pink-500 rounded-2xl flex items-center justify-center mr-4">
                <span className="text-white text-xl">🗄️</span>
              </div>
              <h2 className="text-xl font-bold text-gray-300">Base de Datos</h2>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold mb-3 text-gray-300">Selecciona una base de datos:</label>
                <select
                  className="w-full p-4 bg-gray-700/80 backdrop-blur-sm border border-gray-600 rounded-2xl text-gray-300 focus:ring-1 focus:ring-purple-400 focus:border-purple-400 transition-all duration-200 shadow-sm hover:shadow-md"
                  value={selectedDbFile || ''}
                  onChange={e => {
                    setSelectedDbFile(e.target.value);
                  }}
                >
                  <option value="" disabled className="bg-gray-700 text-gray-300">-- Elige un archivo .db --</option>
                  {dbFiles.map(db => (
                    <option key={db.name} value={db.name} className="bg-gray-700 text-gray-300">{db.name} ({db.size_kb} KB)</option>
                  ))}
                </select>
              </div>

              {loadingSessions && (
                <div className="p-4 bg-gradient-to-r from-purple-900/50 to-pink-900/50 border border-purple-700/50 rounded-2xl shadow-sm">
                  <p className="text-gray-300 font-medium flex items-center">
                    <span className="mr-2">⚙️</span>
                    Aquí aparecerán sus sesiones disponible
                  </p>
                </div>
              )}
              {errorSessions && (
                <div className="p-4 bg-gradient-to-r from-red-900/50 to-rose-900/50 border border-red-700/50 rounded-2xl shadow-sm">
                  <p className="text-red-400 font-medium">{errorSessions}</p>
                </div>
              )}              {!loadingSessions && !errorSessions && (
                <div className="mt-6">
                  <h3 className="text-lg font-bold text-gray-300 mb-4 flex items-center">
                    <span className="mr-2"></span>
                    Sesiones disponibles
                  </h3>
                  {sessions.length === 0 ? (
                    <div className="text-center py-8">
                      <div className="w-16 h-16 bg-gradient-to-r from-gray-700 to-gray-600 rounded-full flex items-center justify-center mx-auto mb-4">
                        <span className="text-2xl">📋</span>
                      </div>
                      <p className="text-gray-500">No hay sesiones de captura disponibles</p>
                    </div>
                  ) : (
                    <div className="bg-gray-700/60 backdrop-blur-sm rounded-2xl border border-gray-600/50 overflow-hidden max-h-96 overflow-y-auto">
                      {sessions.map((session, index) => (
                        <div 
                          key={session.id} 
                          className={`p-4 hover:bg-gradient-to-r hover:from-purple-900/30 hover:to-pink-900/30 transition-all duration-500 cursor-pointer group ${
                            selectedSessionId === session.id 
                              ? 'bg-gradient-to-r from-purple-800/30 to-pink-800/30 border-l-4 border-purple-400' 
                              : ''
                          } ${index !== sessions.length - 1 ? 'border-b border-gray-600' : ''}`}
                          onClick={() => handleSelectSession(session.id)}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="flex items-center mb-2">
                                <div className="w-8 h-8 bg-gradient-to-r from-purple-400 to-pink-500 rounded-lg flex items-center justify-center mr-3">
                                  <span className="text-white text-sm">🔍</span>
                                </div>
                                <p className="font-semibold text-gray-300 group-hover:text-gray-200">ID: {session.id}</p>
                              </div>
                              <p className="text-sm text-gray-400 truncate ml-11">Archivo: {session.file_name}</p>
                              <p className="text-sm text-gray-500 ml-11">Fecha: {new Date(session.capture_date).toLocaleString()}</p>
                            </div>
                            <div className={`transition-all duration-2000 ${selectedSessionId === session.id ? 'text-purple-400' : 'opacity-0 group-hover:opacity-100 text-gray-400'}`}>
                              <span>{selectedSessionId === session.id ? '✓' : '⮞'}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>          {/* Columna de Chat */}
          <div className="lg:col-span-2 bg-gray-800/70 backdrop-blur-sm p-8 rounded-3xl shadow-lg border border-gray-700/50 hover:shadow-xl transition-all duration-300">
            <div className="flex items-center mb-6">
              <div className="w-12 h-12 bg-gradient-to-r from-purple-400 to-pink-500 rounded-2xl flex items-center justify-center mr-4">
                <span className="text-white text-xl">🤖</span>
              </div>
              <h2 className="text-xl font-bold text-gray-300">Asistente de IA</h2>
            </div>
            
            {selectedDbFile ? (
              <ChatInterface dbFile={selectedDbFile} sessionId={selectedSessionId} />
            ) : (
              <div className="flex flex-col items-center justify-center h-96 text-center">
                <div className="w-24 h-24 bg-gradient-to-r from-gray-700 to-gray-600 rounded-full flex items-center justify-center mb-6">
                  <span className="text-4xl">🔍</span>
                </div>
                <h3 className="text-xl font-semibold text-gray-300 mb-2">Selecciona una Base de Datos</h3>
                <p className="text-gray-500 max-w-md">
                  Elige una base de datos y sesión para comenzar a interactuar con el asistente de IA y analizar tus datos de red
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default AnalysisPage;
