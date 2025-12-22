// src/pages/LivePricesPage.jsx
import { useState } from 'react';
import { usePrices } from '../hooks/usePrices';
import { PriceTable } from '../components/Prices/PriceTable';
import { QuickTrade } from '../components/Trade/QuickTrade';
import { useWebSocket } from '../context/WebSocketContext';
import './Pages.css';

export function LivePricesPage() {
  const { prices, isConnected } = usePrices();
  const { subscribe } = useWebSocket();
  const [newSymbol, setNewSymbol] = useState('');
  const [selectedPrice, setSelectedPrice] = useState(null);

  const handleAddSymbol = () => {
    if (newSymbol) {
      subscribe([newSymbol.toUpperCase()]);
      setNewSymbol('');
    }
  };

  const handleTrade = (symbol, price) => {
    setSelectedPrice(prices[symbol] || { symbol, price, timestamp: new Date().toISOString() });
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Live Prices</h1>
        <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
          <span className="connection-dot"></span>
          {isConnected ? 'Connected' : 'Connecting...'}
        </div>
      </div>

      <div className="section">
        <div className="card">
          <div className="subscribe-form">
            <input
              type="text"
              value={newSymbol}
              onChange={(e) => setNewSymbol(e.target.value.toUpperCase())}
              placeholder="Add symbol (e.g., AVAXUSDT)"
              className="input"
              onKeyDown={(e) => e.key === 'Enter' && handleAddSymbol()}
            />
            <button onClick={handleAddSymbol} className="btn btn-primary">
              Subscribe
            </button>
          </div>

          <PriceTable prices={prices} onTrade={handleTrade} />
        </div>
      </div>

      {selectedPrice && (
        <div className="modal-overlay" onClick={() => setSelectedPrice(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="modal-title">Quick Trade - {selectedPrice.symbol}</h3>
              <button onClick={() => setSelectedPrice(null)} className="modal-close">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
            <QuickTrade price={selectedPrice} onSuccess={() => setSelectedPrice(null)} />
          </div>
        </div>
      )}
    </div>
  );
}