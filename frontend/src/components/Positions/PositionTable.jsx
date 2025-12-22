// src/components/Positions/PositionTable.jsx
import { formatCurrency, formatPercentage, formatQuantity, getPnLClass } from '../../utils/helpers';
import './Positions.css';

export function PositionTable({ positions, onClose, closingId }) {
  if (positions.length === 0) {
    return (
      <div className="positions-empty">
        <p>No open positions</p>
      </div>
    );
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <table className="positions-table">
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Type</th>
            <th className="text-right">Quantity</th>
            <th className="text-right">Entry</th>
            <th className="text-right">Current</th>
            <th className="text-right">P&L</th>
            <th className="text-right">P&L %</th>
            <th className="text-center">Action</th>
          </tr>
        </thead>
        <tbody>
          {positions.map((position) => (
            <tr key={position.id}>
              <td style={{ fontWeight: 500 }}>{position.symbol}</td>
              <td>
                <span className={`position-type-badge ${position.position_type.toLowerCase()}`}>
                  {position.position_type}
                </span>
              </td>
              <td className="text-right">{formatQuantity(position.quantity)}</td>
              <td className="text-right">{formatCurrency(position.entry_price)}</td>
              <td className="text-right">{formatCurrency(position.current_price)}</td>
              <td className={`text-right ${getPnLClass(position.unrealized_pnl)}`} style={{ fontWeight: 500 }}>
                {formatCurrency(position.unrealized_pnl)}
              </td>
              <td className={`text-right ${getPnLClass(position.pnl_percentage)}`} style={{ fontWeight: 500 }}>
                {formatPercentage(position.pnl_percentage)}
              </td>
              <td className="text-center">
                <button
                  onClick={() => onClose(position.id)}
                  disabled={closingId === position.id}
                  className="btn btn-danger btn-sm"
                >
                  {closingId === position.id ? 'Closing...' : 'Close'}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}