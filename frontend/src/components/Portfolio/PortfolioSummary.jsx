// src/components/Portfolio/PortfolioSummary.jsx
import { formatCurrency, formatPercentage, getPnLClass } from '../../utils/helpers';
import './Portfolio.css';

export function PortfolioSummary({ portfolio }) {
  const { 
    total_invested, 
    total_current_value, 
    total_unrealized_pnl, 
    total_pnl_percentage, 
    positions 
  } = portfolio;
  
  const isProfit = total_unrealized_pnl >= 0;

  const stats = [
    {
      label: 'Total Invested',
      value: formatCurrency(total_invested),
      colorClass: 'text-primary',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="#3b82f6" strokeWidth="2">
          <line x1="12" y1="1" x2="12" y2="23"></line>
          <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
        </svg>
      )
    },
    {
      label: 'Current Value',
      value: formatCurrency(total_current_value),
      colorClass: 'text-purple',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="#a855f7" strokeWidth="2">
          <path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path>
          <path d="M22 12A10 10 0 0 0 12 2v10z"></path>
        </svg>
      )
    },
    {
      label: 'Unrealized P&L',
      value: formatCurrency(total_unrealized_pnl),
      subValue: formatPercentage(total_pnl_percentage),
      colorClass: getPnLClass(total_unrealized_pnl),
      icon: isProfit ? (
        <svg viewBox="0 0 24 24" fill="none" stroke="#22c55e" strokeWidth="2">
          <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
          <polyline points="17 6 23 6 23 12"></polyline>
        </svg>
      ) : (
        <svg viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2">
          <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline>
          <polyline points="17 18 23 18 23 12"></polyline>
        </svg>
      )
    },
    {
      label: 'Open Positions',
      value: positions.length.toString(),
      colorClass: '',
      icon: (
        <svg viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="3" y1="9" x2="21" y2="9"></line>
          <line x1="9" y1="21" x2="9" y2="9"></line>
        </svg>
      )
    }
  ];

  return (
    <div className="portfolio-summary">
      {stats.map((stat, index) => (
        <div key={index} className="portfolio-stat-card">
          <div className="portfolio-stat-content">
            <span className="portfolio-stat-label">{stat.label}</span>
            <span className={`portfolio-stat-value ${stat.colorClass}`}>{stat.value}</span>
            {stat.subValue && (
              <span className={`portfolio-stat-subvalue ${stat.colorClass}`}>{stat.subValue}</span>
            )}
          </div>
          <div className="portfolio-stat-icon">{stat.icon}</div>
        </div>
      ))}
    </div>
  );
}