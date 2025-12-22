// src/pages/DashboardPage.jsx
import { useState } from 'react';
import { usePortfolio } from '../hooks/usePortfolio';
import { useClosePosition } from '../hooks/usePositions';
import { useTrades } from '../hooks/useTrades';
import { PortfolioSummary } from '../components/Portfolio/PortfolioSummary';
import { PositionCard } from '../components/Positions/PositionCard';
import { PositionTable } from '../components/Positions/PositionTable';
import { Loading } from '../components/common/Loading';
import { Error } from '../components/common/Error';
import { formatCurrency, formatDate, getPnLClass } from '../utils/helpers';
import './Pages.css';

export function DashboardPage() {
  const { portfolio, isLoading, error, refetch } = usePortfolio();
  const closePosition = useClosePosition();
  const { data: trades } = useTrades(0, 10);
  const [viewMode, setViewMode] = useState('table');
  const [closingId, setClosingId] = useState(null);

  const handleClosePosition = async (id) => {
    setClosingId(id);
    try {
      await closePosition.mutateAsync({ id });
    } finally {
      setClosingId(null);
    }
  };

  if (isLoading) return <Loading />;
  if (error) return <Error message="Failed to load portfolio" onRetry={refetch} />;
  if (!portfolio) return null;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <button onClick={() => refetch()} className="refresh-btn">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="23 4 23 10 17 10"></polyline>
            <polyline points="1 20 1 14 7 14"></polyline>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
          </svg>
        </button>
      </div>

      <div className="section">
        <PortfolioSummary portfolio={portfolio} />
      </div>

      <div className="section">
        <div className="card">
          <div className="section-header">
            <h2 className="section-title">Open Positions</h2>
            <div className="view-toggle">
              <button
                onClick={() => setViewMode('table')}
                className={`view-toggle-btn ${viewMode === 'table' ? 'active' : ''}`}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="8" y1="6" x2="21" y2="6"></line>
                  <line x1="8" y1="12" x2="21" y2="12"></line>
                  <line x1="8" y1="18" x2="21" y2="18"></line>
                  <line x1="3" y1="6" x2="3.01" y2="6"></line>
                  <line x1="3" y1="12" x2="3.01" y2="12"></line>
                  <line x1="3" y1="18" x2="3.01" y2="18"></line>
                </svg>
              </button>
              <button
                onClick={() => setViewMode('cards')}
                className={`view-toggle-btn ${viewMode === 'cards' ? 'active' : ''}`}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="3" width="7" height="7"></rect>
                  <rect x="14" y="3" width="7" height="7"></rect>
                  <rect x="14" y="14" width="7" height="7"></rect>
                  <rect x="3" y="14" width="7" height="7"></rect>
                </svg>
              </button>
            </div>
          </div>

          {viewMode === 'table' ? (
            <PositionTable 
              positions={portfolio.positions} 
              onClose={handleClosePosition} 
              closingId={closingId} 
            />
          ) : (
            <div className="positions-grid">
              {portfolio.positions.map((position) => (
                <PositionCard
                  key={position.id}
                  position={position}
                  onClose={handleClosePosition}
                  isClosing={closingId === position.id}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {trades && trades.length > 0 && (
        <div className="section">
          <div className="card">
            <h2 className="section-title" style={{ marginBottom: 16 }}>Recent Trades</h2>
            <div style={{ overflowX: 'auto' }}>
              <table className="trades-table">
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Symbol</th>
                    <th>Side</th>
                    <th className="text-right">Quantity</th>
                    <th className="text-right">Price</th>
                    <th className="text-right">P&L</th>
                  </tr>
                </thead>
                <tbody>
                  {trades.map((trade) => (
                    <tr key={trade.id}>
                      <td style={{ fontSize: 14, color: 'var(--color-text-secondary)' }}>
                        {formatDate(trade.executed_at)}
                      </td>
                      <td style={{ fontWeight: 500 }}>{trade.symbol}</td>
                      <td>
                        <span className={`side-badge ${trade.side.toLowerCase()}`}>
                          {trade.side}
                        </span>
                      </td>
                      <td className="text-right">{trade.quantity}</td>
                      <td className="text-right">{formatCurrency(trade.price)}</td>
                      <td className={`text-right ${getPnLClass(trade.realized_pnl)}`} style={{ fontWeight: 500 }}>
                        {formatCurrency(trade.realized_pnl)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}