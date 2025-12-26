# Quick Start Guide - Stock Prediction System

**Get the app running in 15 minutes!**

---

## ⚡ Fast Setup (For Demo)

### 1. Backend Setup

```bash
# Activate virtual environment
venv\Scripts\activate

# Populate data (this will take ~10 minutes)
python -m scripts.populate_stocks
python -m scripts.fetch_data
python -m scripts.update_stock_info

# Train models and generate predictions (~5 minutes)
python -m scripts.train_models
python -m scripts.generate_predictions

# Start backend
python -m backend.main
```

Backend will run at: **http://localhost:8000**

### 3. Frontend Setup (New Terminal)

```bash
cd frontend
npm start
```

Frontend will run at: **http://localhost:3000**

**Note:** The database (SQLite) initializes automatically when you start the backend. No database setup required!

---

## 🎮 Demo Features

### 1. Trading Signals Dashboard
- Click **🚀 Trading Signals** tab
- See the **Market Status** indicator at top
- Try **Advanced Filters**:
  - Select "Technology" sector
  - Choose "Large Cap" market cap
  - Set confidence to 70%
- Click any **stock symbol** to see details

### 2. Auto-Refresh
- Toggle **Auto-Refresh** to ON
- Select refresh interval (60 seconds)
- Watch predictions update automatically

### 3. Model Performance
- Click **🎯 Model Performance** tab
- View accuracy metrics
- See win rates and charts

### 4. Export Data
- Click **📊 Export to Excel** button
- Open the downloaded file
- See "Predictions" and "Summary" sheets

### 5. Analytics
- Click **📈 Analytics** tab
- View market sentiment charts
- See top predictions

---

## 🔧 Quick Fixes

### If backend won't start:
```bash
# Check if backend is running
curl http://localhost:8000/

# Delete database and restart (recreates automatically)
rm stock_predictions.db
python -m backend.main
```

### If frontend won't start:
```bash
# Clear and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

### If predictions are empty:
```bash
# Regenerate predictions
python -m scripts.generate_predictions
```

---

## 📧 Test Email Alerts (Optional)

1. Edit `.env` file:
```env
ALERT_EMAIL=your-email@gmail.com
ALERT_PASSWORD=your-app-password
RECIPIENT_EMAIL=your-email@gmail.com
```

2. Test:
```bash
python -m scripts.test_email
```

---

## 🎯 Key URLs

- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc
- **Health Check:** http://localhost:8000/api/health

---

## 💡 Demo Talking Points

1. **"Covers 800+ stocks"** - Not just S&P 500, includes NASDAQ-100, Dow 30, Russell 2000
2. **"Real-time updates"** - Auto-refresh with configurable intervals
3. **"Advanced filtering"** - Sector, market cap, price range, confidence
4. **"Custom ML models"** - Ensemble approach with 50+ technical indicators
5. **"Professional dashboards"** - 4 different views for different use cases
6. **"Model transparency"** - Performance metrics visible to users
7. **"Export ready"** - Excel and CSV formats

---

## 🚨 Common Issues

**Problem:** Models not found
**Solution:** Run `python -m scripts.train_models`

**Problem:** No predictions showing
**Solution:** Run `python -m scripts.generate_predictions`

**Problem:** Prices are outdated
**Solution:** Click "🔄 Refresh Prices" button in dashboard

**Problem:** Database connection error
**Solution:** Delete `stock_predictions.db` file and restart the backend (recreates automatically)

---

## 📊 Data Flow

```
1. Stock Universe → Database (populate_stocks.py)
2. Historical Prices → Database (fetch_data.py)
3. Stock Info (sector, market cap) → Database (update_stock_info.py)
4. ML Training → Models (train_models.py)
5. Predictions → Database (generate_predictions.py)
6. Frontend → API → Database → Display
```

---

## ⏱️ Time Estimates

- Populate stocks: 1 minute
- Fetch historical data: 10-15 minutes
- Update stock info: 5-10 minutes
- Train models: 5-10 minutes
- Generate predictions: 2-3 minutes
- **Total first-time setup: ~25-35 minutes**

**Subsequent starts:** ~10 seconds (just start backend + frontend)

**Note:** Database setup is instant with SQLite (no configuration needed)

---

## 🎓 For Daily Updates

Run once per day (preferably before market open):

```bash
python -m scripts.daily_update
```

This will:
- Fetch latest prices
- Regenerate predictions
- Send email alerts (if configured)

---

**You're all set! Open http://localhost:3000 and start exploring! 🚀**
