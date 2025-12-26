"""
Training Script for Stock Prediction Models
Trains models for all timeframes (intraday, swing, position)
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from backend.database.config import get_db
from backend.database.models import Stock, PriceHistory
from backend.models.predictor import StockPredictor
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def fetch_training_data(db: Session) -> pd.DataFrame:
    """
    Fetch all stock data from database for training
    """
    logger.info("Fetching training data from database...")
    
    # Get all stocks
    stocks = db.query(Stock).filter(Stock.is_active == True).all()
    logger.info(f"Loading data for {len(stocks)} stocks...")
    
    all_data = []
    
    for stock in stocks:
        # Get price history
        prices = db.query(PriceHistory).filter(
            PriceHistory.stock_id == stock.id
        ).order_by(PriceHistory.date).all()
        
        if len(prices) < 50:  # Need minimum data
            continue
        
        # Convert to dataframe
        stock_df = pd.DataFrame([{
            'ticker': stock.symbol,
            'date': p.date,
            'open': float(p.open),
            'high': float(p.high),
            'low': float(p.low),
            'close': float(p.close),
            'volume': float(p.volume)
        } for p in prices])
        
        all_data.append(stock_df)
    
    # Combine all stock data
    combined_df = pd.concat(all_data, ignore_index=True)
    
    logger.info(f"Total training samples: {len(combined_df)}")
    
    return combined_df


def train_all_models(training_data: pd.DataFrame):
    """
    Train models for all timeframes
    """
    timeframes = ['intraday', 'swing', 'position']
    
    results = {}
    
    for timeframe in timeframes:
        logger.info(f"\n{'='*60}")
        logger.info(f"Training {timeframe.upper()} model...")
        logger.info(f"{'='*60}\n")
        
        # Initialize predictor
        predictor = StockPredictor(prediction_type=timeframe)
        
        # Train models
        metrics = predictor.train_models(training_data)
        
        if metrics:
            # Save models
            model_file = predictor.save_models()
            
            results[timeframe] = {
                'metrics': metrics,
                'model_file': model_file
            }
            
            # Print results
            logger.info(f"\n{timeframe.upper()} MODEL RESULTS:")
            logger.info(f"Accuracy: {metrics['accuracy']:.2%}")
            logger.info(f"Precision: {metrics['precision']:.2%}")
            logger.info(f"Recall: {metrics['recall']:.2%}")
            logger.info(f"F1 Score: {metrics['f1']:.2%}")
            logger.info(f"Model saved to: {model_file}")
            
            # Top features
            logger.info("\nTop 10 Features:")
            for i, (feature, importance) in enumerate(metrics['top_features'], 1):
                logger.info(f"{i}. {feature}: {importance:.4f}")
        else:
            logger.error(f"Failed to train {timeframe} model!")
    
    return results


def main():
    """
    Main training pipeline
    """
    logger.info("="*60)
    logger.info("TRAINING STOCK PREDICTION MODELS")
    logger.info("="*60)
    
    # Get database session
    db = next(get_db())
    
    try:
        # Fetch training data
        training_data = fetch_training_data(db)
        
        if len(training_data) == 0:
            logger.error("No training data available!")
            return
        
        # Train all models
        results = train_all_models(training_data)
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("✓ MODEL TRAINING COMPLETE!")
        logger.info("="*60)
        
        for timeframe, result in results.items():
            metrics = result['metrics']
            logger.info(f"\n{timeframe.upper()}: Accuracy = {metrics['accuracy']:.2%}")
        
        logger.info("\nNext steps:")
        logger.info("1. Generate predictions: python -m scripts.generate_predictions")
        logger.info("2. Start API server: python -m backend.main")
        
    except Exception as e:
        logger.error(f"Error during training: {str(e)}")
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    main()