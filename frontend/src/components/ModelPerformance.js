/**
 * Model Performance Dashboard
 * Displays ML model accuracy metrics and performance statistics
 */
import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { exportPerformanceToExcel } from '../utils/exportUtils';
import './ModelPerformance.css';

const ModelPerformance = () => {
  const [performance, setPerformance] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadPerformance();
  }, []);

  const loadPerformance = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getModelPerformance();
      setPerformance(Array.isArray(data) ? data : []);
    } catch (err) {
      setError('Failed to load model performance data');
      console.error('Error loading performance:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="performance-container">
        <div className="loading">Loading model performance data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="performance-container">
        <div className="error">{error}</div>
      </div>
    );
  }

  // Prepare data for charts
  const accuracyData = performance.map(p => ({
    name: `${p.prediction_type} (${p.model_name})`,
    accuracy: (p.accuracy * 100).toFixed(1),
    predictions: p.total_predictions
  }));

  const winRateData = performance.map(p => ({
    name: p.prediction_type,
    'Win Rate': (p.win_rate * 100).toFixed(1),
    'Avg Profit': p.avg_profit_percent?.toFixed(2) || 0,
    'Avg Loss': Math.abs(p.avg_loss_percent || 0).toFixed(2)
  }));

  const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

  const handleExportToExcel = () => {
    exportPerformanceToExcel(performance, 'model_performance');
  };

  return (
    <div className="performance-container">
      <header className="performance-header">
        <div>
          <h1>📊 Model Performance Dashboard</h1>
          <p>ML model accuracy metrics and prediction statistics</p>
        </div>
        {performance.length > 0 && (
          <button onClick={handleExportToExcel} className="export-btn" style={{ backgroundColor: '#10b981', color: 'white', padding: '10px 20px', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '14px', fontWeight: '500' }}>
            📗 Export to Excel
          </button>
        )}
      </header>

      {performance.length === 0 ? (
        <div className="no-data">
          <p>No performance data available yet.</p>
          <p>Performance metrics will be calculated once predictions are evaluated.</p>
        </div>
      ) : (
        <>
          {/* Summary Cards */}
          <div className="stats-grid">
            {performance.map((perf, idx) => (
              <div key={idx} className="stat-card">
                <div className="stat-header">
                  <h3>{perf.prediction_type.toUpperCase()}</h3>
                  <span className="model-badge">{perf.model_name} v{perf.model_version}</span>
                </div>
                <div className="stat-metrics">
                  <div className="metric">
                    <span className="metric-label">Accuracy</span>
                    <span className="metric-value accuracy">
                      {(perf.accuracy * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Win Rate</span>
                    <span className="metric-value win-rate">
                      {(perf.win_rate * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Total Predictions</span>
                    <span className="metric-value">{perf.total_predictions}</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Correct</span>
                    <span className="metric-value correct">{perf.correct_predictions}</span>
                  </div>
                </div>
                <div className="stat-financials">
                  <div className="financial-metric">
                    <span>Avg Profit:</span>
                    <span className="profit">+{perf.avg_profit_percent?.toFixed(2) || 0}%</span>
                  </div>
                  <div className="financial-metric">
                    <span>Avg Loss:</span>
                    <span className="loss">{perf.avg_loss_percent?.toFixed(2) || 0}%</span>
                  </div>
                  {perf.sharpe_ratio && (
                    <div className="financial-metric">
                      <span>Sharpe Ratio:</span>
                      <span>{perf.sharpe_ratio.toFixed(2)}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Charts */}
          <div className="charts-grid">
            {/* Accuracy Chart */}
            <div className="chart-card">
              <h3>Model Accuracy by Type</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={accuracyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-20} textAnchor="end" height={80} />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="accuracy" fill="#10b981" name="Accuracy %" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Win Rate Chart */}
            <div className="chart-card">
              <h3>Financial Performance</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={winRateData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="Win Rate" fill="#3b82f6" name="Win Rate %" />
                  <Bar dataKey="Avg Profit" fill="#10b981" name="Avg Profit %" />
                  <Bar dataKey="Avg Loss" fill="#ef4444" name="Avg Loss %" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Total Predictions Pie Chart */}
            <div className="chart-card">
              <h3>Predictions Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={performance}
                    dataKey="total_predictions"
                    nameKey="prediction_type"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label={(entry) => `${entry.prediction_type}: ${entry.total_predictions}`}
                  >
                    {performance.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Correct vs Incorrect */}
            <div className="chart-card">
              <h3>Prediction Accuracy Breakdown</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={performance.map(p => ({
                    name: p.prediction_type,
                    Correct: p.correct_predictions,
                    Incorrect: p.total_predictions - p.correct_predictions
                  }))}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="Correct" stackId="a" fill="#10b981" />
                  <Bar dataKey="Incorrect" stackId="a" fill="#ef4444" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Evaluation Period */}
          {performance.length > 0 && performance[0].evaluation_start_date && (
            <div className="evaluation-period">
              <p>
                Evaluation Period: {new Date(performance[0].evaluation_start_date).toLocaleDateString()} to{' '}
                {new Date(performance[0].evaluation_end_date).toLocaleDateString()}
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ModelPerformance;
