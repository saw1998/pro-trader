// src/components/Positions/PositionCard.jsx
import { formatCurrency, formatPercentage, formatQuantity, getPnLClass } from '../../utils/helpers';
import './Positions.css';

export function PositionCard({ position, onClose, isClosing }) {
  const { 
    id, 
    symbol, 
    quantity, 
    entry_price, 
    current_price, 
    position_type, 
    unrealized_pnl, 
    pnl_percentage 
  } = position;
  
  const isProfit = unrealized_pnl >= 0;
  const isLong = position_type === 'LONG';

  return (
    <div className={`position-card ${isProfit ? 'profit' : 'loss'}`}>
      <div className="position-card-header">
        <div className="position-card-title">
          <span className={`position-type-badge ${isLong ? 'long' : 'short'}`}>
            {position_type}
          </span>
          <span className="position-card-symbol">{symbol}</span>
        </div>
        <button
          onClick={() => onClose(id)}
          disabled={isClosing}
          className="position-card-close"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <div className="position-card-grid">
        <div>
          <div className="position-card-label">Quantity</div>
          <div className="position-card-value">{formatQuantity(quantity)}</div>
        </div>
        <div>
          <div className="position-card-label">Entry Price</div>
          <div className="position-card-value">{formatCurrency(entry_price)}</div>
        </div>
        <div>
          <div className="position-card-label">Current Price</div>
          <div className="position-card-value">{formatCurrency(current_price)}</div>
        </div>
        <div>
          <div className="position-card-label">P&L</div>
          <div className={`position-card-value ${getPnLClass(unrealized_pnl)}`}>
            {formatCurrency(unrealized_pnl)}
          </div>
        </div>
      </div>

      <div className={`position-card-pnl ${getPnLClass(unrealized_pnl)}`}>
        <div className="position-card-pnl-percent">
          {isProfit ? (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
              <polyline points="17 6 23 6 23 12"></polyline>
            </svg>
          ) : (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline>
              <polyline points="17 18 23 18 23 12"></polyline>
            </svg>
          )}
          {formatPercentage(pnl_percentage)}
        </div>
        <div className="position-card-pnl-value">{formatCurrency(unrealized_pnl)}</div>
      </div>
    </div>
  );
}