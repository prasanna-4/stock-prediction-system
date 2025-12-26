"""
Predictions API Router
Endpoints for stock predictions
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from backend.database.config import get_db
from backend.database.models import Prediction, Stock

router = APIRouter()


class PredictionResponse(BaseModel):
    """Prediction response model"""
    id: str
    symbol: str
    prediction_type: str
    direction: str
    confidence: float
    current_price: float
    target_price: float
    stop_loss_price: Optional[float] = None
    entry_price_low: Optional[float] = None
    entry_price_high: Optional[float] = None
    predicted_growth_percent: float
    prediction_date: datetime
    target_date: datetime
    status: str
    # Stock information
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    market_cap_category: Optional[str] = None

    class Config:
        from_attributes = True


def get_market_cap_category(market_cap: Optional[float]) -> Optional[str]:
    """Helper function to categorize market cap"""
    if not market_cap or market_cap == 0:
        return None
    if market_cap >= 200_000_000_000:
        return 'Mega Cap'
    elif market_cap >= 10_000_000_000:
        return 'Large Cap'
    elif market_cap >= 2_000_000_000:
        return 'Mid Cap'
    elif market_cap >= 300_000_000:
        return 'Small Cap'
    elif market_cap >= 50_000_000:
        return 'Micro Cap'
    else:
        return 'Nano Cap'


@router.get("/", response_model=List[PredictionResponse])
async def get_predictions(
    symbol: Optional[str] = None,
    prediction_type: Optional[str] = Query(None, description="intraday, swing, or position"),
    direction: Optional[str] = Query(None, description="up, down, or neutral"),
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    market_cap_category: Optional[str] = Query(None, description="Mega Cap, Large Cap, Mid Cap, Small Cap, Micro Cap, Nano Cap"),
    status: str = "active",
    limit: int = Query(5000, description="Maximum number of predictions to return"),
    db: Session = Depends(get_db)
):
    """
    Get predictions with optional filtering
    Optimized with eager loading for faster performance
    """
    # Use joinedload to fetch stock data in a single query (much faster!)
    query = db.query(Prediction).options(joinedload(Prediction.stock)).join(Stock)

    if symbol:
        query = query.filter(Stock.symbol == symbol.upper())

    if prediction_type:
        query = query.filter(Prediction.prediction_type == prediction_type)

    if direction:
        query = query.filter(Prediction.direction == direction)

    if min_confidence:
        query = query.filter(Prediction.confidence >= min_confidence)

    if sector:
        query = query.filter(Stock.sector == sector)

    if status:
        query = query.filter(Prediction.status == status)

    # Order by confidence (highest first) for better UX, then by date
    predictions = query.order_by(Prediction.confidence.desc(), Prediction.prediction_date.desc()).limit(limit).all()

    # Build response with stock information
    result = []
    for pred in predictions:
        stock_market_cap_category = get_market_cap_category(pred.stock.market_cap)

        # Filter by market cap category if specified
        if market_cap_category and stock_market_cap_category != market_cap_category:
            continue

        pred_dict = {
            "id": pred.id,
            "symbol": pred.stock.symbol,
            "prediction_type": pred.prediction_type,
            "direction": pred.direction,
            "confidence": pred.confidence,
            "current_price": pred.current_price,
            "target_price": pred.target_price,
            "stop_loss_price": pred.stop_loss_price,
            "entry_price_low": pred.entry_price_low,
            "entry_price_high": pred.entry_price_high,
            "predicted_growth_percent": pred.predicted_growth_percent,
            "prediction_date": pred.prediction_date,
            "target_date": pred.target_date,
            "status": pred.status,
            "sector": pred.stock.sector,
            "industry": pred.stock.industry,
            "market_cap": pred.stock.market_cap,
            "market_cap_category": stock_market_cap_category
        }
        result.append(PredictionResponse(**pred_dict))

    return result


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(prediction_id: str, db: Session = Depends(get_db)):
    """
    Get a specific prediction by ID
    """
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    return PredictionResponse(
        id=prediction.id,
        symbol=prediction.stock.symbol,
        prediction_type=prediction.prediction_type,
        direction=prediction.direction,
        confidence=prediction.confidence,
        current_price=prediction.current_price,
        target_price=prediction.target_price,
        predicted_growth_percent=prediction.predicted_growth_percent,
        prediction_date=prediction.prediction_date,
        target_date=prediction.target_date,
        status=prediction.status
    )


@router.get("/filters/sectors")
async def get_available_sectors(db: Session = Depends(get_db)):
    """
    Get list of all available sectors
    """
    sectors = db.query(Stock.sector).distinct().filter(Stock.sector.isnot(None), Stock.sector != 'Unknown').all()
    return {
        "sectors": sorted([s[0] for s in sectors if s[0]])
    }


@router.get("/filters/market-caps")
async def get_market_cap_categories():
    """
    Get available market cap categories
    """
    return {
        "categories": [
            {"value": "Mega Cap", "label": "Mega Cap (>$200B)"},
            {"value": "Large Cap", "label": "Large Cap ($10B-$200B)"},
            {"value": "Mid Cap", "label": "Mid Cap ($2B-$10B)"},
            {"value": "Small Cap", "label": "Small Cap ($300M-$2B)"},
            {"value": "Micro Cap", "label": "Micro Cap ($50M-$300M)"},
            {"value": "Nano Cap", "label": "Nano Cap (<$50M)"}
        ]
    }


@router.get("/stock/{symbol}")
async def get_predictions_for_stock(
    symbol: str,
    prediction_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all predictions for a specific stock
    """
    stock = db.query(Stock).filter(Stock.symbol == symbol.upper()).first()

    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")

    query = db.query(Prediction).filter(Prediction.stock_id == stock.id)

    if prediction_type:
        query = query.filter(Prediction.prediction_type == prediction_type)

    predictions = query.order_by(Prediction.prediction_date.desc()).all()

    return {
        "symbol": symbol.upper(),
        "total_predictions": len(predictions),
        "predictions": [
            {
                "id": p.id,
                "type": p.prediction_type,
                "direction": p.direction,
                "confidence": p.confidence,
                "growth_percent": p.predicted_growth_percent,
                "target_price": p.target_price,
                "prediction_date": p.prediction_date,
                "status": p.status
            }
            for p in predictions
        ]
    }
