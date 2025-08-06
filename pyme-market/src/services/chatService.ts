interface ChatMessage {
  messageId?: string;
  content: string;
  username: string;
  roomId: string;
  timestamp?: string;
}

interface WebSocketMessage {
  type: 'message' | 'history' | 'users_online' | 'user_left' | 'ping';
  messages?: ChatMessage[];
  message?: string;
  content?: string;
  username?: string;
  users_online?: string[];
}

class ChatService {
  private ws: WebSocket | null = null;
  private messageHandlers: ((message: WebSocketMessage) => void)[] = [];
  private connectionHandlers: ((status: boolean) => void)[] = [];
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimeout = 1000;
  private intentionalDisconnect = false;
  private currentUsername: string | null = null;
  private currentRoomId: string | null = null;
  private lastPingTime: number = 0;
  private pingTimeout: number | null = null;

  constructor() {
    this.connect = this.connect.bind(this);
    this.disconnect = this.disconnect.bind(this);
    this.sendMessage = this.sendMessage.bind(this);
    this.onMessage = this.onMessage.bind(this);
  }

  connect(username: string, roomId: string = 'general') {
    this.currentUsername = username;
    this.currentRoomId = roomId;
    this.intentionalDisconnect = false;
    this.lastPingTime = Date.now();

    if (this.ws) {
      this.ws.close();
    }

    const wsUrl = `ws://localhost:8003/chat/ws?username=${encodeURIComponent(username)}&room_id=${encodeURIComponent(roomId)}`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('Conectado al chat');
      this.reconnectAttempts = 0;
      this.reconnectTimeout = 1000;
      this.notifyConnectionStatus(true);
      this.startPingCheck();
    };

    this.ws.onmessage = (event) => {
      try {
        const data: WebSocketMessage = JSON.parse(event.data);
        
        if (data.type === 'ping') {
          this.lastPingTime = Date.now();
          return;
        }
        
        this.messageHandlers.forEach(handler => handler(data));
      } catch (error) {
        console.error('Error parsing message:', error);
      }
    };

    this.ws.onclose = (event) => {
      console.log('Desconectado del chat', event.code, event.reason);
      this.notifyConnectionStatus(false);
      this.stopPingCheck();
      
      if (!this.intentionalDisconnect && this.currentUsername) {
        this.attemptReconnect();
      }
    };

    this.ws.onerror = (error) => {
      console.error('Error en WebSocket:', error);
      this.notifyConnectionStatus(false);
    };
  }

  private startPingCheck() {
    if (this.pingTimeout) {
      clearTimeout(this.pingTimeout);
    }

    this.pingTimeout = window.setInterval(() => {
      const now = Date.now();
      if (now - this.lastPingTime > 45000) {
        console.log('No se han recibido pings, reconectando...');
        if (this.ws) {
          this.ws.close();
        }
      }
    }, 45000);
  }

  private stopPingCheck() {
    if (this.pingTimeout) {
      clearInterval(this.pingTimeout);
      this.pingTimeout = null;
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts && this.currentUsername && !this.intentionalDisconnect) {
      this.reconnectAttempts++;
      console.log(`Intentando reconectar (intento ${this.reconnectAttempts})...`);
      
      const timeout = Math.min(1000 * Math.pow(2, this.reconnectAttempts - 1), 30000);
      
      setTimeout(() => {
        if (this.currentUsername && this.currentRoomId) {
          this.connect(this.currentUsername, this.currentRoomId);
        }
      }, timeout);
    } else if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Se alcanzó el límite de intentos de reconexión');
      this.currentUsername = null;
      this.currentRoomId = null;
    }
  }

  disconnect() {
    this.intentionalDisconnect = true;
    this.currentUsername = null;
    this.currentRoomId = null;
    this.stopPingCheck();
    if (this.ws) {
      this.ws.close(1000, 'Desconexión intencional');
      this.ws = null;
    }
  }

  sendMessage(content: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message = {
        type: 'message',
        content
      };
      this.ws.send(JSON.stringify(message));
    } else {
      console.error('WebSocket no está conectado');
    }
  }

  onMessage(handler: (message: WebSocketMessage) => void) {
    this.messageHandlers.push(handler);
    return () => {
      this.messageHandlers = this.messageHandlers.filter(h => h !== handler);
    };
  }

  onConnectionChange(handler: (status: boolean) => void) {
    this.connectionHandlers.push(handler);
    return () => {
      this.connectionHandlers = this.connectionHandlers.filter(h => h !== handler);
    };
  }

  private notifyConnectionStatus(status: boolean) {
    this.connectionHandlers.forEach(handler => handler(status));
  }
}

export const chatService = new ChatService();