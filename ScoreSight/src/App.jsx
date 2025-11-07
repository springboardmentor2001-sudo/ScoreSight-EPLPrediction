import React, { useState, useEffect } from 'react';
import Navbar from './components/Layout/Navbar';
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import UserInputPredict from './pages/UserInputPredict';
import AIPredictor from './components/AIPredictor';
import GeminiChatbot from './components/GeminiChatbot';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [currentPage, setCurrentPage] = useState('home');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/check-auth', {
        method: 'GET',
        credentials: 'include' // Important for session cookies
      });
      
      const data = await response.json();
      
      if (data.authenticated && data.user) {
        setUser(data.user);
        // Store user info in localStorage for quick access
        localStorage.setItem('user', JSON.stringify(data.user));
      } else {
        setUser(null);
        localStorage.removeItem('user');
      }
    } catch (error) {
      console.error('Error checking auth status:', error);
      setUser(null);
      localStorage.removeItem('user');
    } finally {
      setLoading(false);
    }
  };

  const login = async (userData, token) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
    if (token) {
      localStorage.setItem('token', token);
    }
    setCurrentPage('home');
    
    // Verify the login worked
    await checkAuthStatus();
  };

  const logout = async () => {
    try {
      await fetch('http://localhost:5000/api/logout', {
        method: 'POST',
        credentials: 'include'
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      localStorage.removeItem('user');
      localStorage.removeItem('token');
      setCurrentPage('home');
    }
  };

  const showLogin = () => {
    setCurrentPage('login');
  };

  const showSignup = () => {
    setCurrentPage('signup');
  };

  const renderPage = () => {
    // If no user, show authentication pages
    if (!user) {
      switch (currentPage) {
        case 'login':
          return <Login onLogin={login} />;
        case 'signup':
          return <Signup onLogin={login} />;
        default:
          return <Login onLogin={login} />;
      }
    }

    // If user is authenticated, show app pages
    switch (currentPage) {
      case 'home':
        return <Home user={user} onNavigate={setCurrentPage} />;
      case 'user-input':
        return <UserInputPredict />;
      case 'ai-predictor':
        return <AIPredictor />;
      default:
        return <Home user={user} onNavigate={setCurrentPage} />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800">
      <Navbar 
        user={user} 
        onLogout={logout} 
        currentPage={currentPage}
        onNavigate={setCurrentPage}
        onShowLogin={showLogin}
        onShowSignup={showSignup}
      />
      
      <main className="w-full">
        {renderPage()}
      </main>

      <GeminiChatbot />
    </div>
  );
}

export default App;