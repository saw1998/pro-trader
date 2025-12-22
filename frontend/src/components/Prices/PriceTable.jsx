// src/components/Prices/PriceTable.jsx
import { formatCurrency, formatPercentage, getPnLClass } from '../../utils/helpers';
import './Prices.css';

export function PriceTable({ prices, onTrade }) {
  const priceList = Object.values(prices).sort((a, b) => a.symbol.localeCompare(b.symbol));

  if (priceList.length === 0) {
    return (
      <div className="prices-empty">
        <p>Waiting for price data...</p>
      </div>
    );
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <table className="prices-table">
        <thead>
          <tr>
            <th>Symbol</th>
            <th className="text-right">Price</th>
            <th className="text-right">24h Change</th>
            <th className="text-right">24h High</th>
            <th className="text-right">24h Low</th>
            <th className="text-right">Volume</th>
            {onTrade && <th className="text-center">Action</th>}
          </tr>
        </thead>
        <tbody>
          {priceList.map((price) => (
            <tr key={price.symbol}>
              <td style={{ fontWeight: 500 }}>{price.symbol}</td>
              <td className="text-right price-value">{formatCurrency(price.price)}</td>
              <td className={`text-right ${getPnLClass(price.change_24h || 0)}`} style={{ fontWeight: 500 }}>
                {formatPercentage(price.change_24h || 0)}
              </td>
              <td className="text-right text-muted">{formatCurrency(price.high_24h || 0)}</td>
              <td className="text-right text-muted">{formatCurrency(price.low_24h || 0)}</td>
              <td className="text-right text-muted">
                {(price.volume || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </td>
              {onTrade && (
                <td className="text-center">
                  <button
                    onClick={() => onTrade(price.symbol, price.price)}
                    className="btn btn-primary btn-sm"
                  >
                    Trade
                  </button>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}