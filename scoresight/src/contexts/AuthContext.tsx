import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, AuthContextType } from '../types/auth';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

const API_BASE_URL = 'http://localhost:8000';

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [authMessage, setAuthMessage] = useState<string>('');

  useEffect(() => {
    checkExistingAuth();
  }, []);

  const checkExistingAuth = async () => {
    try {
      const token = localStorage.getItem('scoresight_token');
      const userData = localStorage.getItem('scoresight_user');

      if (token && userData) {
        // Try to verify the token
        try {
          const response = await fetch(`${API_BASE_URL}/api/auth/check`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          
          if (response.ok) {
            const data = await response.json();
            if (data.authenticated && data.user) {
              setUser(data.user);
              setAuthMessage('Welcome back! Ready for some predictions? 🎯');
              return;
            }
          }
        } catch (error) {
          console.log('Token validation failed');
        }
      }
      // Clear if no valid token
      clearAuthData();
    } catch (error) {
      console.error('Auth check failed:', error);
      clearAuthData();
    } finally {
      setLoading(false);
    }
  };

  const clearAuthData = () => {
    localStorage.removeItem('scoresight_token');
    localStorage.removeItem('scoresight_user');
    setUser(null);
  };

  const saveAuthData = (userData: User) => {
    localStorage.setItem('scoresight_token', userData.token);
    localStorage.setItem('scoresight_user', JSON.stringify(userData));
    setUser(userData);
  };

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      setLoading(true);
      setAuthMessage('Checking your credentials... 🤔');
      
      console.log('Attempting login for:', email);
      
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          email: email,
          password: password
        }),
      });

      console.log('Login response status:', response.status);

      if (response.ok) {
        const data = await response.json();
        console.log('Login success:', data);
        
        if (data.success && data.user) {
          saveAuthData(data.user);
          setAuthMessage('Welcome back! Time to make some winning predictions! 🏆');
          return true;
        }
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.log('Login error:', errorData);
        
        if (response.status === 401) {
          setAuthMessage('Oops! Wrong email or password. Are you sure you\'re not a robot? 🤖');
        } else {
          setAuthMessage('Login failed. Even the best strikers miss sometimes! Try again? ⚽');
        }
      }
      return false;
    } catch (error: any) {
      console.error('Login failed:', error);
      setAuthMessage('Network error. Check your connection and try again! 📡');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const signup = async (email: string, password: string, firstName: string, lastName: string): Promise<boolean> => {
    try {
      setLoading(true);
      setAuthMessage('Creating your account... 🚀');
      
      console.log('Attempting signup for:', email, firstName, lastName);
      
      const response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          email: email,
          password: password,
          firstName: firstName,
          lastName: lastName
        }),
      });

      console.log('Signup response status:', response.status);

      if (response.ok) {
        const data = await response.json();
        console.log('Signup success:', data);
        
        if (data.success && data.user) {
          saveAuthData(data.user);
          setAuthMessage('Welcome to Scoresight! Get ready for some winning predictions! 🎯');
          return true;
        }
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.log('Signup error:', errorData);
        
        if (response.status === 400) {
          setAuthMessage('You\'re already part of our winning team! Try logging in instead. 🏆');
        } else if (response.status === 422) {
          setAuthMessage('Check your info - even VAR would flag this one! 📋');
        } else {
          setAuthMessage('Signup failed. Don\'t worry, even Messi misses penalties sometimes! Try again? ⚽');
        }
      }
      return false;
    } catch (error: any) {
      console.error('Signup failed:', error);
      setAuthMessage('Network error. Check your connection and try again! 📡');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setAuthMessage('See you next time! Hope you made some winning predictions! 👋');
    clearAuthData();
  };

  const clearMessage = () => {
    setAuthMessage('');
  };

  const value: AuthContextType = {
    user,
    login,
    signup,
    logout,
    isAuthenticated: !!user,
    loading,
    authMessage,
    clearMessage
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};