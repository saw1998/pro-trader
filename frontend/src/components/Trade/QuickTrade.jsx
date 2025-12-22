// src/components/Trade/QuickTrade.jsx
import { useState } from 'react';
import { useOpenPosition } from '../../hooks/usePositions';
import { formatCurrency } from '../../utils/helpers';
import './Trade.css';

export function QuickTrade({ price, onSuccess }) {
  const openPosition = useOpenPosition();
  const [quantity, setQuantity] = useState('0.01');
  const [positionType, setPositionType] = useState('LONG');

  const totalValue = parseFloat(quantity) * price.price;

  const handleTrade = async () => {
    try {
      await openPosition.mutateAsync({
        symbol: price.symbol,
        quantity: parseFloat(quantity),
        entry_price: price.price,
        position_type: positionType
      });
      onSuccess?.();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="quick-trade">
      <div className="quick-trade-info">
        <div className="quick-trade-symbol">{price.symbol}</div>
        <div className="quick-trade-price">{formatCurrency(price.price)}</div>
      </div>

      <input
        type="number"
        value={quantity}
        onChange={(e) => setQuantity(e.target.value)}
        className="input quick-trade-input"
        step="0.01"
        min="0"
      />

      <select
        value={positionType}
        onChange={(e) => setPositionType(e.target.value)}
        className="input quick-trade-select"
      >
        <option value="LONG">LONG</option>
        <option value="SHORT">SHORT</option>
      </select>

      <div className="quick-trade-total">
        <div className="quick-trade-total-label">Total</div>
        <div className="quick-trade-total-value">{formatCurrency(totalValue)}</div>
      </div>

      <button onClick={handleTrade} disabled={openPosition.isPending} className="btn btn-primary">
        {openPosition.isPending ? '...' : 'Trade'}
      </button>
    </div>
  );
}