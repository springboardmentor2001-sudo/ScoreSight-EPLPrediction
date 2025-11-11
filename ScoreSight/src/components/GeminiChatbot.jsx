import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Trash2, X, MessageCircle } from 'lucide-react';

const GeminiChatbot = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);

  const API_URL = 'http://localhost:5000';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize with welcome message
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          id: 1,
          text: "👋 Hello! I'm your EPL Match Predictor assistant powered by Gemini AI.\n\nI can help you with:\n• Match predictions & analysis\n• Team performance insights\n• Player statistics\n• Historical data\n• Football tactics\n\nWhat would you like to know?",
          sender: 'bot',
          timestamp: new Date()
        }
      ]);
    }
  }, []);

  const sendMessage = async () => {
    if (!inputMessage.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);
    setError('');

    try {
      console.log('Sending message to:', `${API_URL}/chat`);
      console.log('Current user from localStorage:', localStorage.getItem('user'));

      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          message: inputMessage,
          conversation: messages.map(msg => ({
            sender: msg.sender,
            text: msg.text
          })).slice(-10)
        })
      });

      console.log('Response status:', response.status);

      if (response.status === 401) {
        throw new Error('Please login to use the chatbot');
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(errorData.error || `Server error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Response data:', data);

      if (data.response) {
        const botMessage = {
          id: Date.now() + 1,
          text: data.response,
          sender: 'bot',
          timestamp: new Date(),
          fallback: data.fallback || false
        };
        setMessages(prev => [...prev, botMessage]);
      } else {
        throw new Error('No response from server');
      }

    } catch (error) {
      console.error('Chat error:', error);
      
      let errorText = error.message;
      
      if (errorText.includes('login')) {
        errorText = "⚠️ Please login to use the chatbot.\n\nYou need to be authenticated to access the AI assistant.";
      } else if (errorText.includes('fetch')) {
        errorText = "⚠️ Cannot connect to server.\n\nPlease make sure:\n• Flask server is running on port 5000\n• You're logged in to the application";
      }

      const errorMessage = {
        id: Date.now() + 1,
        text: errorText,
        sender: 'bot',
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
      setError(errorText);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: 1,
        text: "👋 Hello! I'm your EPL Match Predictor assistant powered by Gemini AI.\n\nI can help you with:\n• Match predictions & analysis\n• Team performance insights\n• Player statistics\n• Historical data\n• Football tactics\n\nWhat would you like to know?",
        sender: 'bot',
        timestamp: new Date()
      }
    ]);
    setError('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <>
      {/* Floating Chat Button */}
      {!isOpen && (
        <button
  onClick={() => setIsOpen(true)}
  className="fixed bottom-6 right-6 w-16 h-16 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white rounded-full shadow-2xl flex items-center justify-center transition-all duration-300 hover:scale-110 z-50 group"
  aria-label="Open chat"
>
  <Bot size={28} className="group-hover:scale-110 transition-transform" />
</button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-[420px] h-[650px] bg-slate-900 rounded-2xl shadow-2xl border border-slate-700 flex flex-col z-50 animate-fade-in">
          {/* Header */}
          <div className="bg-gradient-to-r from-cyan-600 via-blue-600 to-purple-600 px-5 py-4 rounded-t-2xl flex justify-between items-center">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-lg">
                <Bot size={20} className="text-blue-600" />
              </div>
              <div>
                <h3 className="text-white font-bold text-lg">EPL AI Assistant</h3>
                <p className="text-cyan-100 text-xs flex items-center gap-1">
                  <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                  Online • Powered by Gemini
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={clearChat}
                className="p-2 text-white hover:bg-white/20 rounded-lg transition-colors"
                title="Clear chat"
                aria-label="Clear chat"
              >
                <Trash2 size={18} />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 text-white hover:bg-white/20 rounded-lg transition-colors"
                aria-label="Close chat"
              >
                <X size={18} />
              </button>
            </div>
          </div>

          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-slate-900 to-slate-800">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'} animate-slide-in`}
              >
                {/* Avatar */}
                <div
                  className={`w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg ${
                    message.sender === 'user' 
                      ? 'bg-gradient-to-r from-blue-500 to-blue-600' 
                      : 'bg-gradient-to-r from-cyan-500 to-blue-500'
                  }`}
                >
                  {message.sender === 'user' ? (
                    <User size={18} className="text-white" />
                  ) : (
                    <Bot size={18} className="text-white" />
                  )}
                </div>

                {/* Message Bubble */}
                <div className="flex flex-col max-w-[75%]">
                  <div
                    className={`rounded-2xl px-4 py-3 shadow-lg ${
                      message.sender === 'user'
                        ? 'bg-gradient-to-r from-blue-600 to-blue-500 text-white rounded-br-none'
                        : message.isError
                        ? 'bg-red-900/50 text-red-200 border border-red-700 rounded-bl-none'
                        : 'bg-slate-700 text-slate-100 rounded-bl-none border border-slate-600'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.text}</p>
                    {message.fallback && (
                      <p className="text-xs mt-2 text-yellow-300 bg-yellow-900/30 px-2 py-1 rounded">
                        ⚠️ Fallback mode
                      </p>
                    )}
                  </div>
                  <p
                    className={`text-xs mt-1 px-2 ${
                      message.sender === 'user' ? 'text-right text-slate-400' : 'text-slate-500'
                    }`}
                  >
                    {formatTime(message.timestamp)}
                  </p>
                </div>
              </div>
            ))}

            {/* Loading Indicator */}
            {loading && (
              <div className="flex gap-3 animate-slide-in">
                <div className="w-9 h-9 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 flex items-center justify-center flex-shrink-0 shadow-lg">
                  <Bot size={18} className="text-white" />
                </div>
                <div className="bg-slate-700 text-slate-200 rounded-2xl rounded-bl-none px-4 py-3 border border-slate-600">
                  <div className="flex gap-1.5">
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 border-t border-slate-700 bg-slate-800">
            <div className="flex gap-2 items-end">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me about EPL matches, teams, predictions..."
                className="flex-1 bg-slate-700 border border-slate-600 rounded-xl px-4 py-3 text-white text-sm placeholder-slate-400 resize-none focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all"
                rows="2"
                disabled={loading}
                style={{ maxHeight: '120px' }}
              />
              <button
                onClick={sendMessage}
                disabled={loading || !inputMessage.trim()}
                className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 disabled:from-slate-600 disabled:to-slate-600 disabled:cursor-not-allowed text-white rounded-xl w-12 h-12 flex items-center justify-center transition-all shadow-lg hover:shadow-cyan-500/50 disabled:shadow-none flex-shrink-0"
                aria-label="Send message"
              >
                <Send size={18} />
              </button>
            </div>
            <div className="mt-2 flex items-center justify-between">
              <p className="text-slate-400 text-xs">
                💡 Ask about teams, predictions, or analysis
              </p>
              <p className="text-slate-500 text-xs">
                Press Enter to send
              </p>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes slide-in {
          from {
            opacity: 0;
            transform: translateX(-10px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }

        .animate-fade-in {
          animation: fade-in 0.3s ease-out;
        }

        .animate-slide-in {
          animation: slide-in 0.3s ease-out;
        }
      `}</style>
    </>
  );
};

export default GeminiChatbot;