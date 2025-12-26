"""
Market Data API Router
Endpoints for fetching and updating real-time market data
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict
from datetime import datetime
from pydantic import BaseModel

from backend.database.config import get_db
from backend.services.market_data import get_market_data_service

router = APIRouter()


class PriceUpdateResponse(BaseModel):
    """Response model for price updates"""
    total: int
    successful: int
    failed: int
    timestamp: datetime
    message: str


class CurrentPriceResponse(BaseModel):
    """Response model for current price"""
    symbol: str
    price: float
    timestamp: datetime


@router.post("/refresh-prices", response_model=PriceUpdateResponse)
async def refresh_all_prices(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Refresh current prices for all stocks
    This runs in the background to avoid timeout
    """
    try:
        market_service = get_market_data_service(db)
        
        # Update prices (this might take a minute for 50 stocks)
        result = market_service.update_all_current_prices()
        
        response = PriceUpdateResponse(
            total=result['total'],
            successful=result['successful'],
            failed=result['failed'],
            timestamp=result['timestamp'],
            message=f"Updated {result['successful']} out of {result['total']} stocks"
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing prices: {str(e)}")


@router.get("/current-price/{symbol}", response_model=CurrentPriceResponse)
async def get_current_price(
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    Get current price for a specific stock
    """
    try:
        market_service = get_market_data_service(db)
        price_data = market_service.get_current_price(symbol.upper())
        
        if not price_data:
            raise HTTPException(status_code=404, detail=f"Could not fetch price for {symbol}")
        
        return CurrentPriceResponse(
            symbol=price_data['symbol'],
            price=price_data['price'],
            timestamp=price_data['timestamp']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching price: {str(e)}")


@router.get("/market-status")
async def get_market_status():
    """
    Get current market status (open/closed)
    """
    now = datetime.now()
    
    # Simple market hours check (9:30 AM - 4:00 PM ET, Monday-Friday)
    # This is simplified - production would check holidays too
    is_weekday = now.weekday() < 5  # Monday = 0, Friday = 4
    
    # Note: This doesn't account for timezone - would need pytz in production
    hour = now.hour
    is_market_hours = 9 <= hour < 16
    
    return {
        'is_open': is_weekday and is_market_hours,
        'current_time': now,
        'message': 'Market is open' if (is_weekday and is_market_hours) else 'Market is closed'
    }
