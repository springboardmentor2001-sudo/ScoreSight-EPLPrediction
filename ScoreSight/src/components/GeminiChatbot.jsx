import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Trash2 } from 'lucide-react';

const GeminiChatbot = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const messagesEndRef = useRef(null);

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
          text: "Hello! I'm your EPL Match Predictor assistant. I can help you with match predictions, team analysis, and football insights. How can I assist you today?",
          sender: 'bot',
          timestamp: new Date()
        }
      ]);
    }
  }, []);

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          conversation: messages.slice(-10) // Send last 10 messages for context
        })
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      
      const botMessage = {
        id: Date.now() + 1,
        text: data.response,
        sender: 'bot',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: "I'm sorry, I'm having trouble connecting to the server. Please make sure the Flask server is running.",
        sender: 'bot',
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: 1,
        text: "Hello! I'm your EPL Match Predictor assistant. I can help you with match predictions, team analysis, and football insights. How can I assist you today?",
        sender: 'bot',
        timestamp: new Date()
      }
    ]);
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
      {/* Chat Widget */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 w-16 h-16 bg-cyan-500 hover:bg-cyan-600 text-white rounded-full shadow-2xl flex items-center justify-center transition-all duration-300 hover:scale-110 z-50"
        >
          <Bot size={24} />
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-96 h-[600px] bg-slate-800 rounded-2xl shadow-2xl border border-slate-700 flex flex-col z-50">
          {/* Header */}
          <div className="bg-gradient-to-r from-cyan-600 to-blue-600 px-4 py-3 rounded-t-2xl flex justify-between items-center">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
                <Bot size={16} className="text-cyan-600" />
              </div>
              <div>
                <h3 className="text-white font-bold">EPL Assistant</h3>
                <p className="text-cyan-100 text-xs">Powered by Gemini AI</p>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={clearChat}
                className="p-1 text-white hover:text-cyan-200 transition-colors"
                title="Clear chat"
              >
                <Trash2 size={16} />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="w-6 h-6 text-white hover:text-cyan-200 transition-colors flex items-center justify-center"
              >
                ×
              </button>
            </div>
          </div>

          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-900/50">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
              >
                {/* Avatar */}
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                    message.sender === 'user' 
                      ? 'bg-blue-500' 
                      : 'bg-gradient-to-r from-cyan-500 to-blue-500'
                  }`}
                >
                  {message.sender === 'user' ? (
                    <User size={16} className="text-white" />
                  ) : (
                    <Bot size={16} className="text-white" />
                  )}
                </div>

                {/* Message Bubble */}
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-2 ${
                    message.sender === 'user'
                      ? 'bg-blue-600 text-white rounded-br-none'
                      : message.isError
                      ? 'bg-red-900/50 text-red-200 border border-red-700'
                      : 'bg-slate-700 text-slate-200 rounded-bl-none'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.text}</p>
                  <p
                    className={`text-xs mt-1 ${
                      message.sender === 'user' ? 'text-blue-200' : 'text-slate-400'
                    }`}
                  >
                    {formatTime(message.timestamp)}
                  </p>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 flex items-center justify-center flex-shrink-0">
                  <Bot size={16} className="text-white" />
                </div>
                <div className="bg-slate-700 text-slate-200 rounded-2xl rounded-bl-none px-4 py-2">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 border-t border-slate-700 bg-slate-800">
            <div className="flex gap-2">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about matches, teams, or predictions..."
                className="flex-1 bg-slate-700 border border-slate-600 rounded-xl px-3 py-2 text-white text-sm placeholder-slate-400 resize-none focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
                rows="1"
                style={{ minHeight: '40px', maxHeight: '120px' }}
              />
              <button
                onClick={sendMessage}
                disabled={loading || !inputMessage.trim()}
                className="bg-cyan-500 hover:bg-cyan-600 disabled:bg-slate-600 disabled:cursor-not-allowed text-white rounded-xl w-10 h-10 flex items-center justify-center transition-colors"
              >
                <Send size={16} />
              </button>
            </div>
            <p className="text-slate-400 text-xs mt-2 text-center">
              Ask about EPL teams, match predictions, or football analysis
            </p>
          </div>
        </div>
      )}
    </>
  );
};

export default GeminiChatbot;