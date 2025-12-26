"""
Stocks API Router
Endpoints for managing and querying stocks
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from backend.database.config import get_db
from backend.database.models import Stock

router = APIRouter()


class StockResponse(BaseModel):
    """Stock response model"""
    id: int
    symbol: str
    name: Optional[str]
    sector: Optional[str]
    industry: Optional[str]
    market_cap: Optional[float]
    is_active: bool
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[StockResponse])
async def get_stocks(
    sector: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get list of stocks with optional filtering
    """
    query = db.query(Stock).filter(Stock.is_active == True)
    
    if sector:
        query = query.filter(Stock.sector == sector)
    
    stocks = query.offset(offset).limit(limit).all()
    
    return stocks


@router.get("/{symbol}", response_model=StockResponse)
async def get_stock(symbol: str, db: Session = Depends(get_db)):
    """
    Get a specific stock by symbol
    """
    stock = db.query(Stock).filter(Stock.symbol == symbol.upper()).first()
    
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")
    
    return stock


@router.get("/sectors/list")
async def get_sectors(db: Session = Depends(get_db)):
    """
    Get list of all sectors
    """
    sectors = db.query(Stock.sector).distinct().filter(Stock.sector.isnot(None)).all()
    
    return {
        "sectors": [s[0] for s in sectors if s[0]]
    }
