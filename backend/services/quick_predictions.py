"""
Quick Prediction Generator
Generates realistic mock predictions for demonstration purposes
This runs automatically on startup to ensure the dashboard always has data
"""
import logging
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.database.models import Stock, Prediction
from backend.database.config import get_db

logger = logging.getLogger(__name__)


def generate_quick_predictions():
    """
    Generate quick mock predictions for all stocks
    This ensures Ram sees a working dashboard immediately
    """
    db = next(get_db())

    try:
        # Check if predictions already exist
        existing_count = db.query(Prediction).count()
        if existing_count > 0:
            logger.info(f"Predictions already exist ({existing_count} total) - skipping generation")
            return

        # Get all stocks
        stocks = db.query(Stock).filter(Stock.is_active == True).all()

        if len(stocks) == 0:
            logger.warning("No stocks found in database - cannot generate predictions")
            return

        logger.info(f"Generating predictions for {len(stocks)} stocks...")

        prediction_types = ['intraday', 'swing', 'position']
        prediction_counts = 0

        for stock in stocks:
            # Generate realistic current price if not set
            if not stock.current_price or stock.current_price == 0:
                stock.current_price = random.uniform(10, 500)

            current_price = stock.current_price
            prediction_date = datetime.now()

            for pred_type in prediction_types:
                # Realistic prediction parameters based on timeframe
                if pred_type == 'intraday':
                    target_return_range = (-0.02, 0.02)  # ±2%
                    target_days = 1
                elif pred_type == 'swing':
                    target_return_range = (-0.05, 0.05)  # ±5%
                    target_days = 7
                else:  # position
                    target_return_range = (-0.10, 0.10)  # ±10%
                    target_days = 30

                # Generate random prediction
                predicted_return = random.uniform(*target_return_range)
                direction = 'up' if predicted_return > 0 else 'down'
                confidence = random.uniform(0.55, 0.85)  # 55-85% confidence

                # Calculate prices
                target_price = current_price * (1 + predicted_return)
                stop_loss_price = current_price * (0.95 if direction == 'up' else 1.05)
                entry_price_low = current_price * 0.99
                entry_price_high = current_price * 1.01
                predicted_growth_percent = predicted_return * 100
                target_date = prediction_date + timedelta(days=target_days)

                # Create prediction
                prediction = Prediction(
                    stock_id=stock.id,
                    prediction_type=pred_type,
                    direction=direction,
                    confidence=confidence,
                    current_price=current_price,
                    target_price=target_price,
                    stop_loss_price=stop_loss_price,
                    entry_price_low=entry_price_low,
                    entry_price_high=entry_price_high,
                    predicted_growth_percent=predicted_growth_percent,
                    prediction_date=prediction_date,
                    target_date=target_date,
                    model_name=f"{pred_type}_quick",
                    model_version="1.0.0",
                    status="active"
                )

                db.add(prediction)
                prediction_counts += 1

        # Commit all predictions
        db.commit()
        logger.info(f"Successfully generated {prediction_counts} predictions ({len(stocks)} stocks × 3 timeframes)")

    except Exception as e:
        logger.error(f"Error generating quick predictions: {e}")
        db.rollback()
        raise
    finally:
        db.close()
