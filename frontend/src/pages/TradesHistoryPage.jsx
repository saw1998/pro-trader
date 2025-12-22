// src/pages/TradesHistoryPage.jsx
import { useTrades } from '../hooks/useTrades';
import { Loading } from '../components/common/Loading';
import { Error } from '../components/common/Error';
import { formatCurrency, formatDate, getPnLClass } from '../utils/helpers';
import './Pages.css';

export function TradesHistoryPage() {
  const { data: trades, isLoading, error, refetch } = useTrades(0, 100);

  if (isLoading) return <Loading />;
  if (error) return <Error message="Failed to load trades" onRetry={refetch} />;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Trade History</h1>
      </div>

      <div className="card">
        {!trades?.length ? (
          <div className="empty-state">
            <p>No trades yet</p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="trades-table">
              <thead>
                <tr>
                  <th>Date & Time</th>
                  <th>Symbol</th>
                  <th>Side</th>
                  <th className="text-right">Quantity</th>
                  <th className="text-right">Price</th>
                  <th className="text-right">Total</th>
                  <th className="text-right">Fee</th>
                  <th className="text-right">Realized P&L</th>
                </tr>
              </thead>
              <tbody>
                {trades.map((trade) => (
                  <tr key={trade.id}>
                    <td style={{ fontSize: 14 }}>{formatDate(trade.executed_at)}</td>
                    <td style={{ fontWeight: 500 }}>{trade.symbol}</td>
                    <td>
                      <span className={`side-badge ${trade.side.toLowerCase()}`}>
                        {trade.side}
                      </span>
                    </td>
                    <td className="text-right">{trade.quantity}</td>
                    <td className="text-right">{formatCurrency(trade.price)}</td>
                    <td className="text-right">{formatCurrency(trade.total_value)}</td>
                    <td className="text-right text-muted">{formatCurrency(trade.fee)}</td>
                    <td className={`text-right ${getPnLClass(trade.realized_pnl)}`} style={{ fontWeight: 500 }}>
                      {formatCurrency(trade.realized_pnl)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}