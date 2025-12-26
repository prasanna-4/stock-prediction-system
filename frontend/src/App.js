import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import DashboardEnhanced from './components/DashboardEnhanced';
import Analytics from './components/Analytics';
import ModelPerformance from './components/ModelPerformance';
import './App.css';

function App() {
  const [activeView, setActiveView] = useState('dashboard');

  return (
    <div className="App">
      {/* Navigation Bar */}
      <nav className="app-nav">
        <div className="nav-container">
          <div className="nav-brand">
            <span className="brand-icon">📈</span>
            <span className="brand-text">Stock Prediction System</span>
          </div>
          <div className="nav-links">
            <button
    className={activeView === 'dashboard' ? 'nav-link active' : 'nav-link'}
    onClick={() => setActiveView('dashboard')}
  >
    📊 Classic View
  </button>
  <button
    className={activeView === 'enhanced' ? 'nav-link active' : 'nav-link'}
    onClick={() => setActiveView('enhanced')}
  >
    🚀 Trading Signals
  </button>
  <button
    className={activeView === 'analytics' ? 'nav-link active' : 'nav-link'}
    onClick={() => setActiveView('analytics')}
  >
    📈 Analytics
  </button>
  <button
    className={activeView === 'performance' ? 'nav-link active' : 'nav-link'}
    onClick={() => setActiveView('performance')}
  >
    🎯 Model Performance
  </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="app-content">
        {activeView === 'dashboard' && <Dashboard />}
         {activeView === 'enhanced' && <DashboardEnhanced />}
        {activeView === 'analytics' && <Analytics />}
        {activeView === 'performance' && <ModelPerformance />}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>© 2025 Stock Prediction System | Developed by LaxmiPrasanna Ravikanti</p>
      </footer>
    </div>
  );
}

export default App;
