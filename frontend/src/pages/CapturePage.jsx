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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50 to-cyan-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header Section */}
        <div className="text-center mb-12">
            <h1 className="text-4xl mb-8 font-bold bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 bg-clip-text text-transparent">
              Captura de tráfico de red
            </h1>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            Captura paquetes en tiempo real o procese archivos .pcap existentes
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Panel de Captura de Tráfico */}
          <div className="bg-white/70 backdrop-blur-sm p-8 rounded-3xl shadow-lg border border-white/30 hover:shadow-xl transition-all duration-300">
            <div className="flex items-center mb-6">
              <div className="w-12 h-12 bg-gradient-to-r from-emerald-400 to-teal-500 rounded-2xl flex items-center justify-center mr-4">
                <span className="text-white text-xl">💻</span>
              </div>
              <h2 className="text-2xl font-bold text-slate-700">Captura en vivo</h2>
            </div>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold mb-3 text-slate-700">Seleccionar interfaz de red</label>
                <select 
                  className="w-full p-4 bg-white/80 backdrop-blur-sm border border-slate-200 rounded-2xl text-slate-700 focus:ring-1 focus:ring-emerald-400 focus:border-emerald-400 transition-all duration-200 shadow-sm hover:shadow-md"
                  value={selectedInterface}
                  onChange={(e) => setSelectedInterface(e.target.value)}
                  disabled={isCapturing || loading}
                >
                  {interfaces.map(iface => (
                    <option key={iface.id} value={iface.id} className="bg-white text-slate-700">
                      {iface.name || iface.id}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold mb-3 text-slate-700">Duración (segundos)</label>
                  <input 
                    type="number"
                    className="w-full p-4 bg-white/80 backdrop-blur-sm border border-slate-200 rounded-2xl text-slate-700 focus:ring-1 focus:ring-emerald-400 focus:border-emerald-400 transition-all duration-200 shadow-sm hover:shadow-md"
                    value={duration}
                    onChange={(e) => setDuration(Number(e.target.value) || 0)}
                    disabled={isCapturing || loading}
                    min="1"
                    placeholder="30"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-semibold mb-3 text-slate-700">Límite de paquetes</label>
                  <input 
                    type="number"
                    className="w-full p-4 bg-white/80 backdrop-blur-sm border border-slate-200 rounded-2xl text-slate-700 focus:ring-1 focus:ring-emerald-400 focus:border-emerald-400 transition-all duration-200 shadow-sm hover:shadow-md"
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
                <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl shadow-sm">
                  <p className="text-slate-700 font-medium">{captureStatus}</p>
                </div>
              )}
            </div>
          </div>

          {/* Panel de Generar base de datos desde fichero .pcap */}
          <div className="bg-white/70 backdrop-blur-sm p-8 rounded-3xl shadow-lg border border-white/30 hover:shadow-xl transition-all duration-300">
            <div className="flex items-center mb-6">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-400 to-indigo-500 rounded-2xl flex items-center justify-center mr-4">
                <span className="text-white text-xl">📁</span>
              </div>
              <h2 className="text-2xl font-bold text-slate-700">Procesar archivo .pcap</h2>
            </div>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold mb-3 text-slate-700">Seleccionar fichero .pcap</label>
                <input 
                  ref={fileInputRef}
                  type="file" 
                  className="w-full p-4 bg-white/80 backdrop-blur-sm border border-slate-200 rounded-2xl text-slate-700 focus:ring-1 focus:ring-blue-400 focus:border-blue-400 transition-all duration-200 shadow-sm hover:shadow-md file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-gradient-to-r file:from-blue-50 file:to-indigo-50 file:text-blue-700 hover:file:bg-gradient-to-r hover:file:from-blue-100 hover:file:to-indigo-100"
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
                <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl shadow-sm">
                  <p className="text-slate-700 font-medium">{uploadStatus}</p>
                </div>
              )}
              
              <div className="mt-8">
                <h3 className="text-lg font-bold text-slate-700 mb-4 flex items-center">
                  <span className="mr-2"></span>
                  Archivos .pcap almacenados
                </h3>
                {pcapFiles.length === 0 ? (
                  <div className="text-center py-8">
                    <div className="w-16 h-16 bg-gradient-to-r from-slate-100 to-slate-200 rounded-full flex items-center justify-center mx-auto mb-4">
                      <span className="text-2xl">📄</span>
                    </div>
                    <p className="text-slate-500">No hay archivos .pcap disponibles</p>
                  </div>
                ) : (
                  <div className="bg-white/60 backdrop-blur-sm rounded-2xl border border-white/30 overflow-hidden">
                    {pcapFiles.map((file, index) => (
                      <div 
                        key={file.path} 
                        className={`p-4 hover:bg-gradient-to-r hover:from-blue-50 hover:to-indigo-50 transition-all duration-200 cursor-pointer group ${
                          index !== pcapFiles.length - 1 ? 'border-b border-slate-200' : ''
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            <div className="w-8 h-8 bg-gradient-to-r from-blue-400 to-indigo-500 rounded-lg flex items-center justify-center mr-3">
                              <span className="text-white text-sm">📊</span>
                            </div>
                            <span className="text-slate-700 font-medium group-hover:text-slate-800 transition-colors">
                              {file.name}
                            </span>
                          </div>
                          <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                            <span className="text-slate-400">⮞</span>
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
