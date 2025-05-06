import React, { useState, useEffect, useRef } from 'react';
import { postChatMessage, clearChatHistory } from '../services/api';

function ChatInterface({ sessionId, dbFile }) {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [userPreference, setUserPreference] = useState('corto'); // corto, normal, detallado
  const [userQuestionsHistory, setUserQuestionsHistory] = useState([]);
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
      return;
    }
    if (cmd === 'historial') {
      if (userQuestionsHistory.length === 0) {
        setMessages((prev) => [...prev, { role: 'system', content: 'No hay preguntas en el historial.' }]);
      } else {
        setMessages((prev) => [...prev, { role: 'system', content: 'Historial de preguntas:\n' + userQuestionsHistory.map((q, i) => `${i + 1}. ${q}`).join('\n') }]);
      }
      return;
    }
    if (cmd === 'borrar_historial') {
      setUserQuestionsHistory([]);
      setMessages((prev) => [...prev, { role: 'system', content: 'Historial de preguntas del usuario borrado.' }]);
      return;
    }
    if (["corto", "normal", "detallado"].includes(cmd)) {
      setUserPreference(cmd);
      setMessages((prev) => [...prev, { role: 'system', content: `Preferencia cambiada a: ${cmd}` }]);
      return;
    }
    setMessages((prev) => [...prev, { role: 'system', content: 'Comando no reconocido. Usa /corto, /normal, /detallado, /reiniciar, /historial o /borrar_historial.' }]);
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
  };

  return (
    <div className="mt-6 border-t pt-4">
      <h3 className="text-lg font-semibold mb-3">Chat con IA</h3>
      <div className="mb-2 flex flex-wrap gap-2">
        <span className="text-sm">Preferencia actual:</span>
        <span className="font-bold text-blue-700">{userPreference}</span>
        <button type="button" className={`px-2 py-1 rounded text-xs ${userPreference==='corto' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`} onClick={() => handleCommand('corto')}>/corto</button>
        <button type="button" className={`px-2 py-1 rounded text-xs ${userPreference==='normal' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`} onClick={() => handleCommand('normal')}>/normal</button>
        <button type="button" className={`px-2 py-1 rounded text-xs ${userPreference==='detallado' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`} onClick={() => handleCommand('detallado')}>/detallado</button>
        <button type="button" className="px-2 py-1 rounded text-xs bg-yellow-100" onClick={() => handleCommand('reiniciar')}>/reiniciar</button>
        <button type="button" className="px-2 py-1 rounded text-xs bg-gray-100" onClick={() => handleCommand('historial')}>/historial</button>
        <button type="button" className="px-2 py-1 rounded text-xs bg-red-100" onClick={() => handleCommand('borrar_historial')}>/borrar_historial</button>
      </div>
      {error && <p className="text-red-500 mb-2">{error}</p>}
      <div className="h-64 overflow-y-auto border rounded p-2 mb-3 bg-gray-50">
        {messages.length === 0 && <p className="text-gray-500 text-center mt-4">Inicia la conversación...</p>}
        {messages.map((msg, index) => (
          <div key={index} className={`mb-2 ${msg.role === 'user' ? 'text-right' : msg.role === 'assistant' ? 'text-left' : 'text-center'}`}>
            <span 
              className={`inline-block p-2 rounded-lg ${msg.role === 'user' ? 'bg-blue-500 text-white' : msg.role === 'assistant' ? 'bg-gray-200 text-gray-800' : 'bg-yellow-100 text-gray-800'}`}
            >
              {msg.content}
            </span>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={handleSendMessage} className="flex items-center">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder={sessionId ? `Pregunta sobre la sesión ${sessionId}...` : "Pregunta algo..."}
          className="flex-grow border rounded-l p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={loading}
        />
        <button 
          type="submit"
          className="bg-blue-500 text-white px-4 py-2 rounded-r hover:bg-blue-600 disabled:opacity-50"
          disabled={loading || !inputMessage.trim()}
        >
          {loading ? 'Enviando...' : 'Enviar'}
        </button>
      </form>
      <button 
        onClick={handleClearChat}
        className="mt-2 text-sm text-gray-500 hover:text-red-600"
      >
        Limpiar Chat
      </button>
    </div>
  );
}

export default ChatInterface;
