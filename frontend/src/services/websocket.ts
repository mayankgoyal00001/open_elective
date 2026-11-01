import { SimulationSnapshot } from '../types/simulation';

type MessageCallback = (data: SimulationSnapshot) => void;
type ConnectionCallback = (connected: boolean) => void;

class WebSocketClient {
  private ws: WebSocket | null = null;
  private messageListeners: Set<MessageCallback> = new Set();
  private connectionListeners: Set<ConnectionCallback> = new Set();
  private reconnectTimer: any = null;
  private isExplicitlyClosed = false;

  public isConnected = false;

  constructor() {
    this.connect();
  }

  public connect() {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.isExplicitlyClosed = false;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    // Connect to /ws via Vite proxy or direct
    const wsUrl = `${protocol}//${host}/ws`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        this.isConnected = true;
        this.notifyConnection(true);
      };

      this.ws.onmessage = (event) => {
        try {
          const snapshot = JSON.parse(event.data) as SimulationSnapshot;
          this.notifyMessage(snapshot);
        } catch (e) {
          console.error('Error parsing WebSocket simulation state', e);
        }
      };

      this.ws.onclose = () => {
        this.isConnected = false;
        this.notifyConnection(false);
        if (!this.isExplicitlyClosed) {
          this.scheduleReconnect();
        }
      };

      this.ws.onerror = () => {
        this.isConnected = false;
        this.notifyConnection(false);
      };
    } catch (e) {
      this.isConnected = false;
      this.notifyConnection(false);
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, 2000);
  }

  public sendCommand(command: Record<string, any>) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(command));
    }
  }

  public subscribe(callback: MessageCallback): () => void {
    this.messageListeners.add(callback);
    return () => this.messageListeners.delete(callback);
  }

  public onConnectionChange(callback: ConnectionCallback): () => void {
    this.connectionListeners.add(callback);
    callback(this.isConnected);
    return () => this.connectionListeners.delete(callback);
  }

  private notifyMessage(data: SimulationSnapshot) {
    this.messageListeners.forEach((cb) => cb(data));
  }

  private notifyConnection(connected: boolean) {
    this.connectionListeners.forEach((cb) => cb(connected));
  }

  public disconnect() {
    this.isExplicitlyClosed = true;
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    if (this.ws) this.ws.close();
  }
}

export const wsClient = new WebSocketClient();
