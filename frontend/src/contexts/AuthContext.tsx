import React, { createContext, useContext, useState, useEffect } from 'react';

// Define user type
interface User {
  id: string;
  name: string;
  email: string;
}

// Define auth context type
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string, remember: boolean) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  forgotPassword: (email: string) => Promise<void>;
}

// Create context with default values
const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  login: async () => {},
  register: async () => {},
  logout: async () => {},
  forgotPassword: async () => {},
});

// Hook to use auth context
export const useAuth = () => useContext(AuthContext);

// Provider component
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Check if user is already logged in on mount
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        // In a real app, this would verify token with backend
        const storedUser = localStorage.getItem('cloudPilotUser');
        
        if (storedUser) {
          setUser(JSON.parse(storedUser));
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        // Clear potentially corrupt data
        localStorage.removeItem('cloudPilotUser');
        localStorage.removeItem('cloudPilotToken');
      } finally {
        setIsLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  // Login function
  const login = async (email: string, password: string, remember: boolean) => {
    setIsLoading(true);
    
    try {
      // In a real app, this would call your API
      // Mock successful login after delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Create a mock user object (your API would return a real user)
      const userData: User = {
        id: 'user-' + Date.now(),
        name: email.split('@')[0], // Use part of email as name
        email,
      };
      
      // Store auth data
      setUser(userData);
      
      if (remember) {
        localStorage.setItem('cloudPilotUser', JSON.stringify(userData));
        localStorage.setItem('cloudPilotToken', 'mock-jwt-token-' + Date.now());
      }
    } catch (error) {
      console.error('Login failed:', error);
      throw new Error('Invalid credentials');
    } finally {
      setIsLoading(false);
    }
  };

  // Register function
  const register = async (name: string, email: string, password: string) => {
    setIsLoading(true);
    
    try {
      // In a real app, this would call your API
      // Mock successful registration after delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Create a mock user object (your API would return a real user)
      const userData: User = {
        id: 'user-' + Date.now(),
        name,
        email,
      };
      
      // Store auth data
      setUser(userData);
      localStorage.setItem('cloudPilotUser', JSON.stringify(userData));
      localStorage.setItem('cloudPilotToken', 'mock-jwt-token-' + Date.now());
    } catch (error) {
      console.error('Registration failed:', error);
      throw new Error('Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  // Logout function
  const logout = async () => {
    setIsLoading(true);
    
    try {
      // In a real app, this might call your API to invalidate the token
      // Clear stored data
      localStorage.removeItem('cloudPilotUser');
      localStorage.removeItem('cloudPilotToken');
      setUser(null);
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Forgot password function
  const forgotPassword = async (email: string) => {
    try {
      // In a real app, this would call your API
      await new Promise(resolve => setTimeout(resolve, 1000));
      // Success is handled by the calling component
    } catch (error) {
      console.error('Password reset request failed:', error);
      throw new Error('Failed to send password reset email');
    }
  };

  // Create context value
  const contextValue: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    forgotPassword,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext; 