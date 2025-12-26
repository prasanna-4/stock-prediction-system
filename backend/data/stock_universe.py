"""
Stock Universe Manager
Manages the list of stocks to track and predict
"""

import pandas as pd
import requests
from typing import List, Dict
from sqlalchemy.orm import Session
import logging

from backend.database.models import Stock
from backend.database.config import get_db

logger = logging.getLogger(__name__)


class StockUniverse:
    """Manages the universe of stocks to track"""

    def __init__(self):
        self.sp500_symbols = []
        self.nasdaq100_symbols = []
        self.dow30_symbols = []
        self.russell2000_symbols = []
        self.additional_symbols = []

    def fetch_sp500_list(self) -> List[str]:
        """
        Fetch current S&P 500 constituents from Wikipedia
        """
        try:
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            tables = pd.read_html(url)
            sp500_table = tables[0]

            symbols = sp500_table['Symbol'].tolist()

            # Clean symbols (some have periods for different share classes)
            symbols = [s.replace('.', '-') for s in symbols]

            logger.info(f"Fetched {len(symbols)} S&P 500 stocks")
            return symbols

        except Exception as e:
            logger.error(f"Error fetching S&P 500 list: {e}")
            return self._get_fallback_sp500()

    def fetch_nasdaq100_list(self) -> List[str]:
        """
        Fetch NASDAQ-100 constituents from Wikipedia
        """
        try:
            url = "https://en.wikipedia.org/wiki/Nasdaq-100"
            tables = pd.read_html(url)
            nasdaq_table = tables[4]  # The constituents table

            symbols = nasdaq_table['Ticker'].tolist()
            symbols = [s.replace('.', '-') for s in symbols]

            logger.info(f"Fetched {len(symbols)} NASDAQ-100 stocks")
            return symbols

        except Exception as e:
            logger.error(f"Error fetching NASDAQ-100 list: {e}")
            return self._get_fallback_nasdaq100()

    def fetch_dow30_list(self) -> List[str]:
        """
        Fetch Dow Jones Industrial Average constituents from Wikipedia
        """
        try:
            url = "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average"
            tables = pd.read_html(url)
            dow_table = tables[1]  # The constituents table

            symbols = dow_table['Symbol'].tolist()
            symbols = [s.replace('.', '-') for s in symbols]

            logger.info(f"Fetched {len(symbols)} Dow 30 stocks")
            return symbols

        except Exception as e:
            logger.error(f"Error fetching Dow 30 list: {e}")
            return self._get_fallback_dow30()

    def fetch_russell2000_sample(self) -> List[str]:
        """
        Get a sample of Russell 2000 stocks (popular small caps)
        Note: Full Russell 2000 list requires paid data source
        """
        # Top 200 most liquid Russell 2000 stocks
        return [
            # Financial Services
            'SFNC', 'WTFC', 'FIBK', 'WAFD', 'TFSL', 'CADE', 'FFBC', 'UBSI',
            'NBTB', 'ABCB', 'FULT', 'UMBF', 'HOPE', 'HWC', 'ONB', 'CATY',

            # Healthcare
            'ALKS', 'TGTX', 'RVMD', 'PCRX', 'KRYS', 'PTGX', 'RCKT', 'ANIP',
            'CORT', 'CRNX', 'INSM', 'ITCI', 'KALA', 'MYGN', 'NVCR', 'OCUL',

            # Technology
            'RELY', 'RIOT', 'UPST', 'SMAR', 'FRSH', 'ASAN', 'GTLB', 'MNDY',
            'S', 'SNOW', 'U', 'BILL', 'DOMO', 'FROG', 'NCNO', 'PATH',

            # Industrials
            'ASTE', 'BOOM', 'CMCO', 'DY', 'ESAB', 'FLS', 'GVA', 'HI',
            'MLI', 'NDSN', 'PATK', 'RXO', 'SLGN', 'TPC', 'TREX', 'WMS',

            # Consumer Discretionary
            'AAP', 'ABG', 'AEO', 'ANF', 'BBWI', 'BJ', 'BOOT', 'BURL',
            'CASY', 'CRI', 'DDS', 'DKS', 'DNKN', 'FL', 'GPI', 'HIBB',

            # Energy
            'CIVI', 'CRGY', 'CRC', 'DEN', 'FANG', 'MTDR', 'MUR', 'NOG',
            'OVV', 'PBF', 'PDC', 'PR', 'RRC', 'SM', 'VTN', 'WLL',

            # Real Estate
            'BNL', 'BXMT', 'CIO', 'CTRE', 'DEI', 'EPR', 'ESRT', 'FCPT',
            'GTY', 'HIW', 'INN', 'JBGS', 'KRC', 'LXP', 'NHI', 'NXRT',

            # Materials
            'ARCH', 'BCPC', 'BTU', 'HCC', 'HWKN', 'IOSP', 'KWR', 'MERC',
            'MP', 'NGVT', 'OEC', 'SLVM', 'STLD', 'SXT', 'USLM', 'WOR'
        ]
    
    def _get_fallback_sp500(self) -> List[str]:
        """
        Fallback list of top S&P 500 stocks if Wikipedia fetch fails
        """
        # Top 100 most liquid S&P 500 stocks
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
            'UNH', 'JNJ', 'V', 'XOM', 'JPM', 'WMT', 'PG', 'MA', 'CVX', 'HD',
            'LLY', 'MRK', 'ABBV', 'AVGO', 'KO', 'PEP', 'COST', 'ADBE', 'TMO',
            'MCD', 'CSCO', 'ACN', 'ABT', 'NKE', 'CRM', 'NFLX', 'DHR', 'VZ',
            'CMCSA', 'TXN', 'NEE', 'INTC', 'DIS', 'PM', 'WFC', 'UPS', 'RTX',
            'UNP', 'SPGI', 'QCOM', 'ORCL', 'IBM', 'AMD', 'INTU', 'CAT', 'GE',
            'AMGN', 'HON', 'BA', 'LOW', 'AMAT', 'GS', 'SBUX', 'ELV', 'BLK',
            'T', 'DE', 'AXP', 'GILD', 'LMT', 'PLD', 'MDT', 'SYK', 'MMC', 'ADI',
            'MDLZ', 'BKNG', 'CI', 'TJX', 'CVS', 'VRTX', 'ADP', 'REGN', 'ZTS',
            'NOW', 'TMUS', 'ISRG', 'PGR', 'SLB', 'MO', 'CB', 'BDX', 'DUK',
            'SO', 'BSX', 'EOG', 'ITW', 'MMM', 'CL', 'APD', 'CSX', 'USB'
        ]

    def _get_fallback_nasdaq100(self) -> List[str]:
        """
        Fallback NASDAQ-100 stocks
        """
        return [
            'AAPL', 'MSFT', 'AMZN', 'NVDA', 'META', 'GOOGL', 'GOOG', 'TSLA',
            'AVGO', 'COST', 'NFLX', 'AMD', 'PEP', 'ADBE', 'CSCO', 'CMCSA',
            'INTC', 'TMUS', 'INTU', 'TXN', 'QCOM', 'AMGN', 'HON', 'AMAT',
            'SBUX', 'ISRG', 'BKNG', 'VRTX', 'GILD', 'ADI', 'MDLZ', 'ADP',
            'REGN', 'LRCX', 'PYPL', 'PANW', 'MU', 'SNPS', 'KLAC', 'CDNS',
            'MRVL', 'NXPI', 'ASML', 'ABNB', 'WDAY', 'ORLY', 'CTAS', 'CHTR',
            'MNST', 'MELI', 'FTNT', 'DXCM', 'MAR', 'LULU', 'CRWD', 'ADSK',
            'PCAR', 'AEP', 'ODFL', 'ROST', 'PAYX', 'CPRT', 'MRNA', 'EA',
            'FAST', 'KDP', 'CTSH', 'DDOG', 'GEHC', 'IDXX', 'KHC', 'BKR',
            'BIIB', 'EXC', 'CSGP', 'XEL', 'ZS', 'TEAM', 'ANSS', 'TTWO',
            'ON', 'FANG', 'ILMN', 'WBD', 'CDW', 'MDB', 'GFS', 'ALGN'
        ]

    def _get_fallback_dow30(self) -> List[str]:
        """
        Fallback Dow Jones 30 stocks
        """
        return [
            'AAPL', 'MSFT', 'UNH', 'JNJ', 'V', 'JPM', 'WMT', 'PG', 'HD', 'CVX',
            'MRK', 'ABBV', 'KO', 'PEP', 'MCD', 'CSCO', 'ACN', 'ABT', 'NKE',
            'CRM', 'DIS', 'VZ', 'CMCSA', 'INTC', 'WFC', 'IBM', 'AMGN', 'HON',
            'BA', 'CAT'
        ]
    
    def get_additional_popular_stocks(self) -> List[str]:
        """
        Additional popular stocks not in S&P 500
        """
        return [
            # Tech/Growth
            'COIN', 'PLTR', 'SNOW', 'CRWD', 'DDOG', 'NET', 'ZM', 'SHOP',
            'SQ', 'ROKU', 'TWLO', 'DOCU', 'UBER', 'LYFT', 'DASH', 'ABNB',
            
            # Biotech
            'MRNA', 'BNTX', 'NVAX', 'CRSP', 'EDIT', 'NTLA',
            
            # EV/Clean Energy
            'RIVN', 'LCID', 'NIO', 'XPEV', 'LI', 'PLUG', 'FCEL', 'ENPH',
            
            # Meme/Popular
            'GME', 'AMC', 'BB', 'BBBY',
            
            # Crypto-related
            'MSTR', 'RIOT', 'MARA', 'HOOD',
            
            # ETFs (popular)
            'SPY', 'QQQ', 'IWM', 'DIA', 'VOO', 'VTI', 'VEA', 'VWO',
            'AGG', 'BND', 'TLT', 'GLD', 'SLV', 'USO', 'XLE', 'XLF',
            'XLK', 'XLV', 'XLP', 'XLI', 'XLB', 'XLRE', 'XLU', 'XLY'
        ]
    
    def get_full_universe(self, limit: int = None, include_all: bool = True) -> List[str]:
        """
        Get complete universe of stocks to track

        Args:
            limit: Optional limit on number of stocks (for testing)
            include_all: If True, includes all indices (S&P 500, NASDAQ-100, Dow 30, Russell 2000 sample)

        Returns:
            List of stock symbols
        """
        all_symbols = []

        # Get S&P 500
        logger.info("Fetching S&P 500...")
        sp500 = self.fetch_sp500_list()
        all_symbols.extend(sp500)

        if include_all:
            # Get NASDAQ-100
            logger.info("Fetching NASDAQ-100...")
            nasdaq100 = self.fetch_nasdaq100_list()
            all_symbols.extend(nasdaq100)

            # Get Dow 30
            logger.info("Fetching Dow 30...")
            dow30 = self.fetch_dow30_list()
            all_symbols.extend(dow30)

            # Get Russell 2000 sample
            logger.info("Adding Russell 2000 sample...")
            russell = self.fetch_russell2000_sample()
            all_symbols.extend(russell)

            # Get additional popular stocks
            logger.info("Adding popular stocks and ETFs...")
            additional = self.get_additional_popular_stocks()
            all_symbols.extend(additional)

        # Deduplicate and sort
        all_symbols = list(set(all_symbols))
        all_symbols.sort()

        if limit:
            all_symbols = all_symbols[:limit]

        logger.info(f"Total universe: {len(all_symbols)} stocks")
        logger.info(f"  - S&P 500: ~{len(sp500)} stocks")
        if include_all:
            logger.info(f"  - NASDAQ-100: ~{len(nasdaq100)} stocks")
            logger.info(f"  - Dow 30: ~{len(dow30)} stocks")
            logger.info(f"  - Russell 2000 sample: ~{len(russell)} stocks")
            logger.info(f"  - Additional: ~{len(self.get_additional_popular_stocks())} stocks")

        return all_symbols
    
    def populate_database(self, db: Session, symbols: List[str] = None):
        """
        Populate database with stock symbols
        
        Args:
            db: Database session
            symbols: List of symbols to add (if None, uses full universe)
        """
        if symbols is None:
            symbols = self.get_full_universe()
        
        added = 0
        updated = 0
        
        for symbol in symbols:
            # Check if stock already exists
            existing = db.query(Stock).filter(Stock.symbol == symbol).first()
            
            if existing:
                # Update if needed
                if not existing.is_active:
                    existing.is_active = True
                    updated += 1
            else:
                # Add new stock
                stock = Stock(
                    symbol=symbol,
                    name=f"{symbol} (To be updated)",  # Will be updated by data fetcher
                    is_active=True
                )
                db.add(stock)
                added += 1
        
        db.commit()
        
        logger.info(f"Database populated: {added} added, {updated} updated")
        
        return {
            "added": added,
            "updated": updated,
            "total": added + updated
        }
    
    def get_stocks_by_sector(self, sector: str) -> List[str]:
        """
        Get stocks filtered by sector (placeholder - will be enhanced)
        """
        # This will be populated when we fetch company info
        pass


def get_stock_universe(limit: int = None) -> List[str]:
    """
    Convenience function to get stock universe
    """
    manager = StockUniverse()
    return manager.get_full_universe(limit=limit)


if __name__ == "__main__":
    # Test the stock universe
    logging.basicConfig(level=logging.INFO)
    
    manager = StockUniverse()
    symbols = manager.get_full_universe(limit=50)
    
    print(f"\nFirst 50 stocks in universe:")
    for i, symbol in enumerate(symbols, 1):
        print(f"{i}. {symbol}")
    
    print(f"\nTotal stocks: {len(symbols)}")
