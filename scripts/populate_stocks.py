"""
Populate Stock Universe
Fetches and populates all stocks from major US indices into the database
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.database.config import SessionLocal
from backend.data.stock_universe import StockUniverse
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Populate stock universe in database"""

    print("="*80)
    print("📊 STOCK UNIVERSE POPULATION")
    print("="*80)
    print()

    db = SessionLocal()

    try:
        # Create stock universe manager
        universe = StockUniverse()

        # Get full universe of stocks
        print("Fetching stock symbols from multiple sources...")
        print("This will include:")
        print("  - S&P 500")
        print("  - NASDAQ-100")
        print("  - Dow Jones 30")
        print("  - Russell 2000 sample")
        print("  - Popular ETFs")
        print()

        symbols = universe.get_full_universe()

        print(f"✅ Found {len(symbols)} unique stock symbols")
        print()

        # Populate database
        print("Populating database...")
        results = universe.populate_database(db, symbols)

        print()
        print("="*80)
        print("✅ POPULATION COMPLETE!")
        print("="*80)
        print(f"Added: {results['added']} new stocks")
        print(f"Updated: {results['updated']} existing stocks")
        print(f"Total: {results['total']} stocks in database")
        print()
        print("Next steps:")
        print("1. Run: python -m scripts.fetch_data")
        print("2. Run: python -m scripts.update_stock_info")
        print("3. Run: python -m scripts.train_models")
        print("4. Run: python -m scripts.generate_predictions")
        print()

    except Exception as e:
        logger.error(f"Error during population: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
