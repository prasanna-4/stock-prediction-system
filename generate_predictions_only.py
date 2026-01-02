"""
Generate predictions using already-trained models
"""
import logging
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.database.config import SessionLocal
from backend.database.models import Stock, PriceHistory, Prediction
from backend.models.predictor import StockPredictor
from sqlalchemy import func
import pandas as pd
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

            if total_predictions % 50 == 0 and total_predictions > 0:
                db.commit()
                logger.info(f"Generated {total_predictions} predictions so far...")

        except Exception as e:
            logger.warning(f"Error predicting for {stock.symbol}: {e}")
            continue

    db.commit()
    logger.info(f"✓ Generated {total_predictions} total predictions!")

except Exception as e:
    logger.error(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
