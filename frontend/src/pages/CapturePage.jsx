import React, { useState, useEffect, useRef } from 'react'; // Añadir useRef
import { getInterfaces, startCapture, listPcapFiles, uploadPcapFile } from '../services/api';

function CapturePage() {
  const [interfaces, setInterfaces] = useState([]);
  const [selectedInterface, setSelectedInterface] = useState('');
  const [duration, setDuration] = useState(30); // Duración en segundos
  const [packetCount, setPacketCount] = useState(1000); // Límite de paquetes
  const [isCapturing, setIsCapturing] = useState(false);
  const [captureStatus, setCaptureStatus] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Estado para archivo PCAP
  const [pcapFiles, setPcapFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [fileLoading, setFileLoading] = useState(false);
  const fileInputRef = useRef(null); // Crear una referencia para el input file

  // Cargar interfaces disponibles al montar el componente
  useEffect(() => {
    async function fetchInterfaces() {
      try {
        const response = await getInterfaces();
        setInterfaces(response.data);
        if (response.data.length > 0) {
          setSelectedInterface(response.data[0].id);
        }
      } catch (error) {
        console.error('Error al obtener interfaces:', error);
        setCaptureStatus('Error al cargar interfaces. Verifica que el backend esté funcionando.');
      }
    }
    
    async function fetchPcapFiles() {
      try {
        const response = await listPcapFiles();
        setPcapFiles(response.data);
      } catch (error) {
        console.error('Error al obtener archivos PCAP:', error);
      }
    }

    fetchInterfaces();
    fetchPcapFiles();
  }, []);

  // Iniciar captura
  const handleStartCapture = () => {
    setLoading(true);
    setIsCapturing(true);
    setCaptureStatus('🛜 Iniciando captura...');

    // Lanzar la petición pero no esperar a que termine para reactivar el botón
    startCapture(selectedInterface, duration, packetCount).catch((error) => {
      console.error('Error al iniciar captura:', error);
      setCaptureStatus(`Error al iniciar captura: ${error.response?.data?.detail || error.message}`);
      setIsCapturing(false);
      setLoading(false);
    });

    setCaptureStatus('⚙️ Capturando tráfico de red... ');
    setTimeout(async () => {
      try {
        const filesResponse = await listPcapFiles();
        setPcapFiles(filesResponse.data);
        setCaptureStatus('✅ Captura completada.');
      } catch (err) {
        console.error('Error al actualizar archivos:', err);
      }
      setIsCapturing(false);
      setLoading(false);
    }, (duration + 5) * 1000);
  };

  // Manejar cambio de archivo seleccionado
  const handleFileChange = (event) => {
    if (event.target.files.length > 0) {
      setSelectedFile(event.target.files[0]);
    } else {
      setSelectedFile(null);
    }
  };

  // Subir archivo PCAP
  const handleFileUpload = async () => {
    if (!selectedFile) return;
    
    try {
      setFileLoading(true);
      setUploadStatus('Generando base de datos...');
      
      const response = await uploadPcapFile(
        selectedFile,
        true, // Siempre procesamos inmediatamente
        selectedInterface
      );
      
      setUploadStatus(`Base de datos generada.`);
      
      // Actualizar lista de archivos
      const filesResponse = await listPcapFiles();
      setPcapFiles(filesResponse.data);
      setSelectedFile(null); // Limpiar el estado del archivo seleccionado
      if (fileInputRef.current) {
        fileInputRef.current.value = null; // Limpiar el input file visualmente
      }
      
    } catch (error) {
      console.error('Error al subir archivo:', error);
      // Mejorar el manejo de errores para mostrar mensajes específicos
      if (error.response?.status === 409) {
        // Error de conflicto - archivo duplicado
        setUploadStatus(`Error: ${error.response.data.detail}`);
      } else {
        setUploadStatus(`Error al generar base de datos: ${error.response?.data?.detail || error.message}`);
      }
    } finally {
      setFileLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Captura de Tráfico de Red</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Sección de Captura en Vivo */}
        <div className="bg-white p-4 rounded-lg shadow-md">
          {/* <h2 className="text-xl font-semibold mb-4">Captura en Vivo</h2> */}
          
          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">Interfaz de Red</label>
            <select 
              className="w-full border rounded p-2"
              value={selectedInterface}
              onChange={(e) => setSelectedInterface(e.target.value)}
              disabled={isCapturing || loading}
            >
              {interfaces.map(iface => (
                <option key={iface.id} value={iface.id}>
                  {iface.name || iface.id}
                </option>
              ))}
            </select>
          </div>
          
          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">Duración (segundos)</label>
            <input 
              type="text" // Cambiado de number a text
              className="w-full border rounded p-2"
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value) || 0)} // Asegurar que sea un número o 0
              disabled={isCapturing || loading}
              min="1"
            />
          </div>
          
          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">Límite de Paquetes</label>
            <input 
              type="text" // Cambiado de number a text
              className="w-full border rounded p-2"
              value={packetCount}
              onChange={(e) => setPacketCount(Number(e.target.value) || 0)} // Asegurar que sea un número o 0
              disabled={isCapturing || loading}
              min="1"
            />
          </div>
          
          <button 
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
            onClick={handleStartCapture}
            disabled={isCapturing || loading || !selectedInterface}
          >
            {isCapturing ? 'Capturando...' : 'Iniciar Captura'}
          </button>
          
          {captureStatus && (
            <div className="mt-3 p-2 border rounded bg-gray-50">
              <p>{captureStatus}</p>
            </div>
          )}
        </div>
        
        {/* Sección de Subida de Archivos PCAP */}
        <div className="bg-white p-4 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Generar base de datos desde fichero .pcap</h2>
          
          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">Archivo PCAP</label>
            <input 
              ref={fileInputRef} // Asignar la referencia al input
              type="file" 
              className="w-full border rounded p-2"
              accept=".pcap,.pcapng"
              onChange={handleFileChange}
              disabled={fileLoading}
            />
          </div>
          
          <button 
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 disabled:opacity-50"
            onClick={handleFileUpload}
            disabled={fileLoading || !selectedFile} // Modificado: deshabilitado si carga o no hay archivo
          >
            {fileLoading ? 'Subiendo...' : 'Subir Archivo'}
          </button>
          
          {uploadStatus && (
            <div className="mt-3 p-2 border rounded bg-gray-50">
              <p>{uploadStatus}</p>
            </div>
          )}
          
          {/* Lista de archivos PCAP existentes - sin botón Procesar */}
          <div className="mt-6">
            <h3 className="text-lg font-medium mb-2">Archivos .pcap almacenados</h3>
            {pcapFiles.length === 0 ? (
              <p className="text-gray-500">No hay archivos PCAP disponibles.</p>
            ) : (
              <ul className="divide-y border rounded">
                {pcapFiles.map(file => (
                  <li key={file.path} className="p-2 hover:bg-gray-50">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">{file.name}</span>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default CapturePage;
