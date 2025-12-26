/**
 * Market Status Component
 * Displays current market status (open/closed) with countdown
 */
import React, { useState, useEffect } from 'react';
import { getMarketStatus } from '../utils/marketHours';
import './MarketStatus.css';

const MarketStatus = ({ onRefresh, refreshing }) => {
  const [marketStatus, setMarketStatus] = useState(getMarketStatus());

  useEffect(() => {
    // Update market status every minute
    const interval = setInterval(() => {
      setMarketStatus(getMarketStatus());
    }, 60000); // 60 seconds

    return () => clearInterval(interval);
  }, []);

  // Auto-refresh when market opens (if enabled)
  useEffect(() => {
    if (marketStatus.isOpen && marketStatus.hours === 0 && marketStatus.minutes <= 1) {
      // Market just opened, auto-refresh
      if (onRefresh && !refreshing) {
        console.log('Market opened - auto-refreshing prices');
        onRefresh();
      }
    }
  }, [marketStatus, onRefresh, refreshing]);

  return (
    <div className={`market-status ${marketStatus.isOpen ? 'market-open' : 'market-closed'}`}>
      <div className="market-status-indicator">
        <span className="status-dot"></span>
        <span className="status-text">{marketStatus.status}</span>
      </div>

      <div className="market-status-message">
        {marketStatus.message}
      </div>
    </div>
  );
};

export default MarketStatus;
