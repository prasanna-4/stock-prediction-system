"""
Full System Initialization with REAL ML
Downloads historical data, trains models, generates real predictions
This takes 25-30 minutes but gives GENUINE ML predictions
"""
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.database.config import SessionLocal, get_db
from backend.database.models import Stock, PriceHistory, Prediction
from backend.services.market_data import MarketDataService
from backend.models.predictor import StockPredictor
from backend.features.feature_engineer import FeatureEngineer
from sqlalchemy import func
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def download_historical_data():
    """
    Download 2 years of historical data for all stocks
    This is STEP 1 - Required for real ML
    """
    logger.info("=" * 80)
    logger.info("STEP 1: Downloading historical market data (this takes 10-15 minutes)")
    logger.info("=" * 80)

    db = SessionLocal()

    try:
        stocks = db.query(Stock).filter(Stock.is_active == True).all()
        total = len(stocks)
        logger.info(f"Fetching 2 years of data for {total} stocks...")

        market_service = MarketDataService(db)
        successful = 0
        failed = 0

        for idx, stock in enumerate(stocks, 1):
            try:
                logger.info(f"[{idx}/{total}] Fetching {stock.symbol}...")

                # Fetch 2 years of historical data
                df = market_service.fetch_historical_data(stock.symbol, period='2y')

                if df.empty:
                    logger.warning(f"  No data for {stock.symbol}")
                    failed += 1
                    continue

                # Save to database
                for _, row in df.iterrows():
                    # Skip rows with NaN values (missing data)
                    if pd.isna(row['open']) or pd.isna(row['high']) or pd.isna(row['low']) or pd.isna(row['close']):
                        continue

                    # Check if record exists
                    existing = db.query(PriceHistory).filter(
                        PriceHistory.stock_id == stock.id,
                        PriceHistory.date == row['date'].date()
                    ).first()

                    if not existing:
                        price_record = PriceHistory(
                            stock_id=stock.id,
                            date=row['date'].date(),
                            open=float(row['open']),
                            high=float(row['high']),
                            low=float(row['low']),
                            close=float(row['close']),
                            volume=int(row['volume']) if 'volume' in row and not pd.isna(row['volume']) else 0
                        )
                        db.add(price_record)

                # Update current price (skip if NaN)
                latest_close = df['close'].iloc[-1]
                if not pd.isna(latest_close):
                    stock.current_price = float(latest_close)

                db.commit()
                successful += 1
                logger.info(f"  Success: {len(df)} days of data")

            except Exception as e:
                logger.error(f"  Error with {stock.symbol}: {e}")
                db.rollback()
                failed += 1
                continue

        logger.info("=" * 80)
        logger.info(f"Historical data download complete:")
        logger.info(f"  Successful: {successful}/{total}")
        logger.info(f"  Failed: {failed}/{total}")
        logger.info("=" * 80)

        return successful > 0

    finally:
        db.close()


def train_ml_models():
    """
    Train REAL XGBoost + LightGBM models
    This is STEP 2 - The actual ML training
    """
    logger.info("=" * 80)
    logger.info("STEP 2: Training ML models (XGBoost + LightGBM)")
    logger.info("=" * 80)

    db = SessionLocal()

    try:
        # Get stocks with sufficient price history
        stocks_with_data = db.query(Stock).join(PriceHistory).group_by(Stock.id).having(
            func.count(PriceHistory.id) >= 200
        ).all()

        logger.info(f"Found {len(stocks_with_data)} stocks with sufficient data for training")

        if len(stocks_with_data) < 10:
            logger.error("Not enough stocks with historical data. Download data first!")
            return False

        # Train models for each timeframe
        timeframes = ['intraday', 'swing', 'position']

        for timeframe in timeframes:
            logger.info(f"\nTraining {timeframe} model...")

            predictor = StockPredictor(prediction_type=timeframe)

            # Collect training data from multiple stocks
            all_training_data = []

            for stock in stocks_with_data[:100]:  # Use top 100 stocks for training
                price_data = db.query(PriceHistory).filter(
                    PriceHistory.stock_id == stock.id
                ).order_by(PriceHistory.date).all()

                if len(price_data) < 200:
                    continue

                # Convert to DataFrame
                df = pd.DataFrame([{
                    'date': p.date,
                    'open': p.open,
                    'high': p.high,
                    'low': p.low,
                    'close': p.close,
                    'volume': p.volume
                } for p in price_data])

                try:
                    # Prepare training data
                    df_prepared = predictor.prepare_training_data(df)
                    all_training_data.append(df_prepared)
                except Exception as e:
                    continue

            if not all_training_data:
                logger.error(f"No training data for {timeframe}")
                continue

            # Combine all stock data
            combined_data = pd.concat(all_training_data, ignore_index=True)
            logger.info(f"  Training samples: {len(combined_data)}")

            # Train the model
            metrics = predictor.train(combined_data)

            # Save the model
            predictor.save_models()

            logger.info(f"  {timeframe.upper()} Model trained successfully!")
            logger.info(f"    Accuracy: {metrics.get('accuracy', 0):.2%}")
            logger.info(f"    Precision: {metrics.get('precision', 0):.2%}")

        logger.info("=" * 80)
        logger.info("ML model training complete!")
        logger.info("=" * 80)

        return True

    except Exception as e:
        logger.error(f"Error training models: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def generate_real_predictions():
    """
    Generate REAL predictions using trained models
    This is STEP 3 - The actual predictions
    """
    logger.info("=" * 80)
    logger.info("STEP 3: Generating real ML predictions")
    logger.info("=" * 80)

    # Import and run the existing prediction generator
    from scripts.generate_predictions import generate_predictions_for_all_stocks

    try:
        generate_predictions_for_all_stocks()
        return True
    except Exception as e:
        logger.error(f"Error generating predictions: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_full_initialization():
    """
    Complete initialization: Data → Models → Predictions
    """
    start_time = datetime.now()

    logger.info("\n" + "=" * 80)
    logger.info("FULL SYSTEM INITIALIZATION - REAL ML PREDICTIONS")
    logger.info("=" * 80)
    logger.info("This will take 25-30 minutes but generates REAL predictions")
    logger.info(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80 + "\n")

    # Step 1: Download historical data
    if not download_historical_data():
        logger.error("Failed to download historical data. Aborting.")
        return False

    # Step 2: Train ML models
    if not train_ml_models():
        logger.error("Failed to train ML models. Aborting.")
        return False

    # Step 3: Generate predictions
    if not generate_real_predictions():
        logger.error("Failed to generate predictions. Aborting.")
        return False

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 60

    logger.info("\n" + "=" * 80)
    logger.info("INITIALIZATION COMPLETE!")
    logger.info("=" * 80)
    logger.info(f"Total time: {duration:.1f} minutes")
    logger.info(f"Finished at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
    logger.info("\nYour system now has REAL ML predictions!")
    logger.info("Start the backend and frontend to see the results.")
    logger.info("=" * 80 + "\n")

    return True


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    run_full_initialization()
