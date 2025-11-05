export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  token: string;
  created_at?: string;
}

export interface LoginFormData {
  email: string;
  password: string;
}

export interface SignupFormData {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<boolean>;
  signup: (email: string, password: string, firstName: string, lastName: string) => Promise<boolean>;
  logout: () => void;
  isAuthenticated: boolean;
  loading: boolean;
  authMessage: string;
  clearMessage: () => void;
}