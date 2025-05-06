import axios from 'axios';

const API_URL = 'http://localhost:8000/api'; // URL base de tu API backend

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- Funciones existentes ---
export const getInterfaces = () => apiClient.get('/capture/interfaces');

export const startCapture = (interfaceId, duration, packetCount) => {
  return apiClient.post('/capture/start', null, {
    params: {
      interface_id: interfaceId,
      duration: duration,
      packet_count: packetCount,
    },
  });
};

export const listPcapFiles = () => apiClient.get('/capture/files');

export const uploadPcapFile = (file, processNow, interfaceId) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('process_now', processNow);
  if (interfaceId) {
    formData.append('interface', interfaceId);
  }
  return apiClient.post('/processing/upload-pcap', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const processPcapFile = (filePath, interfaceId) => {
  return apiClient.post('/processing/process-pcap', null, {
    params: {
      file_path: filePath,
      interface: interfaceId,
    },
  });
};

// --- Nuevas funciones para Análisis ---

// Obtener lista de sesiones de una base de datos específica
export const getSessions = (dbFile) => apiClient.get('/database/sessions', { params: dbFile ? { db_file: dbFile } : {} });

// Obtener detalles de una sesión de una base de datos específica
export const getSessionDetails = (sessionId, dbFile) => apiClient.get(`/database/sessions/${sessionId}`, { params: dbFile ? { db_file: dbFile } : {} });

// Obtener paquetes de una sesión (con filtros/paginación)
export const getSessionPackets = (sessionId, params) => {
  // params should include limit, offset, and optional filters like src_ip, dst_ip, protocol
  return apiClient.get(`/database/sessions/${sessionId}/packets`, { params });
};

// Obtener anomalías de una sesión (con filtros/paginación)
export const getSessionAnomalies = (sessionId, params) => {
  // params should include limit, offset, and potentially filters like severity, type
  return apiClient.get(`/database/sessions/${sessionId}/anomalies`, { params });
};

// Obtener análisis estadísticos de una sesión
export const getSessionAnalytics = (sessionId) => apiClient.get(`/database/analytics/${sessionId}`);

// Listar bases de datos disponibles
export const listDbFiles = () => apiClient.get('/database/list-db-files');

// Enviar mensaje al chat de IA con base de datos y preferencia de usuario
export const postChatMessage = (message, sessionId = null, dbFile = null, userPreference = null) => {
  return apiClient.post('/ai/chat', { message, session_id: sessionId, db_file: dbFile, user_preference: userPreference });
};

// Limpiar historial de chat de IA
export const clearChatHistory = () => apiClient.post('/ai/clear-chat');

export default apiClient;
