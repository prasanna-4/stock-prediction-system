"""
Daily Update Script - Makes System Fully Dynamic
Run this daily to: fetch prices → regenerate predictions → send alerts
"""

import sys
from pathlib import Path
from datetime import datetime
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.database.config import SessionLocal
from backend.database.models import Stock, Prediction
from backend.services.market_data import MarketDataService
from backend.services.email_alerts import EmailAlertService
from backend.config.settings import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_daily_update():
    """
    Complete daily update workflow
    """
    print("="*80)
    print("🔄 DAILY STOCK PREDICTION UPDATE")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    db = SessionLocal()
    
    try:
        # STEP 1: Fetch Latest Real-Time Prices
        print("📊 STEP 1: Fetching real-time market data...")
        print("-" * 80)
        
        market_service = MarketDataService(db)
        update_result = market_service.update_all_current_prices()
        
        print(f"✅ Price Update Complete:")
        print(f"   - Total stocks: {update_result['total']}")
        print(f"   - Successfully updated: {update_result['successful']}")
        print(f"   - Failed: {update_result['failed']}")
        print()
        
        if update_result['successful'] == 0:
            print("❌ No prices updated. Aborting prediction generation.")
            return
        
        # STEP 2: Delete Old Predictions
        print("🗑️  STEP 2: Clearing old predictions...")
        print("-" * 80)
        
        old_count = db.query(Prediction).count()
        db.query(Prediction).delete()
        db.commit()
        
        print(f"✅ Deleted {old_count} old predictions")
        print()
        
        # STEP 3: Generate New Predictions
        print("🤖 STEP 3: Generating new predictions with latest data...")
        print("-" * 80)
        
        # Import here to avoid circular imports
        from scripts.generate_predictions import generate_predictions_for_all_stocks
        
        # This will generate fresh predictions using the updated prices
        generate_predictions_for_all_stocks()
        
        print()
        
        # STEP 4: Send Email Alerts (if configured)
        print("📧 STEP 4: Sending email alerts...")
        print("-" * 80)
        
        # Check if email is configured
        if not hasattr(settings, 'ALERT_EMAIL') or not settings.ALERT_EMAIL:
            print("⚠️  Email alerts not configured. Skipping.")
            print("   To enable alerts, add these to backend/config/settings.py:")
            print("   ALERT_EMAIL = 'your-email@gmail.com'")
            print("   ALERT_PASSWORD = 'your-app-password'")
            print("   RECIPIENT_EMAIL = 'recipient@email.com'")
        else:
            try:
                # Get high-confidence predictions
                high_conf_predictions = db.query(Prediction).filter(
                    Prediction.confidence >= 0.7,
                    Prediction.status == 'active'
                ).join(Stock).all()
                
                if not high_conf_predictions:
                    print("ℹ️  No high-confidence predictions to alert about")
                else:
                    # Convert to dict format for email
                    predictions_data = []
                    for pred in high_conf_predictions:
                        predictions_data.append({
                            'symbol': pred.stock.symbol,
                            'direction': pred.direction,
                            'confidence': pred.confidence,
                            'prediction_type': pred.prediction_type,
                            'current_price': pred.current_price,
                            'target_price': pred.target_price,
                            'entry_price_low': pred.entry_price_low,
                            'entry_price_high': pred.entry_price_high,
                            'stop_loss_price': pred.stop_loss_price,
                            'predicted_growth_percent': pred.predicted_growth_percent,
                            'target_date': pred.target_date.strftime('%Y-%m-%d')
                        })
                    
                    # Send email
                    email_service = EmailAlertService(
                        sender_email=settings.ALERT_EMAIL,
                        sender_password=settings.ALERT_PASSWORD
                    )
                    
                    recipient = getattr(settings, 'RECIPIENT_EMAIL', settings.ALERT_EMAIL)
                    
                    success = email_service.send_high_confidence_alerts(
                        predictions_data,
                        recipient,
                        min_confidence=0.7
                    )
                    
                    if success:
                        print(f"✅ Alert email sent successfully to {recipient}")
                        print(f"   - {len(predictions_data)} high-confidence signals included")
                    else:
                        print("❌ Failed to send alert email")
                        
            except Exception as e:
                print(f"❌ Error sending alerts: {e}")
                logger.exception("Alert error")
        
        print()
        print("="*80)
        print("✅ DAILY UPDATE COMPLETE!")
        print("="*80)
        print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("Summary:")
        print(f"  - Prices updated: {update_result['successful']}/{update_result['total']}")
        
        new_predictions = db.query(Prediction).count()
        print(f"  - New predictions: {new_predictions}")
        
        high_conf = db.query(Prediction).filter(Prediction.confidence >= 0.7).count()
        print(f"  - High confidence (>70%): {high_conf}")
        print()
        
    except Exception as e:
        print(f"❌ Error during update: {e}")
        logger.exception("Update error")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_daily_update()