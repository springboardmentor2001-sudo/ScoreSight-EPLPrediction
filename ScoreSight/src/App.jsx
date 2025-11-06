import React, { useState, useEffect } from 'react';
import Navbar from './components/Layout/Navbar';
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
// import ModelPredict from './pages/ModelPredict';
import UserInputPredict from './pages/UserInputPredict';
import AIPredictor from './components/AIPredictor';
import GeminiChatbot from './components/GeminiChatbot';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [currentPage, setCurrentPage] = useState('home');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetchUserProfile(token);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUserProfile = async (token) => {
    try {
      const response = await fetch('http://localhost:5000/api/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
      } else {
        localStorage.removeItem('token');
      }
    } catch (error) {
      console.error('Error fetching user profile:', error);
      localStorage.removeItem('token');
    } finally {
      setLoading(false);
    }
  };

  const login = (userData, token) => {
    setUser(userData);
    localStorage.setItem('token', token);
    setCurrentPage('home');
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('token');
    setCurrentPage('home');
  };

  const showLogin = () => {
    setCurrentPage('login');
  };

  const showSignup = () => {
    setCurrentPage('signup');
  };

  const renderPage = () => {
    if (!user) {
      if (currentPage === 'login') return <Login onLogin={login} />;
      if (currentPage === 'signup') return <Signup onLogin={login} />;
      return <Login onLogin={login} />;
    }

    switch (currentPage) {
      case 'home':
        return <Home user={user} onNavigate={setCurrentPage} />;
      case 'user-input':
        return <UserInputPredict />;
      // case 'model-predict':
        // return <ModelPredict />;
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