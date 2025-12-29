"""
Auto-initialization service
Automatically populates database on first run
"""
import logging
from sqlalchemy.orm import Session
from backend.database.config import get_db
from backend.database.models import Stock, Prediction
from backend.data.stock_universe import StockUniverse

logger = logging.getLogger(__name__)


def check_and_initialize_database():
    """
    Check if database is empty and initialize if needed
    This runs automatically on app startup
    """
    db = next(get_db())

    try:
        # Check if stocks table is empty
        stock_count = db.query(Stock).count()

        if stock_count == 0:
            logger.info("Database is empty - running first-time initialization...")
            logger.info("Populating stock universe (339+ stocks)...")

            # Populate stocks
            universe = StockUniverse()
            symbols = universe.get_full_universe()
            universe.populate_database(db, symbols)

            logger.info(f"Successfully populated {len(symbols)} stocks")
            logger.info("To generate REAL ML predictions, run:")
            logger.info("  python -m backend.services.full_initialization")
        else:
            logger.info(f"Database already contains {stock_count} stocks")

        # Check if predictions exist
        prediction_count = db.query(Prediction).count()
        if prediction_count > 0:
            logger.info(f"Found {prediction_count} predictions in database")
        else:
            logger.info("No predictions yet. Run full_initialization to generate them.")

    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
        raise
    finally:
        db.close()


def is_database_ready() -> bool:
    """
    Check if database has minimum required data
    """
    db = next(get_db())

    try:
        stock_count = db.query(Stock).count()
        return stock_count > 0
    finally:
        db.close()
