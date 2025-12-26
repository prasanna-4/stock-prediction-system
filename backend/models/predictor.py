"""
ML Model Trainer
Trains XGBoost and LightGBM models for stock prediction
This is the BRAIN of the system
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
import joblib
import logging
from pathlib import Path
from datetime import datetime, timedelta

from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import xgboost as xgb
import lightgbm as lgb

from sqlalchemy.orm import Session
from backend.database.config import get_db
from backend.database.models import Stock, PriceHistory
from backend.features.feature_engineer import FeatureEngineer

logger = logging.getLogger(__name__)


class StockPredictor:
    """
    Multi-timeframe stock prediction model
    """
    
    def __init__(self, prediction_type: str = "swing"):
        """
        Args:
            prediction_type: 'intraday' (1-day), 'swing' (3-7 days), 'position' (2-4 weeks)
        """
        self.prediction_type = prediction_type
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_names = []
        
        # Define forecast horizons
        self.horizons = {
            'intraday': 1,   # 1 day ahead
            'swing': 5,      # 5 days ahead  
            'position': 20   # 20 days ahead (4 weeks)
        }
        
        self.forecast_days = self.horizons.get(prediction_type, 5)
        
        # Model save path
        self.model_dir = Path("ml_models/trained_models")
        self.model_dir.mkdir(parents=True, exist_ok=True)
    
    def prepare_training_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare data for training
        
        Creates target variable: Will price go up by X% in N days?
        """
        # Calculate features
        engineer = FeatureEngineer()
        df_features = engineer.calculate_all_features(df)
        
        # Create target variable
        # Target: 1 if price increases by threshold, 0 otherwise
        threshold = self._get_threshold()
        
        df_features['future_return'] = (
            df_features['close'].shift(-self.forecast_days) / df_features['close'] - 1
        )
        
        df_features['target'] = (df_features['future_return'] > threshold).astype(int)
        
        # Also create regression target (actual return)
        df_features['target_return'] = df_features['future_return']
        
        # Drop rows with NaN target (last N days)
        df_features = df_features.dropna(subset=['target', 'target_return'])
        
        return df_features
    
    def _get_threshold(self) -> float:
        """
        Get minimum return threshold for positive prediction
        """
        thresholds = {
            'intraday': 0.01,   # 1% for intraday
            'swing': 0.02,      # 2% for swing
            'position': 0.05    # 5% for position
        }
        return thresholds.get(self.prediction_type, 0.02)
    
    def select_features(self, df: pd.DataFrame) -> List[str]:
        """
        Select features for model training
        """
        # Exclude target and price columns
        exclude_cols = [
            'target', 'target_return', 'future_return',
            'open', 'high', 'low', 'close', 'volume',
            'datetime', 'date', 'ticker', 'symbol'
        ]
        
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Remove any remaining NaN columns
        feature_cols = [col for col in feature_cols if df[col].notna().sum() > 0]
        
        logger.info(f"Selected {len(feature_cols)} features for training")
        
        return feature_cols
    
    def train_models(self, df: pd.DataFrame) -> Dict:
        """
        Train XGBoost and LightGBM models
        
        Returns:
            Dict with model performance metrics
        """
        logger.info(f"Training {self.prediction_type} models...")
        
        # Prepare data
        df_prepared = self.prepare_training_data(df)
        
        if len(df_prepared) < 100:
            logger.error("Not enough data for training")
            return {}
        
        # Select features
        self.feature_names = self.select_features(df_prepared)
        
        X = df_prepared[self.feature_names]
        y_class = df_prepared['target']
        y_reg = df_prepared['target_return']
        
        # Handle infinite values
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(X.mean(numeric_only=True))
        
        # Time series split (80/20 train/test)
        split_idx = int(len(X) * 0.8)
        
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y_class[:split_idx], y_class[split_idx:]
        y_train_reg, y_test_reg = y_reg[:split_idx], y_reg[split_idx:]
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train XGBoost (Classification)
        logger.info("Training XGBoost...")
        self.models['xgb_class'] = self._train_xgboost(
            X_train_scaled, y_train, X_test_scaled, y_test
        )
        
        # Train LightGBM (Classification)
        logger.info("Training LightGBM...")
        self.models['lgb_class'] = self._train_lightgbm(
            X_train_scaled, y_train, X_test_scaled, y_test
        )
        
        # Train XGBoost Regression (for price target estimation)
        logger.info("Training XGBoost Regressor...")
        self.models['xgb_reg'] = self._train_xgboost_regressor(
            X_train_scaled, y_train_reg, X_test_scaled, y_test_reg
        )
        
        # Evaluate ensemble
        metrics = self._evaluate_ensemble(X_test_scaled, y_test, y_test_reg)
        
        logger.info(f"Training complete! Accuracy: {metrics['accuracy']:.2%}")
        
        return metrics
    
    def _train_xgboost(self, X_train, y_train, X_test, y_test):
        """Train XGBoost classifier"""
        
        model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='logloss'
        )
        
        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )
        
        return model
    
    def _train_lightgbm(self, X_train, y_train, X_test, y_test):
        """Train LightGBM classifier"""
        
        model = lgb.LGBMClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            num_leaves=31,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            verbose=-1
        )
        
        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            eval_metric='binary_logloss',
            callbacks=[lgb.early_stopping(50, verbose=False)]
        )
        
        return model
    
    def _train_xgboost_regressor(self, X_train, y_train, X_test, y_test):
        """Train XGBoost regressor for return prediction"""
        
        model = xgb.XGBRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )
        
        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )
        
        return model
    
    def _evaluate_ensemble(self, X_test, y_test, y_test_reg) -> Dict:
        """
        Evaluate ensemble of models
        """
        # Get predictions from both classifiers
        xgb_pred_proba = self.models['xgb_class'].predict_proba(X_test)[:, 1]
        lgb_pred_proba = self.models['lgb_class'].predict_proba(X_test)[:, 1]
        
        # Ensemble: Average probabilities
        ensemble_proba = (xgb_pred_proba + lgb_pred_proba) / 2
        ensemble_pred = (ensemble_proba > 0.5).astype(int)
        
        # Calculate metrics
        metrics = {
            'accuracy': accuracy_score(y_test, ensemble_pred),
            'precision': precision_score(y_test, ensemble_pred, zero_division=0),
            'recall': recall_score(y_test, ensemble_pred, zero_division=0),
            'f1': f1_score(y_test, ensemble_pred, zero_division=0),
            'xgb_accuracy': accuracy_score(y_test, self.models['xgb_class'].predict(X_test)),
            'lgb_accuracy': accuracy_score(y_test, self.models['lgb_class'].predict(X_test))
        }
        
        # Get feature importances
        xgb_importance = self.models['xgb_class'].feature_importances_
        lgb_importance = self.models['lgb_class'].feature_importances_
        
        avg_importance = (xgb_importance + lgb_importance) / 2
        
        # Top 10 features
        top_features_idx = np.argsort(avg_importance)[-10:]
        top_features = [(self.feature_names[i], avg_importance[i]) for i in top_features_idx]
        
        metrics['top_features'] = top_features
        
        return metrics
    
    def predict(self, df: pd.DataFrame) -> Dict:
        """
        Make prediction for a stock
        
        Returns:
            Dict with prediction, confidence, price targets
        """
        # Calculate features
        engineer = FeatureEngineer()
        df_features = engineer.calculate_all_features(df)
        
        # Get latest row
        latest = df_features.iloc[-1:]
        
        # Extract features
        X = latest[self.feature_names]
        
        # Handle missing/inf values
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(X.mean(numeric_only=True))
        
        # Scale
        X_scaled = self.scaler.transform(X)
        
        # Get predictions from ensemble
        xgb_proba = self.models['xgb_class'].predict_proba(X_scaled)[0, 1]
        lgb_proba = self.models['lgb_class'].predict_proba(X_scaled)[0, 1]
        
        # Average probability
        confidence = (xgb_proba + lgb_proba) / 2
        
        # Get predicted return
        predicted_return = self.models['xgb_reg'].predict(X_scaled)[0]
        
        # Current price
        current_price = float(df['close'].iloc[-1])
        
        # Calculate targets
        target_price = current_price * (1 + predicted_return)
        
        # Direction
        direction = 'up' if confidence > 0.5 else 'down'
        
        # Stop loss (based on ATR if available)
        if 'atr_14' in df_features.columns:
            atr = df_features['atr_14'].iloc[-1]
            stop_loss = current_price - (2 * atr) if direction == 'up' else current_price + (2 * atr)
        else:
            # Fallback: 3% stop loss
            stop_loss = current_price * 0.97 if direction == 'up' else current_price * 1.03
        
        return {
            'direction': direction,
            'confidence': float(confidence),
            'predicted_return': float(predicted_return),
            'current_price': current_price,
            'target_price': float(target_price),
            'stop_loss': float(stop_loss),
            'forecast_days': self.forecast_days
        }
    
    def save_models(self):
        """Save trained models to disk"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_file = self.model_dir / f"{self.prediction_type}_model_{timestamp}.pkl"
        
        model_package = {
            'models': self.models,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'prediction_type': self.prediction_type,
            'forecast_days': self.forecast_days
        }
        
        joblib.dump(model_package, model_file)
        
        # Also save as latest
        latest_file = self.model_dir / f"{self.prediction_type}_model_latest.pkl"
        joblib.dump(model_package, latest_file)
        
        logger.info(f"Models saved to {model_file}")
        
        return str(model_file)
    
    def load_models(self, model_file: str = None):
        """Load trained models from disk"""
        
        if model_file is None:
            model_file = self.model_dir / f"{self.prediction_type}_model_latest.pkl"
        
        model_package = joblib.load(model_file)
        
        self.models = model_package['models']
        self.scaler = model_package['scaler']
        self.feature_names = model_package['feature_names']
        self.prediction_type = model_package['prediction_type']
        self.forecast_days = model_package['forecast_days']
        
        logger.info(f"Models loaded from {model_file}")



if __name__ == "__main__":
    # Test the predictor
    logging.basicConfig(level=logging.INFO)
    
    print("\nTesting StockPredictor...")
    print("This would normally train on real stock data")
