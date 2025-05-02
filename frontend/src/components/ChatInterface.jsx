import React, { useState, useEffect, useRef } from 'react';
import { postChatMessage, clearChatHistory } from '../services/api';

function ChatInterface({ sessionId }) {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null); // Ref to scroll to bottom

  // Scroll to bottom whenever messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || loading) return;

    const userMessage = { role: 'user', content: inputMessage };
    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);
    setError(null);

    try {
      // Pass sessionId if available
      const response = await postChatMessage(userMessage.content, sessionId);
      const assistantMessage = { role: 'assistant', content: response.data.response };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error("Error sending chat message:", err);
      setError("Error al enviar el mensaje o recibir la respuesta de la IA.");
      // Optionally remove the user message if the API call failed
      // setMessages(prev => prev.slice(0, -1)); 
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
      console.error("Error clearing chat history:", err);
      setError("Error al limpiar el historial del chat.");
    }
  };

  return (
    <div className="mt-6 border-t pt-4">
      <h3 className="text-lg font-semibold mb-3">Chat con IA</h3>
      
      {error && <p className="text-red-500 mb-2">{error}</p>}

      <div className="h-64 overflow-y-auto border rounded p-2 mb-3 bg-gray-50">
        {messages.length === 0 && <p className="text-gray-500 text-center mt-4">Inicia la conversación...</p>}
        {messages.map((msg, index) => (
          <div key={index} className={`mb-2 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
            <span 
              className={`inline-block p-2 rounded-lg ${msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'}`}
            >
              {msg.content}
            </span>
          </div>
        ))}
        {/* Element to scroll to */} 
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
