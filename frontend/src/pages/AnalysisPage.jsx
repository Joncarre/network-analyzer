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
    <div className="container mx-auto p-6 min-h-screen" style={{ background: '#222831', borderRadius: '1.5rem' }}>
      <h1 className="text-2xl font-bold mb-6 text-[#e9d7a5]">Análisis de Sesiones</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Selector de base de datos */}
        <div className="md:col-span-1 p-4 rounded-2xl shadow-md" style={{ background: '#393E46' }}>
          <label className="block mb-2 font-semibold text-[#DFD0B8]">Selecciona una base de datos:</label>
          <select
            className="w-full border rounded p-2 bg-[#222831] text-[#DFD0B8] focus:ring-2 focus:ring-[#e9d7a5]"
            value={selectedDbFile || ''}
            onChange={e => {
              setSelectedDbFile(e.target.value);
            }}
          >
            <option value="" disabled>-- Elige un archivo .db --</option>
            {dbFiles.map(db => (
              <option key={db.name} value={db.name}>{db.name} ({db.size_kb} KB)</option>
            ))}
          </select>

          {loadingSessions && <p className="text-[#DFD0B8] mt-4">Cargando sesiones...</p>}
          {errorSessions && <p className="text-red-400 mt-4">{errorSessions}</p>}

          {!loadingSessions && !errorSessions && (
            <div className="mt-6">
              <h2 className="text-xl font-semibold mb-3 text-[#DFD0B8]">Sesiones Disponibles</h2>
              {sessions.length === 0 ? (
                <p className="text-[#DFD0B8]/70">No hay sesiones de captura disponibles.</p>
              ) : (
                <ul className="divide-y divide-[#948979] max-h-96 overflow-y-auto">
                  {sessions.map((session) => (
                    <li 
                      key={session.id} 
                      className={`py-3 px-2 cursor-pointer rounded-xl transition-all duration-150 ${selectedSessionId === session.id ? 'bg-[#948979] text-[#222831]' : 'hover:bg-[#222831] hover:text-[#e9d7a5] text-[#DFD0B8]'}`}
                      onClick={() => handleSelectSession(session.id)}
                    >
                      <p className="font-medium">ID: {session.id}</p>
                      <p className="text-sm truncate">Archivo: {session.file_name}</p>
                      <p className="text-sm">Fecha: {new Date(session.capture_date).toLocaleString()}</p>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>

        {/* Columna de Chat */}
        <div className="md:col-span-2 p-4 rounded-2xl shadow-md mt-10 md:mt-0" style={{ background: '#393E46' }}>
          {selectedDbFile ? (
            <ChatInterface dbFile={selectedDbFile} sessionId={selectedSessionId} />
          ) : (
            <div className="flex items-center justify-center h-full text-[#DFD0B8]/70">
              <p>Selecciona una base de datos para ver el chat con IA.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default AnalysisPage;
