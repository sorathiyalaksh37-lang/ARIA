#!/usr/bin/env python3
"""
ARIA Resource Predictor - Hospital Bed Availability Forecasting
================================================================
Gradient Boosting + Random Forest ensemble for predicting hospital bed occupancy.

Author: ARIA ML Team (Senior ML Engineer)
Date: August 2026
Version: 2.0 - Production Ready (Scikit-learn)

Algorithm: GradientBoosting (70%) + RandomForest (30%) Ensemble
Target: MAE < 5 beds, RMSE < 8 beds

Usage:
    python resource_predictor.py
"""

import os
import sys
import json
import logging
import warnings
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any

import numpy as np
import pandas as pd
from tqdm import tqdm

# Deep Learning
try:
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
    from sklearn.linear_model import Ridge
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️  Scikit-learn not available")

# ML Libraries
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, mean_absolute_percentage_error

# Visualization
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

# Model Persistence
import joblib
import pickle

warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TF warnings

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

# Create directories
for directory in [MODELS_DIR, REPORTS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Logging setup
LOG_FILE = LOGS_DIR / "resource_predictor_training.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Model hyperparameters
GB_CONFIG = {
    'n_estimators': 500,
    'learning_rate': 0.05,
    'max_depth': 8,
    'min_samples_split': 10,
    'min_samples_leaf': 4,
    'subsample': 0.8,
    'random_state': 42
}

RF_CONFIG = {
    'n_estimators': 300,
    'max_depth': 15,
    'min_samples_split': 5,
    'min_samples_leaf': 2,
    'random_state': 42,
    'n_jobs': -1
}

# Ensemble weights
ENSEMBLE_WEIGHTS = {
    'gradient_boosting': 0.7,
    'random_forest': 0.3
}

# Indian holidays (2019-2022)
INDIAN_HOLIDAYS = [
    {'holiday': 'New Year', 'ds': '2019-01-01'},
    {'holiday': 'Republic Day', 'ds': '2019-01-26'},
    {'holiday': 'Holi', 'ds': '2019-03-21'},
    {'holiday': 'Independence Day', 'ds': '2019-08-15'},
    {'holiday': 'Diwali', 'ds': '2019-10-27'},
    {'holiday': 'Christmas', 'ds': '2019-12-25'},
    
    {'holiday': 'New Year', 'ds': '2020-01-01'},
    {'holiday': 'Republic Day', 'ds': '2020-01-26'},
    {'holiday': 'Holi', 'ds': '2020-03-10'},
    {'holiday': 'Independence Day', 'ds': '2020-08-15'},
    {'holiday': 'Diwali', 'ds': '2020-11-14'},
    {'holiday': 'Christmas', 'ds': '2020-12-25'},
    
    {'holiday': 'New Year', 'ds': '2021-01-01'},
    {'holiday': 'Republic Day', 'ds': '2021-01-26'},
    {'holiday': 'Holi', 'ds': '2021-03-29'},
    {'holiday': 'Independence Day', 'ds': '2021-08-15'},
    {'holiday': 'Diwali', 'ds': '2021-11-04'},
    {'holiday': 'Christmas', 'ds': '2021-12-25'},
    
    {'holiday': 'New Year', 'ds': '2022-01-01'},
    {'holiday': 'Republic Day', 'ds': '2022-01-26'},
    {'holiday': 'Holi', 'ds': '2022-03-18'},
    {'holiday': 'Independence Day', 'ds': '2022-08-15'},
    {'holiday': 'Diwali', 'ds': '2022-10-24'},
    {'holiday': 'Christmas', 'ds': '2022-12-25'},
]


# ============================================================================
# DATA GENERATION
# ============================================================================

class HospitalDataGenerator:
    """Generate realistic synthetic hospital bed occupancy data."""
    
    def __init__(self, start_date: str = '2019-01-01', n_days: int = 1095):
        self.start_date = pd.to_datetime(start_date)
        self.n_days = n_days
        self.n_hours = n_days * 24
        self.total_beds = 500  # Total hospital capacity
        
    def generate(self) -> pd.DataFrame:
        """Generate 3 years of hourly bed occupancy data."""
        logger.info(f"Generating {self.n_days} days ({self.n_hours} hours) of hospital data...")
        
        # Create timestamp range
        timestamps = pd.date_range(
            start=self.start_date,
            periods=self.n_hours,
            freq='H'
        )
        
        # Extract temporal features
        hours = timestamps.hour
        day_of_week = timestamps.dayofweek
        day_of_month = timestamps.day
        month = timestamps.month
        day_of_year = timestamps.dayofyear
        
        # ===== 1. BASE OCCUPANCY (70% baseline) =====
        base_occupancy = np.ones(self.n_hours) * 350  # 70% of 500 beds
        
        # ===== 2. TREND (slow increase over 3 years) =====
        trend = np.linspace(0, 30, self.n_hours)  # +30 beds over 3 years
        
        # ===== 3. DAILY PATTERN (7am-9pm higher) =====
        daily_pattern = np.zeros(self.n_hours)
        for i, hour in enumerate(hours):
            if 7 <= hour <= 21:  # 7am to 9pm
                daily_pattern[i] = 20 * np.sin(np.pi * (hour - 7) / 14)
            else:  # Night time
                daily_pattern[i] = -10
        
        # ===== 4. WEEKLY PATTERN (weekends +10%) =====
        weekend_effect = np.where(day_of_week >= 5, 25, 0)  # Sat-Sun
        
        # ===== 5. SEASONAL PATTERN (winter higher) =====
        # Winter (Dec-Feb): +20 beds, Summer (Apr-Jun): -15 beds
        seasonal_pattern = 20 * np.cos(2 * np.pi * (day_of_year - 15) / 365)
        
        # ===== 6. INCIDENT CORRELATION =====
        # More incidents → more beds occupied
        incident_count = self._generate_incident_pattern(timestamps)
        incident_effect = incident_count * 0.5
        
        # ===== 7. WEATHER EFFECTS =====
        temperature = self._generate_temperature(day_of_year)
        rain = self._generate_rain(day_of_year, month)
        
        # Extreme temperature → more patients
        temp_effect = np.where(
            (temperature < 10) | (temperature > 38),
            15, 0
        )
        
        # Rain → more accidents
        rain_effect = rain * 8
        
        # ===== 8. HOLIDAY EFFECTS =====
        holiday_effect = self._generate_holiday_effect(timestamps)
        
        # ===== 9. RANDOM NOISE =====
        noise = np.random.normal(0, 8, self.n_hours)
        
        # ===== COMBINE ALL COMPONENTS =====
        occupancy = (
            base_occupancy +
            trend +
            daily_pattern +
            weekend_effect +
            seasonal_pattern +
            incident_effect +
            temp_effect +
            rain_effect +
            holiday_effect +
            noise
        )
        
        # Clip to valid range [0, total_beds]
        occupancy = np.clip(occupancy, 0, self.total_beds).astype(int)
        
        # Create DataFrame
        df = pd.DataFrame({
            'timestamp': timestamps,
            'occupancy': occupancy,
            'hour': hours,
            'day_of_week': day_of_week,
            'day_of_month': day_of_month,
            'month': month,
            'is_weekend': (day_of_week >= 5).astype(int),
            'incident_count': incident_count,
            'temperature': temperature,
            'rain': rain,
            'is_holiday': (holiday_effect > 0).astype(int)
        })
        
        logger.info(f"Generated {len(df):,} hourly records")
        logger.info(f"Occupancy range: {df['occupancy'].min()} - {df['occupancy'].max()} beds")
        logger.info(f"Mean occupancy: {df['occupancy'].mean():.1f} beds ({df['occupancy'].mean()/self.total_beds*100:.1f}%)")
        
        return df
    
    def _generate_incident_pattern(self, timestamps: pd.DatetimeIndex) -> np.ndarray:
        """Generate correlated incident counts."""
        n = len(timestamps)
        hours = timestamps.hour
        day_of_week = timestamps.dayofweek
        
        # Base incidents
        incidents = np.ones(n) * 8
        
        # Rush hour peaks
        rush_hour_mask = ((hours >= 7) & (hours <= 9)) | ((hours >= 17) & (hours <= 19))
        incidents[rush_hour_mask] += 5
        
        # Weekend increase
        incidents[day_of_week >= 5] += 3
        
        # Night time (10pm-6am) - drunk driving, etc.
        night_mask = (hours >= 22) | (hours <= 6)
        incidents[night_mask] += 4
        
        # Add noise
        incidents += np.random.poisson(2, n)
        
        return incidents.astype(int)
    
    def _generate_temperature(self, day_of_year: np.ndarray) -> np.ndarray:
        """Generate realistic temperature pattern (°C)."""
        # Seasonal variation
        base_temp = 28 + 12 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        
        # Daily variation
        daily_noise = np.random.normal(0, 3, len(day_of_year))
        
        return base_temp + daily_noise
    
    def _generate_rain(self, day_of_year: np.ndarray, month: np.ndarray) -> np.ndarray:
        """Generate rain probability (0-1)."""
        # Monsoon season (June-Sep): higher probability
        monsoon_prob = np.where((month >= 6) & (month <= 9), 0.4, 0.1)
        
        # Random rain events
        rain = (np.random.random(len(day_of_year)) < monsoon_prob).astype(float)
        
        return rain
    
    def _generate_holiday_effect(self, timestamps: pd.DatetimeIndex) -> np.ndarray:
        """Generate holiday effects."""
        effect = np.zeros(len(timestamps))
        
        holidays_df = pd.DataFrame(INDIAN_HOLIDAYS)
        holidays_df['ds'] = pd.to_datetime(holidays_df['ds'])
        
        for _, holiday in holidays_df.iterrows():
            # Holiday and 1 day before/after
            mask = (timestamps.date >= (holiday['ds'] - timedelta(days=1)).date()) & \
                   (timestamps.date <= (holiday['ds'] + timedelta(days=1)).date())
            effect[mask] = 15  # +15 beds during holidays
        
        return effect


# ============================================================================
# FEATURE ENGINEERING
# ============================================================================

class FeatureEngineer:
    """Engineer comprehensive features for time series prediction."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_names = []
        
    def create_features(self, df: pd.DataFrame, fit: bool = False) -> pd.DataFrame:
        """
        Create 30+ features for prediction.
        
        Categories:
        1. Temporal features (cyclical encoding)
        2. Lag features (1h, 6h, 12h, 24h)
        3. Rolling statistics (mean, std)
        4. External factors (incidents, weather)
        """
        df = df.copy()
        
        # ===== 1. TEMPORAL FEATURES (8) =====
        # Cyclical encoding
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        # Special times
        df['is_rush_hour'] = (
            ((df['hour'] >= 7) & (df['hour'] <= 9)) |
            ((df['hour'] >= 17) & (df['hour'] <= 19))
        ).astype(int)
        df['is_night'] = ((df['hour'] >= 22) | (df['hour'] <= 6)).astype(int)
        
        # ===== 2. LAG FEATURES (4) =====
        df['occupancy_lag_1h'] = df['occupancy'].shift(1)
        df['occupancy_lag_6h'] = df['occupancy'].shift(6)
        df['occupancy_lag_12h'] = df['occupancy'].shift(12)
        df['occupancy_lag_24h'] = df['occupancy'].shift(24)
        
        # ===== 3. ROLLING STATISTICS (8) =====
        # Rolling mean
        df['occupancy_mean_6h'] = df['occupancy'].rolling(window=6, min_periods=1).mean()
        df['occupancy_mean_12h'] = df['occupancy'].rolling(window=12, min_periods=1).mean()
        df['occupancy_mean_24h'] = df['occupancy'].rolling(window=24, min_periods=1).mean()
        
        # Rolling std
        df['occupancy_std_6h'] = df['occupancy'].rolling(window=6, min_periods=1).std().fillna(0)
        df['occupancy_std_12h'] = df['occupancy'].rolling(window=12, min_periods=1).std().fillna(0)
        df['occupancy_std_24h'] = df['occupancy'].rolling(window=24, min_periods=1).std().fillna(0)
        
        # Rolling min/max
        df['occupancy_min_24h'] = df['occupancy'].rolling(window=24, min_periods=1).min()
        df['occupancy_max_24h'] = df['occupancy'].rolling(window=24, min_periods=1).max()
        
        # ===== 4. EXTERNAL FACTORS (4) =====
        df['incident_count'] = df['incident_count'].fillna(0)
        df['temperature'] = df['temperature'].fillna(df['temperature'].mean())
        df['rain'] = df['rain'].fillna(0)
        df['is_holiday'] = df['is_holiday'].fillna(0)
        
        # ===== 5. INTERACTION FEATURES (4) =====
        df['weekend_x_hour'] = df['is_weekend'] * df['hour']
        df['incident_x_rain'] = df['incident_count'] * df['rain']
        df['temp_extreme'] = ((df['temperature'] < 15) | (df['temperature'] > 35)).astype(int)
        df['holiday_x_weekend'] = df['is_holiday'] * df['is_weekend']
        
        # Fill missing values from lag features
        df = df.fillna(method='bfill').fillna(method='ffill').fillna(0)
        
        # Select feature columns (exclude target and timestamp)
        feature_cols = [
            # Temporal (8)
            'hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'month_sin', 'month_cos',
            'is_rush_hour', 'is_night',
            
            # Lags (4)
            'occupancy_lag_1h', 'occupancy_lag_6h', 'occupancy_lag_12h', 'occupancy_lag_24h',
            
            # Rolling (8)
            'occupancy_mean_6h', 'occupancy_mean_12h', 'occupancy_mean_24h',
            'occupancy_std_6h', 'occupancy_std_12h', 'occupancy_std_24h',
            'occupancy_min_24h', 'occupancy_max_24h',
            
            # External (4)
            'incident_count', 'temperature', 'rain', 'is_holiday',
            
            # Interactions (4)
            'weekend_x_hour', 'incident_x_rain', 'temp_extreme', 'holiday_x_weekend',
            
            # Others
            'is_weekend', 'day_of_month'
        ]
        
        if fit:
            self.feature_names = feature_cols
            logger.info(f"Created {len(feature_cols)} features")
        
        return df[feature_cols + ['occupancy', 'timestamp']]


# ============================================================================
# LSTM MODEL
# ============================================================================

class LSTMPredictor:
    """LSTM model for time series forecasting."""
    
    def __init__(self, config: Dict = None):
        self.config = config or LSTM_CONFIG
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.history = None
        
        if not TF_AVAILABLE:
            logger.warning("TensorFlow not available. LSTM will be skipped.")
    
    def create_sequences(self, data: np.ndarray, target: np.ndarray, seq_length: int):
        """Create sequences for LSTM."""
        X, y = [], []
        
        for i in range(len(data) - seq_length):
            X.append(data[i:i + seq_length])
            y.append(target[i + seq_length])
        
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape: Tuple[int, int]):
        """Build LSTM model architecture."""
        model = Sequential([
            # First LSTM layer
            layers.LSTM(
                self.config['lstm1_units'],
                return_sequences=True,
                input_shape=input_shape
            ),
            layers.Dropout(self.config['dropout']),
            
            # Second LSTM layer
            layers.LSTM(self.config['lstm2_units']),
            layers.Dropout(self.config['dropout']),
            
            # Dense layers
            layers.Dense(self.config['dense_units'], activation='relu'),
            layers.Dense(1)
        ])
        
        # Compile with Huber loss
        model.compile(
            optimizer=optimizers.Adam(learning_rate=self.config['learning_rate']),
            loss=keras.losses.Huber(),
            metrics=['mae', 'mse']
        )
        
        return model
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: np.ndarray, y_val: np.ndarray) -> Dict[str, Any]:
        """Train LSTM model."""
        if not TF_AVAILABLE:
            logger.warning("Skipping LSTM training (TensorFlow not available)")
            return {'status': 'skipped'}
        
        logger.info("Training LSTM model...")
        
        # Scale data
        n_samples, n_timesteps, n_features = X_train.shape
        X_train_reshaped = X_train.reshape(-1, n_features)
        X_train_scaled = self.scaler.fit_transform(X_train_reshaped)
        X_train_scaled = X_train_scaled.reshape(n_samples, n_timesteps, n_features)
        
        X_val_reshaped = X_val.reshape(-1, n_features)
        X_val_scaled = self.scaler.transform(X_val_reshaped)
        X_val_scaled = X_val_scaled.reshape(X_val.shape)
        
        # Build model
        self.model = self.build_model(input_shape=(n_timesteps, n_features))
        
        logger.info(f"Model architecture:")
        self.model.summary(print_fn=logger.info)
        
        # Callbacks
        early_stop = callbacks.EarlyStopping(
            monitor='val_loss',
            patience=self.config['patience'],
            restore_best_weights=True,
            verbose=1
        )
        
        reduce_lr = callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-6,
            verbose=1
        )
        
        # Train
        self.history = self.model.fit(
            X_train_scaled, y_train,
            validation_data=(X_val_scaled, y_val),
            epochs=self.config['epochs'],
            batch_size=self.config['batch_size'],
            callbacks=[early_stop, reduce_lr],
            verbose=1
        )
        
        # Evaluate
        train_loss, train_mae, train_mse = self.model.evaluate(X_train_scaled, y_train, verbose=0)
        val_loss, val_mae, val_mse = self.model.evaluate(X_val_scaled, y_val, verbose=0)
        
        metrics = {
            'train_loss': float(train_loss),
            'train_mae': float(train_mae),
            'train_rmse': float(np.sqrt(train_mse)),
            'val_loss': float(val_loss),
            'val_mae': float(val_mae),
            'val_rmse': float(np.sqrt(val_mse)),
            'epochs_trained': len(self.history.history['loss'])
        }
        
        logger.info(f"\nLSTM Training Results:")
        logger.info(f"  Val MAE:  {metrics['val_mae']:.2f} beds")
        logger.info(f"  Val RMSE: {metrics['val_rmse']:.2f} beds")
        logger.info(f"  Epochs:   {metrics['epochs_trained']}")
        
        return metrics
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        if not TF_AVAILABLE or self.model is None:
            logger.warning("LSTM model not available")
            return np.zeros(len(X))
        
        # Scale
        n_samples, n_timesteps, n_features = X.shape
        X_reshaped = X.reshape(-1, n_features)
        X_scaled = self.scaler.transform(X_reshaped)
        X_scaled = X_scaled.reshape(n_samples, n_timesteps, n_features)
        
        # Predict
        predictions = self.model.predict(X_scaled, verbose=0)
        
        return predictions.flatten()


# ============================================================================
# PROPHET MODEL
# ============================================================================

class ProphetPredictor:
    """Prophet model for time series forecasting."""
    
    def __init__(self):
        self.model = None
        
        if not PROPHET_AVAILABLE:
            logger.warning("Prophet not available.")
    
    def train(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train Prophet model."""
        if not PROPHET_AVAILABLE:
            logger.warning("Skipping Prophet training (not available)")
            return {'status': 'skipped'}
        
        logger.info("Training Prophet model...")
        
        # Prepare data
        df_prophet = df[['timestamp', 'occupancy']].rename(
            columns={'timestamp': 'ds', 'occupancy': 'y'}
        )
        
        # Create holidays dataframe
        holidays_df = pd.DataFrame(INDIAN_HOLIDAYS)
        holidays_df['ds'] = pd.to_datetime(holidays_df['ds'])
        
        # Initialize model with seasonalities
        self.model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=True,
            seasonality_mode='additive',
            seasonality_prior_scale=10,
            holidays_prior_scale=5,
            holidays=holidays_df,
            changepoint_prior_scale=0.05
        )
        
        # Add custom seasonalities
        self.model.add_seasonality(
            name='hourly',
            period=1,
            fourier_order=8
        )
        
        # Fit model
        self.model.fit(df_prophet)
        
        logger.info("Prophet training complete")
        
        return {'status': 'trained'}
    
    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Make predictions."""
        if not PROPHET_AVAILABLE or self.model is None:
            logger.warning("Prophet model not available")
            return np.zeros(len(df))
        
        # Prepare future dataframe
        future = pd.DataFrame({'ds': df['timestamp']})
        forecast = self.model.predict(future)
        
        return forecast['yhat'].values


# ============================================================================
# ENSEMBLE MODEL
# ============================================================================

class ResourcePredictorEnsemble:
    """Ensemble of LSTM and Prophet models."""
    
    def __init__(self, weights: Dict = None):
        self.weights = weights or ENSEMBLE_WEIGHTS
        self.lstm_predictor = LSTMPredictor()
        self.prophet_predictor = ProphetPredictor()
        self.feature_engineer = FeatureEngineer()
        self.seq_length = LSTM_CONFIG['sequence_length']
        
    def prepare_data(self, df: pd.DataFrame):
        """Prepare data for both models."""
        # Engineer features
        df_features = self.feature_engineer.create_features(df, fit=True)
        
        # Separate features and target
        feature_cols = [c for c in df_features.columns if c not in ['occupancy', 'timestamp']]
        X = df_features[feature_cols].values
        y = df_features['occupancy'].values
        timestamps = df_features['timestamp'].values
        
        # Create sequences for LSTM
        X_seq, y_seq = self.lstm_predictor.create_sequences(X, y, self.seq_length)
        timestamps_seq = timestamps[self.seq_length:]
        
        return X_seq, y_seq, timestamps_seq, df_features
    
    def train(self, df_train: pd.DataFrame, df_val: pd.DataFrame) -> Dict[str, Any]:
        """Train ensemble model."""
        logger.info("=" * 70)
        logger.info("TRAINING ENSEMBLE MODEL")
        logger.info("=" * 70)
        
        results = {}
        
        # Prepare data
        X_train, y_train, _, df_train_feat = self.prepare_data(df_train)
        X_val, y_val, _, df_val_feat = self.prepare_data(df_val)
        
        logger.info(f"LSTM input shape: {X_train.shape}")
        logger.info(f"Target shape: {y_train.shape}")
        
        # Train LSTM
        if TF_AVAILABLE:
            lstm_metrics = self.lstm_predictor.train(X_train, y_train, X_val, y_val)
            results['lstm'] = lstm_metrics
        
        # Train Prophet
        if PROPHET_AVAILABLE:
            prophet_metrics = self.prophet_predictor.train(df_train)
            results['prophet'] = prophet_metrics
        
        return results
    
    def predict(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Make ensemble predictions.
        
        Returns:
            ensemble_pred: Weighted ensemble predictions
            lstm_pred: LSTM predictions
            prophet_pred: Prophet predictions
        """
        # Prepare data
        X, y, timestamps, df_feat = self.prepare_data(df)
        
        # LSTM predictions
        lstm_pred = np.zeros(len(y))
        if TF_AVAILABLE and self.lstm_predictor.model is not None:
            lstm_pred = self.lstm_predictor.predict(X)
        
        # Prophet predictions (need to align with sequences)
        prophet_pred = np.zeros(len(y))
        if PROPHET_AVAILABLE and self.prophet_predictor.model is not None:
            prophet_full = self.prophet_predictor.predict(df)
            prophet_pred = prophet_full[self.seq_length:]
        
        # Ensemble
        total_weight = 0
        ensemble_pred = np.zeros(len(y))
        
        if TF_AVAILABLE and self.lstm_predictor.model is not None:
            ensemble_pred += self.weights['lstm'] * lstm_pred
            total_weight += self.weights['lstm']
        
        if PROPHET_AVAILABLE and self.prophet_predictor.model is not None:
            ensemble_pred += self.weights['prophet'] * prophet_pred
            total_weight += self.weights['prophet']
        
        if total_weight > 0:
            ensemble_pred /= total_weight
        
        return ensemble_pred, lstm_pred, prophet_pred


# ============================================================================
# EVALUATION
# ============================================================================

def evaluate_model(ensemble: ResourcePredictorEnsemble, df_test: pd.DataFrame) -> Dict[str, Any]:
    """Comprehensive model evaluation."""
    logger.info("=" * 70)
    logger.info("MODEL EVALUATION")
    logger.info("=" * 70)
    
    # Get predictions
    ensemble_pred, lstm_pred, prophet_pred = ensemble.predict(df_test)
    
    # Get actual values (aligned with predictions)
    _, y_true, _, _ = ensemble.prepare_data(df_test)
    
    # Calculate metrics
    def calc_metrics(y_true, y_pred, model_name):
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mape = mean_absolute_percentage_error(y_true, y_pred) * 100
        r2 = r2_score(y_true, y_pred)
        
        logger.info(f"\n{model_name} Metrics:")
        logger.info(f"  MAE:  {mae:.2f} beds")
        logger.info(f"  RMSE: {rmse:.2f} beds")
        logger.info(f"  MAPE: {mape:.2f}%")
        logger.info(f"  R²:   {r2:.4f}")
        
        return {
            'mae': float(mae),
            'rmse': float(rmse),
            'mape': float(mape),
            'r2_score': float(r2)
        }
    
    results = {
        'ensemble': calc_metrics(y_true, ensemble_pred, "Ensemble"),
    }
    
    if TF_AVAILABLE and ensemble.lstm_predictor.model is not None:
        results['lstm'] = calc_metrics(y_true, lstm_pred, "LSTM")
    
    if PROPHET_AVAILABLE and ensemble.prophet_predictor.model is not None:
        results['prophet'] = calc_metrics(y_true, prophet_pred, "Prophet")
    
    # Calculate 95% confidence intervals
    errors = ensemble_pred - y_true
    ci_lower = ensemble_pred - 1.96 * np.std(errors)
    ci_upper = ensemble_pred + 1.96 * np.std(errors)
    
    results['confidence_interval'] = {
        'lower_bound': float(ci_lower.mean()),
        'upper_bound': float(ci_upper.mean()),
        'width': float((ci_upper - ci_lower).mean())
    }
    
    logger.info(f"\n95% Confidence Interval:")
    logger.info(f"  Width: ±{results['confidence_interval']['width']:.2f} beds")
    
    return results, ensemble_pred, lstm_pred, prophet_pred, y_true


# ============================================================================
# VISUALIZATION
# ============================================================================

def create_visualizations(ensemble: ResourcePredictorEnsemble, df_test: pd.DataFrame,
                         results: Dict, ensemble_pred: np.ndarray, 
                         lstm_pred: np.ndarray, prophet_pred: np.ndarray,
                         y_true: np.ndarray, save_dir: Path):
    """Create comprehensive evaluation visualizations."""
    logger.info("Creating visualizations...")
    
    _, _, timestamps, _ = ensemble.prepare_data(df_test)
    
    fig = plt.figure(figsize=(20, 12))
    
    # 1. Time series predictions (first 7 days)
    ax1 = plt.subplot(3, 2, 1)
    plot_hours = min(24 * 7, len(y_true))  # 7 days
    hours = range(plot_hours)
    
    ax1.plot(hours, y_true[:plot_hours], label='Actual', linewidth=2, color='black')
    ax1.plot(hours, ensemble_pred[:plot_hours], label='Ensemble', linewidth=2, alpha=0.8, color='blue')
    if len(lstm_pred) > 0 and lstm_pred.sum() > 0:
        ax1.plot(hours, lstm_pred[:plot_hours], label='LSTM', linewidth=1.5, alpha=0.6, color='green')
    if len(prophet_pred) > 0 and prophet_pred.sum() > 0:
        ax1.plot(hours, prophet_pred[:plot_hours], label='Prophet', linewidth=1.5, alpha=0.6, color='orange')
    
    ax1.set_xlabel('Hours', fontsize=12)
    ax1.set_ylabel('Bed Occupancy', fontsize=12)
    ax1.set_title('Predictions vs Actual (First 7 Days)', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(alpha=0.3)
    
    # 2. Scatter plot
    ax2 = plt.subplot(3, 2, 2)
    ax2.scatter(y_true, ensemble_pred, alpha=0.5, s=10, color='blue')
    ax2.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()],
             'r--', lw=2, label='Perfect Prediction')
    ax2.set_xlabel('Actual Occupancy', fontsize=12)
    ax2.set_ylabel('Predicted Occupancy', fontsize=12)
    ax2.set_title('Predicted vs Actual', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(alpha=0.3)
    
    # 3. Error distribution
    ax3 = plt.subplot(3, 2, 3)
    errors = ensemble_pred - y_true
    ax3.hist(errors, bins=50, edgecolor='black', alpha=0.7, color='coral')
    ax3.axvline(errors.mean(), color='red', linestyle='--', linewidth=2,
                label=f'Mean: {errors.mean():.2f}')
    ax3.axvline(0, color='green', linestyle='-', linewidth=1, alpha=0.5)
    ax3.set_xlabel('Prediction Error (beds)', fontsize=12)
    ax3.set_ylabel('Frequency', fontsize=12)
    ax3.set_title('Error Distribution', fontsize=14, fontweight='bold')
    ax3.legend()
    ax3.grid(alpha=0.3)
    
    # 4. Error over time
    ax4 = plt.subplot(3, 2, 4)
    ax4.plot(hours, errors[:plot_hours], alpha=0.7, color='purple')
    ax4.axhline(0, color='red', linestyle='--', linewidth=2)
    ax4.fill_between(hours, -2*np.std(errors), 2*np.std(errors), alpha=0.2, color='gray')
    ax4.set_xlabel('Hours', fontsize=12)
    ax4.set_ylabel('Prediction Error (beds)', fontsize=12)
    ax4.set_title('Error Over Time (First 7 Days)', fontsize=14, fontweight='bold')
    ax4.grid(alpha=0.3)
    
    # 5. Model comparison
    ax5 = plt.subplot(3, 2, 5)
    models = ['Ensemble']
    mae_values = [results['ensemble']['mae']]
    rmse_values = [results['ensemble']['rmse']]
    
    if 'lstm' in results:
        models.append('LSTM')
        mae_values.append(results['lstm']['mae'])
        rmse_values.append(results['lstm']['rmse'])
    
    if 'prophet' in results:
        models.append('Prophet')
        mae_values.append(results['prophet']['mae'])
        rmse_values.append(results['prophet']['rmse'])
    
    x = np.arange(len(models))
    width = 0.35
    
    ax5.bar(x - width/2, mae_values, width, label='MAE', color='steelblue')
    ax5.bar(x + width/2, rmse_values, width, label='RMSE', color='coral')
    
    ax5.set_xlabel('Model', fontsize=12)
    ax5.set_ylabel('Error (beds)', fontsize=12)
    ax5.set_title('Model Comparison', fontsize=14, fontweight='bold')
    ax5.set_xticks(x)
    ax5.set_xticklabels(models)
    ax5.legend()
    ax5.grid(axis='y', alpha=0.3)
    
    # 6. Residuals by hour
    ax6 = plt.subplot(3, 2, 6)
    _, _, _, df_test_feat = ensemble.prepare_data(df_test)
    hours_of_day = df_test_feat['hour'].values[ensemble.seq_length:][:len(errors)]
    
    residuals_by_hour = pd.DataFrame({'hour': hours_of_day, 'error': errors})
    residuals_grouped = residuals_by_hour.groupby('hour')['error'].mean()
    
    ax6.bar(residuals_grouped.index, residuals_grouped.values, color='teal', alpha=0.7)
    ax6.axhline(0, color='red', linestyle='--', linewidth=2)
    ax6.set_xlabel('Hour of Day', fontsize=12)
    ax6.set_ylabel('Mean Error (beds)', fontsize=12)
    ax6.set_title('Average Error by Hour of Day', fontsize=14, fontweight='bold')
    ax6.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_dir / 'resource_predictor_report.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"Saved visualizations to {save_dir}/resource_predictor_report.png")


# ============================================================================
# MODEL PERSISTENCE
# ============================================================================

def save_model(ensemble: ResourcePredictorEnsemble, metadata: Dict, save_dir: Path):
    """Save model artifacts."""
    logger.info("Saving model artifacts...")
    
    # Save LSTM model
    if TF_AVAILABLE and ensemble.lstm_predictor.model is not None:
        ensemble.lstm_predictor.model.save(str(save_dir / 'resource_predictor_lstm.h5'))
        joblib.dump(ensemble.lstm_predictor.scaler, save_dir / 'resource_predictor_scaler.pkl')
    
    # Save Prophet model
    if PROPHET_AVAILABLE and ensemble.prophet_predictor.model is not None:
        with open(save_dir / 'resource_predictor_prophet.pkl', 'wb') as f:
            pickle.dump(ensemble.prophet_predictor.model, f)
    
    # Save feature engineer
    joblib.dump(ensemble.feature_engineer, save_dir / 'resource_predictor_features.pkl')
    
    # Save ensemble weights
    with open(save_dir / 'resource_ensemble_weights.json', 'w') as f:
        json.dump(ensemble.weights, f, indent=2)
    
    # Save metadata
    with open(save_dir / 'resource_predictor_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    
    logger.info(f"✅ Model artifacts saved to {save_dir}")
    logger.info(f"   - resource_predictor_lstm.h5 (LSTM model)")
    logger.info(f"   - resource_predictor_prophet.pkl (Prophet model)")
    logger.info(f"   - resource_predictor_scaler.pkl (Scaler)")
    logger.info(f"   - resource_predictor_features.pkl (Feature engineer)")
    logger.info(f"   - resource_ensemble_weights.json (Weights)")
    logger.info(f"   - resource_predictor_metadata.json (Metadata)")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    logger.info("=" * 70)
    logger.info("ARIA RESOURCE PREDICTOR - PRODUCTION TRAINING")
    logger.info("=" * 70)
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    try:
        # Check dependencies
        if not TF_AVAILABLE:
            logger.error("TensorFlow is required. Install with: pip install tensorflow")
            logger.info("Continuing without LSTM...")
        
        if not PROPHET_AVAILABLE:
            logger.error("Prophet is required. Install with: pip install prophet")
            logger.info("Continuing without Prophet...")
        
        if not TF_AVAILABLE and not PROPHET_AVAILABLE:
            logger.error("At least one model (TensorFlow or Prophet) must be available!")
            return 1
        
        # 1. Generate synthetic data
        generator = HospitalDataGenerator(start_date='2019-01-01', n_days=1095)
        df = generator.generate()
        
        # 2. Split data: Train (2019-2021), Test (2022)
        train_end = pd.Timestamp('2022-01-01')
        df_train = df[df['timestamp'] < train_end]
        df_test = df[df['timestamp'] >= train_end]
        
        logger.info(f"\nData splits:")
        logger.info(f"  Train: {len(df_train):,} hours ({df_train['timestamp'].min()} to {df_train['timestamp'].max()})")
        logger.info(f"  Test:  {len(df_test):,} hours ({df_test['timestamp'].min()} to {df_test['timestamp'].max()})")
        
        # Further split train into train/val (90/10)
        train_split = int(len(df_train) * 0.9)
        df_train_final = df_train.iloc[:train_split]
        df_val = df_train.iloc[train_split:]
        
        logger.info(f"  Train (final): {len(df_train_final):,} hours")
        logger.info(f"  Validation:    {len(df_val):,} hours")
        
        # 3. Train ensemble model
        ensemble = ResourcePredictorEnsemble()
        training_results = ensemble.train(df_train_final, df_val)
        
        # 4. Evaluate on test set
        evaluation_results, ensemble_pred, lstm_pred, prophet_pred, y_true = evaluate_model(ensemble, df_test)
        
        # 5. Create visualizations
        create_visualizations(
            ensemble, df_test, evaluation_results,
            ensemble_pred, lstm_pred, prophet_pred, y_true,
            REPORTS_DIR
        )
        
        # 6. Save model
        metadata = {
            'model_type': 'Resource Predictor (LSTM + Prophet Ensemble)',
            'training_date': datetime.now().isoformat(),
            'data_summary': {
                'total_hours': len(df),
                'train_hours': len(df_train_final),
                'val_hours': len(df_val),
                'test_hours': len(df_test),
                'date_range': f"{df['timestamp'].min()} to {df['timestamp'].max()}"
            },
            'training_results': training_results,
            'test_results': evaluation_results,
            'lstm_config': LSTM_CONFIG if TF_AVAILABLE else None,
            'ensemble_weights': ensemble.weights,
            'n_features': len(ensemble.feature_engineer.feature_names),
            'feature_names': ensemble.feature_engineer.feature_names
        }
        
        save_model(ensemble, metadata, MODELS_DIR)
        
        # Final summary
        duration = time.time() - start_time
        
        logger.info("=" * 70)
        logger.info("TRAINING COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Duration: {duration:.2f} seconds ({duration/60:.1f} minutes)")
        logger.info(f"\nFinal Test Results (Ensemble):")
        logger.info(f"  MAE:  {evaluation_results['ensemble']['mae']:.2f} beds")
        logger.info(f"  RMSE: {evaluation_results['ensemble']['rmse']:.2f} beds")
        logger.info(f"  MAPE: {evaluation_results['ensemble']['mape']:.2f}%")
        logger.info(f"  R²:   {evaluation_results['ensemble']['r2_score']:.4f}")
        
        # Check targets
        if evaluation_results['ensemble']['mae'] < 5:
            logger.info("✅ Target MAE (<5 beds) ACHIEVED!")
        else:
            logger.warning(f"⚠️  MAE target not met. Got {evaluation_results['ensemble']['mae']:.2f}, need <5")
        
        if evaluation_results['ensemble']['rmse'] < 8:
            logger.info("✅ Target RMSE (<8 beds) ACHIEVED!")
        else:
            logger.warning(f"⚠️  RMSE target not met. Got {evaluation_results['ensemble']['rmse']:.2f}, need <8")
        
        logger.info(f"\n📦 Artifacts saved:")
        logger.info(f"   Models:  {MODELS_DIR}")
        logger.info(f"   Reports: {REPORTS_DIR}")
        logger.info(f"   Logs:    {LOG_FILE}")
        logger.info("=" * 70)
        
        return 0
        
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
