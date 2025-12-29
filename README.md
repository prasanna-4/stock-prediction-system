# Stock Prediction System

**AI-Powered Stock Market Prediction Tool for US Markets**

A full-stack machine learning application that analyzes and predicts stock price movements for major US stocks and ETFs using ensemble ML models (XGBoost + LightGBM) with 50+ technical indicators.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.13-green)
![React](https://img.shields.io/badge/react-19.2.3-blue)
![FastAPI](https://img.shields.io/badge/fastapi-latest-teal)

---

## 🌟 Key Features

### 📊 **Comprehensive Stock Coverage**
- **S&P 500** - Large-cap stocks
- **NASDAQ-100** - Tech and growth stocks
- **Dow Jones 30** - Blue-chip industrial stocks
- **Russell 2000** - Small-cap stocks
- **Popular ETFs** - SPY, QQQ, sector ETFs, and more
- **Total Coverage:** 339+ stocks and ETFs

### 🤖 **Multi-Timeframe ML Predictions**
Three distinct trading strategies with separate models:

1. **Intraday** (1 trading day, 1% target)
2. **Swing** (5 trading days, 2% target)
3. **Position** (20 trading days, 5% target)

### 🎯 **Advanced Features**
- ✅ Real-time price updates with market hours indicator
- ✅ Auto-refresh functionality (configurable intervals)
- ✅ Advanced filtering (sector, market cap, price range, confidence, signals)
- ✅ Trading signals (BUY NOW, BUY ZONE, WATCH, EXIT, HOLD)
- ✅ Entry zones, target prices, and stop losses
- ✅ Model performance dashboard with accuracy metrics
- ✅ Email alerts for high-confidence predictions
- ✅ CSV and Excel export functionality
- ✅ Individual stock detail view
- ✅ Power BI-style analytics dashboard

### 📈 **Technical Analysis**
50+ technical indicators including:
- Price Features (returns, momentum, spreads)
- Momentum Indicators (RSI, Stochastic, ROC, Williams %R)
- Trend Indicators (SMA/EMA, MACD, ADX)
- Volatility Indicators (Bollinger Bands, ATR)
- Volume Features (OBV, volume ratios, VPT)
- Pattern Recognition (Doji, Hammer, Gaps)

---

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI (Python)
- **Database:** SQLite with SQLAlchemy ORM (PostgreSQL supported)
- **ML Libraries:** XGBoost, LightGBM, scikit-learn
- **Technical Analysis:** TA-Lib wrapper
- **Data Source:** Yahoo Finance (yfinance)
- **Server:** Uvicorn ASGI

### Frontend
- **Framework:** React 19.2.3
- **Routing:** React Router DOM
- **Charts:** Recharts
- **HTTP Client:** Axios
- **Styling:** Custom CSS

---

## 📋 Prerequisites

- **Python** 3.10+ (tested on 3.13)
- **Node.js** 16+ and npm
- **Git**

---

## 🚀 Installation & Setup

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd StockPrediction
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Configure Environment Variables

The `.env` file is already configured to use SQLite (no database installation required):

```env
# Database (SQLite - no installation required)
DATABASE_URL=sqlite:///./stock_predictions.db

# Email Alerts (Optional - for Gmail SMTP)
ALERT_EMAIL=your-email@gmail.com
ALERT_PASSWORD=your-app-password
RECIPIENT_EMAIL=recipient@gmail.com

# Stock Universe
STOCK_UNIVERSE=ALL  # Options: SP500, RUSSELL1000, ALL
```

**For PostgreSQL (Optional):** If you prefer PostgreSQL, update DATABASE_URL:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/stock_predictions
```

**Note:** For Gmail alerts, you need an "App Password":
1. Enable 2-Factor Authentication
2. Go to https://myaccount.google.com/apppasswords
3. Generate app password and use it in `.env`

#### Initialize Database

The database and stock data **initialize automatically** when you start the backend for the first time. The system will:
- ✅ Create database tables
- ✅ Populate 339+ stock symbols automatically
- ✅ Set up background tasks for daily updates

**No manual data population required!**

### 3. Frontend Setup

```bash
cd frontend
npm install
```

---

## 🎮 Running the Application

### Start Backend Server

```bash
# From project root
python -m backend.main

# Backend will run at: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

### Start Frontend

```bash
# In a new terminal
cd frontend
npm start

# Frontend will run at: http://localhost:3000
```

---

## 📱 Using the Application

### Dashboard Views

1. **📊 Classic View**
   - Table view with all predictions
   - Basic filters (symbol, timeframe, direction, confidence)
   - CSV/Excel export

2. **🚀 Trading Signals**
   - Enhanced view with BUY/EXIT signals
   - Advanced filters (sector, market cap, price range)
   - Real-time market status indicator
   - Auto-refresh functionality
   - Entry zones and stop losses

3. **📈 Analytics**
   - Power BI-style visualizations
   - Charts: Bar, Pie, Area
   - Market sentiment analysis
   - Top predictions by confidence

4. **🎯 Model Performance**
   - Accuracy metrics by timeframe
   - Win rates and financial performance
   - Sharpe ratio and drawdown analysis
   - Performance charts

### Stock Detail View

Click any stock symbol to see:
- All predictions for that stock
- Statistics (bullish/bearish count, avg confidence)
- Filtered by timeframe (Intraday/Swing/Position)
- Signal badges and detailed metrics

---

## 🔄 Automatic Daily Updates

The system includes **built-in background tasks** that automatically:
- 📊 Refresh stock prices daily at 6:00 PM ET (after market close)
- 🔄 Update predictions with latest data
- 📧 Send email alerts for high-confidence signals (if configured)

**No manual intervention required!** Updates run automatically while the backend is running.

### Manual Update (Optional)

If you want to trigger an update manually:

```bash
python -m scripts.daily_update
```

---

## 📧 Email Alerts

To enable email alerts for high-confidence predictions:

1. Configure email settings in `.env`
2. Test email configuration:

```bash
python -m scripts.test_email
```

3. Alerts are automatically sent when running `daily_update.py`

---

## 📊 API Endpoints

### Predictions
- `GET /api/v1/predictions` - Get predictions with filters
- `GET /api/v1/predictions/{id}` - Get specific prediction
- `GET /api/v1/predictions/stock/{symbol}` - Get predictions for a stock
- `GET /api/v1/predictions/filters/sectors` - Get available sectors
- `GET /api/v1/predictions/filters/market-caps` - Get market cap categories

### Market Data
- `POST /api/v1/market/refresh-prices` - Refresh current prices
- `GET /api/v1/market/price/{symbol}` - Get current price for symbol

### Performance
- `GET /api/v1/performance` - Get model performance metrics

Full API documentation: http://localhost:8000/api/docs

---

## 🧪 Testing

### Test Individual Components

```bash
# Test stock universe
python backend/data/stock_universe.py

# Test email alerts
python scripts/test_email.py

# Test model training
python scripts/train_models.py
```

---

## 📁 Project Structure

```
StockPrediction/
├── backend/
│   ├── api/                 # FastAPI routes
│   ├── config/              # Configuration and settings
│   ├── data/                # Stock universe management
│   ├── database/            # Database models and config
│   ├── ml/                  # ML models and feature engineering
│   └── services/            # Business logic services
├── frontend/
│   ├── public/              # Static files
│   └── src/
│       ├── components/      # React components
│       ├── services/        # API service layer
│       └── utils/           # Utility functions
├── ml_models/
│   └── trained_models/      # Serialized ML models
├── scripts/                 # Utility scripts
├── logs/                    # Application logs
└── .env                     # Environment variables
```

---

## 🔧 Configuration Options

### Stock Universe

Edit `STOCK_UNIVERSE` in `.env`:
- `SP500` - Only S&P 500 stocks
- `RUSSELL1000` - Russell 1000 index
- `ALL` - Full universe (S&P 500 + NASDAQ-100 + Dow 30 + Russell 2000 sample + ETFs)

### Model Retraining

Edit `RETRAIN_INTERVAL_DAYS` in `.env` to control how often models should be retrained (default: 7 days).

### Auto-Refresh

In the Trading Signals dashboard, use the Auto-Refresh toggle to enable automatic price updates:
- 30 seconds
- 60 seconds (default)
- 2 minutes
- 5 minutes

---

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Check if backend is running
# Test the health endpoint:
curl http://localhost:8000/
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Model Not Found

```bash
# Retrain models
python -m scripts.train_models
```

### Frontend Build Issues

```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## 📝 License

This project is for educational purposes. Please check the licenses of all dependencies.

---

## 👤 Author

**LaxmiPrasanna Ravikanti**

---

## 🙏 Acknowledgments

- Yahoo Finance for market data
- scikit-learn, XGBoost, and LightGBM teams
- FastAPI and React communities
- TA-Lib for technical indicators

---

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review API docs at http://localhost:8000/api/docs
3. Check application logs in `logs/` directory

---

**Made with ❤️ for traders and ML enthusiasts**
