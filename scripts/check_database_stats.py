"""
Check Database Statistics
Quick script to see how many stocks and predictions are in the database
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.database.config import SessionLocal
from backend.database.models import Stock, Prediction

def check_stats():
    """Check database statistics"""

    db = SessionLocal()

    try:
        # Stock statistics
        total_stocks = db.query(Stock).count()
        active_stocks = db.query(Stock).filter(Stock.is_active == True).count()

        # Prediction statistics
        total_predictions = db.query(Prediction).count()
        active_predictions = db.query(Prediction).filter(Prediction.status == 'active').count()

        # Unique stocks with predictions
        unique_stocks_with_predictions = db.query(Prediction.stock_id).distinct().count()

        # Predictions by type
        intraday = db.query(Prediction).filter(
            Prediction.prediction_type == 'intraday',
            Prediction.status == 'active'
        ).count()

        swing = db.query(Prediction).filter(
            Prediction.prediction_type == 'swing',
            Prediction.status == 'active'
        ).count()

        position = db.query(Prediction).filter(
            Prediction.prediction_type == 'position',
            Prediction.status == 'active'
        ).count()

        print("="*70)
        print("📊 DATABASE STATISTICS")
        print("="*70)
        print()
        print("STOCKS:")
        print(f"  • Total Stocks in Database: {total_stocks}")
        print(f"  • Active Stocks: {active_stocks}")
        print(f"  • Stocks with Predictions: {unique_stocks_with_predictions}")
        print()
        print("PREDICTIONS:")
        print(f"  • Total Predictions (All Time): {total_predictions}")
        print(f"  • Active Predictions: {active_predictions}")
        print()
        print("PREDICTIONS BY TYPE (Active):")
        print(f"  • Intraday: {intraday}")
        print(f"  • Swing: {swing}")
        print(f"  • Position: {position}")
        print()
        print("="*70)
        print()

        if total_stocks < 800:
            print("⚠️  You have fewer than 800 stocks!")
            print(f"   Current: {total_stocks} stocks")
            print(f"   Expected: 800+ stocks")
            print()
            print("To populate more stocks, run:")
            print("   python -m scripts.populate_stocks")
            print()

        if unique_stocks_with_predictions < total_stocks:
            print(f"ℹ️  Only {unique_stocks_with_predictions} out of {total_stocks} stocks have predictions")
            print()
            print("To generate predictions for all stocks, run:")
            print("   python -m scripts.generate_predictions")
            print()

    finally:
        db.close()


if __name__ == "__main__":
    check_stats()
