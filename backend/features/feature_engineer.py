"""
Feature Engineering for Stock Prediction
Calculates 50+ technical indicators and features
This is what makes our predictions UNIQUE
"""
from __future__ import annotations
import pandas as pd
import numpy as np
from typing import List
from ta import add_all_ta_features
from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator, ROCIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator, VolumeWeightedAveragePrice
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Calculate comprehensive technical features for ML models
    """
    
    def __init__(self):
        self.feature_names = []
    
    def calculate_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate ALL features for a stock
        
        Args:
            df: DataFrame with columns: open, high, low, close, volume, datetime
        
        Returns:
            DataFrame with all features added
        """
        if df.empty or len(df) < 50:
            logger.warning("Not enough data to calculate features")
            return df
        
        # Make a copy to avoid modifying original
        data = df.copy()
        
        # Ensure required columns exist
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in data.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Convert to numeric
        for col in required_cols:
            data[col] = pd.to_numeric(data[col], errors='coerce')
        
        # Calculate features in groups
        data = self._add_price_features(data)
        data = self._add_momentum_features(data)
        data = self._add_trend_features(data)
        data = self._add_volatility_features(data)
        data = self._add_volume_features(data)
        data = self._add_pattern_features(data)
        data = self._add_custom_features(data)
        
        # Drop NaN values from indicator calculations
        data = data.fillna(method='bfill').fillna(method='ffill')
        
        logger.info(f"Calculated {len(data.columns) - len(required_cols)} features")
        
        return data
    
    def _add_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Basic price-based features"""
        
        # Returns
        df['returns'] = df['close'].pct_change()
        df['returns_5d'] = df['close'].pct_change(periods=5)
        df['returns_10d'] = df['close'].pct_change(periods=10)
        df['returns_20d'] = df['close'].pct_change(periods=20)
        
        # Price momentum
        df['price_momentum_5'] = df['close'] / df['close'].shift(5) - 1
        df['price_momentum_10'] = df['close'] / df['close'].shift(10) - 1
        df['price_momentum_20'] = df['close'] / df['close'].shift(20) - 1
        
        # High-Low spread
        df['hl_pct'] = (df['high'] - df['low']) / df['close']
        df['co_pct'] = (df['close'] - df['open']) / df['open']
        
        return df
    
    def _add_momentum_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Momentum indicators"""
        
        # RSI (multiple periods)
        for period in [7, 14, 21]:
            rsi = RSIIndicator(df['close'], window=period)
            df[f'rsi_{period}'] = rsi.rsi()
        
        # Stochastic Oscillator
        stoch = StochasticOscillator(df['high'], df['low'], df['close'])
        df['stoch_k'] = stoch.stoch()
        df['stoch_d'] = stoch.stoch_signal()
        
        # Rate of Change
        for period in [5, 10, 20]:
            roc = ROCIndicator(df['close'], window=period)
            df[f'roc_{period}'] = roc.roc()
        
        # Williams %R
        df['williams_r'] = ((df['high'].rolling(14).max() - df['close']) /
                            (df['high'].rolling(14).max() - df['low'].rolling(14).min())) * -100
        
        return df
    
    def _add_trend_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Trend indicators"""
        
        # Moving Averages
        for period in [5, 10, 20, 50, 200]:
            sma = SMAIndicator(df['close'], window=period)
            df[f'sma_{period}'] = sma.sma_indicator()
            
            ema = EMAIndicator(df['close'], window=period)
            df[f'ema_{period}'] = ema.ema_indicator()
        
        # Distance from moving averages
        df['dist_sma_20'] = (df['close'] - df['sma_20']) / df['sma_20']
        df['dist_sma_50'] = (df['close'] - df['sma_50']) / df['sma_50']
        df['dist_sma_200'] = (df['close'] - df['sma_200']) / df['sma_200']
        
        # Moving average crossovers
        df['sma_cross_50_200'] = (df['sma_50'] - df['sma_200']) / df['sma_200']
        df['ema_cross_12_26'] = (df['ema_5'] - df['ema_20']) / df['ema_20'] if 'ema_5' in df.columns and 'ema_20' in df.columns else 0
        
        # MACD
        macd = MACD(df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()
        
        # ADX (trend strength)
        adx = ADXIndicator(df['high'], df['low'], df['close'], window=14)
        df['adx'] = adx.adx()
        df['adx_pos'] = adx.adx_pos()
        df['adx_neg'] = adx.adx_neg()
        
        return df
    
    def _add_volatility_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Volatility indicators"""
        
        # Bollinger Bands
        for period in [20]:
            bb = BollingerBands(df['close'], window=period, window_dev=2)
            df[f'bb_high_{period}'] = bb.bollinger_hband()
            df[f'bb_mid_{period}'] = bb.bollinger_mavg()
            df[f'bb_low_{period}'] = bb.bollinger_lband()
            df[f'bb_width_{period}'] = bb.bollinger_wband()
            df[f'bb_pct_{period}'] = bb.bollinger_pband()
        
        # ATR (Average True Range)
        for period in [7, 14, 21]:
            atr = AverageTrueRange(df['high'], df['low'], df['close'], window=period)
            df[f'atr_{period}'] = atr.average_true_range()
        
        # Historical Volatility
        df['volatility_10'] = df['returns'].rolling(10).std()
        df['volatility_20'] = df['returns'].rolling(20).std()
        df['volatility_30'] = df['returns'].rolling(30).std()
        
        return df
    
    def _add_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Volume-based features"""
        
        # Volume changes
        df['volume_change'] = df['volume'].pct_change()
        df['volume_ma_5'] = df['volume'].rolling(5).mean()
        df['volume_ma_10'] = df['volume'].rolling(10).mean()
        df['volume_ma_20'] = df['volume'].rolling(20).mean()
        
        # Volume ratio
        df['volume_ratio_5'] = df['volume'] / df['volume_ma_5']
        df['volume_ratio_10'] = df['volume'] / df['volume_ma_10']
        
        # On-Balance Volume
        obv = OnBalanceVolumeIndicator(df['close'], df['volume'])
        df['obv'] = obv.on_balance_volume()
        df['obv_mean'] = df['obv'].rolling(20).mean()
        
        # Volume-Price Trend
        df['vpt'] = ((df['close'] - df['close'].shift(1)) / df['close'].shift(1) * df['volume']).cumsum()
        
        return df
    
    def _add_pattern_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Pattern recognition features"""
        
        # Candlestick patterns
        df['doji'] = ((abs(df['close'] - df['open']) / (df['high'] - df['low'])) < 0.1).astype(int)
        df['hammer'] = (((df['high'] - df['low']) > 3 * (df['open'] - df['close'])) & 
                        ((df['close'] - df['low']) / (.001 + df['high'] - df['low']) > 0.6)).astype(int)
        
        # Higher highs, lower lows
        df['higher_high'] = (df['high'] > df['high'].shift(1)).astype(int)
        df['lower_low'] = (df['low'] < df['low'].shift(1)).astype(int)
        
        # Gap detection
        df['gap_up'] = (df['low'] > df['high'].shift(1)).astype(int)
        df['gap_down'] = (df['high'] < df['low'].shift(1)).astype(int)
        
        return df
    
    def _add_custom_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Custom proprietary features - THIS IS WHAT MAKES US UNIQUE"""
        
        # Money Flow Index (custom implementation)
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        money_flow = typical_price * df['volume']
        
        positive_flow = money_flow.where(df['close'] > df['close'].shift(1), 0)
        negative_flow = money_flow.where(df['close'] < df['close'].shift(1), 0)
        
        positive_mf = positive_flow.rolling(14).sum()
        negative_mf = negative_flow.rolling(14).sum()
        
        df['mfi'] = 100 - (100 / (1 + positive_mf / (negative_mf + 1)))
        
        # Trend Intensity
        df['trend_intensity'] = abs(df['close'] - df['sma_20']) / df['atr_14'] if 'atr_14' in df.columns else 0
        
        # Volatility Regime (low/medium/high)
        df['volatility_regime'] = pd.qcut(df['volatility_20'], q=3, labels=[0, 1, 2], duplicates='drop')
        df['volatility_regime'] = df['volatility_regime'].astype(float)
        
        # Price Acceleration
        df['price_acceleration'] = df['returns'] - df['returns'].shift(1)
        
        # Volume Surge Detection
        volume_mean = df['volume'].rolling(20).mean()
        volume_std = df['volume'].rolling(20).std()
        df['volume_surge'] = ((df['volume'] - volume_mean) / (volume_std + 1) > 2).astype(int)
        
        # Support/Resistance proximity (simplified)
        df['near_20d_high'] = ((df['high'].rolling(20).max() - df['close']) / df['close'] < 0.02).astype(int)
        df['near_20d_low'] = ((df['close'] - df['low'].rolling(20).min()) / df['close'] < 0.02).astype(int)
        
        return df
    
    def get_feature_importance_names(self) -> list[str]:
        """
        Get list of feature names for model training
        (excludes price columns and datetime)
        """
        # This will be populated after calculating features
        exclude = ['open', 'high', 'low', 'close', 'volume', 'datetime', 'date']
        return [col for col in self.feature_names if col not in exclude]


def calculate_features_for_stock(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convenience function to calculate features for a stock
    """
    engineer = FeatureEngineer()
    return engineer.calculate_all_features(df)


if __name__ == "__main__":
    # Test feature engineering
    logging.basicConfig(level=logging.INFO)
    
    # Create sample data
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    sample_df = pd.DataFrame({
        'datetime': dates,
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 102,
        'low': np.random.randn(100).cumsum() + 98,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000000, 10000000, 100)
    })
    
    print("Testing feature engineering...")
    engineer = FeatureEngineer()
    result = engineer.calculate_all_features(sample_df)
    
    print(f"\nOriginal columns: {len(sample_df.columns)}")
    print(f"Total columns after features: {len(result.columns)}")
    print(f"Features added: {len(result.columns) - len(sample_df.columns)}")
    
    print("\nFeature columns:")
    feature_cols = [col for col in result.columns if col not in sample_df.columns]
    for i, col in enumerate(feature_cols, 1):
        print(f"{i}. {col}")
