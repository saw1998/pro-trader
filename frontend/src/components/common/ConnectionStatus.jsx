// src/components/common/ConnectionStatus.jsx
import { useWebSocket } from '../../context/WebSocketContext';
import './Common.css';

export function ConnectionStatus() {
  const { isConnected } = useWebSocket();

  return (
    <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
      <span className="connection-dot"></span>
      {isConnected ? 'Live' : 'Connecting...'}
    </div>
  );
}