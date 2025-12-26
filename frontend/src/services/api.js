/**
 * API Configuration and Helper Functions
 */
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';
const API_KEY = 'dev-api-key-12345';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'x-api-key': API_KEY
  }
});

// API Functions
export const apiService = {
  // Get all predictions
  getPredictions: async (params = {}) => {
    const response = await api.get('/predictions', { params });
    return response.data;
  },

  // Get predictions by symbol
  getPredictionsBySymbol: async (symbol) => {
    const response = await api.get('/predictions', {
      params: { symbol }
    });
    return response.data;
  },

  // Get predictions by type
  getPredictionsByType: async (predictionType) => {
    const response = await api.get('/predictions', {
      params: { prediction_type: predictionType }
    });
    return response.data;
  },

  // Get high confidence predictions
  getHighConfidencePredictions: async (minConfidence = 0.7) => {
    const response = await api.get('/predictions', {
      params: { min_confidence: minConfidence }
    });
    return response.data;
  },

  // Get all stocks
  getStocks: async () => {
    const response = await api.get('/stocks');
    return response.data;
  },

  // Get stock by symbol
  getStock: async (symbol) => {
    const response = await api.get(`/stocks/${symbol}`);
    return response.data;
  },

  // Health check
  getHealth: async () => {
    const response = await axios.get('http://localhost:8000/api/v1/health');
    return response.data;
  },

  // Refresh market prices
  refreshMarketPrices: async () => {
    const response = await api.post('/market/refresh-prices');
    return response.data;
  },

  // Get current price for a stock
  getCurrentPrice: async (symbol) => {
    const response = await api.get(`/market/current-price/${symbol}`);
    return response.data;
  },

  // Get market status
  getMarketStatus: async () => {
    const response = await api.get('/market/market-status');
    return response.data;
  },

  // Get available sectors for filtering
  getAvailableSectors: async () => {
    const response = await api.get('/predictions/filters/sectors');
    return response.data;
  },

  // Get market cap categories for filtering
  getMarketCapCategories: async () => {
    const response = await api.get('/predictions/filters/market-caps');
    return response.data;
  },

  // Get model performance metrics
  getModelPerformance: async () => {
    const response = await api.get('/performance');
    return response.data;
  }
};

export default api;

