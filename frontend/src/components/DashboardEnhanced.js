/**
 * Enhanced Stock Predictions Dashboard with BUY/EXIT Signals
 * Shows clear entry and exit points with real-time price refresh
 */
import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import MarketStatus from './MarketStatus';
import StockDetail from './StockDetail';
import { exportToCSV, exportToExcel } from '../utils/exportUtils';
import './DashboardEnhanced.css';

const DashboardEnhanced = () => {
  const [predictions, setPredictions] = useState([]);
  const [filteredPredictions, setFilteredPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [selectedStock, setSelectedStock] = useState(null);

  // Auto-refresh state
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(60); // seconds

  // Filter options from API
  const [availableSectors, setAvailableSectors] = useState([]);
  const [availableMarketCaps, setAvailableMarketCaps] = useState([]);

  // Filters
  const [symbolFilter, setSymbolFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [directionFilter, setDirectionFilter] = useState('all');
  const [minConfidence, setMinConfidence] = useState(0);
  const [signalFilter, setSignalFilter] = useState('all');
  const [sectorFilter, setSectorFilter] = useState('all');
  const [marketCapFilter, setMarketCapFilter] = useState('all');
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');

  useEffect(() => {
    loadPredictions();
    loadFilterOptions();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [predictions, symbolFilter, typeFilter, directionFilter, minConfidence, signalFilter, sectorFilter, marketCapFilter, minPrice, maxPrice]);

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

  const loadFilterOptions = async () => {
    try {
      const [sectorsResponse, marketCapsResponse] = await Promise.all([
        apiService.getAvailableSectors(),
        apiService.getMarketCapCategories()
      ]);
      // Extract arrays from response objects
      setAvailableSectors(sectorsResponse.sectors || []);
      setAvailableMarketCaps(marketCapsResponse.categories || []);
    } catch (err) {
      console.error('Error loading filter options:', err);
      setAvailableSectors([]);
      setAvailableMarketCaps([]);
    }
  };

  const loadPredictions = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getPredictions();
      
      // Validate data
      if (!Array.isArray(data)) {
        throw new Error('Invalid data format received');
      }
      
      // Filter out any invalid predictions
      const validPredictions = data.filter(p => 
        p && p.symbol && p.prediction_type && p.direction && typeof p.confidence === 'number'
      );
      
      if (validPredictions.length !== data.length) {
        console.warn(`Filtered out ${data.length - validPredictions.length} invalid predictions`);
      }
      
      setPredictions(validPredictions);
      setLastUpdated(new Date());
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
      
      alert(`✅ Prices updated! ${response.successful} out of ${response.total} stocks refreshed.`);
    } catch (err) {
      alert('❌ Error refreshing prices: ' + err.message);
    } finally {
      setRefreshing(false);
    }
  };

  const getSignalStatus = (pred) => {
    // Safely get values with defaults
    const currentPrice = pred.current_price || 0;
    const entryLow = pred.entry_price_low || (currentPrice * 0.99);
    const entryHigh = pred.entry_price_high || (currentPrice * 1.01);
    const targetPrice = pred.target_price || currentPrice;
    const confidence = pred.confidence || 0;
    
    // High confidence threshold
    const isHighConfidence = confidence >= 0.7;
    
    // Check if price is in buy zone
    const inBuyZone = currentPrice >= entryLow && currentPrice <= entryHigh;
    
    // Check if near target
    const nearTarget = targetPrice > 0 && Math.abs(currentPrice - targetPrice) / targetPrice < 0.05;
    
    if (nearTarget) {
      return { status: 'EXIT', color: 'signal-exit', icon: '🎯' };
    } else if (inBuyZone && isHighConfidence) {
      return { status: 'BUY NOW', color: 'signal-buy-strong', icon: '🚀' };
    } else if (inBuyZone) {
      return { status: 'BUY ZONE', color: 'signal-buy', icon: '✅' };
    } else if (isHighConfidence && pred.direction === 'up') {
      return { status: 'WATCH', color: 'signal-watch', icon: '👀' };
    } else {
      return { status: 'HOLD', color: 'signal-hold', icon: '⏸️' };
    }
  };

  const applyFilters = () => {
    let filtered = [...predictions];

    if (symbolFilter) {
      filtered = filtered.filter(p =>
        p.symbol.toLowerCase().includes(symbolFilter.toLowerCase())
      );
    }

    if (typeFilter !== 'all') {
      filtered = filtered.filter(p => p.prediction_type === typeFilter);
    }

    if (directionFilter !== 'all') {
      filtered = filtered.filter(p => p.direction === directionFilter);
    }

    if (minConfidence > 0) {
      filtered = filtered.filter(p => p.confidence >= minConfidence / 100);
    }

    if (signalFilter !== 'all') {
      filtered = filtered.filter(p => {
        const signal = getSignalStatus(p);
        return signal.status === signalFilter;
      });
    }

    if (sectorFilter !== 'all') {
      filtered = filtered.filter(p => p.sector === sectorFilter);
    }

    if (marketCapFilter !== 'all') {
      filtered = filtered.filter(p => p.market_cap_category === marketCapFilter);
    }

    if (minPrice !== '' && !isNaN(parseFloat(minPrice))) {
      filtered = filtered.filter(p => (p.current_price || 0) >= parseFloat(minPrice));
    }

    if (maxPrice !== '' && !isNaN(parseFloat(maxPrice))) {
      filtered = filtered.filter(p => (p.current_price || 0) <= parseFloat(maxPrice));
    }

    setFilteredPredictions(filtered);
  };

  const handleExportToCSV = () => {
    exportToCSV(filteredPredictions, 'stock_signals');
  };

  const handleExportToExcel = () => {
    exportToExcel(filteredPredictions, 'stock_signals');
  };

  const getDirectionColor = (direction) => {
    if (direction === 'up') return '#10b981';
    if (direction === 'down') return '#ef4444';
    return '#6b7280';
  };

  const getConfidenceClass = (confidence) => {
    if (confidence >= 0.7) return 'confidence-high';
    if (confidence >= 0.5) return 'confidence-medium';
    return 'confidence-low';
  };

  if (loading) {
    return (
      <div className="dashboard-enhanced">
        <div className="loading">⏳ Loading predictions...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-enhanced">
        <div className="error">{error}</div>
        <button onClick={loadPredictions}>Retry</button>
      </div>
    );
  }

  return (
    <div className="dashboard-enhanced">
      <header className="dashboard-header">
        <div className="header-content">
          <div>
            <h1>📊 Stock Trading Signals</h1>
            <p>AI-Powered Buy/Exit Recommendations with Real-Time Data</p>
          </div>
          <div className="header-actions">
            <button
              onClick={loadPredictions}
              className="refresh-btn"
              disabled={loading}
            >
              {loading ? '🔄 Refreshing...' : '🔄 Refresh'}
            </button>
            {lastUpdated && (
              <span className="last-updated">
                Updated: {lastUpdated.toLocaleTimeString()}
              </span>
            )}
          </div>
        </div>
      </header>

      <MarketStatus onRefresh={refreshPrices} refreshing={refreshing} />

      <div className="stats-bar">
        <div className="stat">
          <span className="stat-label">Total Signals</span>
          <span className="stat-value">{predictions.length}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Filtered Results</span>
          <span className="stat-value">{filteredPredictions.length}</span>
        </div>
        <div className="stat">
          <span className="stat-label">BUY NOW Signals</span>
          <span className="stat-value green">
            {predictions.filter(p => {
              try {
                return getSignalStatus(p).status === 'BUY NOW';
              } catch {
                return false;
              }
            }).length}
          </span>
        </div>
        <div className="stat">
          <span className="stat-label">High Confidence (&gt;70%)</span>
          <span className="stat-value">
            {predictions.filter(p => (p.confidence || 0) >= 0.7).length}
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
          <label>🎯 Signal Type:</label>
          <select value={signalFilter} onChange={(e) => setSignalFilter(e.target.value)}>
            <option value="all">All Signals</option>
            <option value="BUY NOW">🚀 BUY NOW</option>
            <option value="BUY ZONE">✅ BUY ZONE</option>
            <option value="WATCH">👀 WATCH</option>
            <option value="EXIT">🎯 EXIT</option>
            <option value="HOLD">⏸️ HOLD</option>
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
          <label>🏢 Sector:</label>
          <select value={sectorFilter} onChange={(e) => setSectorFilter(e.target.value)}>
            <option value="all">All Sectors</option>
            {availableSectors.map(sector => (
              <option key={sector} value={sector}>{sector}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>💰 Market Cap:</label>
          <select value={marketCapFilter} onChange={(e) => setMarketCapFilter(e.target.value)}>
            <option value="all">All Market Caps</option>
            {availableMarketCaps.map(cap => (
              <option key={cap.value} value={cap.value}>{cap.label}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>💵 Price Range:</label>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <input
              type="number"
              placeholder="Min"
              value={minPrice}
              onChange={(e) => setMinPrice(e.target.value)}
              style={{ width: '80px' }}
              min="0"
              step="0.01"
            />
            <span>-</span>
            <input
              type="number"
              placeholder="Max"
              value={maxPrice}
              onChange={(e) => setMaxPrice(e.target.value)}
              style={{ width: '80px' }}
              min="0"
              step="0.01"
            />
          </div>
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
            setSignalFilter('all');
            setSectorFilter('all');
            setMarketCapFilter('all');
            setMinPrice('');
            setMaxPrice('');
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
              <th>Signal</th>
              <th>Symbol</th>
              <th>Type</th>
              <th>Direction</th>
              <th>Confidence</th>
              <th>Sector</th>
              <th>Market Cap</th>
              <th colSpan="3" className="section-header buy-section">🟢 BUY SIGNAL</th>
              <th colSpan="3" className="section-header exit-section">🔴 EXIT SIGNAL</th>
            </tr>
            <tr>
              <th></th>
              <th></th>
              <th></th>
              <th></th>
              <th></th>
              <th></th>
              <th></th>
              <th>Current Price</th>
              <th>Entry Zone</th>
              <th>Entry Date</th>
              <th>Target Price</th>
              <th>Stop Loss</th>
              <th>Target Date</th>
            </tr>
          </thead>
          <tbody>
            {filteredPredictions.length === 0 ? (
              <tr>
                <td colSpan="13" style={{ textAlign: 'center', padding: '40px' }}>
                  No predictions match your filters
                </td>
              </tr>
            ) : (
              filteredPredictions.map((pred) => {
                const signal = getSignalStatus(pred);
                // Safely calculate missing values
                const currentPrice = pred.current_price || 0;
                const entryLow = pred.entry_price_low || (currentPrice * 0.99);
                const entryHigh = pred.entry_price_high || (currentPrice * 1.01);
                const targetPrice = pred.target_price || currentPrice;
                const stopLoss = pred.stop_loss_price || (pred.direction === 'up' ? currentPrice * 0.95 : currentPrice * 1.05);

                return (
                  <tr key={pred.id}>
                    <td className={`signal-badge ${signal.color}`}>
                      {signal.icon} {signal.status}
                    </td>
                    <td
                      className="symbol"
                      onClick={() => setSelectedStock(pred.symbol)}
                      style={{ cursor: 'pointer' }}
                    >
                      {pred.symbol}
                    </td>
                    <td className="type">{pred.prediction_type}</td>
                    <td style={{ color: getDirectionColor(pred.direction), fontWeight: '600' }}>
                      {pred.direction.toUpperCase()} {pred.direction === 'up' ? '📈' : '📉'}
                    </td>
                    <td className={getConfidenceClass(pred.confidence)}>
                      {((pred.confidence || 0) * 100).toFixed(1)}%
                    </td>
                    <td className="sector">{pred.sector || 'N/A'}</td>
                    <td className="market-cap">{pred.market_cap_category || 'N/A'}</td>
                    <td className="price">${currentPrice.toFixed(2)}</td>
                    <td className="entry-zone">
                      ${entryLow.toFixed(2)} - ${entryHigh.toFixed(2)}
                    </td>
                    <td className="date">{new Date().toLocaleDateString()}</td>
                    <td className="price target">${targetPrice.toFixed(2)}</td>
                    <td className="price stop-loss">${stopLoss.toFixed(2)}</td>
                    <td className="date">{new Date(pred.target_date).toLocaleDateString()}</td>
                  </tr>
                );
              })
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

export default DashboardEnhanced;