import { EventEmitter } from 'events';

interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

class WebSocketService extends EventEmitter {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10; // Increased from 5 to 10
  private reconnectTimeout = 1000; // Start with 1 second
  private url: string;
  private isConnecting = false;

  constructor() {
    super();
    // Use environment variables with fallbacks for local development
    const backendHost = process.env.REACT_APP_BACKEND_HOST || 'localhost';
    const backendPort = process.env.REACT_APP_BACKEND_PORT || '8000';
    
    // Log the environment variables for debugging
    console.log('Environment variables:', {
      REACT_APP_BACKEND_HOST: process.env.REACT_APP_BACKEND_HOST,
      REACT_APP_BACKEND_PORT: process.env.REACT_APP_BACKEND_PORT,
      hostname: window.location.hostname
    });
    
    // Use the environment variables for the WebSocket URL
    this.url = `ws://${backendHost}:${backendPort}/ws/ai-assist`;
    console.log('WebSocket URL:', this.url);
    
    // Connect with a slight delay to ensure the DOM is fully loaded
    setTimeout(() => this.connect(), 1000);
    
    // Add event listener for online/offline status
    window.addEventListener('online', () => {
      console.log('Browser is online, attempting to reconnect WebSocket');
      this.connect();
    });
    
    window.addEventListener('offline', () => {
      console.log('Browser is offline, WebSocket will reconnect when online');
      this.disconnect();
    });
  }

  private async connect() {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      console.log('WebSocket already connecting or connected');
      return;
    }
    
    this.isConnecting = true;
    console.log(`Attempting to connect to WebSocket at ${this.url}...`);
    
    try {
      // First, check if the backend is reachable with a simple fetch
      try {
        console.log('Testing backend connectivity with fetch...');
        const response = await fetch(`http://${window.location.hostname}:8000/docs`, { 
          method: 'GET',
          mode: 'no-cors' // This allows the request to be sent without CORS headers
        });
        console.log('Backend connectivity test result:', response);
      } catch (error) {
        console.warn('Backend connectivity test failed:', error);
        // Continue anyway, the WebSocket might still work
      }
      
      // Add a timeout to detect connection issues
      const connectionTimeout = setTimeout(() => {
        if (this.ws && this.ws.readyState !== WebSocket.OPEN) {
          console.error('WebSocket connection timeout - could not connect within 5 seconds');
          this.ws.close();
          this.isConnecting = false;
          this.emit('error', new Error('Connection timeout'));
          this.attemptReconnect();
        }
      }, 5000);
      
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log('WebSocket connected successfully');
        clearTimeout(connectionTimeout);
        this.reconnectAttempts = 0;
        this.isConnecting = false;
        this.emit('connected');
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('WebSocket message received:', data);

          if (data.type === 'connection_status') {
            console.log('Connection status message received:', data);
            if (data.status === 'connected') {
              console.log('Backend confirmed WebSocket connection');
              this.emit('connected');
            }
          } else if (data.type === 'confirmation') {
            // Emit confirmation events for the UI to handle
            this.emit('confirmation', data);
          } else if (data.type === 'progress') {
            // Handle progress messages
            if (data.data && data.data.execute_terraform) {
              console.log('Terraform execution data received:', data.data.execute_terraform);
              // Emit terraform execution data
              this.emit('terraformApply', data.data.execute_terraform);

              // If there's a result, also emit it as a message
              if (data.data.execute_terraform.result) {
                this.emit('results', {
                  message: 'Terraform execution completed.',
                  structuredContent: {
                    title: 'Terraform Apply',
                    sections: [
                      {
                        type: 'heading',
                        content: 'Terraform Apply Results',
                        metadata: { level: 1 }
                      },
                      {
                        type: 'text',
                        content: `Status: ${data.data.execute_terraform.error ? 'Error' : 'Complete'}`
                      }
                    ]
                  }
                });
              }
            }

            // For all other messages, emit the results
            if (data.data && data.data.results) {
              console.log('Emitting results:', data.data.results);
              this.emit('results', data.data.results);
            }
          } else if (data.type === 'error') {
            console.error('WebSocket error message received:', data.error);
            this.emit('error', new Error(data.error));
          } else {
            // For all other messages, emit the results
            if (data.results) {
              console.log('Emitting results from non-progress message:', data.results);
              this.emit('results', data.results);
            }
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onclose = (event) => {
        console.log(`WebSocket disconnected with code ${event.code}, reason: ${event.reason}`);
        clearTimeout(connectionTimeout);
        this.isConnecting = false;
        this.emit('disconnected');
        
        // Log more detailed information about the close code
        switch (event.code) {
          case 1000:
            console.log('Normal closure');
            break;
          case 1001:
            console.log('Going away - The endpoint is going away (e.g., server shutdown)');
            break;
          case 1002:
            console.log('Protocol error - The endpoint terminated the connection due to a protocol error');
            break;
          case 1003:
            console.log('Unsupported data - The endpoint received data of a type it cannot accept');
            break;
          case 1005:
            console.log('No status received - No status code was provided');
            break;
          case 1006:
            console.log('Abnormal closure - The connection was closed abnormally (e.g., without sending a close frame)');
            break;
          case 1007:
            console.log('Invalid frame payload data - The endpoint received a message that contained inconsistent data');
            break;
          case 1008:
            console.log('Policy violation - The endpoint received a message that violated its policy');
            break;
          case 1009:
            console.log('Message too big - The endpoint received a message that is too big to process');
            break;
          case 1010:
            console.log('Missing extension - The client expected the server to negotiate an extension but the server didn\'t');
            break;
          case 1011:
            console.log('Internal error - The server encountered an unexpected condition that prevented it from fulfilling the request');
            break;
          case 1015:
            console.log('TLS handshake failure - The connection was closed due to a failure to perform a TLS handshake');
            break;
          default:
            console.log(`Unknown close code: ${event.code}`);
        }
        
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        // Try to get more information about the error
        console.error('Error type:', error.type);
        console.error('Error target:', error.target);
        
        this.isConnecting = false;
        this.emit('error', error);
        // Don't attempt reconnect here, let onclose handle it
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      this.isConnecting = false;
      this.attemptReconnect();
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectTimeout * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts}) in ${delay}ms...`);

      setTimeout(() => {
        console.log(`Reconnecting now (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
        this.connect();
      }, delay);
    } else {
      console.error('Max reconnection attempts reached');
      this.emit('maxReconnectAttemptsReached');
    }
  }

  public sendTask(taskData: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message: WebSocketMessage = {
        type: 'new_task',
        message: taskData.message,
        timestamp: taskData.timestamp,
        mode: taskData.mode || 'normal' // Include the mode parameter
      };
      console.log('Sending task:', message);
      this.ws.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected, cannot send task');
      this.connect(); // Try to reconnect
      this.emit('error', new Error('WebSocket is not connected'));
      throw new Error('WebSocket is not connected');
    }
  }

  public sendConfirmation(confirmed: boolean, data?: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message: WebSocketMessage = {
        type: 'confirmation_response',
        approved: confirmed,
        ...data
      };
      console.log('Sending confirmation:', message);
      this.ws.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected, cannot send confirmation');
      this.connect(); // Try to reconnect
      this.emit('error', new Error('WebSocket is not connected'));
      throw new Error('WebSocket is not connected');
    }
  }

  public getConnectionStatus(): string {
    if (!this.ws) return 'CLOSED';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'CONNECTING';
      case WebSocket.OPEN:
        return 'OPEN';
      case WebSocket.CLOSING:
        return 'CLOSING';
      case WebSocket.CLOSED:
        return 'CLOSED';
      default:
        return 'UNKNOWN';
    }
  }

  public disconnect() {
    if (this.ws) {
      console.log('Disconnecting WebSocket');
      this.ws.close();
      this.ws = null;
    }
  }
  
  public forceReconnect() {
    console.log('Force reconnecting WebSocket');
    this.disconnect();
    this.reconnectAttempts = 0;
    this.connect();
  }
}

// Create a singleton instance
export const websocketService = new WebSocketService();
export default websocketService;