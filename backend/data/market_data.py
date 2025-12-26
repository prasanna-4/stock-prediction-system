"""
Market Data Fetcher
Fetches historical and current market data from Yahoo Finance
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
import logging
import time

from backend.database.models import Stock, PriceHistory
from backend.database.config import get_db

logger = logging.getLogger(__name__)


class MarketDataFetcher:
    """Fetches and manages market data"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = timedelta(minutes=15)
    
    def fetch_stock_info(self, symbol: str) -> Dict:
        """
        Fetch company information for a stock
        
        Returns:
            Dict with name, sector, industry, market_cap
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'name': info.get('longName', symbol),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'market_cap': info.get('marketCap')
            }
        except Exception as e:
            logger.warning(f"Error fetching info for {symbol}: {e}")
            return {
                'name': symbol,
                'sector': None,
                'industry': None,
                'market_cap': None
            }
    
    def fetch_historical_data(
        self,
        symbol: str,
        period: str = "2y",
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Fetch historical price data
        
        Args:
            symbol: Stock symbol
            period: Time period (1mo, 3mo, 6mo, 1y, 2y, 5y, max)
            interval: Data interval (1m, 5m, 15m, 1h, 1d, 1wk, 1mo)
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                logger.warning(f"No data returned for {symbol}")
                return pd.DataFrame()
            
            # Clean column names
            df.columns = [col.lower() for col in df.columns]
            
            # Reset index to get date as column
            df = df.reset_index()
            df.columns = [col.lower() for col in df.columns]
            
            # Rename date column
            if 'date' in df.columns:
                df = df.rename(columns={'date': 'datetime'})
            elif 'datetime' not in df.columns:
                df['datetime'] = df.index
            
            logger.info(f"Fetched {len(df)} rows for {symbol}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current/latest price for a stock
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Try to get real-time price
            info = ticker.info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            
            if current_price:
                return float(current_price)
            
            # Fallback: get latest close from history
            df = self.fetch_historical_data(symbol, period="1d", interval="1d")
            if not df.empty:
                return float(df['close'].iloc[-1])
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            return None
    
    def save_historical_data_to_db(
        self,
        symbol: str,
        db: Session,
        period: str = "2y"
    ):
        """
        Fetch historical data and save to database
        """
        # Get stock from database
        stock = db.query(Stock).filter(Stock.symbol == symbol).first()
        
        if not stock:
            logger.warning(f"Stock {symbol} not found in database")
            return False
        
        # Fetch historical data
        df = self.fetch_historical_data(symbol, period=period)
        
        if df.empty:
            return False
        
        # Save each row to database
        saved_count = 0
        for _, row in df.iterrows():
            try:
                # Check if this date already exists
                existing = db.query(PriceHistory).filter(
                    PriceHistory.stock_id == stock.id,
                    PriceHistory.date == row['datetime']
                ).first()
                
                if existing:
                    # Update existing record
                    existing.open = float(row['open'])
                    existing.high = float(row['high'])
                    existing.low = float(row['low'])
                    existing.close = float(row['close'])
                    existing.volume = float(row['volume'])
                else:
                    # Create new record
                    price_history = PriceHistory(
                        stock_id=stock.id,
                        date=row['datetime'],
                        open=float(row['open']),
                        high=float(row['high']),
                        low=float(row['low']),
                        close=float(row['close']),
                        volume=float(row['volume'])
                    )
                    db.add(price_history)
                
                saved_count += 1
                
            except Exception as e:
                logger.warning(f"Error saving row for {symbol}: {e}")
                continue
        
        db.commit()
        logger.info(f"Saved {saved_count} price records for {symbol}")
        
        return True
    
    def bulk_fetch_and_save(
        self,
        symbols: List[str],
        db: Session,
        period: str = "2y",
        delay: float = 0.5
    ):
        """
        Fetch and save data for multiple stocks
        
        Args:
            symbols: List of stock symbols
            db: Database session
            period: Time period to fetch
            delay: Delay between requests (to avoid rate limiting)
        """
        successful = 0
        failed = 0
        
        total = len(symbols)
        
        for i, symbol in enumerate(symbols, 1):
            logger.info(f"Processing {symbol} ({i}/{total})...")
            
            try:
                # Update stock info
                info = self.fetch_stock_info(symbol)
                stock = db.query(Stock).filter(Stock.symbol == symbol).first()
                
                if stock:
                    stock.name = info['name']
                    stock.sector = info['sector']
                    stock.industry = info['industry']
                    stock.market_cap = info['market_cap']
                    db.commit()
                
                # Fetch and save historical data
                success = self.save_historical_data_to_db(symbol, db, period)
                
                if success:
                    successful += 1
                else:
                    failed += 1
                
                # Rate limiting
                time.sleep(delay)
                
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                failed += 1
                continue
        
        logger.info(f"Bulk fetch complete: {successful} successful, {failed} failed")
        
        return {
            "successful": successful,
            "failed": failed,
            "total": total
        }
    
    def get_latest_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        Get latest prices for multiple symbols
        
        Returns:
            Dict mapping symbol to current price
        """
        prices = {}
        
        for symbol in symbols:
            price = self.get_current_price(symbol)
            if price:
                prices[symbol] = price
        
        return prices


def fetch_data_for_stock(symbol: str, db: Session, period: str = "2y") -> bool:
    """
    Convenience function to fetch data for a single stock
    """
    fetcher = MarketDataFetcher()
    return fetcher.save_historical_data_to_db(symbol, db, period)


if __name__ == "__main__":
    # Test the data fetcher
    logging.basicConfig(level=logging.INFO)
    
    fetcher = MarketDataFetcher()
    
    # Test single stock
    print("\nTesting single stock fetch (AAPL)...")
    df = fetcher.fetch_historical_data("AAPL", period="1mo")
    print(f"Fetched {len(df)} days of data")
    print(df.head())
    
    # Test current price
    price = fetcher.get_current_price("AAPL")
    print(f"\nCurrent AAPL price: ${price}")
    
    # Test stock info
    info = fetcher.fetch_stock_info("AAPL")
    print(f"\nAAPL Info:")
    print(f"Name: {info['name']}")
    print(f"Sector: {info['sector']}")
    print(f"Industry: {info['industry']}")
    print(f"Market Cap: ${info['market_cap']:,}" if info['market_cap'] else "N/A")
