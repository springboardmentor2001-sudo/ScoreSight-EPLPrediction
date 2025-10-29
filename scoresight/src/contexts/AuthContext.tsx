import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, AuthContextType, LoginFormData, SignupFormData } from '../types/auth';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // Check if user is logged in on app start
    const savedUser = localStorage.getItem('scoresight_user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    // Simulate API call - replace with actual authentication
    return new Promise((resolve) => {
      setTimeout(() => {
        if (email && password) {
          const userData: User = {
            id: '1',
            email,
            firstName: 'John',
            lastName: 'Doe'
          };
          setUser(userData);
          localStorage.setItem('scoresight_user', JSON.stringify(userData));
          resolve(true);
        } else {
          resolve(false);
        }
      }, 1000);
    });
  };

  const signup = async (email: string, password: string, firstName: string, lastName: string): Promise<boolean> => {
    // Simulate API call - replace with actual authentication
    return new Promise((resolve) => {
      setTimeout(() => {
        if (email && password && firstName && lastName) {
          const userData: User = {
            id: '1',
            email,
            firstName,
            lastName
          };
          setUser(userData);
          localStorage.setItem('scoresight_user', JSON.stringify(userData));
          resolve(true);
        } else {
          resolve(false);
        }
      }, 1000);
    });
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('scoresight_user');
  };

  const value: AuthContextType = {
    user,
    login,
    signup,
    logout,
    isAuthenticated: !!user
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