import React, { useState, useEffect, useRef } from 'react';
import { getInterfaces, startCapture, listPcapFiles, uploadPcapFile } from '../services/api';

function CapturePage() {
  const [interfaces, setInterfaces] = useState([]);
  const [selectedInterface, setSelectedInterface] = useState('');
  const [duration, setDuration] = useState(30);
  const [packetCount, setPacketCount] = useState(1000);
  const [isCapturing, setIsCapturing] = useState(false);
  const [captureStatus, setCaptureStatus] = useState('');
  const [loading, setLoading] = useState(false);
  
  const [pcapFiles, setPcapFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [fileLoading, setFileLoading] = useState(false);
  const fileInputRef = useRef(null);

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

  const handleStartCapture = () => {
    setLoading(true);
    setIsCapturing(true);
    setCaptureStatus('🛜 Iniciando captura...');

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

  const handleFileChange = (event) => {
    if (event.target.files.length > 0) {
      setSelectedFile(event.target.files[0]);
    } else {
      setSelectedFile(null);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) return;
    
    try {
      setFileLoading(true);
      setUploadStatus('Generando base de datos...');
      
      const response = await uploadPcapFile(
        selectedFile,
        true,
        selectedInterface
      );
      
      setUploadStatus(`Base de datos generada.`);
      
      const filesResponse = await listPcapFiles();
      setPcapFiles(filesResponse.data);
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = null;
      }
      
    } catch (error) {
      console.error('Error al subir archivo:', error);
      if (error.response?.status === 409) {
        setUploadStatus(`Error: ${error.response.data.detail}`);
      } else {
        setUploadStatus(`Error al generar base de datos: ${error.response?.data?.detail || error.message}`);
      }
    } finally {
      setFileLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header Section */}
        <div className="text-center mb-12">
            <h1 className="text-4xl mb-8 font-bold bg-gradient-to-r from-emerald-400 via-teal-400 to-cyan-400 bg-clip-text text-transparent">
              Captura de tráfico de red
            </h1>
          <p className="text-lg text-gray-400 max-w-2xl mx-auto">
            Captura paquetes en tiempo real o procese archivos .pcap existentes
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Panel de Captura de Tráfico */}
          <div className="bg-gray-800/70 backdrop-blur-sm p-8 rounded-3xl shadow-lg border border-gray-700/50 hover:shadow-xl transition-all duration-300">
            <div className="flex items-center mb-6">
              <div className="w-12 h-12 bg-gradient-to-r from-emerald-400 to-teal-500 rounded-2xl flex items-center justify-center mr-4">
                <span className="text-white text-xl">💻</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-300">Captura en vivo</h2>
            </div>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold mb-3 text-gray-300">Seleccionar interfaz de red</label>
                <select 
                  className="w-full p-4 bg-gray-700/80 backdrop-blur-sm border border-gray-600 rounded-2xl text-gray-300 focus:ring-1 focus:ring-emerald-400 focus:border-emerald-400 transition-all duration-200 shadow-sm hover:shadow-md"
                  value={selectedInterface}
                  onChange={(e) => setSelectedInterface(e.target.value)}
                  disabled={isCapturing || loading}
                >
                  {interfaces.map(iface => (
                    <option key={iface.id} value={iface.id} className="bg-gray-700 text-gray-300">
                      {iface.name || iface.id}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold mb-3 text-gray-300">Duración (segundos)</label>
                  <input 
                    type="number"
                    className="w-full p-4 bg-gray-700/80 backdrop-blur-sm border border-gray-600 rounded-2xl text-gray-300 focus:ring-1 focus:ring-emerald-400 focus:border-emerald-400 transition-all duration-200 shadow-sm hover:shadow-md"
                    value={duration}
                    onChange={(e) => setDuration(Number(e.target.value) || 0)}
                    disabled={isCapturing || loading}
                    min="1"
                    placeholder="30"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-semibold mb-3 text-gray-300">Límite de paquetes</label>
                  <input 
                    type="number"
                    className="w-full p-4 bg-gray-700/80 backdrop-blur-sm border border-gray-600 rounded-2xl text-gray-300 focus:ring-1 focus:ring-emerald-400 focus:border-emerald-400 transition-all duration-200 shadow-sm hover:shadow-md"
                    value={packetCount}
                    onChange={(e) => setPacketCount(Number(e.target.value) || 0)}
                    disabled={isCapturing || loading}
                    min="1"
                    placeholder="1000"
                  />
                </div>
              </div>
              
              <button 
                className={`w-full py-4 px-6 rounded-2xl font-semibold text-white shadow-lg transition-all duration-300 transform hover:-translate-y-1 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none ${
                  isCapturing 
                    ? 'bg-gradient-to-r from-amber-400 to-orange-500 hover:from-amber-500 hover:to-orange-600' 
                    : 'bg-gradient-to-r from-emerald-400 to-teal-500 hover:from-emerald-500 hover:to-teal-600 hover:shadow-xl'
                }`}
                onClick={handleStartCapture}
                disabled={isCapturing || loading || !selectedInterface}
              >
                {isCapturing ? (
                  <span className="flex items-center justify-center">
                    <span className="animate-spin mr-2">⚙️</span>
                    Capturando...
                  </span>
                ) : (
                  <span className="flex items-center justify-center">
                    <span className="mr-2"></span>
                    Iniciar captura
                  </span>
                )}
              </button>
              
              {captureStatus && (
                <div className="p-4 bg-gradient-to-r from-blue-900/50 to-indigo-900/50 border border-blue-700/50 rounded-2xl shadow-sm">
                  <p className="text-gray-300 font-medium">{captureStatus}</p>
                </div>
              )}
            </div>
          </div>

          {/* Panel de Generar base de datos desde fichero .pcap */}
          <div className="bg-gray-800/70 backdrop-blur-sm p-8 rounded-3xl shadow-lg border border-gray-700/50 hover:shadow-xl transition-all duration-300">
            <div className="flex items-center mb-6">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-400 to-indigo-500 rounded-2xl flex items-center justify-center mr-4">
                <span className="text-white text-xl">📁</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-300">Procesar archivo .pcap</h2>
            </div>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold mb-3 text-gray-300">Seleccionar fichero .pcap</label>
                <input 
                  ref={fileInputRef}
                  type="file" 
                  className="w-full p-4 bg-gray-700/80 backdrop-blur-sm border border-gray-600 rounded-2xl text-gray-300 focus:ring-1 focus:ring-blue-400 focus:border-blue-400 transition-all duration-200 shadow-sm hover:shadow-md file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-gradient-to-r file:from-blue-900/50 file:to-indigo-900/50 file:text-blue-300 hover:file:bg-gradient-to-r hover:file:from-blue-800/50 hover:file:to-indigo-800/50"
                  accept=".pcap,.pcapng"
                  onChange={handleFileChange}
                  disabled={fileLoading}
                />
              </div>
              
              <button 
                className={`w-full py-4 px-6 rounded-2xl font-semibold text-white shadow-lg transition-all duration-300 transform hover:-translate-y-1 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none ${
                  fileLoading 
                    ? 'bg-gradient-to-r from-amber-400 to-orange-500 hover:from-amber-500 hover:to-orange-600' 
                    : 'bg-gradient-to-r from-blue-400 to-indigo-500 hover:from-blue-500 hover:to-indigo-600 hover:shadow-xl'
                }`}
                onClick={handleFileUpload}
                disabled={fileLoading || !selectedFile}
              >
                {fileLoading ? (
                  <span className="flex items-center justify-center">
                    <span className="animate-spin mr-2">⚙️</span>
                    Procesando...
                  </span>
                ) : (
                  <span className="flex items-center justify-center">
                    <span className="mr-2"></span>
                    Procesar archivo
                  </span>
                )}
              </button>
              
              {uploadStatus && (
                <div className="p-4 bg-gradient-to-r from-blue-900/50 to-indigo-900/50 border border-blue-700/50 rounded-2xl shadow-sm">
                  <p className="text-gray-300 font-medium">{uploadStatus}</p>
                </div>
              )}
              
              <div className="mt-8">
                <h3 className="text-lg font-bold text-gray-300 mb-4 flex items-center">
                  <span className="mr-2"></span>
                  Archivos .pcap almacenados
                </h3>
                {pcapFiles.length === 0 ? (
                  <div className="text-center py-8">
                    <div className="w-16 h-16 bg-gradient-to-r from-gray-700 to-gray-600 rounded-full flex items-center justify-center mx-auto mb-4">
                      <span className="text-2xl">📄</span>
                    </div>
                    <p className="text-gray-500">No hay archivos .pcap disponibles</p>
                  </div>
                ) : (
                  <div className="bg-gray-700/60 backdrop-blur-sm rounded-2xl border border-gray-600/50 overflow-hidden">
                    {pcapFiles.map((file, index) => (
                      <div 
                        key={file.path} 
                        className={`p-4 hover:bg-gradient-to-r hover:from-blue-900/30 hover:to-indigo-900/30 transition-all duration-200 cursor-pointer group ${
                          index !== pcapFiles.length - 1 ? 'border-b border-gray-600' : ''
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            <div className="w-8 h-8 bg-gradient-to-r from-blue-400 to-indigo-500 rounded-lg flex items-center justify-center mr-3">
                              <span className="text-white text-sm">📊</span>
                            </div>
                            <span className="text-gray-300 font-medium group-hover:text-gray-200 transition-colors">
                              {file.name}
                            </span>
                          </div>
                          <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                            <span className="text-gray-400">⮞</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CapturePage;
