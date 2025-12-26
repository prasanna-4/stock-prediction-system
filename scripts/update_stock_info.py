"""
Update Stock Information Script
Fetches and updates sector, industry, and market cap for all stocks
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.database.config import SessionLocal
from backend.services.stock_info import StockInfoService
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Update stock information for all stocks in database"""

    print("="*80)
    print("📊 STOCK INFORMATION UPDATE")
    print("="*80)
    print()

    db = SessionLocal()

    try:
        service = StockInfoService(db)

        print("Fetching stock information from Yahoo Finance...")
        print("This may take several minutes depending on number of stocks...")
        print()

        # Update all stocks
        results = service.update_all_stocks_info()

        print()
        print("="*80)
        print("✅ UPDATE COMPLETE!")
        print("="*80)
        print(f"Total stocks: {results['total']}")
        print(f"Successfully updated: {results['successful']}")
        print(f"Failed: {results['failed']}")

        if results['errors']:
            print()
            print("Failed symbols:")
            for symbol in results['errors'][:20]:  # Show first 20
                print(f"  - {symbol}")
            if len(results['errors']) > 20:
                print(f"  ... and {len(results['errors']) - 20} more")

    except Exception as e:
        logger.error(f"Error during update: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
