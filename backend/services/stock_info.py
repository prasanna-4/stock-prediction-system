"""
Stock Information Service
Fetches company info like sector, industry, market cap from Yahoo Finance
"""

import yfinance as yf
from sqlalchemy.orm import Session
from typing import Dict, Optional
import logging
from backend.database.models import Stock

logger = logging.getLogger(__name__)


class StockInfoService:
    """Service to fetch and update stock information"""

    def __init__(self, db: Session):
        self.db = db

    def fetch_stock_info(self, symbol: str) -> Optional[Dict]:
        """
        Fetch detailed stock information from Yahoo Finance

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with stock info or None if failed
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                'name': info.get('longName', info.get('shortName', symbol)),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'current_price': info.get('currentPrice', info.get('regularMarketPrice', 0))
            }

        except Exception as e:
            logger.error(f"Error fetching info for {symbol}: {e}")
            return None

    def update_stock_info(self, symbol: str) -> bool:
        """
        Update stock information in database

        Args:
            symbol: Stock symbol

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get stock from database
            stock = self.db.query(Stock).filter(Stock.symbol == symbol).first()

            if not stock:
                logger.warning(f"Stock {symbol} not found in database")
                return False

            # Fetch info
            info = self.fetch_stock_info(symbol)

            if not info:
                return False

            # Update database
            stock.name = info['name']
            stock.sector = info['sector']
            stock.industry = info['industry']
            stock.market_cap = info['market_cap']

            self.db.commit()

            logger.info(f"Updated info for {symbol}: {info['name']} ({info['sector']})")
            return True

        except Exception as e:
            logger.error(f"Error updating stock info for {symbol}: {e}")
            self.db.rollback()
            return False

    def update_all_stocks_info(self, limit: int = None) -> Dict:
        """
        Update information for all active stocks

        Args:
            limit: Optional limit for number of stocks to update

        Returns:
            Dictionary with update results
        """
        query = self.db.query(Stock).filter(Stock.is_active == True)

        if limit:
            query = query.limit(limit)

        stocks = query.all()

        results = {
            'total': len(stocks),
            'successful': 0,
            'failed': 0,
            'errors': []
        }

        for i, stock in enumerate(stocks, 1):
            logger.info(f"Updating {i}/{len(stocks)}: {stock.symbol}")

            success = self.update_stock_info(stock.symbol)

            if success:
                results['successful'] += 1
            else:
                results['failed'] += 1
                results['errors'].append(stock.symbol)

        logger.info(f"Stock info update complete: {results['successful']}/{results['total']} successful")

        return results

    def get_market_cap_category(self, market_cap: float) -> str:
        """
        Categorize market cap

        Args:
            market_cap: Market capitalization value

        Returns:
            Category string
        """
        if market_cap >= 200_000_000_000:  # $200B+
            return 'Mega Cap'
        elif market_cap >= 10_000_000_000:  # $10B+
            return 'Large Cap'
        elif market_cap >= 2_000_000_000:  # $2B+
            return 'Mid Cap'
        elif market_cap >= 300_000_000:  # $300M+
            return 'Small Cap'
        elif market_cap >= 50_000_000:  # $50M+
            return 'Micro Cap'
        else:
            return 'Nano Cap'


def get_stock_info_service(db: Session) -> StockInfoService:
    """
    Convenience function to get stock info service

    Args:
        db: Database session

    Returns:
        StockInfoService instance
    """
    return StockInfoService(db)


if __name__ == "__main__":
    # Test the service
    from backend.database.config import SessionLocal

    logging.basicConfig(level=logging.INFO)

    db = SessionLocal()

    try:
        service = StockInfoService(db)

        # Test with a few stocks
        test_symbols = ['AAPL', 'MSFT', 'GOOGL']

        for symbol in test_symbols:
            print(f"\nFetching info for {symbol}...")
            info = service.fetch_stock_info(symbol)

            if info:
                print(f"  Name: {info['name']}")
                print(f"  Sector: {info['sector']}")
                print(f"  Industry: {info['industry']}")
                print(f"  Market Cap: ${info['market_cap']:,.0f}")
                print(f"  Category: {service.get_market_cap_category(info['market_cap'])}")

    finally:
        db.close()
