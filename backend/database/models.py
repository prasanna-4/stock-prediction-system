"""
Database Models
SQLAlchemy ORM models for the stock prediction system
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from .config import Base


class Stock(Base):
    """Stock/ETF information"""
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, index=True, nullable=False)
    name = Column(String(255))
    sector = Column(String(100), index=True)
    industry = Column(String(100))
    market_cap = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    predictions = relationship("Prediction", back_populates="stock")
    price_history = relationship("PriceHistory", back_populates="stock")
    
    def __repr__(self):
        return f"<Stock {self.symbol}: {self.name}>"


class Prediction(Base):
    """ML predictions for stocks"""
    __tablename__ = "predictions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    
    # Prediction details
    prediction_type = Column(String(20), nullable=False)  # 'intraday', 'swing', 'position'
    direction = Column(String(10), nullable=False)  # 'up', 'down', 'neutral'
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    
    # Price predictions
    current_price = Column(Float, nullable=False)
    target_price = Column(Float, nullable=False)
    stop_loss_price = Column(Float)
    entry_price_low = Column(Float)
    entry_price_high = Column(Float)
    
    # Growth prediction
    predicted_growth_percent = Column(Float, nullable=False)
    
    # Dates
    prediction_date = Column(DateTime(timezone=True), server_default=func.now())
    target_date = Column(DateTime(timezone=True), nullable=False)
    exit_date = Column(DateTime(timezone=True))
    
    # Model information
    model_name = Column(String(50))
    model_version = Column(String(20))
    features_used = Column(JSON)
    
    # Performance tracking
    actual_price = Column(Float)
    actual_growth_percent = Column(Float)
    was_correct = Column(Boolean)
    profit_loss_percent = Column(Float)
    
    # Status
    status = Column(String(20), default='active')  # 'active', 'hit_target', 'hit_stop', 'expired'
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    evaluated_at = Column(DateTime(timezone=True))
    
    # Relationships
    stock = relationship("Stock", back_populates="predictions")
    
    # Indexes for faster queries
    __table_args__ = (
        Index('ix_predictions_symbol_type', 'stock_id', 'prediction_type'),
        Index('ix_predictions_date', 'prediction_date'),
        Index('ix_predictions_target_date', 'target_date'),
        Index('ix_predictions_status', 'status'),
        Index('ix_predictions_confidence', 'confidence'),
    )
    
    def __repr__(self):
        return f"<Prediction {self.stock.symbol if self.stock else 'N/A'}: {self.direction} {self.predicted_growth_percent:.2f}%>"


class PriceHistory(Base):
    """Historical price data"""
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    
    date = Column(DateTime(timezone=True), nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    
    # Adjusted prices
    adj_close = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    stock = relationship("Stock", back_populates="price_history")
    
    # Indexes
    __table_args__ = (
        Index('ix_price_history_symbol_date', 'stock_id', 'date'),
    )
    
    def __repr__(self):
        return f"<PriceHistory {self.stock.symbol if self.stock else 'N/A'}: {self.date}>"


class ModelPerformance(Base):
    """Track ML model performance over time"""
    __tablename__ = "model_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    
    model_name = Column(String(50), nullable=False)
    model_version = Column(String(20), nullable=False)
    prediction_type = Column(String(20), nullable=False)
    
    # Performance metrics
    total_predictions = Column(Integer, default=0)
    correct_predictions = Column(Integer, default=0)
    accuracy = Column(Float)
    
    # Financial metrics
    avg_profit_percent = Column(Float)
    avg_loss_percent = Column(Float)
    win_rate = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    
    # Date range
    evaluation_start_date = Column(DateTime(timezone=True))
    evaluation_end_date = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ModelPerformance {self.model_name} v{self.model_version}: {self.accuracy:.2%} accuracy>"


class UserWatchlist(Base):
    """User's custom watchlist"""
    __tablename__ = "user_watchlist"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), default="default_user")  # For future multi-user support
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    
    # Alert preferences
    alert_on_prediction = Column(Boolean, default=True)
    alert_on_target_hit = Column(Boolean, default=True)
    min_confidence = Column(Float, default=0.6)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('ix_watchlist_user', 'user_id'),
    )


class Alert(Base):
    """Alert history"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(String(36), ForeignKey("predictions.id"))
    
    alert_type = Column(String(50), nullable=False)  # 'new_prediction', 'target_hit', 'stop_hit'
    message = Column(String(500), nullable=False)
    
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_via = Column(String(20))  # 'email', 'sms', 'both'
    was_successful = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Alert {self.alert_type}: {self.sent_at}>"
