/**
 * Stock Predictions Dashboard
 * Main component displaying ML predictions with filters
 */
import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import MarketStatus from './MarketStatus';
import StockDetail from './StockDetail';
import { exportToCSV, exportToExcel } from '../utils/exportUtils';
import './Dashboard.css';

const Dashboard = () => {
  const [predictions, setPredictions] = useState([]);
  const [filteredPredictions, setFilteredPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [selectedStock, setSelectedStock] = useState(null);

  // Auto-refresh state
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(60); // seconds

  // Filters
  const [symbolFilter, setSymbolFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [directionFilter, setDirectionFilter] = useState('all');
  const [minConfidence, setMinConfidence] = useState(0);

  // Load predictions on mount
  useEffect(() => {
    loadPredictions();
  }, []);

  // Apply filters whenever they change
  useEffect(() => {
    applyFilters();
  }, [predictions, symbolFilter, typeFilter, directionFilter, minConfidence]);

  // Auto-refresh effect
  useEffect(() => {
    let interval = null;

    if (autoRefresh) {
      interval = setInterval(() => {
        console.log('Auto-refresh triggered');
        loadPredictions();
      }, refreshInterval * 1000); // Convert seconds to milliseconds
    }

    // Cleanup interval on unmount or when autoRefresh/refreshInterval changes
    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [autoRefresh, refreshInterval]);

  const loadPredictions = async () => {
    try {
      setLoading(true);
      const data = await apiService.getPredictions();
      setPredictions(data);
      setError(null);
    } catch (err) {
      setError('Failed to load predictions: ' + err.message);
      console.error('Error loading predictions:', err);
    } finally {
      setLoading(false);
    }
  };

  const refreshPrices = async () => {
    try {
      setRefreshing(true);
      const response = await apiService.refreshMarketPrices();

      // Reload predictions after price refresh
      await loadPredictions();

      alert(`Prices updated! ${response.successful} out of ${response.total} stocks refreshed.`);
    } catch (err) {
      alert('Error refreshing prices: ' + err.message);
    } finally {
      setRefreshing(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...predictions];

    // Symbol filter
    if (symbolFilter) {
      filtered = filtered.filter(p => 
        p.symbol.toLowerCase().includes(symbolFilter.toLowerCase())
      );
    }

    // Type filter
    if (typeFilter !== 'all') {
      filtered = filtered.filter(p => p.prediction_type === typeFilter);
    }

    // Direction filter
    if (directionFilter !== 'all') {
      filtered = filtered.filter(p => p.direction === directionFilter);
    }

    // Confidence filter
    if (minConfidence > 0) {
      filtered = filtered.filter(p => p.confidence >= minConfidence / 100);
    }

    setFilteredPredictions(filtered);
  };

  const handleExportToCSV = () => {
    exportToCSV(filteredPredictions, 'predictions');
  };

  const handleExportToExcel = () => {
    exportToExcel(filteredPredictions, 'predictions');
  };

  const getDirectionColor = (direction) => {
    if (direction === 'up') return 'green';
    if (direction === 'down') return 'red';
    return 'gray';
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.7) return 'high-confidence';
    if (confidence >= 0.5) return 'medium-confidence';
    return 'low-confidence';
  };

  if (loading) {
    return (
      <div className="dashboard">
        <div className="loading">Loading predictions...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard">
        <div className="error">{error}</div>
        <button onClick={loadPredictions}>Retry</button>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>📈 Stock Predictions Dashboard</h1>
        <p>AI-Powered Multi-Timeframe Stock Predictions</p>
      </header>

      <MarketStatus onRefresh={refreshPrices} refreshing={refreshing} />

      <div className="stats-bar">
        <div className="stat">
          <span className="stat-label">Total Predictions</span>
          <span className="stat-value">{predictions.length}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Filtered Results</span>
          <span className="stat-value">{filteredPredictions.length}</span>
        </div>
        <div className="stat">
          <span className="stat-label">High Confidence (&gt;70%)</span>
          <span className="stat-value">
            {predictions.filter(p => p.confidence >= 0.7).length}
          </span>
        </div>
        <div className="stat">
          <span className="stat-label">Bullish Signals</span>
          <span className="stat-value green">
            {predictions.filter(p => p.direction === 'up').length}
          </span>
        </div>
      </div>

      <div className="filters">
        <div className="filter-group">
          <label>🔍 Search Symbol:</label>
          <input
            type="text"
            placeholder="e.g., AAPL"
            value={symbolFilter}
            onChange={(e) => setSymbolFilter(e.target.value)}
          />
        </div>

        <div className="filter-group">
          <label>⏱️ Timeframe:</label>
          <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
            <option value="all">All Types</option>
            <option value="intraday">Intraday (1 day)</option>
            <option value="swing">Swing (5 days)</option>
            <option value="position">Position (20 days)</option>
          </select>
        </div>

        <div className="filter-group">
          <label>📊 Direction:</label>
          <select value={directionFilter} onChange={(e) => setDirectionFilter(e.target.value)}>
            <option value="all">All Directions</option>
            <option value="up">Bullish (UP)</option>
            <option value="down">Bearish (DOWN)</option>
          </select>
        </div>

        <div className="filter-group">
          <label>🎯 Min Confidence: {minConfidence}%</label>
          <input
            type="range"
            min="0"
            max="100"
            value={minConfidence}
            onChange={(e) => setMinConfidence(Number(e.target.value))}
          />
        </div>

        <div className="filter-group">
          <label>🔄 Auto-Refresh:</label>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={autoRefresh ? 'auto-refresh-btn active' : 'auto-refresh-btn'}
              style={{
                padding: '8px 16px',
                backgroundColor: autoRefresh ? '#10b981' : '#6b7280',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              {autoRefresh ? 'ON' : 'OFF'}
            </button>
            {autoRefresh && (
              <select
                value={refreshInterval}
                onChange={(e) => setRefreshInterval(Number(e.target.value))}
                style={{ padding: '8px' }}
              >
                <option value={30}>30 sec</option>
                <option value={60}>60 sec</option>
                <option value={120}>2 min</option>
                <option value={300}>5 min</option>
              </select>
            )}
          </div>
        </div>

        <div className="filter-actions">
          <button onClick={() => {
            setSymbolFilter('');
            setTypeFilter('all');
            setDirectionFilter('all');
            setMinConfidence(0);
          }}>
            Clear Filters
          </button>
          <button onClick={handleExportToCSV} className="export-btn">
            📥 Export to CSV
          </button>
          <button onClick={handleExportToExcel} className="export-btn excel-btn" style={{ backgroundColor: '#10b981' }}>
            📊 Export to Excel
          </button>
        </div>
      </div>

      <div className="table-container">
        <table className="predictions-table">
          <thead>
            <tr>
              <th>Symbol</th>
              <th>Type</th>
              <th>Direction</th>
              <th>Confidence</th>
              <th>Current Price</th>
              <th>Target Price</th>
              <th>Growth %</th>
              <th>Target Date</th>
            </tr>
          </thead>
          <tbody>
            {filteredPredictions.length === 0 ? (
              <tr>
                <td colSpan="8" style={{ textAlign: 'center', padding: '40px' }}>
                  No predictions match your filters
                </td>
              </tr>
            ) : (
              filteredPredictions.map((pred) => (
                <tr key={pred.id}>
                  <td
                    className="symbol"
                    onClick={() => setSelectedStock(pred.symbol)}
                    style={{ cursor: 'pointer' }}
                  >
                    {pred.symbol}
                  </td>
                  <td className="type">{pred.prediction_type}</td>
                  <td className="direction" style={{ color: getDirectionColor(pred.direction) }}>
                    {pred.direction.toUpperCase()} {pred.direction === 'up' ? '📈' : '📉'}
                  </td>
                  <td className={`confidence ${getConfidenceColor(pred.confidence)}`}>
                    {(pred.confidence * 100).toFixed(1)}%
                  </td>
                  <td className="price">${pred.current_price.toFixed(2)}</td>
                  <td className="price">${pred.target_price.toFixed(2)}</td>
                  <td 
                    className="growth"
                    style={{ color: pred.predicted_growth_percent >= 0 ? 'green' : 'red' }}
                  >
                    {pred.predicted_growth_percent >= 0 ? '+' : ''}
                    {pred.predicted_growth_percent.toFixed(2)}%
                  </td>
                  <td className="date">
                    {new Date(pred.target_date).toLocaleDateString()}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {selectedStock && (
        <StockDetail
          symbol={selectedStock}
          onClose={() => setSelectedStock(null)}
        />
      )}
    </div>
  );
};

export default Dashboard;
