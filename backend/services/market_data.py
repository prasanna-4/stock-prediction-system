"""
Real-Time Market Data Service
Fetches live stock prices using yfinance (no API key required)
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from backend.database.models import Stock, PriceHistory

logger = logging.getLogger(__name__)


class MarketDataService:
    """
    Service for fetching real-time and historical market data
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_current_price(self, symbol: str) -> Optional[Dict]:
        """
        Get current (latest) price for a stock
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dict with current price data or None if failed
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Get current data
            info = ticker.info
            
            # Get latest price from fast_info (more reliable for current price)
            try:
                current_price = ticker.fast_info['lastPrice']
            except:
                # Fallback to regular price
                current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            
            if current_price is None:
                logger.warning(f"Could not get current price for {symbol}")
                return None
            
            return {
                'symbol': symbol,
                'price': float(current_price),
                'timestamp': datetime.now(),
                'volume': info.get('volume', 0)
            }
            
        except Exception as e:
            logger.error(f"Error fetching current price for {symbol}: {e}")
            return None
    
    def get_latest_prices_batch(self, symbols: List[str]) -> Dict[str, float]:
        """
        Get current prices for multiple stocks efficiently
        
        Args:
            symbols: List of stock ticker symbols
            
        Returns:
            Dict mapping symbol to current price
        """
        prices = {}
        
        try:
            # Batch download for efficiency
            symbols_str = ' '.join(symbols)
            data = yf.download(
                symbols_str, 
                period='1d', 
                interval='1m',
                progress=False,
                show_errors=False
            )
            
            if len(symbols) == 1:
                # Single stock
                if not data.empty:
                    prices[symbols[0]] = float(data['Close'].iloc[-1])
            else:
                # Multiple stocks
                if not data.empty and 'Close' in data.columns:
                    for symbol in symbols:
                        try:
                            if symbol in data['Close'].columns:
                                price = data['Close'][symbol].iloc[-1]
                                if pd.notna(price):
                                    prices[symbol] = float(price)
                        except:
                            pass
            
        except Exception as e:
            logger.error(f"Error in batch price fetch: {e}")
        
        # Fallback: fetch individually for any missing prices
        for symbol in symbols:
            if symbol not in prices:
                price_data = self.get_current_price(symbol)
                if price_data:
                    prices[symbol] = price_data['price']
        
        return prices
    
    def fetch_historical_data(
        self, 
        symbol: str, 
        start_date: datetime = None,
        end_date: datetime = None,
        period: str = '2y'
    ) -> pd.DataFrame:
        """
        Fetch historical price data for a stock
        
        Args:
            symbol: Stock ticker
            start_date: Start date for historical data
            end_date: End date for historical data
            period: Period string if dates not specified (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            ticker = yf.Ticker(symbol)
            
            if start_date and end_date:
                df = ticker.history(start=start_date, end=end_date)
            else:
                df = ticker.history(period=period)
            
            if df.empty:
                logger.warning(f"No historical data for {symbol}")
                return pd.DataFrame()
            
            # Standardize column names to match our database
            df = df.reset_index()
            df.columns = [col.lower() for col in df.columns]
            
            # Rename to match our database schema
            df = df.rename(columns={
                'date': 'date'
            })
            
            # Keep only needed columns
            needed_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
            df = df[[col for col in needed_cols if col in df.columns]]
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    def update_stock_current_price(self, symbol: str) -> bool:
        """
        Update the latest price in PriceHistory table
        
        Args:
            symbol: Stock ticker
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get stock from database
            stock = self.db.query(Stock).filter(Stock.symbol == symbol).first()
            if not stock:
                logger.warning(f"Stock {symbol} not found in database")
                return False
            
            # Get current price
            price_data = self.get_current_price(symbol)
            if not price_data:
                return False
            
            # Check if we already have today's data
            today = datetime.now().date()
            existing = self.db.query(PriceHistory).filter(
                PriceHistory.stock_id == stock.id,
                PriceHistory.date == today
            ).first()
            
            if existing:
                # Update existing record
                existing.close = price_data['price']
                existing.volume = price_data.get('volume', existing.volume)
                logger.info(f"Updated today's price for {symbol}: ${price_data['price']:.2f}")
            else:
                # Get yesterday's close as open price
                yesterday = self.db.query(PriceHistory).filter(
                    PriceHistory.stock_id == stock.id
                ).order_by(PriceHistory.date.desc()).first()
                
                open_price = yesterday.close if yesterday else price_data['price']
                
                # Create new record for today
                new_record = PriceHistory(
                    stock_id=stock.id,
                    date=today,
                    open=open_price,
                    high=price_data['price'],  # Will be updated if price goes higher
                    low=price_data['price'],   # Will be updated if price goes lower
                    close=price_data['price'],
                    volume=price_data.get('volume', 0)
                )
                self.db.add(new_record)
                logger.info(f"Added today's price for {symbol}: ${price_data['price']:.2f}")
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error updating price for {symbol}: {e}")
            self.db.rollback()
            return False
    
    def update_all_current_prices(self) -> Dict:
        """
        Update current prices for all active stocks
        
        Returns:
            Dict with update statistics
        """
        try:
            # Get all active stocks
            stocks = self.db.query(Stock).filter(Stock.is_active == True).all()
            symbols = [stock.symbol for stock in stocks]
            
            logger.info(f"Updating prices for {len(symbols)} stocks...")
            
            # Fetch prices in batch
            prices = self.get_latest_prices_batch(symbols)
            
            successful = 0
            failed = 0
            
            for symbol in symbols:
                if symbol in prices:
                    if self.update_stock_current_price(symbol):
                        successful += 1
                    else:
                        failed += 1
                else:
                    failed += 1
            
            result = {
                'total': len(symbols),
                'successful': successful,
                'failed': failed,
                'timestamp': datetime.now()
            }
            
            logger.info(f"Price update complete: {successful} successful, {failed} failed")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in batch price update: {e}")
            return {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'error': str(e),
                'timestamp': datetime.now()
            }


# Convenience function
def get_market_data_service(db: Session) -> MarketDataService:
    """Get market data service instance"""
    return MarketDataService(db)
