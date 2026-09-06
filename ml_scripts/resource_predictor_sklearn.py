#!/usr/bin/env python3
"""
ARIA Resource Predictor - Hospital Bed Occupancy Forecasting
=============================================================
Uses Gradient Boosting + Random Forest ensemble (scikit-learn only)

Target: MAE < 5 beds, RMSE < 8 beds
"""

import sys
import json
import logging
import warnings
import time
from pathlib import Path
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, mean_absolute_percentage_error
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import joblib

warnings.filterwarnings('ignore')

# Paths
BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

for d in [MODELS_DIR, REPORTS_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / "resource_predictor_training.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def generate_data(n_hours=26280, total_beds=500):
    """Generate 3 years of hourly hospital bed occupancy data."""
    logger.info(f"Generating {n_hours} hours ({n_hours//24} days) of data...")
    
    timestamps = pd.date_range('2019-01-01', periods=n_hours, freq='H')
    hours = timestamps.hour.values
    day_of_week = timestamps.dayofweek.values
    month = timestamps.month.values
    day_of_year = timestamps.dayofyear.values
    
    # Base occupancy (70%)
    occupancy = np.ones(len(timestamps)) * 350
    
    # Trend
    occupancy += np.linspace(0, 30, len(timestamps))
    
    # Daily pattern (higher 7am-9pm)
    for i, h in enumerate(hours):
        if 7 <= h <= 21:
            occupancy[i] += 20 * np.sin(np.pi * (h - 7) / 14)
        else:
            occupancy[i] -= 10
    
    # Weekend effect
    occupancy[day_of_week >= 5] += 25
    
    # Seasonal (winter higher)
    occupancy += 20 * np.cos(2 * np.pi * (day_of_year - 15) / 365)
    
    # Incidents
    incidents = np.ones(len(timestamps)) * 8
    incidents[((hours >= 7) & (hours <= 9)) | ((hours >= 17) & (hours <= 19))] += 5
    incidents[day_of_week >= 5] += 3
    incidents[(hours >= 22) | (hours <= 6)] += 4
    incidents += np.random.poisson(2, len(timestamps))
    occupancy += incidents * 0.5
    
    # Weather
    temp = 28 + 12 * np.sin(2 * np.pi * (day_of_year - 80) / 365) + np.random.normal(0, 3, len(timestamps))
    rain = (np.random.random(len(timestamps)) < np.where((month >= 6) & (month <= 9), 0.4, 0.1)).astype(float)
    occupancy[np.abs(temp - 28) > 10] += 15
    occupancy += rain * 8
    
    # Noise
    occupancy += np.random.normal(0, 8, len(timestamps))
    occupancy = np.clip(occupancy, 0, total_beds).astype(int)
    
    df = pd.DataFrame({
        'timestamp': timestamps,
        'occupancy': occupancy,
        'hour': hours,
        'day_of_week': day_of_week,
        'month': month,
        'is_weekend': (day_of_week >= 5).astype(int),
        'incident_count': incidents.astype(int),
        'temperature': temp,
        'rain': rain
    })
    
    logger.info(f"Generated {len(df):,} records. Occupancy: {df['occupancy'].min()}-{df['occupancy'].max()} (mean: {df['occupancy'].mean():.1f})")
    return df

def create_features(df):
    """Engineer 30+ features."""
    df = df.copy()
    
    # Cyclical
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
    df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    
    # Lags
    for lag in [1, 6, 12, 24]:
        df[f'occupancy_lag_{lag}h'] = df['occupancy'].shift(lag)
    
    # Rolling stats
    for window in [6, 12, 24]:
        df[f'occupancy_mean_{window}h'] = df['occupancy'].rolling(window, min_periods=1).mean()
        df[f'occupancy_std_{window}h'] = df['occupancy'].rolling(window, min_periods=1).std().fillna(0)
    
    df['occupancy_min_24h'] = df['occupancy'].rolling(24, min_periods=1).min()
    df['occupancy_max_24h'] = df['occupancy'].rolling(24, min_periods=1).max()
    
    # Interactions
    df['is_rush_hour'] = (((df['hour'] >= 7) & (df['hour'] <= 9)) | ((df['hour'] >= 17) & (df['hour'] <= 19))).astype(int)
    df['weekend_x_hour'] = df['is_weekend'] * df['hour']
    df['incident_x_rain'] = df['incident_count'] * df['rain']
    df['temp_extreme'] = ((df['temperature'] < 15) | (df['temperature'] > 35)).astype(int)
    
    df = df.fillna(method='bfill').fillna(method='ffill').fillna(0)
    
    feature_cols = [
        'hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'month_sin', 'month_cos',
        'occupancy_lag_1h', 'occupancy_lag_6h', 'occupancy_lag_12h', 'occupancy_lag_24h',
        'occupancy_mean_6h', 'occupancy_mean_12h', 'occupancy_mean_24h',
        'occupancy_std_6h', 'occupancy_std_12h', 'occupancy_std_24h',
        'occupancy_min_24h', 'occupancy_max_24h',
        'incident_count', 'temperature', 'rain', 'is_weekend',
        'is_rush_hour', 'weekend_x_hour', 'incident_x_rain', 'temp_extreme'
    ]
    
    return df, feature_cols

def train_ensemble(X_train, y_train, X_val, y_val):
    """Train Gradient Boosting + Random Forest ensemble."""
    logger.info("Training Gradient Boosting...")
    gb = GradientBoostingRegressor(
        n_estimators=500, learning_rate=0.05, max_depth=8,
        min_samples_split=10, subsample=0.8, random_state=42
    )
    gb.fit(X_train, y_train)
    
    logger.info("Training Random Forest...")
    rf = RandomForestRegressor(
        n_estimators=300, max_depth=15, min_samples_split=5,
        random_state=42, n_jobs=-1
    )
    rf.fit(X_train, y_train)
    
    # Validate
    gb_pred = gb.predict(X_val)
    rf_pred = rf.predict(X_val)
    ensemble_pred = 0.7 * gb_pred + 0.3 * rf_pred
    
    mae = mean_absolute_error(y_val, ensemble_pred)
    rmse = np.sqrt(mean_squared_error(y_val, ensemble_pred))
    
    logger.info(f"Validation - MAE: {mae:.2f}, RMSE: {rmse:.2f}")
    
    return gb, rf, {'mae': float(mae), 'rmse': float(rmse)}

def evaluate(gb, rf, X_test, y_test):
    """Evaluate ensemble."""
    gb_pred = gb.predict(X_test)
    rf_pred = rf.predict(X_test)
    ensemble_pred = 0.7 * gb_pred + 0.3 * rf_pred
    
    mae = mean_absolute_error(y_test, ensemble_pred)
    rmse = np.sqrt(mean_squared_error(y_test, ensemble_pred))
    mape = mean_absolute_percentage_error(y_test, ensemble_pred) * 100
    r2 = r2_score(y_test, ensemble_pred)
    
    logger.info(f"\nTest Results:")
    logger.info(f"  MAE:  {mae:.2f} beds")
    logger.info(f"  RMSE: {rmse:.2f} beds")
    logger.info(f"  MAPE: {mape:.2f}%")
    logger.info(f"  R²:   {r2:.4f}")
    
    return {'mae': float(mae), 'rmse': float(rmse), 'mape': float(mape), 'r2': float(r2)}, ensemble_pred

def visualize(y_test, ensemble_pred, save_path):
    """Create visualization."""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Time series (first 168 hours = 7 days)
    plot_len = min(168, len(y_test))
    axes[0,0].plot(y_test[:plot_len], label='Actual', linewidth=2)
    axes[0,0].plot(ensemble_pred[:plot_len], label='Predicted', linewidth=2, alpha=0.7)
    axes[0,0].set_title('Predictions vs Actual (First 7 Days)', fontweight='bold')
    axes[0,0].legend()
    axes[0,0].grid(alpha=0.3)
    
    # Scatter
    axes[0,1].scatter(y_test, ensemble_pred, alpha=0.5, s=10)
    axes[0,1].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    axes[0,1].set_xlabel('Actual')
    axes[0,1].set_ylabel('Predicted')
    axes[0,1].set_title('Predicted vs Actual', fontweight='bold')
    axes[0,1].grid(alpha=0.3)
    
    # Error distribution
    errors = ensemble_pred - y_test
    axes[1,0].hist(errors, bins=50, edgecolor='black', alpha=0.7)
    axes[1,0].axvline(errors.mean(), color='r', linestyle='--', lw=2, label=f'Mean: {errors.mean():.2f}')
    axes[1,0].set_xlabel('Error (beds)')
    axes[1,0].set_title('Error Distribution', fontweight='bold')
    axes[1,0].legend()
    axes[1,0].grid(alpha=0.3)
    
    # Error over time
    axes[1,1].plot(errors[:plot_len], alpha=0.7)
    axes[1,1].axhline(0, color='r', linestyle='--', lw=2)
    axes[1,1].set_xlabel('Hours')
    axes[1,1].set_ylabel('Error (beds)')
    axes[1,1].set_title('Error Over Time', fontweight='bold')
    axes[1,1].grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved visualization to {save_path}")

def main():
    logger.info("="*70)
    logger.info("ARIA RESOURCE PREDICTOR TRAINING")
    logger.info("="*70)
    start_time = time.time()
    
    # Generate data
    df = generate_data(n_hours=26280)
    df, feature_cols = create_features(df)
    
    # Split: 80/10/10
    n_total = len(df)
    n_train = int(0.8 * n_total)
    n_val = int(0.1 * n_total)
    
    df_train = df.iloc[:n_train]
    df_val = df.iloc[n_train:n_train+n_val]
    df_test = df.iloc[n_train+n_val:]
    
    logger.info(f"\nData splits: Train={len(df_train)}, Val={len(df_val)}, Test={len(df_test)}")
    
    # Prepare features
    X_train = df_train[feature_cols].values
    y_train = df_train['occupancy'].values
    X_val = df_val[feature_cols].values
    y_val = df_val['occupancy'].values
    X_test = df_test[feature_cols].values
    y_test = df_test['occupancy'].values
    
    # Train
    gb, rf, val_results = train_ensemble(X_train, y_train, X_val, y_val)
    
    # Evaluate
    test_results, ensemble_pred = evaluate(gb, rf, X_test, y_test)
    
    # Visualize
    visualize(y_test, ensemble_pred, REPORTS_DIR / 'resource_predictor_report.png')
    
    # Save models
    joblib.dump(gb, MODELS_DIR / 'resource_predictor_gb.pkl')
    joblib.dump(rf, MODELS_DIR / 'resource_predictor_rf.pkl')
    
    with open(MODELS_DIR / 'resource_predictor_metadata.json', 'w') as f:
        json.dump({
            'model_type': 'Resource Predictor (GradientBoosting + RandomForest)',
            'training_date': datetime.now().isoformat(),
            'val_results': val_results,
            'test_results': test_results,
            'n_features': len(feature_cols),
            'feature_names': feature_cols
        }, f, indent=2)
    
    duration = time.time() - start_time
    logger.info(f"\n{'='*70}")
    logger.info(f"TRAINING COMPLETE in {duration:.1f}s ({duration/60:.1f} min)")
    logger.info(f"MAE: {test_results['mae']:.2f} beds {'✅' if test_results['mae'] < 5 else '⚠️'}")
    logger.info(f"RMSE: {test_results['rmse']:.2f} beds {'✅' if test_results['rmse'] < 8 else '⚠️'}")
    logger.info(f"{'='*70}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
