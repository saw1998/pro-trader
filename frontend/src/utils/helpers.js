// src/utils/helpers.js
export const formatCurrency = (value, decimals = 2) => {
  const formatted = Math.abs(value).toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  });
  return value >= 0 ? `$${formatted}` : `-$${formatted}`;
};

export const formatPercentage = (value) => {
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}%`;
};

export const formatQuantity = (value) => {
  return value >= 1 ? value.toFixed(4) : value.toFixed(8);
};

export const getPnLClass = (value) => {
  if (value > 0) return 'text-success';
  if (value < 0) return 'text-danger';
  return 'text-muted';
};

export const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString();
};

export const getSessionId = () => {
  return localStorage.getItem('session_id');
};

export const setSessionId = (sessionId) => {
  localStorage.setItem('session_id', sessionId);
};

export const removeSessionId = () => {
  localStorage.removeItem('session_id');
};