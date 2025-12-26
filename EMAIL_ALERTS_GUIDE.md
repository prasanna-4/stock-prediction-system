# Email Alerts Configuration Guide

## 📧 How to Enable Email Alerts

The system can automatically send email alerts for high-confidence stock predictions (>70% confidence).

---

## ⚙️ Setup Instructions (3 Steps)

### Step 1: Get Your Gmail App Password

**Important**: Don't use your regular Gmail password! Use an "App Password" instead.

1. Go to your Google Account: https://myaccount.google.com/
2. Click on **Security** (left sidebar)
3. Under "Signing in to Google", enable **2-Step Verification** if not already enabled
4. After enabling 2-Step Verification, scroll down and click **App passwords**
5. Select:
   - App: **Mail**
   - Device: **Windows Computer** (or your device)
6. Click **Generate**
7. **Copy the 16-character password** (looks like: `abcd efgh ijkl mnop`)

### Step 2: Configure .env File

Open the `.env` file in the project root and add:

```env
# Email Alerts Configuration
ALERT_EMAIL=your-email@gmail.com
ALERT_PASSWORD=abcd efgh ijkl mnop
RECIPIENT_EMAIL=recipient@email.com
```

**Replace with your details:**
- `ALERT_EMAIL`: Your Gmail address (the one sending emails)
- `ALERT_PASSWORD`: The 16-character app password from Step 1
- `RECIPIENT_EMAIL`: Email address to receive alerts (can be same as ALERT_EMAIL)

**Example:**
```env
ALERT_EMAIL=john.doe@gmail.com
ALERT_PASSWORD=abcd efgh ijkl mnop
RECIPIENT_EMAIL=john.doe@gmail.com
```

### Step 3: Test Email Alerts

Run the test script to verify it works:

```bash
# Make sure virtual environment is activated
# venv\Scripts\activate  (on Windows)
# source venv/bin/activate  (on Mac/Linux)

python -m scripts.test_email
```

You should see:
```
✅ Email sent successfully!
Check your inbox at: recipient@email.com
```

---

## 🤖 How Email Alerts Work

### Automatic Daily Alerts

Run the daily update script to get automatic emails:

```bash
python -m scripts.daily_update
```

**This script will:**
1. Fetch latest stock prices
2. Generate fresh predictions
3. **Send email alerts** for high-confidence predictions (>70%)

### Schedule Daily Alerts (Optional)

**On Windows (Task Scheduler):**
1. Open Task Scheduler
2. Create Basic Task
3. Name: "Stock Predictions Daily Update"
4. Trigger: Daily at 6:00 AM
5. Action: Start a Program
   - Program: `C:\Path\To\Your\venv\Scripts\python.exe`
   - Arguments: `-m scripts.daily_update`
   - Start in: `C:\Path\To\StockPrediction`

**On Mac/Linux (Crontab):**
```bash
# Open crontab editor
crontab -e

# Add this line (runs daily at 6 AM)
0 6 * * * cd /path/to/StockPrediction && /path/to/venv/bin/python -m scripts.daily_update
```

---

## 📧 What the Email Contains

The alert email includes:

- **Subject**: "🚨 High-Confidence Stock Trading Signals - [Date]"
- **Content**:
  - Number of high-confidence predictions
  - Table with:
    - Stock Symbol
    - Direction (UP/DOWN)
    - Confidence %
    - Current Price
    - Target Price
    - Entry Range
    - Stop Loss
    - Expected Growth %
    - Target Date
  - Grouped by timeframe (Intraday, Swing, Position)

---

## 🔧 Troubleshooting

### Error: "Authentication failed"
- **Solution**: Make sure you're using an **App Password**, not your regular Gmail password
- Verify 2-Step Verification is enabled on your Google Account

### Error: "SMTPAuthenticationError"
- **Solution**: Double-check the email and app password in .env
- Remove any spaces from the app password

### Error: "SMTPServerDisconnected"
- **Solution**: Gmail might be blocking the connection
- Go to https://myaccount.google.com/security
- Enable "Less secure app access" (if available)
- Or make sure you're using App Passwords (recommended)

### Not Receiving Emails
- Check your spam/junk folder
- Verify RECIPIENT_EMAIL is correct in .env
- Run test script again to see error messages

---

## 🔒 Security Best Practices

### ✅ DO:
- Use App Passwords (16-character codes)
- Keep .env file private (it's in .gitignore)
- Use different passwords for different apps
- Revoke App Passwords when no longer needed

### ❌ DON'T:
- Share your .env file
- Commit .env to Git
- Use your main Gmail password
- Hardcode credentials in Python files

---

## 📝 Email Configuration Reference

### Full .env Example

```env
# Database (SQLite - no installation required)
DATABASE_URL=sqlite:///./stock_predictions.db

# API Security
API_KEY=dev-api-key-12345

# Email Alerts (Optional - leave blank to disable)
ALERT_EMAIL=your-email@gmail.com
ALERT_PASSWORD=your-16-char-app-password
RECIPIENT_EMAIL=recipient@email.com

# Application
DEBUG=True
LOG_LEVEL=INFO
ALLOWED_ORIGINS=["http://localhost:3000"]
```

### Disable Email Alerts

To disable email alerts, simply leave these fields blank in .env:

```env
ALERT_EMAIL=
ALERT_PASSWORD=
RECIPIENT_EMAIL=
```

The system will skip email sending and continue working normally.

---

## 🎯 For End Users

If you're sharing this system with others, they can enable email alerts by:

1. **Copy .env.example to .env**
   ```bash
   cp .env.example .env
   ```

2. **Edit .env and add their email credentials**
   ```bash
   # Use any text editor
   notepad .env  # Windows
   nano .env     # Mac/Linux
   ```

3. **Follow "Step 1: Get Your Gmail App Password" above**

4. **Test with:**
   ```bash
   python -m scripts.test_email
   ```

**No code changes needed!** Everything is configured through the .env file.

---

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your .env file format matches the examples
3. Run the test script to see detailed error messages
4. Check logs/app.log for detailed error information

---

**Email alerts configured! 📧✅**
