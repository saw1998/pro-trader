// src/components/Layout/Navbar.jsx
import { useAuth } from '../../context/AuthContext';
import { ConnectionStatus } from '../common/ConnectionStatus';
import './Navbar.css';

export function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="navbar">
      <div className="navbar-content">
        <h1 className="navbar-brand">📈 Trading System</h1>
        
        <div className="navbar-right">
          <ConnectionStatus />
          
          <div className="navbar-user">
            <svg className="navbar-user-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
            <span>{user?.username}</span>
          </div>
          
          <button onClick={logout} className="navbar-logout">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
              <polyline points="16 17 21 12 16 7"></polyline>
              <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
          </button>
        </div>
      </div>
    </nav>
  );
}