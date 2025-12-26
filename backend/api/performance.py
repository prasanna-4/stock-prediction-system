"""
Performance API Router
Endpoints for model performance metrics
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from backend.database.config import get_db
from backend.database.models import Prediction, ModelPerformance

router = APIRouter()


@router.get("/")
async def get_all_performance_metrics(db: Session = Depends(get_db)):
    """
    Get all performance metrics from ModelPerformance table
    """
    models = db.query(ModelPerformance).all()

    if not models:
        return []

    return [
        {
            "model_name": m.model_name,
            "model_version": m.model_version,
            "prediction_type": m.prediction_type,
            "total_predictions": m.total_predictions,
            "correct_predictions": m.correct_predictions,
            "accuracy": m.accuracy or 0.0,
            "win_rate": m.win_rate or 0.0,
            "avg_profit_percent": m.avg_profit_percent or 0.0,
            "avg_loss_percent": m.avg_loss_percent or 0.0,
            "sharpe_ratio": m.sharpe_ratio,
            "max_drawdown": m.max_drawdown,
            "evaluation_start_date": m.evaluation_start_date,
            "evaluation_end_date": m.evaluation_end_date
        }
        for m in models
    ]


@router.get("/overview")
async def get_performance_overview(
    prediction_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get overall performance metrics
    """
    query = db.query(Prediction).filter(Prediction.was_correct.isnot(None))
    
    if prediction_type:
        query = query.filter(Prediction.prediction_type == prediction_type)
    
    predictions = query.all()
    
    if not predictions:
        return {
            "total_predictions": 0,
            "accuracy": 0.0,
            "message": "No evaluated predictions yet"
        }
    
    total = len(predictions)
    correct = sum(1 for p in predictions if p.was_correct)
    
    avg_profit = sum(p.profit_loss_percent for p in predictions if p.profit_loss_percent) / total if total > 0 else 0
    
    winning_predictions = [p for p in predictions if p.profit_loss_percent and p.profit_loss_percent > 0]
    losing_predictions = [p for p in predictions if p.profit_loss_percent and p.profit_loss_percent < 0]
    
    return {
        "total_predictions": total,
        "correct_predictions": correct,
        "accuracy": correct / total if total > 0 else 0,
        "average_profit_loss_percent": round(avg_profit, 2),
        "win_rate": len(winning_predictions) / total if total > 0 else 0,
        "total_wins": len(winning_predictions),
        "total_losses": len(losing_predictions),
        "average_win": round(sum(p.profit_loss_percent for p in winning_predictions) / len(winning_predictions), 2) if winning_predictions else 0,
        "average_loss": round(sum(p.profit_loss_percent for p in losing_predictions) / len(losing_predictions), 2) if losing_predictions else 0
    }


@router.get("/by-type")
async def get_performance_by_type(db: Session = Depends(get_db)):
    """
    Get performance metrics broken down by prediction type
    """
    results = {}
    
    for pred_type in ["intraday", "swing", "position"]:
        query = db.query(Prediction).filter(
            Prediction.prediction_type == pred_type,
            Prediction.was_correct.isnot(None)
        )
        
        predictions = query.all()
        
        if predictions:
            total = len(predictions)
            correct = sum(1 for p in predictions if p.was_correct)
            
            results[pred_type] = {
                "total": total,
                "accuracy": correct / total if total > 0 else 0,
                "correct": correct
            }
        else:
            results[pred_type] = {
                "total": 0,
                "accuracy": 0.0,
                "correct": 0
            }
    
    return results


@router.get("/models")
async def get_model_performance(db: Session = Depends(get_db)):
    """
    Get performance metrics for all models
    """
    models = db.query(ModelPerformance).all()
    
    return {
        "models": [
            {
                "name": m.model_name,
                "version": m.model_version,
                "type": m.prediction_type,
                "accuracy": m.accuracy,
                "total_predictions": m.total_predictions,
                "win_rate": m.win_rate,
                "sharpe_ratio": m.sharpe_ratio
            }
            for m in models
        ]
    }
