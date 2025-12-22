// src/config/index.js
export const config = {
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  wsUrl: import.meta.env.VITE_WS_URL || 'ws://localhost:8000',
  defaultSymbols: [
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT',
    'DOGEUSDT', 'SOLUSDT', 'DOTUSDT', 'MATICUSDT', 'LTCUSDT'
  ]
};