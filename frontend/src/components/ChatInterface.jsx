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
      setSystemMessage({ type: 'info', content: 'Chat reiniciado.' });
      return;
    }
    if (cmd === 'historial') {
      if (userQuestionsHistory.length === 0) {
        setSystemMessage({ type: 'info', content: 'No hay preguntas en el historial.' });
      } else {
        setSystemMessage({ type: 'historial', content: 'Historial de preguntas:\n' + userQuestionsHistory.map((q, i) => `${i + 1}. ${q}`).join('\n') });
      }
      return;
    }
    if (cmd === 'borrar_historial') {
      setUserQuestionsHistory([]);
      setSystemMessage({ type: 'info', content: 'Historial de preguntas del usuario borrado.' });
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
  };

  return (
    <div className="mt-6 border-t pt-4 rounded-2xl shadow-md" style={{ background: '#393E46' }}>
      <h3 className="text-lg font-semibold mb-3 text-[#DFD0B8]">Chat con IA</h3>
      {systemMessage && (
        <div className={`flex justify-center mb-4`}>
          {systemMessage.type === 'info' && systemMessage.content.startsWith('Preferencia cambiada a:') ? (
            <div className="max-w-xl text-center px-4 py-2 rounded-xl font-medium text-[#e9d7a5] bg-transparent">
              {systemMessage.content}
            </div>
          ) : (
            <div
              className={`max-w-xl text-center px-4 py-2 rounded-xl font-medium whitespace-pre-line
                ${systemMessage.type === 'historial' ? 'bg-[#e9d7a5] text-[#222831]' : 'bg-[#948979] text-[#222831]'}`}
            >
              {systemMessage.content}
            </div>
          )}
        </div>
      )}
      <div className="mb-2 flex flex-wrap gap-2">
        <span className="text-sm text-[#DFD0B8]">Preferencia actual:</span>
        <span className="font-bold text-[#948979]">{userPreference}</span>
        <button type="button" className={`px-2 py-1 rounded text-xs ${userPreference==='corto' ? 'bg-[#948979] text-[#222831]' : 'bg-[#DFD0B8] text-[#222831]'}`} onClick={() => handleCommand('corto')}>/corto</button>
        <button type="button" className={`px-2 py-1 rounded text-xs ${userPreference==='normal' ? 'bg-[#948979] text-[#222831]' : 'bg-[#DFD0B8] text-[#222831]'}`} onClick={() => handleCommand('normal')}>/normal</button>
        <button type="button" className={`px-2 py-1 rounded text-xs ${userPreference==='detallado' ? 'bg-[#948979] text-[#222831]' : 'bg-[#DFD0B8] text-[#222831]'}`} onClick={() => handleCommand('detallado')}>/detallado</button>
        <button type="button" className="px-2 py-1 rounded text-xs bg-[#e9d7a5] text-[#222831]" onClick={() => handleCommand('reiniciar')}>/reiniciar</button>
        <button type="button" className="px-2 py-1 rounded text-xs bg-[#393E46] text-[#DFD0B8]" onClick={() => handleCommand('historial')}>/historial</button>
        <button type="button" className="px-2 py-1 rounded text-xs bg-red-400 text-white" onClick={() => handleCommand('borrar_historial')}>/borrar_historial</button>
      </div>
      {error && <p className="text-red-400 mb-2">{error}</p>}
      <div className="h-64 overflow-y-auto border rounded p-2 mb-3 bg-[#222831]">
        {messages.length === 0 && <p className="text-[#DFD0B8]/70 text-center mt-4">Inicia la conversación...</p>}
        {messages.map((msg, index) => (
          <div key={index} className={`mb-2 ${msg.role === 'user' ? 'text-right' : msg.role === 'assistant' ? 'text-left' : 'text-center'}`}>
            <span 
              className={`inline-block p-2 rounded-lg ${msg.role === 'user' ? 'bg-[#948979] text-[#222831]' : msg.role === 'assistant' ? 'bg-[#DFD0B8] text-[#222831]' : 'bg-[#e9d7a5] text-[#222831]'}`}
            >
              {msg.content}
            </span>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={handleSendMessage} className="flex items-center gap-0">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder={sessionId ? `Pregunta sobre la sesión ${sessionId}...` : "Pregunta algo..."}
          className="flex-grow border rounded-l p-2 bg-[#222831] text-[#DFD0B8] focus:outline-none focus:ring-2 focus:ring-[#e9d7a5] h-12"
          disabled={loading}
        />
        <button 
          type="submit"
          className="bg-[#948979] text-[#222831] px-8 py-3 rounded-r hover:bg-[#e9d7a5] disabled:opacity-50 font-semibold h-12"
          style={{ minWidth: '110px' }}
          disabled={loading || !inputMessage.trim()}
        >
          {loading ? 'Enviando...' : 'Enviar'}
        </button>
      </form>
      <div className="flex justify-center mt-4">
        <button 
          onClick={handleClearChat}
          className="px-6 py-2 rounded-xl bg-[#e9d7a5] text-[#222831] font-semibold shadow hover:bg-[#948979] transition-colors"
        >
          Limpiar Chat
        </button>
      </div>
    </div>
  );
}

export default ChatInterface;
