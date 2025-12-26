/**
 * Stock Detail View Component
 * Displays detailed information for a single stock with all predictions
 */
import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import './StockDetail.css';

const StockDetail = ({ symbol, onClose }) => {
  const [stockData, setStockData] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedType, setSelectedType] = useState('all');

  useEffect(() => {
    if (symbol) {
      loadStockDetails();
    }
  }, [symbol]);

  const loadStockDetails = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch predictions for this stock
      const data = await apiService.getPredictions({ symbol });

      if (data && data.length > 0) {
        setPredictions(data);
        setStockData({
          symbol: data[0].symbol,
          sector: data[0].sector,
          industry: data[0].industry,
          market_cap: data[0].market_cap,
          market_cap_category: data[0].market_cap_category,
          current_price: data[0].current_price
        });
      } else {
        setError(`No predictions found for ${symbol}`);
      }
    } catch (err) {
      setError('Failed to load stock details');
      console.error('Error loading stock details:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredPredictions = selectedType === 'all'
    ? predictions
    : predictions.filter(p => p.prediction_type === selectedType);

  const getDirectionColor = (direction) => {
    return direction === 'up' ? '#10b981' : '#ef4444';
  };

  const getSignalBadge = (pred) => {
    const currentPrice = pred.current_price || 0;
    const entryLow = pred.entry_price_low || (currentPrice * 0.99);
    const entryHigh = pred.entry_price_high || (currentPrice * 1.01);
    const confidence = pred.confidence || 0;

    const isHighConfidence = confidence >= 0.7;
    const inBuyZone = currentPrice >= entryLow && currentPrice <= entryHigh;

    if (inBuyZone && isHighConfidence) {
      return { text: 'BUY NOW', class: 'signal-buy-now' };
    } else if (inBuyZone) {
      return { text: 'BUY ZONE', class: 'signal-buy-zone' };
    } else if (isHighConfidence && pred.direction === 'up') {
      return { text: 'WATCH', class: 'signal-watch' };
    } else {
      return { text: 'HOLD', class: 'signal-hold' };
    }
  };

  if (loading) {
    return (
      <div className="stock-detail-overlay">
        <div className="stock-detail-modal">
          <div className="loading">Loading stock details...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="stock-detail-overlay" onClick={onClose}>
        <div className="stock-detail-modal" onClick={e => e.stopPropagation()}>
          <button className="close-btn" onClick={onClose}>✕</button>
          <div className="error">{error}</div>
        </div>
      </div>
    );
  }

  if (!stockData) {
    return null;
  }

  const stats = {
    total: predictions.length,
    bullish: predictions.filter(p => p.direction === 'up').length,
    bearish: predictions.filter(p => p.direction === 'down').length,
    highConfidence: predictions.filter(p => p.confidence >= 0.7).length,
    avgConfidence: predictions.reduce((sum, p) => sum + p.confidence, 0) / predictions.length,
    avgGrowth: predictions.reduce((sum, p) => sum + (p.predicted_growth_percent || 0), 0) / predictions.length
  };

  return (
    <div className="stock-detail-overlay" onClick={onClose}>
      <div className="stock-detail-modal" onClick={e => e.stopPropagation()}>
        <button className="close-btn" onClick={onClose}>✕</button>

        {/* Header */}
        <div className="stock-header">
          <div className="stock-title">
            <h1>{stockData.symbol}</h1>
            <div className="stock-meta">
              {stockData.sector && <span className="sector-badge">{stockData.sector}</span>}
              {stockData.market_cap_category && (
                <span className="market-cap-badge">{stockData.market_cap_category}</span>
              )}
            </div>
          </div>
          <div className="stock-price">
            <div className="price-label">Current Price</div>
            <div className="price-value">${stockData.current_price?.toFixed(2)}</div>
            {stockData.market_cap && (
              <div className="market-cap-value">
                Market Cap: ${(stockData.market_cap / 1e9).toFixed(2)}B
              </div>
            )}
          </div>
        </div>

        {/* Statistics */}
        <div className="stock-stats">
          <div className="stat-item">
            <div className="stat-label">Total Predictions</div>
            <div className="stat-value">{stats.total}</div>
          </div>
          <div className="stat-item bullish">
            <div className="stat-label">Bullish</div>
            <div className="stat-value">{stats.bullish}</div>
          </div>
          <div className="stat-item bearish">
            <div className="stat-label">Bearish</div>
            <div className="stat-value">{stats.bearish}</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">High Confidence</div>
            <div className="stat-value">{stats.highConfidence}</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">Avg Confidence</div>
            <div className="stat-value">{(stats.avgConfidence * 100).toFixed(1)}%</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">Avg Growth</div>
            <div className="stat-value">{stats.avgGrowth.toFixed(2)}%</div>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="prediction-filter">
          <button
            className={selectedType === 'all' ? 'filter-tab active' : 'filter-tab'}
            onClick={() => setSelectedType('all')}
          >
            All ({predictions.length})
          </button>
          <button
            className={selectedType === 'intraday' ? 'filter-tab active' : 'filter-tab'}
            onClick={() => setSelectedType('intraday')}
          >
            Intraday ({predictions.filter(p => p.prediction_type === 'intraday').length})
          </button>
          <button
            className={selectedType === 'swing' ? 'filter-tab active' : 'filter-tab'}
            onClick={() => setSelectedType('swing')}
          >
            Swing ({predictions.filter(p => p.prediction_type === 'swing').length})
          </button>
          <button
            className={selectedType === 'position' ? 'filter-tab active' : 'filter-tab'}
            onClick={() => setSelectedType('position')}
          >
            Position ({predictions.filter(p => p.prediction_type === 'position').length})
          </button>
        </div>

        {/* Predictions List */}
        <div className="predictions-list">
          {filteredPredictions.length === 0 ? (
            <div className="no-predictions">No {selectedType} predictions available</div>
          ) : (
            filteredPredictions.map((pred, idx) => {
              const signal = getSignalBadge(pred);
              return (
                <div key={idx} className="prediction-card">
                  <div className="prediction-header">
                    <div className="prediction-type">
                      {pred.prediction_type.toUpperCase()}
                    </div>
                    <div className={`signal-badge ${signal.class}`}>
                      {signal.text}
                    </div>
                  </div>

                  <div className="prediction-body">
                    <div className="prediction-row">
                      <div className="prediction-col">
                        <div className="label">Direction</div>
                        <div
                          className="value direction"
                          style={{ color: getDirectionColor(pred.direction) }}
                        >
                          {pred.direction === 'up' ? '📈 UP' : '📉 DOWN'}
                        </div>
                      </div>
                      <div className="prediction-col">
                        <div className="label">Confidence</div>
                        <div className="value confidence">
                          {(pred.confidence * 100).toFixed(1)}%
                        </div>
                      </div>
                      <div className="prediction-col">
                        <div className="label">Growth</div>
                        <div
                          className="value"
                          style={{ color: getDirectionColor(pred.direction) }}
                        >
                          {pred.predicted_growth_percent > 0 ? '+' : ''}
                          {pred.predicted_growth_percent?.toFixed(2)}%
                        </div>
                      </div>
                    </div>

                    <div className="prediction-row">
                      <div className="prediction-col">
                        <div className="label">Entry Zone</div>
                        <div className="value">
                          ${(pred.entry_price_low || pred.current_price * 0.99).toFixed(2)} -
                          ${(pred.entry_price_high || pred.current_price * 1.01).toFixed(2)}
                        </div>
                      </div>
                      <div className="prediction-col">
                        <div className="label">Target Price</div>
                        <div className="value target">
                          ${pred.target_price?.toFixed(2)}
                        </div>
                      </div>
                      <div className="prediction-col">
                        <div className="label">Stop Loss</div>
                        <div className="value stop-loss">
                          ${pred.stop_loss_price?.toFixed(2)}
                        </div>
                      </div>
                    </div>

                    <div className="prediction-row">
                      <div className="prediction-col">
                        <div className="label">Entry Date</div>
                        <div className="value date">
                          {new Date(pred.prediction_date).toLocaleDateString()}
                        </div>
                      </div>
                      <div className="prediction-col">
                        <div className="label">Target Date</div>
                        <div className="value date">
                          {new Date(pred.target_date).toLocaleDateString()}
                        </div>
                      </div>
                      <div className="prediction-col">
                        <div className="label">Status</div>
                        <div className={`value status status-${pred.status}`}>
                          {pred.status}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};

export default StockDetail;
