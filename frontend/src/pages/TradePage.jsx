// src/pages/TradePage.jsx
import { useState } from 'react';
import { OpenPositionForm } from '../components/Trade/OpenPositionForm';
import { usePositions, useClosePosition } from '../hooks/usePositions';
import { usePrices } from '../hooks/usePrices';
import { formatCurrency, formatQuantity, getPnLClass } from '../utils/helpers';
import { Loading } from '../components/common/Loading';
import './Pages.css';

export function TradePage() {
  const { data: positions, isLoading } = usePositions('OPEN');
  const closePosition = useClosePosition();
  const { prices } = usePrices();
  const [selectedPositionId, setSelectedPositionId] = useState('');
  const [exitPrice, setExitPrice] = useState('');
  const [useMarket, setUseMarket] = useState(true);

  const handleClosePosition = async () => {
    if (!selectedPositionId) return;
    
    await closePosition.mutateAsync({
      id: selectedPositionId,
      data: useMarket ? undefined : { exit_price: parseFloat(exitPrice) }
    });
    
    setSelectedPositionId('');
    setExitPrice('');
  };

  const selectedPosition = positions?.find((p) => p.id === selectedPositionId);
  const currentPrice = selectedPosition ? prices[selectedPosition.symbol]?.price : null;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Trade</h1>
      </div>

      <div className="page-grid">
        <OpenPositionForm />

        <div className="card">
          <h3 className="trade-form-title">Close Position</h3>
          
          {isLoading ? (
            <Loading />
          ) : !positions?.length ? (
            <div className="empty-state">
              <p>No open positions to close</p>
            </div>
          ) : (
            <div className="close-form">
              <div className="form-group">
                <label className="form-label">Select Position</label>
                <select
                  value={selectedPositionId}
                  onChange={(e) => setSelectedPositionId(e.target.value)}
                  className="input"
                >
                  <option value="">Select a position...</option>
                  {positions.map((pos) => (
                    <option key={pos.id} value={pos.id}>
                      {pos.symbol} - {pos.position_type} - {formatQuantity(pos.quantity)}
                    </option>
                  ))}
                </select>
              </div>

              {selectedPosition && (
                <>
                  <div className="position-details">
                    <div className="position-details-row">
                      <span className="position-details-label">Symbol</span>
                      <span className="position-details-value">{selectedPosition.symbol}</span>
                    </div>
                    <div className="position-details-row">
                      <span className="position-details-label">Type</span>
                      <span className={selectedPosition.position_type === 'LONG' ? 'text-success' : 'text-danger'}>
                        {selectedPosition.position_type}
                      </span>
                    </div>
                    <div className="position-details-row">
                      <span className="position-details-label">Quantity</span>
                      <span className="position-details-value">{formatQuantity(selectedPosition.quantity)}</span>
                    </div>
                    <div className="position-details-row">
                      <span className="position-details-label">Entry Price</span>
                      <span className="position-details-value">{formatCurrency(selectedPosition.entry_price)}</span>
                    </div>
                    {currentPrice && (
                      <div className="position-details-row">
                        <span className="position-details-label">Current Price</span>
                        <span className="position-details-value" style={{ fontFamily: 'var(--font-mono)' }}>
                          {formatCurrency(currentPrice)}
                        </span>
                      </div>
                    )}
                  </div>

                  <div>
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={useMarket}
                        onChange={(e) => setUseMarket(e.target.checked)}
                      />
                      <span>Use market price</span>
                    </label>
                    
                    {!useMarket && (
                      <input
                        type="number"
                        value={exitPrice}
                        onChange={(e) => setExitPrice(e.target.value)}
                        placeholder="Exit price"
                        className="input"
                        style={{ marginTop: 12 }}
                        step="0.01"
                      />
                    )}
                  </div>

                  <button
                    onClick={handleClosePosition}
                    disabled={closePosition.isPending}
                    className="btn btn-danger btn-full"
                  >
                    {closePosition.isPending ? 'Closing...' : 'Close Position'}
                  </button>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}