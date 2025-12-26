"""
Generate Stock Predictions - FIXED WITH TRADING DAYS
Uses trained ML models to generate predictions for all stocks
Now correctly calculates target dates using TRADING DAYS ONLY (excludes weekends and holidays)
"""

import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.database.config import SessionLocal
from backend.database.models import Stock, PriceHistory, Prediction
from backend.models.predictor import StockPredictor
from backend.utils.trading_days import get_target_date


def generate_predictions_for_all_stocks():
    """
    Generate predictions for all stocks across all timeframes
    """
    db = SessionLocal()
    
    try:
        # Get all active stocks
        stocks = db.query(Stock).filter(Stock.is_active == True).all()
        print(f"Found {len(stocks)} active stocks")
        
        # Prediction types
        prediction_types = ['intraday', 'swing', 'position']
        
        total_predictions = 0
        
        for stock in stocks:
            print(f"\nProcessing {stock.symbol}...")
            
            # Get price history for this stock
            price_data = db.query(PriceHistory).filter(
                PriceHistory.stock_id == stock.id
            ).order_by(PriceHistory.date.desc()).limit(500).all()
            
            if len(price_data) < 100:
                print(f"  Skipping {stock.symbol} - insufficient data ({len(price_data)} days)")
                continue
            
            # Convert to DataFrame - FIXED: Use correct column names
            df = pd.DataFrame([{
                'date': p.date,
                'open': p.open,      # Fixed: was p.open_price
                'high': p.high,      # Fixed: was p.high_price
                'low': p.low,        # Fixed: was p.low_price
                'close': p.close,    # Fixed: was p.close_price
                'volume': p.volume
            } for p in reversed(price_data)])
            
            df['date'] = pd.to_datetime(df['date'], utc=True)
            df = df.sort_values('date').reset_index(drop=True)
            
            # Current price (most recent close)
            current_price = float(df['close'].iloc[-1])
            prediction_date = datetime.now()
            
            # Generate predictions for each timeframe
            for timeframe in prediction_types:
                try:
                    # Load predictor for this timeframe
                    predictor = StockPredictor(prediction_type=timeframe)
                    predictor.load_models()
                    
                    # Generate prediction
                    prediction_result = predictor.predict(df)
                    
                    if prediction_result is None:
                        print(f"  {timeframe}: Failed to generate prediction")
                        continue
                    
                    # Extract prediction details
                    direction = prediction_result['direction']
                    confidence = float(prediction_result['confidence'])
                    predicted_return = float(prediction_result['predicted_return'])
                    
                    # Calculate target price based on predicted return
                    target_price = current_price * (1 + predicted_return)
                    
                    # Calculate stop loss (5% safety margin)
                    if direction == 'up':
                        stop_loss_price = current_price * 0.95
                    else:
                        stop_loss_price = current_price * 1.05
                    
                    # Entry zone (±1% from current price)
                    entry_price_low = current_price * 0.99
                    entry_price_high = current_price * 1.01
                    
                    # Calculate growth percentage
                    predicted_growth_percent = ((target_price - current_price) / current_price) * 100
                    
                    # Calculate target date using TRADING DAYS
                    target_date = get_target_date(timeframe, prediction_date)
                    
                    # Create prediction record
                    prediction = Prediction(
                        stock_id=stock.id,
                        prediction_type=timeframe,
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
                        model_name=f"{timeframe}_ensemble",
                        model_version="1.0.0",
                        status="active"
                    )
                    
                    db.add(prediction)
                    total_predictions += 1
                    
                    # Calculate trading days until target
                    days_diff = (target_date - prediction_date).days
                    
                    print(f"  {timeframe:8} -> {direction.upper():5} "
                          f"(conf: {confidence*100:5.1f}%) "
                          f"Target: ${target_price:.2f} ({predicted_growth_percent:+.2f}%) "
                          f"Date: {target_date.strftime('%Y-%m-%d %A')} ({days_diff} calendar days)")
                    
                except Exception as e:
                    print(f"  Error generating {timeframe} prediction: {str(e)}")
                    continue
        
        # Commit all predictions
        db.commit()
        print(f"\n{'='*80}")
        print(f"✅ Successfully generated {total_predictions} predictions!")
        print(f"   ({len(stocks)} stocks × {len(prediction_types)} timeframes)")
        print(f"{'='*80}")
        
        # Show sample predictions
        print("\n📊 Sample Predictions (with TRADING DAY targets):")
        sample_preds = db.query(Prediction).join(Stock).limit(10).all()
        for pred in sample_preds:
            trading_days = {
                'intraday': 1,
                'swing': 5,
                'position': 20
            }
            print(f"  {pred.stock.symbol:6} | {pred.prediction_type:8} | "
                  f"{pred.direction.upper():5} | {pred.confidence*100:5.1f}% | "
                  f"Target: {pred.target_date.strftime('%Y-%m-%d %A')} "
                  f"({trading_days[pred.prediction_type]} trading days)")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("="*80)
    print("🤖 STOCK PREDICTION GENERATOR (WITH TRADING DAY CALCULATIONS)")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("📅 Using TRADING DAYS (excludes weekends and NYSE holidays)")
    print("   - Intraday:  1 trading day")
    print("   - Swing:     5 trading days (~1 week)")
    print("   - Position: 20 trading days (~1 month)")
    print()
    
    generate_predictions_for_all_stocks()