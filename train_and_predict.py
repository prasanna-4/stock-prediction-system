"""
Quick ML Training and Prediction Generation
Uses existing data in database to train models and generate predictions
"""
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.database.config import SessionLocal
from backend.database.models import Stock, PriceHistory, Prediction
from backend.models.predictor import StockPredictor
from backend.features.feature_engineer import FeatureEngineer
from sqlalchemy import func
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def train_models():
    """Train ML models using existing price history"""
    logger.info("=" * 80)
    logger.info("STEP 1: Training ML models")
    logger.info("=" * 80)

    db = SessionLocal()

    try:
        # Get stocks with sufficient price history
        stocks_with_data = db.query(Stock).join(PriceHistory).group_by(Stock.id).having(
            func.count(PriceHistory.id) >= 200
        ).all()

        logger.info(f"Found {len(stocks_with_data)} stocks with sufficient data")

        if len(stocks_with_data) < 10:
            logger.error("Not enough stocks with data! Need at least 10.")
            return False

        # Get sample of price data for training
        logger.info("Fetching price history for model training...")
        all_price_data = []

        for stock in stocks_with_data[:50]:  # Use first 50 stocks for faster training
            price_records = db.query(PriceHistory).filter(
                PriceHistory.stock_id == stock.id
            ).order_by(PriceHistory.date).all()

            if len(price_records) >= 200:
                df = pd.DataFrame([{
                    'date': p.date,
                    'open': p.open,
                    'high': p.high,
                    'low': p.low,
                    'close': p.close,
                    'volume': p.volume
                } for p in price_records])
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date')
                all_price_data.append(df)

        logger.info(f"Collected data from {len(all_price_data)} stocks for training")

        # Train models for each timeframe
        timeframes = ['intraday', 'swing', 'position']

        for timeframe in timeframes:
            logger.info(f"Training {timeframe} model...")
            predictor = StockPredictor(prediction_type=timeframe)

            # Combine all stock data for training
            combined_df = pd.concat(all_price_data)

            # Train the model
            predictor.train_models(combined_df)
            predictor.save_models()
            logger.info(f"✓ {timeframe} model trained and saved successfully")

        logger.info("=" * 80)
        logger.info("All models trained successfully!")
        logger.info("=" * 80)
        return True

    except Exception as e:
        logger.error(f"Error training models: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def generate_predictions():
    """Generate predictions for all stocks"""
    logger.info("=" * 80)
    logger.info("STEP 2: Generating predictions")
    logger.info("=" * 80)

    db = SessionLocal()

    try:
        # Delete old predictions
        old_count = db.query(Prediction).delete()
        db.commit()
        logger.info(f"Deleted {old_count} old predictions")

        # Get stocks with data
        stocks_with_data = db.query(Stock).join(PriceHistory).group_by(Stock.id).having(
            func.count(PriceHistory.id) >= 100
        ).all()

        logger.info(f"Generating predictions for {len(stocks_with_data)} stocks")

        timeframes = ['intraday', 'swing', 'position']
        total_predictions = 0

        for stock in stocks_with_data:
            try:
                # Get price history
                price_records = db.query(PriceHistory).filter(
                    PriceHistory.stock_id == stock.id
                ).order_by(PriceHistory.date).limit(500).all()

                if len(price_records) < 100:
                    continue

                df = pd.DataFrame([{
                    'date': p.date,
                    'open': p.open,
                    'high': p.high,
                    'low': p.low,
                    'close': p.close,
                    'volume': p.volume
                } for p in price_records])
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date')

                current_price = float(df['close'].iloc[-1])

                # Generate prediction for each timeframe
                for timeframe in timeframes:
                    predictor = StockPredictor(prediction_type=timeframe)
                    predictor.load_models()  # Load the trained models

                    prediction_data = predictor.predict(df)

                    if prediction_data:
                        # Calculate target prices
                        targets = {'intraday': 0.01, 'swing': 0.02, 'position': 0.05}
                        target_pct = targets[timeframe]

                        direction = prediction_data['direction']
                        confidence = prediction_data['confidence']

                        if direction == 'up':
                            target_price = current_price * (1 + target_pct)
                            stop_loss = current_price * 0.98
                        else:
                            target_price = current_price * (1 - target_pct)
                            stop_loss = current_price * 1.02

                        # Create prediction
                        prediction = Prediction(
                            stock_id=stock.id,
                            prediction_type=timeframe,
                            direction=direction,
                            confidence=confidence,
                            current_price=current_price,
                            target_price=target_price,
                            stop_loss_price=stop_loss,
                            entry_price_low=current_price * 0.99,
                            entry_price_high=current_price * 1.01,
                            predicted_growth_percent=target_pct * 100,
                            prediction_date=datetime.now(),
                            target_date=datetime.now() + timedelta(days=predictor.horizons[timeframe]),
                            status='active'
                        )
                        db.add(prediction)
                        total_predictions += 1

                if total_predictions % 50 == 0:
                    db.commit()
                    logger.info(f"Generated {total_predictions} predictions so far...")

            except Exception as e:
                logger.warning(f"Error predicting for {stock.symbol}: {e}")
                continue

        db.commit()
        logger.info("=" * 80)
        logger.info(f"✓ Generated {total_predictions} total predictions!")
        logger.info("=" * 80)
        return True

    except Exception as e:
        logger.error(f"Error generating predictions: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("QUICK ML TRAINING & PREDICTION GENERATION")
    logger.info("Using existing price history data")
    logger.info("=" * 80)

    # Train models
    if not train_models():
        logger.error("Model training failed!")
        sys.exit(1)

    # Generate predictions
    if not generate_predictions():
        logger.error("Prediction generation failed!")
        sys.exit(1)

    logger.info("=" * 80)
    logger.info("✓ COMPLETE! Your system now has real ML predictions.")
    logger.info("=" * 80)
