#!/usr/bin/env python3
"""
ARIA ETA Predictor - XGBoost Regressor
=======================================
Predict ambulance arrival time based on route and context features.

Author: ARIA ML Team
Date: August 2026
Version: 1.0

Model Details:
- Algorithm: XGBoost Regressor with Quantile Regression
- Target: Predict ETA in minutes
- MAE Target: <2 minutes

Usage:
    python eta_predictor.py
"""

import os
import sys
import json
import logging
import warnings
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any

import numpy as np
import pandas as pd
from tqdm import tqdm

# ML Libraries
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb

# Hyperparameter Optimization
try:
    import optuna
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False
    print("⚠️  Optuna not available. Skipping hyperparameter optimization.")

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

# Model Persistence
import joblib

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

# Create directories
MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Logging setup
LOG_FILE = LOGS_DIR / "eta_predictor_training.log"
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
XGBOOST_PARAMS = {
    'n_estimators': 300,
    'max_depth': 10,
    'learning_rate': 0.1,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'objective': 'reg:squarederror',
    'random_state': 42
}

# ============================================================================
# DATA GENERATION
# ============================================================================

class ETADataGenerator:
    """Generate synthetic ambulance trip data."""
    
    def __init__(self, n_samples: int = 50000):
        self.n_samples = n_samples
        self.random_state = 42
        np.random.seed(self.random_state)
        
    def generate_data(self) -> pd.DataFrame:
        """Generate synthetic ETA dataset."""
        logger.info(f"Generating {self.n_samples:,} synthetic ambulance trips...")
        
        # Distance (1-20km, exponential distribution)
        distance_km = np.random.exponential(scale=5, size=self.n_samples)
        distance_km = np.clip(distance_km, 1, 20)
        
        # Traffic levels
        traffic_levels = np.random.choice(
            ['LOW', 'MODERATE', 'HIGH', 'SEVERE'],
            size=self.n_samples,
            p=[0.3, 0.4, 0.2, 0.1]
        )
        
        # Time features
        hour_of_day = np.random.randint(0, 24, size=self.n_samples)
        day_of_week = np.random.randint(0, 7, size=self.n_samples)
        
        # Weather conditions
        weather = np.random.choice(
            ['CLEAR', 'RAIN', 'FOG', 'STORM'],
            size=self.n_samples,
            p=[0.6, 0.25, 0.10, 0.05]
        )
        
        # Road features
        road_type = np.random.choice(
            ['HIGHWAY', 'MAIN_ROAD', 'SIDE_STREET'],
            size=self.n_samples,
            p=[0.3, 0.5, 0.2]
        )
        speed_limit = np.where(
            road_type == 'HIGHWAY', 80,
            np.where(road_type == 'MAIN_ROAD', 50, 30)
        )
        num_signals = np.random.poisson(lam=distance_km * 2, size=self.n_samples)
        turns_count = np.random.poisson(lam=distance_km * 1.5, size=self.n_samples)
        
        # Ambulance features
        ambulance_type = np.random.choice(
            ['BASIC', 'ALS', 'CRITICAL_CARE'],
            size=self.n_samples,
            p=[0.3, 0.5, 0.2]
        )
        driver_experience = np.random.gamma(shape=3, scale=2, size=self.n_samples)
        driver_experience = np.clip(driver_experience, 0.5, 20)
        
        # Calculate base ETA
        base_speed = 40  # km/h
        
        # Adjust speed based on factors
        speed_multiplier = np.ones(self.n_samples)
        
        # Traffic impact
        traffic_multipliers = {
            'LOW': 1.0, 'MODERATE': 0.8, 'HIGH': 0.6, 'SEVERE': 0.4
        }
        for level, mult in traffic_multipliers.items():
            speed_multiplier[traffic_levels == level] *= mult
        
        # Weather impact
        weather_multipliers = {
            'CLEAR': 1.0, 'RAIN': 0.85, 'FOG': 0.7, 'STORM': 0.6
        }
        for cond, mult in weather_multipliers.items():
            speed_multiplier[weather == cond] *= mult
        
        # Rush hour impact (7-9am, 5-7pm)
        is_rush_hour = ((hour_of_day >= 7) & (hour_of_day <= 9)) | \
                       ((hour_of_day >= 17) & (hour_of_day <= 19))
        speed_multiplier[is_rush_hour] *= 0.7
        
        # Calculate ETA
        effective_speed = base_speed * speed_multiplier
        travel_time_minutes = (distance_km / effective_speed) * 60
        
        # Add delays for signals and turns
        signal_delay = num_signals * np.random.uniform(0.3, 0.8, size=self.n_samples)
        turn_delay = turns_count * np.random.uniform(0.1, 0.3, size=self.n_samples)
        
        eta_minutes = travel_time_minutes + signal_delay + turn_delay
        
        # Add random noise
        eta_minutes += np.random.normal(0, 0.5, size=self.n_samples)
        eta_minutes = np.clip(eta_minutes, 2, 60)
        
        # Create DataFrame
        df = pd.DataFrame({
            'distance_km': distance_km,
            'traffic_level': traffic_levels,
            'hour_of_day': hour_of_day,
            'day_of_week': day_of_week,
            'weather': weather,
            'road_type': road_type,
            'speed_limit': speed_limit,
            'num_signals': num_signals,
            'turns_count': turns_count,
            'ambulance_type': ambulance_type,
            'driver_experience': driver_experience,
            'eta_minutes': eta_minutes
        })
        
        logger.info(f"Generated {len(df):,} samples")
        logger.info(f"ETA range: {df['eta_minutes'].min():.1f} - {df['eta_minutes'].max():.1f} minutes")
        logger.info(f"Mean ETA: {df['eta_minutes'].mean():.1f} minutes")
        
        return df


# ============================================================================
# FEATURE ENGINEERING
# ============================================================================

class ETAFeatureEngineer:
    """Feature engineering for ETA prediction."""
    
    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.feature_names = []
        
    def create_features(self, df: pd.DataFrame, fit: bool = False) -> pd.DataFrame:
        """Create comprehensive feature set."""
        df = df.copy()
        
        # Distance features
        df['log_distance'] = np.log1p(df['distance_km'])
        df['distance_squared'] = df['distance_km'] ** 2
        
        # Temporal features (cyclical encoding)
        df['hour_sin'] = np.sin(2 * np.pi * df['hour_of_day'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour_of_day'] / 24)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        # Rush hour indicator
        df['is_rush_hour'] = (
            ((df['hour_of_day'] >= 7) & (df['hour_of_day'] <= 9)) |
            ((df['hour_of_day'] >= 17) & (df['hour_of_day'] <= 19))
        ).astype(int)
        
        # Weekend indicator
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # Encode categorical variables
        categorical_cols = ['traffic_level', 'weather', 'road_type', 'ambulance_type']
        
        for col in categorical_cols:
            if fit:
                self.label_encoders[col] = LabelEncoder()
                df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df[col])
            else:
                df[f'{col}_encoded'] = self.label_encoders[col].transform(df[col])
        
        # Interaction features
        df['distance_x_traffic'] = df['distance_km'] * df['traffic_level_encoded']
        df['distance_x_weather'] = df['distance_km'] * df['weather_encoded']
        df['signals_per_km'] = df['num_signals'] / (df['distance_km'] + 1)
        df['turns_per_km'] = df['turns_count'] / (df['distance_km'] + 1)
        
        # Road complexity score
        df['complexity_score'] = (
            df['num_signals'] * 0.3 +
            df['turns_count'] * 0.2 +
            (1 / (df['speed_limit'] + 1)) * 100
        )
        
        # Driver factor
        df['driver_factor'] = df['driver_experience'] / 10
        
        # Select feature columns
        feature_cols = [
            'distance_km', 'log_distance', 'distance_squared',
            'hour_sin', 'hour_cos', 'day_sin', 'day_cos',
            'is_rush_hour', 'is_weekend',
            'traffic_level_encoded', 'weather_encoded', 'road_type_encoded',
            'ambulance_type_encoded',
            'speed_limit', 'num_signals', 'turns_count',
            'driver_experience', 'driver_factor',
            'distance_x_traffic', 'distance_x_weather',
            'signals_per_km', 'turns_per_km', 'complexity_score'
        ]
        
        if fit:
            self.feature_names = feature_cols
        
        return df[feature_cols]


# ============================================================================
# ETA PREDICTOR MODEL
# ============================================================================

class ETAPredictorModel:
    """XGBoost-based ETA predictor with quantile regression."""
    
    def __init__(self, params: Dict = None):
        self.params = params or XGBOOST_PARAMS
        self.model = None
        self.model_q05 = None  # Lower bound (5th percentile)
        self.model_q95 = None  # Upper bound (95th percentile)
        self.feature_engineer = ETAFeatureEngineer()
        
    def train(self, X_train: pd.DataFrame, y_train: np.ndarray,
              X_val: pd.DataFrame, y_val: np.ndarray) -> Dict[str, float]:
        """Train ETA prediction models."""
        logger.info("Training ETA Predictor...")
        
        # Feature engineering
        X_train_features = self.feature_engineer.create_features(X_train, fit=True)
        X_val_features = self.feature_engineer.create_features(X_val, fit=False)
        
        logger.info(f"Feature matrix shape: {X_train_features.shape}")
        logger.info(f"Features: {len(self.feature_engineer.feature_names)}")
        
        # Train main model (median prediction)
        logger.info("Training main model...")
        self.model = xgb.XGBRegressor(**self.params)
        
        self.model.fit(
            X_train_features, y_train,
            verbose=False
        )
        
        # Train quantile models for confidence intervals
        logger.info("Training quantile models...")
        
        # 5th percentile (lower bound)
        params_q05 = self.params.copy()
        params_q05['objective'] = 'reg:quantileerror'
        params_q05['quantile_alpha'] = 0.05
        self.model_q05 = xgb.XGBRegressor(**params_q05)
        self.model_q05.fit(X_train_features, y_train, verbose=False)
        
        # 95th percentile (upper bound)
        params_q95 = self.params.copy()
        params_q95['objective'] = 'reg:quantileerror'
        params_q95['quantile_alpha'] = 0.95
        self.model_q95 = xgb.XGBRegressor(**params_q95)
        self.model_q95.fit(X_train_features, y_train, verbose=False)
        
        # Evaluate
        y_pred = self.model.predict(X_val_features)
        
        mae = mean_absolute_error(y_val, y_pred)
        rmse = np.sqrt(mean_squared_error(y_val, y_pred))
        mape = np.mean(np.abs((y_val - y_pred) / y_val)) * 100
        r2 = r2_score(y_val, y_pred)
        
        metrics = {
            'mae': mae,
            'rmse': rmse,
            'mape': mape,
            'r2_score': r2
        }
        
        logger.info(f"\nValidation Metrics:")
        logger.info(f"  MAE:  {mae:.4f} minutes")
        logger.info(f"  RMSE: {rmse:.4f} minutes")
        logger.info(f"  MAPE: {mape:.2f}%")
        logger.info(f"  R²:   {r2:.4f}")
        
        return metrics
    
    def predict(self, X: pd.DataFrame, return_intervals: bool = False) -> np.ndarray:
        """Predict ETA with optional confidence intervals."""
        X_features = self.feature_engineer.create_features(X, fit=False)
        
        # Median prediction
        y_pred = self.model.predict(X_features)
        
        if return_intervals:
            y_pred_lower = self.model_q05.predict(X_features)
            y_pred_upper = self.model_q95.predict(X_features)
            
            return np.column_stack([y_pred_lower, y_pred, y_pred_upper])
        
        return y_pred
    
    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance."""
        importance = self.model.feature_importances_
        
        return pd.DataFrame({
            'feature': self.feature_engineer.feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)


# ============================================================================
# HYPERPARAMETER OPTIMIZATION
# ============================================================================

def optimize_hyperparameters(X_train: pd.DataFrame, y_train: np.ndarray,
                            X_val: pd.DataFrame, y_val: np.ndarray,
                            n_trials: int = 20) -> Dict:
    """Optimize hyperparameters using Optuna."""
    if not OPTUNA_AVAILABLE:
        logger.warning("Optuna not available, using default parameters")
        return XGBOOST_PARAMS
    
    logger.info(f"Optimizing hyperparameters ({n_trials} trials)...")
    
    feature_engineer = ETAFeatureEngineer()
    X_train_features = feature_engineer.create_features(X_train, fit=True)
    X_val_features = feature_engineer.create_features(X_val, fit=False)
    
    def objective(trial):
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 100, 500),
            'max_depth': trial.suggest_int('max_depth', 5, 15),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'subsample': trial.suggest_float('subsample', 0.6, 0.9),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 0.9),
            'objective': 'reg:squarederror',
            'random_state': 42
        }
        
        model = xgb.XGBRegressor(**params)
        model.fit(X_train_features, y_train, verbose=False)
        y_pred = model.predict(X_val_features)
        
        mae = mean_absolute_error(y_val, y_pred)
        return mae
    
    study = optuna.create_study(direction='minimize')
    study.optimize(objective, n_trials=n_trials, show_progress_bar=True)
    
    logger.info(f"Best MAE: {study.best_value:.4f}")
    logger.info(f"Best parameters: {study.best_params}")
    
    best_params = study.best_params
    best_params['objective'] = 'reg:squarederror'
    best_params['random_state'] = 42
    
    return best_params


# ============================================================================
# EVALUATION AND VISUALIZATION
# ============================================================================

def evaluate_model(model: ETAPredictorModel, X_test: pd.DataFrame,
                   y_test: np.ndarray) -> Dict[str, Any]:
    """Comprehensive model evaluation."""
    logger.info("=" * 70)
    logger.info("MODEL EVALUATION")
    logger.info("=" * 70)
    
    # Predictions
    y_pred = model.predict(X_test)
    predictions_with_intervals = model.predict(X_test, return_intervals=True)
    
    # Metrics
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
    r2 = r2_score(y_test, y_pred)
    
    # Error analysis
    errors = y_pred - y_test
    
    logger.info(f"\nTest Set Metrics:")
    logger.info(f"  MAE:  {mae:.4f} minutes")
    logger.info(f"  RMSE: {rmse:.4f} minutes")
    logger.info(f"  MAPE: {mape:.2f}%")
    logger.info(f"  R²:   {r2:.4f}")
    
    logger.info(f"\nError Distribution:")
    logger.info(f"  Mean Error:   {errors.mean():.4f}")
    logger.info(f"  Std Error:    {errors.std():.4f}")
    logger.info(f"  Min Error:    {errors.min():.4f}")
    logger.info(f"  Max Error:    {errors.max():.4f}")
    logger.info(f"  Median Error: {np.median(errors):.4f}")
    
    results = {
        'mae': mae,
        'rmse': rmse,
        'mape': mape,
        'r2_score': r2,
        'error_stats': {
            'mean': float(errors.mean()),
            'std': float(errors.std()),
            'min': float(errors.min()),
            'max': float(errors.max()),
            'median': float(np.median(errors))
        }
    }
    
    return results


def create_visualizations(model: ETAPredictorModel, X_test: pd.DataFrame,
                         y_test: np.ndarray, save_dir: Path):
    """Create evaluation visualizations."""
    logger.info("Creating visualizations...")
    
    y_pred = model.predict(X_test)
    errors = y_pred - y_test
    
    # Create figure with subplots
    fig = plt.figure(figsize=(16, 12))
    
    # 1. Predicted vs Actual
    ax1 = plt.subplot(2, 2, 1)
    ax1.scatter(y_test, y_pred, alpha=0.5, s=10)
    ax1.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 
             'r--', lw=2, label='Perfect Prediction')
    ax1.set_xlabel('Actual ETA (minutes)', fontsize=12)
    ax1.set_ylabel('Predicted ETA (minutes)', fontsize=12)
    ax1.set_title('Predicted vs Actual ETA', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(alpha=0.3)
    
    # 2. Error Distribution
    ax2 = plt.subplot(2, 2, 2)
    ax2.hist(errors, bins=50, edgecolor='black', alpha=0.7)
    ax2.axvline(errors.mean(), color='r', linestyle='--', linewidth=2, 
                label=f'Mean: {errors.mean():.2f}')
    ax2.set_xlabel('Prediction Error (minutes)', fontsize=12)
    ax2.set_ylabel('Frequency', fontsize=12)
    ax2.set_title('Error Distribution', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(alpha=0.3)
    
    # 3. Feature Importance
    ax3 = plt.subplot(2, 2, 3)
    feature_importance = model.get_feature_importance()
    top_features = feature_importance.head(10)
    ax3.barh(range(len(top_features)), top_features['importance'].values)
    ax3.set_yticks(range(len(top_features)))
    ax3.set_yticklabels(top_features['feature'].values)
    ax3.set_xlabel('Importance', fontsize=12)
    ax3.set_title('Top 10 Feature Importance', fontsize=14, fontweight='bold')
    ax3.grid(axis='x', alpha=0.3)
    
    # 4. Error vs Distance
    ax4 = plt.subplot(2, 2, 4)
    ax4.scatter(X_test['distance_km'], errors, alpha=0.5, s=10)
    ax4.axhline(0, color='r', linestyle='--', linewidth=2)
    ax4.set_xlabel('Distance (km)', fontsize=12)
    ax4.set_ylabel('Prediction Error (minutes)', fontsize=12)
    ax4.set_title('Error vs Distance', fontsize=14, fontweight='bold')
    ax4.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_dir / 'eta_predictor_evaluation.png', dpi=300)
    plt.close()
    
    logger.info(f"Saved visualizations to {save_dir}/eta_predictor_evaluation.png")


# ============================================================================
# MODEL PERSISTENCE
# ============================================================================

def save_model(model: ETAPredictorModel, metadata: Dict, save_dir: Path):
    """Save model artifacts."""
    logger.info("Saving model artifacts...")
    
    # Save main model
    joblib.dump(model.model, save_dir / 'eta_predictor.pkl')
    
    # Save quantile models
    joblib.dump(model.model_q05, save_dir / 'eta_predictor_q05.pkl')
    joblib.dump(model.model_q95, save_dir / 'eta_predictor_q95.pkl')
    
    # Save feature engineer (includes encoders and scaler)
    joblib.dump(model.feature_engineer, save_dir / 'eta_predictor_scaler.pkl')
    
    # Save feature names
    with open(save_dir / 'eta_predictor_features.json', 'w') as f:
        json.dump({
            'features': model.feature_engineer.feature_names,
            'num_features': len(model.feature_engineer.feature_names)
        }, f, indent=2)
    
    # Save metadata
    with open(save_dir / 'eta_predictor_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    
    logger.info(f"Model artifacts saved to {save_dir}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    logger.info("=" * 70)
    logger.info("ARIA ETA PREDICTOR TRAINING")
    logger.info("=" * 70)
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    try:
        # Generate data
        generator = ETADataGenerator(n_samples=50000)
        df = generator.generate_data()
        
        # Split features and target
        X = df.drop('eta_minutes', axis=1)
        y = df['eta_minutes'].values
        
        # Split data (80% train, 20% test)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Further split train into train and validation
        X_train, X_val, y_train, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42
        )
        
        logger.info(f"\nData splits:")
        logger.info(f"  Train: {len(X_train):,} samples")
        logger.info(f"  Val:   {len(X_val):,} samples")
        logger.info(f"  Test:  {len(X_test):,} samples")
        
        # Optimize hyperparameters (optional)
        # optimized_params = optimize_hyperparameters(X_train, y_train, X_val, y_val)
        
        # Train model
        model = ETAPredictorModel()
        training_results = model.train(X_train, y_train, X_val, y_val)
        
        # Evaluate on test set
        evaluation_results = evaluate_model(model, X_test, y_test)
        
        # Create visualizations
        create_visualizations(model, X_test, y_test, REPORTS_DIR)
        
        # Feature importance
        feature_importance = model.get_feature_importance()
        logger.info("\nTop 10 Important Features:")
        for idx, row in feature_importance.head(10).iterrows():
            logger.info(f"  {row['feature']}: {row['importance']:.4f}")
        
        # Save model
        metadata = {
            'model_type': 'ETA Predictor (XGBoost Regressor)',
            'training_date': datetime.now().isoformat(),
            'train_samples': len(X_train),
            'val_samples': len(X_val),
            'test_samples': len(X_test),
            'training_results': training_results,
            'test_results': evaluation_results,
            'xgboost_params': model.params,
            'feature_names': model.feature_engineer.feature_names,
            'num_features': len(model.feature_engineer.feature_names)
        }
        
        save_model(model, metadata, MODELS_DIR)
        
        # Final summary
        duration = time.time() - start_time
        
        logger.info("=" * 70)
        logger.info("TRAINING COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Final Test MAE: {evaluation_results['mae']:.4f} minutes")
        logger.info(f"Final Test RMSE: {evaluation_results['rmse']:.4f} minutes")
        logger.info(f"Final Test R²: {evaluation_results['r2_score']:.4f}")
        
        # Check if target met
        if evaluation_results['mae'] < 2.0:
            logger.info("✅ Target MAE (<2 minutes) ACHIEVED!")
        else:
            logger.warning(f"⚠️  Target MAE not met. Got {evaluation_results['mae']:.4f}, need <2.0")
        
        logger.info(f"\nModel saved to: {MODELS_DIR}")
        logger.info(f"Reports saved to: {REPORTS_DIR}")
        logger.info("=" * 70)
        
        return 0
        
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
