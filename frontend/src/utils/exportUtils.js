/**
 * Export Utilities
 * Functions for exporting data to CSV and Excel formats
 */
import * as XLSX from 'xlsx';

/**
 * Export predictions to CSV format
 */
export const exportToCSV = (predictions, filename = 'stock_predictions') => {
  const headers = [
    'Symbol', 'Type', 'Direction', 'Confidence %', 'Signal',
    'Current Price', 'Entry Low', 'Entry High', 'Target Price',
    'Stop Loss', 'Growth %', 'Sector', 'Market Cap',
    'Market Cap Category', 'Entry Date', 'Target Date'
  ];

  const rows = predictions.map(p => {
    const signal = p.signal || 'N/A';
    const currentPrice = p.current_price || 0;
    const entryLow = p.entry_price_low || (currentPrice * 0.99);
    const entryHigh = p.entry_price_high || (currentPrice * 1.01);

    return [
      p.symbol,
      p.prediction_type,
      p.direction,
      (p.confidence * 100).toFixed(1),
      signal,
      currentPrice.toFixed(2),
      entryLow.toFixed(2),
      entryHigh.toFixed(2),
      (p.target_price || 0).toFixed(2),
      (p.stop_loss_price || 0).toFixed(2),
      (p.predicted_growth_percent || 0).toFixed(2),
      p.sector || 'N/A',
      p.market_cap ? `$${(p.market_cap / 1e9).toFixed(2)}B` : 'N/A',
      p.market_cap_category || 'N/A',
      p.prediction_date ? new Date(p.prediction_date).toLocaleDateString() : 'N/A',
      p.target_date ? new Date(p.target_date).toLocaleDateString() : 'N/A'
    ];
  });

  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);

  link.setAttribute('href', url);
  link.setAttribute('download', `${filename}_${new Date().toISOString().split('T')[0]}.csv`);
  link.style.visibility = 'hidden';

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

/**
 * Export predictions to Excel format (.xlsx)
 */
export const exportToExcel = (predictions, filename = 'stock_predictions') => {
  // Prepare data for Excel
  const data = predictions.map(p => ({
    'Symbol': p.symbol,
    'Type': p.prediction_type,
    'Direction': p.direction,
    'Confidence %': (p.confidence * 100).toFixed(1),
    'Signal': p.signal || 'N/A',
    'Current Price': p.current_price?.toFixed(2) || 0,
    'Entry Low': (p.entry_price_low || p.current_price * 0.99)?.toFixed(2),
    'Entry High': (p.entry_price_high || p.current_price * 1.01)?.toFixed(2),
    'Target Price': p.target_price?.toFixed(2) || 0,
    'Stop Loss': p.stop_loss_price?.toFixed(2) || 0,
    'Growth %': p.predicted_growth_percent?.toFixed(2) || 0,
    'Sector': p.sector || 'N/A',
    'Industry': p.industry || 'N/A',
    'Market Cap': p.market_cap ? `$${(p.market_cap / 1e9).toFixed(2)}B` : 'N/A',
    'Market Cap Category': p.market_cap_category || 'N/A',
    'Entry Date': p.prediction_date ? new Date(p.prediction_date).toLocaleDateString() : 'N/A',
    'Target Date': p.target_date ? new Date(p.target_date).toLocaleDateString() : 'N/A'
  }));

  // Create workbook and worksheet
  const wb = XLSX.utils.book_new();
  const ws = XLSX.utils.json_to_sheet(data);

  // Set column widths
  const colWidths = [
    { wch: 8 },  // Symbol
    { wch: 10 }, // Type
    { wch: 10 }, // Direction
    { wch: 12 }, // Confidence
    { wch: 10 }, // Signal
    { wch: 12 }, // Current Price
    { wch: 12 }, // Entry Low
    { wch: 12 }, // Entry High
    { wch: 12 }, // Target Price
    { wch: 12 }, // Stop Loss
    { wch: 10 }, // Growth %
    { wch: 20 }, // Sector
    { wch: 25 }, // Industry
    { wch: 15 }, // Market Cap
    { wch: 18 }, // Market Cap Category
    { wch: 12 }, // Entry Date
    { wch: 12 }  // Target Date
  ];
  ws['!cols'] = colWidths;

  // Add worksheet to workbook
  XLSX.utils.book_append_sheet(wb, ws, 'Predictions');

  // Create summary sheet
  const summary = [
    { Metric: 'Total Predictions', Value: predictions.length },
    { Metric: 'Bullish (Up)', Value: predictions.filter(p => p.direction === 'up').length },
    { Metric: 'Bearish (Down)', Value: predictions.filter(p => p.direction === 'down').length },
    { Metric: 'High Confidence (>70%)', Value: predictions.filter(p => p.confidence >= 0.7).length },
    { Metric: 'Intraday', Value: predictions.filter(p => p.prediction_type === 'intraday').length },
    { Metric: 'Swing', Value: predictions.filter(p => p.prediction_type === 'swing').length },
    { Metric: 'Position', Value: predictions.filter(p => p.prediction_type === 'position').length },
    { Metric: 'Avg Confidence', Value: `${(predictions.reduce((sum, p) => sum + p.confidence, 0) / predictions.length * 100).toFixed(1)}%` },
    { Metric: 'Avg Predicted Growth', Value: `${(predictions.reduce((sum, p) => sum + (p.predicted_growth_percent || 0), 0) / predictions.length).toFixed(2)}%` }
  ];

  const wsSummary = XLSX.utils.json_to_sheet(summary);
  wsSummary['!cols'] = [{ wch: 25 }, { wch: 20 }];
  XLSX.utils.book_append_sheet(wb, wsSummary, 'Summary');

  // Generate Excel file
  XLSX.writeFile(wb, `${filename}_${new Date().toISOString().split('T')[0]}.xlsx`);
};

/**
 * Export model performance data to Excel
 */
export const exportPerformanceToExcel = (performanceData, filename = 'model_performance') => {
  if (!performanceData || performanceData.length === 0) {
    alert('No performance data to export');
    return;
  }

  const wb = XLSX.utils.book_new();

  // Performance metrics sheet
  const metricsData = performanceData.map(p => ({
    'Model': `${p.model_name} v${p.model_version}`,
    'Prediction Type': p.prediction_type,
    'Total Predictions': p.total_predictions,
    'Correct Predictions': p.correct_predictions,
    'Accuracy %': (p.accuracy * 100).toFixed(2),
    'Win Rate %': (p.win_rate * 100).toFixed(2),
    'Avg Profit %': p.avg_profit_percent?.toFixed(2) || 'N/A',
    'Avg Loss %': p.avg_loss_percent?.toFixed(2) || 'N/A',
    'Sharpe Ratio': p.sharpe_ratio?.toFixed(2) || 'N/A',
    'Max Drawdown %': p.max_drawdown?.toFixed(2) || 'N/A',
    'Evaluation Start': p.evaluation_start_date ? new Date(p.evaluation_start_date).toLocaleDateString() : 'N/A',
    'Evaluation End': p.evaluation_end_date ? new Date(p.evaluation_end_date).toLocaleDateString() : 'N/A'
  }));

  const wsMetrics = XLSX.utils.json_to_sheet(metricsData);
  wsMetrics['!cols'] = [
    { wch: 20 }, { wch: 15 }, { wch: 18 }, { wch: 18 },
    { wch: 12 }, { wch: 12 }, { wch: 12 }, { wch: 12 },
    { wch: 12 }, { wch: 15 }, { wch: 15 }, { wch: 15 }
  ];

  XLSX.utils.book_append_sheet(wb, wsMetrics, 'Performance Metrics');

  XLSX.writeFile(wb, `${filename}_${new Date().toISOString().split('T')[0]}.xlsx`);
};
