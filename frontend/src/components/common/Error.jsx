import './Common.css';

export function Error({ message, onRetry }) {
  return (
    <div className="error-container">
      <svg className="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
      </svg>
      <p className="error-message">{message}</p>
      {onRetry && (
        <button onClick={onRetry} className="btn btn-primary">
          Retry
        </button>
      )}
    </div>
  );
}