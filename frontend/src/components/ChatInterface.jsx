import React, { useState, useEffect, useRef } from 'react';
import { postChatMessage, clearChatHistory } from '../services/api';

function ChatInterface({ sessionId, dbFile }) {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [userPreference, setUserPreference] = useState('corto'); // corto, normal, detallado
  const [userQuestionsHistory, setUserQuestionsHistory] = useState([]);
  const [systemMessage, setSystemMessage] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Manejar comandos especiales
  const handleCommand = async (cmd) => {
    if (cmd === 'reiniciar') {
      await handleClearChat();
      setMessages([]);
      setUserQuestionsHistory([]);
      setError(null);
      setSystemMessage({ type: 'info', content: 'Chat reiniciado' });
      return;
    }
    if (cmd === 'historial') {
      if (userQuestionsHistory.length === 0) {
        setSystemMessage({ type: 'info', content: 'No hay preguntas en el historial' });
      } else {
        setSystemMessage({ type: 'historial', content: 'Historial de preguntas:\n' + userQuestionsHistory.map((q, i) => `${i + 1}. ${q}`).join('\n') });
      }
      return;
    }
    if (cmd === 'borrar_historial') {
      setUserQuestionsHistory([]);
      setSystemMessage({ type: 'info', content: 'Historial de preguntas del usuario borrado' });
      return;
    }
    if (["corto", "normal", "detallado"].includes(cmd)) {
      setUserPreference(cmd);
      setSystemMessage({ type: 'info', content: `Preferencia cambiada a: ${cmd}` });
      return;
    }
    setSystemMessage({ type: 'info', content: 'Comando no reconocido. Usa /corto, /normal, /detallado, /reiniciar, /historial o /borrar_historial.' });
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || loading) return;
    const query = inputMessage.trim();
    setInputMessage('');
    setError(null);

    // Comando
    if (query.startsWith('/')) {
      await handleCommand(query.slice(1).toLowerCase());
      return;
    }

    // Pregunta normal
    const userMessage = { role: 'user', content: query };
    setMessages((prev) => [...prev, userMessage]);
    setUserQuestionsHistory((prev) => [...prev, query]);
    setLoading(true);
    try {
      let messageToSend = query;
      const response = await postChatMessage(messageToSend, sessionId, dbFile, userPreference);
      const assistantMessage = { role: 'assistant', content: response.data.response };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError("Error al enviar el mensaje o recibir la respuesta de la IA.");
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = async () => {
    try {
      await clearChatHistory();
      setMessages([]);
      setError(null);
    } catch (err) {
      setError("Error al limpiar el historial del chat.");
    }
  };  return (
    <div className="h-full flex flex-col">
      {/* Header con Asistente de IA */}
      <div className="mb-4 flex flex-wrap gap-2">
        <span className="text-sm font-semibold text-gray-400 flex items-center">Modo de respuesta:</span>
        <button type="button" className={`px-3 py-1 rounded-xl text-xs font-medium transition-all duration-500 focus:outline-none border ${userPreference==='corto' ? 'bg-gradient-to-r from-fuchsia-400 to-pink-400 text-white border-purple-500' : 'bg-gray-700/80 text-gray-300 hover:bg-gradient-to-r hover:from-blue-800/50 hover:to-indigo-800/50 border-gray-600'}`} onClick={() => handleCommand('corto')}>corto</button>
        <button type="button" className={`px-3 py-1 rounded-xl text-xs font-medium transition-all duration-500 focus:outline-none border ${userPreference==='normal' ? 'bg-gradient-to-r from-fuchsia-400 to-pink-400 text-white border-purple-500' : 'bg-gray-700/80 text-gray-300 hover:bg-gradient-to-r hover:from-blue-800/50 hover:to-indigo-800/50 border-gray-600'}`} onClick={() => handleCommand('normal')}>normal</button>
        <button type="button" className={`px-3 py-1 rounded-xl text-xs font-medium transition-all duration-500 focus:outline-none border ${userPreference==='detallado' ? 'bg-gradient-to-r from-fuchsia-400 to-pink-400 text-white border-purple-500' : 'bg-gray-700/80 text-gray-300 hover:bg-gradient-to-r hover:from-blue-800/50 hover:to-indigo-800/50 border-gray-600'}`} onClick={() => handleCommand('detallado')}>detallado</button>
        <button type="button" className="px-3 py-1 rounded-xl text-xs font-medium transition-all duration-500 bg-gray-700/80 text-gray-300 hover:bg-gradient-to-r hover:from-orange-800/50 hover:to-amber-800/50 border border-gray-600 active:bg-gradient-to-r active:from-orange-700/50 active:to-amber-700/50 focus:outline-none" onClick={() => handleCommand('reiniciar')}>reiniciar</button>
        <button type="button" className="px-3 py-1 rounded-xl text-xs font-medium transition-all duration-500 bg-gray-700/80 text-gray-300 hover:bg-gradient-to-r hover:from-green-800/50 hover:to-emerald-800/50 border border-gray-600 active:bg-gradient-to-r active:from-green-700/50 active:to-emerald-700/50 focus:outline-none" onClick={() => handleCommand('historial')}>historial</button>
        <button type="button" className="px-3 py-1 rounded-xl text-xs font-medium transition-all duration-500 bg-gradient-to-r from-red-400 to-rose-500 text-white hover:from-red-500 hover:to-rose-600 active:bg-gradient-to-r active:from-red-600 active:to-rose-700 active:text-white border border-red-500 focus:outline-none" onClick={() => handleCommand('borrar_historial')}>borrar historial</button>
      </div>
      
      {error && (
        <div className="p-3 bg-gradient-to-r from-red-900/50 to-rose-900/50 border border-red-700/50 rounded-2xl shadow-sm mb-4">
          <p className="text-red-400 font-medium">{error}</p>
        </div>
      )}
        {/* Contenedor del chat que crece para ocupar el espacio disponible */}
      <div className="h-100 overflow-y-auto bg-gray-700/60 backdrop-blur-sm border border-gray-600/50 rounded-2xl p-4 mb-4 shadow-inner min-h-0">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 bg-gradient-to-r from-blue-800/50 to-indigo-800/50 rounded-full flex items-center justify-center mb-4">
              <span className="text-2xl">💬</span>
            </div>
            <p className="text-gray-400 font-medium">Inicia la conversación...</p>
            <p className="text-gray-500 text-sm mt-1">Haz una pregunta sobre tus datos de red</p>
          </div>
        )}
        {messages.map((msg, index) => (
          <div key={index} className={`mb-3 ${msg.role === 'user' ? 'flex justify-end' : 'flex justify-start'}`}>
            <div className={`max-w-[80%] p-3 rounded-2xl shadow-sm ${
              msg.role === 'user' 
                ? 'bg-gradient-to-r from-fuchsia-400 to-purple-300 text-white ml-auto' 
                : 'bg-gray-800/80 backdrop-blur-sm text-gray-300 border border-gray-600/50'
            }`}>
              <div className="flex items-start gap-2">
                {msg.role === 'assistant' && (
                  <div className="w-6 h-6 bg-gradient-to-r from-emerald-400 to-teal-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-white text-xs">🤖</span>
                  </div>
                )}
                <div className="flex-1">
                  <p className="text-sm leading-relaxed whitespace-pre-line">{msg.content}</p>
                </div>
              </div>
            </div>
          </div>
        ))}        <div ref={messagesEndRef} />
      </div>
      
      {/* Input form fijo en la parte inferior */}
      <form onSubmit={handleSendMessage} className="flex gap-2">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder={sessionId ? `Pregunta sobre la sesión ${sessionId}...` : "Pregunta algo..."}
          className="flex-1 p-4 bg-gray-700/80 backdrop-blur-sm border border-gray-600 rounded-2xl text-gray-300 focus:ring-1 focus:ring-pink-500 focus:border-pink-400 transition-all duration-200 shadow-sm hover:shadow-md disabled:opacity-50 focus:outline-none"
          disabled={loading}
        />
        <button 
          type="submit"
          className={`px-6 py-4 rounded-2xl font-semibold text-white shadow-lg transition-all duration-300 transform hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none focus:outline-none ${
            loading 
              ? 'bg-gradient-to-r from-amber-400 to-orange-500' 
              : 'bg-gradient-to-r from-pink-400 to-purple-500 hover:from-pink-500 hover:to-purple-600 hover:shadow-xl'
          }`}
          disabled={loading || !inputMessage.trim()}
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <span className="animate-spin">⚙️</span>
              Enviando...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <span>📤</span>
              Enviar
            </span>
          )}
        </button>
      </form>
      
      {/* Sistema de mensajes centrado debajo del input */}
      {systemMessage && systemMessage.type === 'info' && (systemMessage.content.startsWith('Preferencia cambiada a:') ||
        systemMessage.content === 'Chat reiniciado' ||
        systemMessage.content === 'No hay preguntas en el historial' ||
        systemMessage.content === 'Historial de preguntas del usuario borrado') && (
        <div className="flex justify-center mt-4">
          <div className="px-4 py-2 rounded-2xl font-medium text-purple-300 bg-gradient-to-r from-purple-900/50 to-pink-900/50 border border-purple-700/50 shadow-sm text-sm">
            {systemMessage.content}
          </div>
        </div>
      )}
    </div>
  );
}

export default ChatInterface;
