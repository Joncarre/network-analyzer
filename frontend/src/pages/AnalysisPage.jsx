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

  // Solo mostrar el chat si hay una base de datos seleccionada
  return (
    <div className="container mx-auto p-4 grid grid-cols-1 md:grid-cols-3 gap-4">
      {/* Selector de base de datos */}
      <div className="md:col-span-1">
        <h1 className="text-2xl font-bold mb-4">Análisis de Sesiones</h1>
        <div className="mb-4">
          <label className="block mb-2 font-semibold">Selecciona una base de datos:</label>
          <select
            className="w-full border rounded p-2"
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
        </div>

        {loadingSessions && <p>Cargando sesiones...</p>}
        {errorSessions && <p className="text-red-500">{errorSessions}</p>}

        {!loadingSessions && !errorSessions && (
          <div className="bg-white shadow-md rounded-lg p-4">
            <h2 className="text-xl font-semibold mb-3">Sesiones Disponibles</h2>
            {sessions.length === 0 ? (
              <p>No hay sesiones de captura disponibles.</p>
            ) : (
              <ul className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
                {sessions.map((session) => (
                  <li 
                    key={session.id} 
                    className={`py-3 px-2 cursor-pointer hover:bg-gray-100 ${selectedSessionId === session.id ? 'bg-blue-100' : ''}`}
                    onClick={() => handleSelectSession(session.id)}
                  >
                    <p className="font-medium">ID: {session.id}</p>
                    <p className="text-sm text-gray-600 truncate">Archivo: {session.file_name}</p>
                    <p className="text-sm text-gray-500">Fecha: {new Date(session.capture_date).toLocaleString()}</p>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>

      {/* Columna de Chat */}
      <div className="md:col-span-2">
        {selectedDbFile ? (
          <div className="bg-white shadow-md rounded-lg p-4 mt-10 md:mt-0">
            <ChatInterface dbFile={selectedDbFile} sessionId={selectedSessionId} />
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            <p>Selecciona una base de datos para ver el chat con IA.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default AnalysisPage;
