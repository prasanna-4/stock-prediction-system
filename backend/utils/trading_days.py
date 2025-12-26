"""
Trading Day Calculator
Handles trading day calculations excluding weekends and market holidays
"""

from datetime import datetime, timedelta
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay


class TradingDayCalculator:
    """
    Calculate target dates based on trading days (excludes weekends and holidays)
    """
    
    def __init__(self):
        # US Federal holidays calendar (includes NYSE holidays)
        self.calendar = USFederalHolidayCalendar()
        
        # Custom business day offset (excludes weekends and federal holidays)
        self.business_day = CustomBusinessDay(calendar=self.calendar)
    
    def add_trading_days(self, start_date, num_days):
        """
        Add N trading days to a start date
        
        Args:
            start_date: Starting date (datetime or string)
            num_days: Number of trading days to add
        
        Returns:
            datetime: Target date after N trading days
        """
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date)
        
        # Add trading days using pandas business day offset
        target_date = start_date + (num_days * self.business_day)
        
        return target_date.to_pydatetime()
    
    def get_prediction_target_date(self, prediction_type, start_date=None):
        """
        Get target date based on prediction type
        
        Args:
            prediction_type: 'intraday', 'swing', or 'position'
            start_date: Starting date (defaults to today)
        
        Returns:
            datetime: Target date for the prediction
        """
        if start_date is None:
            start_date = datetime.now()
        
        # Trading days for each prediction type
        trading_days_map = {
            'intraday': 1,      # 1 trading day (next market day)
            'swing': 5,         # 5 trading days (approximately 1 week)
            'position': 20      # 20 trading days (approximately 1 month)
        }
        
        num_days = trading_days_map.get(prediction_type, 1)
        return self.add_trading_days(start_date, num_days)
    
    def is_trading_day(self, date):
        """
        Check if a date is a trading day
        
        Args:
            date: Date to check
        
        Returns:
            bool: True if trading day, False otherwise
        """
        if isinstance(date, str):
            date = pd.to_datetime(date)
        
        # Check if weekend
        if date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        # Check if holiday
        holidays = self.calendar.holidays(start=date, end=date)
        if len(holidays) > 0:
            return False
        
        return True
    
    def count_trading_days_between(self, start_date, end_date):
        """
        Count number of trading days between two dates
        
        Args:
            start_date: Start date
            end_date: End date
        
        Returns:
            int: Number of trading days
        """
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date)
        if isinstance(end_date, str):
            end_date = pd.to_datetime(end_date)
        
        # Create date range
        all_days = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Filter to business days only
        business_days = pd.bdate_range(
            start=start_date, 
            end=end_date,
            freq=self.business_day
        )
        
        return len(business_days)


# Create global instance
trading_day_calculator = TradingDayCalculator()


def get_target_date(prediction_type, start_date=None):
    """
    Convenience function to get target date
    
    Args:
        prediction_type: 'intraday', 'swing', or 'position'
        start_date: Starting date (defaults to today)
    
    Returns:
        datetime: Target date
    """
    return trading_day_calculator.get_prediction_target_date(prediction_type, start_date)


# Example usage and testing
if __name__ == "__main__":
    calc = TradingDayCalculator()
    
    # Test with different prediction types
    today = datetime.now()
    print(f"Today: {today.strftime('%Y-%m-%d %A')}")
    print()
    
    for pred_type in ['intraday', 'swing', 'position']:
        target = calc.get_prediction_target_date(pred_type)
        print(f"{pred_type.upper():10} -> {target.strftime('%Y-%m-%d %A')}")
    
    print()
    
    # Test specific dates
    print("Testing specific scenarios:")
    
    # Friday to Monday (skip weekend)
    friday = datetime(2025, 12, 26)  # December 26, 2025 is Friday
    monday = calc.add_trading_days(friday, 1)
    print(f"Friday Dec 26 + 1 trading day = {monday.strftime('%Y-%m-%d %A')}")
    
    # Before holiday
    dec_24 = datetime(2025, 12, 24)  # Day before Christmas
    after_christmas = calc.add_trading_days(dec_24, 1)
    print(f"Dec 24 + 1 trading day (skip Christmas) = {after_christmas.strftime('%Y-%m-%d %A')}")
    
    # Check if today is trading day
    print(f"\nIs today a trading day? {calc.is_trading_day(today)}")
