// src/components/Trade/OpenPositionForm.jsx
import { useState } from 'react';
import { useOpenPosition } from '../../hooks/usePositions';
import { usePrices } from '../../hooks/usePrices';
import { config } from '../../config';
import { formatCurrency } from '../../utils/helpers';
import './Trade.css';

export function OpenPositionForm({ initialSymbol, initialPrice }) {
  const { prices } = usePrices();
  const openPosition = useOpenPosition();
  
  const [symbol, setSymbol] = useState(initialSymbol || 'BTCUSDT');
  const [quantity, setQuantity] = useState('0.01');
  const [positionType, setPositionType] = useState('LONG');
  const [useMarketPrice, setUseMarketPrice] = useState(true);
  const [customPrice, setCustomPrice] = useState(initialPrice?.toString() || '');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const currentPrice = prices[symbol]?.price || initialPrice || 0;
  const entryPrice = useMarketPrice ? currentPrice : parseFloat(customPrice) || 0;
  const totalValue = parseFloat(quantity) * entryPrice;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!symbol || !quantity || entryPrice <= 0) {
      setError('Please fill all fields correctly');
      return;
    }

    try {
      await openPosition.mutateAsync({
        symbol: symbol.toUpperCase(),
        quantity: parseFloat(quantity),
        entry_price: entryPrice,
        position_type: positionType
      });
      setSuccess(`Opened ${positionType} position for ${symbol}`);
      setQuantity('0.01');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to open position');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="card trade-form">
      <h3 className="trade-form-title">Open New Position</h3>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <div className="trade-form-row">
        <div className="form-group">
          <label className="form-label">Symbol</label>
          <select value={symbol} onChange={(e) => setSymbol(e.target.value)} className="input">
            {config.defaultSymbols.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Position Type</label>
          <div className="trade-type-buttons">
            <button
              type="button"
              onClick={() => setPositionType('LONG')}
              className={`trade-type-btn ${positionType === 'LONG' ? 'active long' : ''}`}
            >
              LONG
            </button>
            <button
              type="button"
              onClick={() => setPositionType('SHORT')}
              className={`trade-type-btn ${positionType === 'SHORT' ? 'active short' : ''}`}
            >
              SHORT
            </button>
          </div>
        </div>
      </div>

      <div className="trade-form-row">
        <div className="form-group">
          <label className="form-label">Quantity</label>
          <input
            type="number"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            className="input"
            step="0.00000001"
            min="0"
          />
        </div>

        <div className="form-group">
          <label className="form-label">
            Entry Price
            <label className="checkbox-label" style={{ marginLeft: 12, display: 'inline-flex' }}>
              <input
                type="checkbox"
                checked={useMarketPrice}
                onChange={(e) => setUseMarketPrice(e.target.checked)}
              />
              <span>Market</span>
            </label>
          </label>
          {useMarketPrice ? (
            <div className="input" style={{ backgroundColor: 'var(--color-bg-tertiary)', cursor: 'not-allowed' }}>
              {formatCurrency(currentPrice)}
            </div>
          ) : (
            <input
              type="number"
              value={customPrice}
              onChange={(e) => setCustomPrice(e.target.value)}
              className="input"
              step="0.01"
              min="0"
            />
          )}
        </div>
      </div>

      <div className="trade-summary">
        <div className="trade-summary-row">
          <span className="trade-summary-label">Total Value</span>
          <span className="trade-summary-value">{formatCurrency(totalValue)}</span>
        </div>
      </div>

      <button
        type="submit"
        disabled={openPosition.isPending}
        className={`btn btn-full ${positionType === 'LONG' ? 'btn-success' : 'btn-danger'}`}
      >
        {openPosition.isPending ? 'Opening...' : `Open ${positionType} Position`}
      </button>
    </form>
  );
}