import { EventEmitter } from 'events';

interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

class WebSocketService extends EventEmitter {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimeout = 1000; // Start with 1 second
  private url = 'ws://127.0.0.1:8000/ws/ai-assist';

  constructor() {
    super();
    this.connect();
  }

  private connect() {
    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        this.emit('connected');
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('WebSocket message received:', data);

          if (data.type === 'confirmation') {
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
            if (data.results) {
              this.emit('results', data.results);
            }
          } else {
            // For all other messages, emit the results
            if (data.results) {
              this.emit('results', data.results);
            }
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.emit('disconnected');
        this.attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.emit('error', error);
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      this.attemptReconnect();
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

      setTimeout(() => {
        this.connect();
      }, this.reconnectTimeout * Math.pow(2, this.reconnectAttempts - 1)); // Exponential backoff
    } else {
      console.error('Max reconnection attempts reached');
      this.emit('maxReconnectAttemptsReached');
    }
  }

  public sendTask(taskData: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message: WebSocketMessage = {
        type: 'new_task',
        ...taskData
      };
      this.ws.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
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
      this.ws.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
      throw new Error('WebSocket is not connected');
    }
  }

  public disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// Create a singleton instance
export const websocketService = new WebSocketService();
export default websocketService;