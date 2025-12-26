"""
Test Email Alerts
Quick script to verify email configuration works
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.services.email_alerts import EmailAlertService
from backend.config.settings import settings
from datetime import datetime


def test_email_alerts():
    """Test if email alerts are configured and working"""
    
    print("="*80)
    print("📧 EMAIL ALERT TEST")
    print("="*80)
    print()
    
    # Check configuration
    print("1. Checking email configuration...")

    if not hasattr(settings, 'ALERT_EMAIL') or not settings.ALERT_EMAIL:
        print("❌ ALERT_EMAIL not configured in .env file")
        print()
        print("To configure email alerts:")
        print("   1. Open .env file in project root")
        print("   2. Add these lines:")
        print("      ALERT_EMAIL=your-email@gmail.com")
        print("      ALERT_PASSWORD=your-16-char-app-password")
        print("      RECIPIENT_EMAIL=recipient@email.com")
        print()
        print("   3. For Gmail, use App Password (not regular password)")
        print("      Get it from: https://myaccount.google.com/apppasswords")
        print()
        print("See EMAIL_ALERTS_GUIDE.md for detailed setup instructions")
        return False

    print(f"✅ Sender email: {settings.ALERT_EMAIL}")

    if hasattr(settings, 'RECIPIENT_EMAIL') and settings.RECIPIENT_EMAIL:
        recipient = settings.RECIPIENT_EMAIL
        print(f"✅ Recipient email: {recipient}")
    else:
        recipient = settings.ALERT_EMAIL
        print(f"⚠️  No RECIPIENT_EMAIL set, using sender as recipient: {recipient}")
    
    print()
    
    # Create test prediction
    print("2. Creating test prediction...")
    
    test_prediction = {
        'symbol': 'AAPL',
        'direction': 'up',
        'confidence': 0.85,
        'prediction_type': 'swing',
        'current_price': 180.50,
        'target_price': 195.00,
        'entry_price_low': 179.00,
        'entry_price_high': 182.00,
        'stop_loss_price': 171.50,
        'predicted_growth_percent': 8.03,
        'target_date': '2025-12-30'
    }
    
    print(f"✅ Test prediction created for {test_prediction['symbol']}")
    print()
    
    # Send test email
    print("3. Sending test email...")
    
    try:
        email_service = EmailAlertService(
            sender_email=settings.ALERT_EMAIL,
            sender_password=settings.ALERT_PASSWORD
        )
        
        success = email_service.send_high_confidence_alerts(
            [test_prediction],
            recipient,
            min_confidence=0.7
        )
        
        if success:
            print("✅ Test email sent successfully!")
            print()
            print(f"📬 Check your inbox: {recipient}")
            print("   - Subject: 🚀 1 High-Confidence Stock Signals - [date]")
            print("   - Look for AAPL test prediction")
            print()
            return True
        else:
            print("❌ Failed to send test email")
            print()
            print("Common issues:")
            print("  1. Gmail: Need 'App Password' (not regular password)")
            print("     - Enable 2FA in Google Account")
            print("     - Generate App Password at: https://myaccount.google.com/apppasswords")
            print("  2. Check SMTP settings in email_alerts.py")
            print("  3. Verify email/password are correct")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Troubleshooting:")
        print("  - Verify ALERT_EMAIL and ALERT_PASSWORD in settings.py")
        print("  - For Gmail: Use App Password, not regular password")
        print("  - Check if 'Less secure app access' is enabled (if not using 2FA)")
        return False


if __name__ == "__main__":
    test_email_alerts()