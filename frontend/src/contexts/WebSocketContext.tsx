import React, { createContext, useContext, useEffect, useState } from 'react';
import websocketService from '../services/websocket';

interface WebSocketContextType {
  isConnected: boolean;
  sendTask: (data: any) => void;
  sendConfirmation: (confirmed: boolean, data?: any) => void;
  lastResult: any | null;
  confirmationData: any | null;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastResult, setLastResult] = useState<any | null>(null);
  const [confirmationData, setConfirmationData] = useState<any | null>(null);

  useEffect(() => {
    const handleConnect = () => setIsConnected(true);
    const handleDisconnect = () => setIsConnected(false);
    const handleResults = (results: any) => setLastResult(results);
    const handleConfirmation = (data: any) => setConfirmationData(data);

    websocketService.on('connected', handleConnect);
    websocketService.on('disconnected', handleDisconnect);
    websocketService.on('results', handleResults);
    websocketService.on('confirmation', handleConfirmation);

    return () => {
      websocketService.off('connected', handleConnect);
      websocketService.off('disconnected', handleDisconnect);
      websocketService.off('results', handleResults);
      websocketService.off('confirmation', handleConfirmation);
      websocketService.disconnect();
    };
  }, []);

  const sendTask = (data: any) => {
    websocketService.sendTask(data);
  };

  const sendConfirmation = (confirmed: boolean, data?: any) => {
    websocketService.sendConfirmation(confirmed, data);
    setConfirmationData(null); // Clear the confirmation data after responding
  };

  const value = {
    isConnected,
    sendTask,
    sendConfirmation,
    lastResult,
    confirmationData,
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
}; 