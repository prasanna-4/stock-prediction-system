# Quick Setup Guide - Stock Prediction System

## ⚡ Super Simple Setup (5 Minutes)

### 1. Clone the Repository
```bash
git clone https://github.com/prasanna-4/stock-prediction-system.git
cd stock-prediction-system
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
cd ..
```

### 4. Start the Application

**Terminal 1 - Backend:**
```bash
python -m backend.main
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

### 5. Open Your Browser
Navigate to: **http://localhost:3000**

---

## ✅ That's It!

The system will automatically:
- ✅ Create database on first run
- ✅ Populate 339+ stock symbols
- ✅ Set up background tasks
- ✅ Update predictions daily at 6 PM ET

**No manual scripts needed!** Everything works out-of-the-box.

---

## 📊 What You'll See

1. **Trading Signals Dashboard** - Real-time predictions with BUY/SELL signals
2. **Analytics** - Charts and market insights
3. **Model Performance** - Accuracy metrics and win rates
4. **Stock Details** - Click any symbol for detailed analysis

---

## 🔧 Optional Configuration

### Email Alerts (Optional)
To receive email alerts for high-confidence predictions:

1. Copy `.env.example` to `.env`
2. Add your Gmail credentials:
   ```env
   ALERT_EMAIL=your-email@gmail.com
   ALERT_PASSWORD=your-app-password
   RECIPIENT_EMAIL=where-to-send@gmail.com
   ```

### Database (Optional)
By default uses SQLite (zero setup). To use PostgreSQL:

1. Install PostgreSQL
2. Update `.env`:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/stocks
   ```

---

## 🎯 Features Working Automatically

- ✅ **Auto Data Population** - 339+ stocks added on first run
- ✅ **Daily Updates** - Prices refresh every day at 6 PM ET
- ✅ **Background Tasks** - Runs while backend is active
- ✅ **Real-time Market Status** - Shows if market is open/closed
- ✅ **Auto-Refresh** - Dashboard updates automatically
- ✅ **Mobile Responsive** - Works on all devices

---

## 💡 Tips

1. **First Load**: App starts instantly, predictions load on demand
2. **Port Already in Use**: Kill process on port 8000 or 3000
3. **Update Predictions**: Just restart the backend

---

## 🐛 Troubleshooting

**Backend won't start?**
- Make sure virtual environment is activated
- Check Python version: `python --version` (need 3.10+)

**Frontend won't start?**
- Delete `node_modules` and run `npm install` again
- Check Node version: `node --version` (need 16+)

**No predictions showing?**
- Normal on first run - they generate on demand
- Wait a few seconds and refresh

---

## 📞 Questions?

Check the main README.md for detailed documentation.

---

**Made with ❤️ - Production-Ready Stock Prediction System**
