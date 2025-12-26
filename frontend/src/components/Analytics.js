/**
 * Analytics Dashboard - Power BI Style
 * Charts and visualizations for prediction insights
 */
import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import {
  BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import './Analytics.css';

const Analytics = () => {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState('overview');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await apiService.getPredictions();
      setPredictions(data);
    } catch (err) {
      console.error('Error loading analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  // Calculate stats
  const getTimeframeDistribution = () => {
    const dist = { intraday: 0, swing: 0, position: 0 };
    predictions.forEach(p => {
      dist[p.prediction_type] = (dist[p.prediction_type] || 0) + 1;
    });
    return [
      { name: 'Intraday (1 day)', value: dist.intraday, color: '#8b5cf6' },
      { name: 'Swing (5 days)', value: dist.swing, color: '#3b82f6' },
      { name: 'Position (20 days)', value: dist.position, color: '#10b981' }
    ];
  };

  const getDirectionDistribution = () => {
    const dist = { up: 0, down: 0, neutral: 0 };
    predictions.forEach(p => {
      dist[p.direction] = (dist[p.direction] || 0) + 1;
    });
    return [
      { name: 'Bullish (UP)', value: dist.up, color: '#10b981' },
      { name: 'Bearish (DOWN)', value: dist.down, color: '#ef4444' },
      { name: 'Neutral', value: dist.neutral, color: '#6b7280' }
    ];
  };

  const getConfidenceDistribution = () => {
    const ranges = [
      { name: '0-30%', min: 0, max: 0.3, count: 0 },
      { name: '30-50%', min: 0.3, max: 0.5, count: 0 },
      { name: '50-70%', min: 0.5, max: 0.7, count: 0 },
      { name: '70-90%', min: 0.7, max: 0.9, count: 0 },
      { name: '90-100%', min: 0.9, max: 1.0, count: 0 }
    ];

    predictions.forEach(p => {
      const range = ranges.find(r => p.confidence >= r.min && p.confidence < r.max);
      if (range) range.count++;
    });

    return ranges;
  };

  const getTopPredictions = () => {
    return [...predictions]
      .sort((a, b) => b.confidence - a.confidence)
      .slice(0, 10);
  };

  const getSectorPerformance = () => {
    const sectors = {};
    predictions.forEach(p => {
      if (!sectors[p.symbol]) {
        sectors[p.symbol] = {
          symbol: p.symbol,
          avgConfidence: 0,
          predictions: [],
          avgGrowth: 0
        };
      }
      sectors[p.symbol].predictions.push(p);
    });

    return Object.values(sectors).map(s => ({
      symbol: s.symbol,
      avgConfidence: (s.predictions.reduce((sum, p) => sum + p.confidence, 0) / s.predictions.length * 100).toFixed(1),
      avgGrowth: (s.predictions.reduce((sum, p) => sum + p.predicted_growth_percent, 0) / s.predictions.length).toFixed(2),
      count: s.predictions.length
    })).sort((a, b) => b.avgConfidence - a.avgConfidence).slice(0, 15);
  };

  const COLORS = ['#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444'];

  if (loading) {
    return <div className="analytics-loading">Loading analytics...</div>;
  }

  return (
    <div className="analytics-dashboard">
      <div className="analytics-header">
        <h1>📊 Advanced Analytics</h1>
        <p>Power BI-Style Market Intelligence Dashboard</p>
      </div>

      {/* View Selector */}
      <div className="view-selector">
        <button
          className={activeView === 'overview' ? 'active' : ''}
          onClick={() => setActiveView('overview')}
        >
          📈 Overview
        </button>
        <button
          className={activeView === 'distribution' ? 'active' : ''}
          onClick={() => setActiveView('distribution')}
        >
          📊 Distribution
        </button>
        <button
          className={activeView === 'top-picks' ? 'active' : ''}
          onClick={() => setActiveView('top-picks')}
        >
          🏆 Top Picks
        </button>
      </div>

      {/* Overview View */}
      {activeView === 'overview' && (
        <div className="analytics-grid">
          {/* Timeframe Distribution */}
          <div className="chart-card">
            <h3>⏱️ Prediction Timeframe Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={getTimeframeDistribution()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#8b5cf6">
                  {getTimeframeDistribution().map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Direction Distribution */}
          <div className="chart-card">
            <h3>📊 Market Sentiment (Direction)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={getDirectionDistribution()}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {getDirectionDistribution().map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Confidence Distribution */}
          <div className="chart-card full-width">
            <h3>🎯 Confidence Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={getConfidenceDistribution()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Area type="monotone" dataKey="count" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.6} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Distribution View */}
      {activeView === 'distribution' && (
        <div className="analytics-grid">
          <div className="chart-card full-width">
            <h3>📈 Stock Performance Overview</h3>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={getSectorPerformance()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="symbol" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Bar yAxisId="left" dataKey="avgConfidence" fill="#8b5cf6" name="Avg Confidence %" />
                <Bar yAxisId="right" dataKey="avgGrowth" fill="#10b981" name="Avg Growth %" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Key Metrics */}
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-icon">📊</div>
              <div className="metric-value">
                {(predictions.reduce((sum, p) => sum + p.confidence, 0) / predictions.length * 100).toFixed(1)}%
              </div>
              <div className="metric-label">Average Confidence</div>
            </div>

            <div className="metric-card">
              <div className="metric-icon">📈</div>
              <div className="metric-value">
                {(predictions.reduce((sum, p) => sum + p.predicted_growth_percent, 0) / predictions.length).toFixed(2)}%
              </div>
              <div className="metric-label">Average Predicted Growth</div>
            </div>

            <div className="metric-card">
              <div className="metric-icon">🎯</div>
              <div className="metric-value">
                {predictions.filter(p => p.confidence >= 0.7).length}
              </div>
              <div className="metric-label">High Confidence Signals</div>
            </div>

            <div className="metric-card">
              <div className="metric-icon">🚀</div>
              <div className="metric-value">
                {predictions.filter(p => p.direction === 'up' && p.confidence >= 0.7).length}
              </div>
              <div className="metric-label">Strong Buy Signals</div>
            </div>
          </div>
        </div>
      )}

      {/* Top Picks View */}
      {activeView === 'top-picks' && (
        <div className="top-picks-container">
          <div className="chart-card">
            <h3>🏆 Top 10 Highest Confidence Predictions</h3>
            <div className="top-picks-table">
              <table>
                <thead>
                  <tr>
                    <th>Rank</th>
                    <th>Symbol</th>
                    <th>Type</th>
                    <th>Direction</th>
                    <th>Confidence</th>
                    <th>Growth %</th>
                    <th>Target Price</th>
                  </tr>
                </thead>
                <tbody>
                  {getTopPredictions().map((pred, idx) => (
                    <tr key={pred.id} className={idx < 3 ? 'highlight' : ''}>
                      <td className="rank">
                        {idx === 0 && '🥇'}
                        {idx === 1 && '🥈'}
                        {idx === 2 && '🥉'}
                        {idx > 2 && `#${idx + 1}`}
                      </td>
                      <td className="symbol">{pred.symbol}</td>
                      <td>{pred.prediction_type}</td>
                      <td className={`direction ${pred.direction}`}>
                        {pred.direction.toUpperCase()} {pred.direction === 'up' ? '📈' : '📉'}
                      </td>
                      <td className="confidence-high">{(pred.confidence * 100).toFixed(1)}%</td>
                      <td className={pred.predicted_growth_percent >= 0 ? 'positive' : 'negative'}>
                        {pred.predicted_growth_percent >= 0 ? '+' : ''}
                        {pred.predicted_growth_percent.toFixed(2)}%
                      </td>
                      <td className="price">${pred.target_price.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Analytics;
