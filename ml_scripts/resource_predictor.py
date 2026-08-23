#!/usr/bin/env python3
"""
ARIA Resource Predictor - LSTM + Prophet Ensemble
==================================================
Predict ambulance/hospital resource demand over time.

Author: ARIA ML Team
Date: August 2026
Version: 1.0

Model Details:
- Algorithm: LSTM + Prophet Ensemble
- Purpose: Time-series resource demand forecasting
- Target: RMSE < 0.05 (normalized)

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
    import torch
    import torch.nn as nn
    from torch.utils.data import Dataset, DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("⚠️  PyTorch not available. Install with: pip install torch")

# Prophet
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("⚠️  Prophet not available. Install with: pip install prophet")

# ML Libraries
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

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
LSTM_PARAMS = {
    'input_size': 10,
    'hidden_size': 64,
    'num_layers': 2,
    'dropout': 0.2,
    'sequence_length': 24,  # 24 hours lookback
    'batch_size': 32,
    'epochs': 50,
    'learning_rate': 0.001
}

ENSEMBLE_WEIGHTS = {
    'lstm': 0.6,
    'prophet': 0.4
}

# ============================================================================
# DATA GENERATION
# ============================================================================

class ResourceDemandDataGenerator:
    """Generate synthetic resource demand time series."""
    
    def __init__(self, n_days: int = 365):
        self.n_days = n_days
        self.random_state = 42
        np.random.seed(self.random_state)
        
    def generate_data(self) -> pd.DataFrame:
        """Generate synthetic hourly resource demand data."""
        logger.info(f"Generating {self.n_days} days of hourly demand data...")
        
        # Generate hourly timestamps
        start_date = datetime(2025, 1, 1)
        timestamps = [start_date + timedelta(hours=i) for i in range(self.n_days * 24)]
        
        # Base demand with trend
        trend = np.linspace(50, 80, len(timestamps))
        
        # Weekly seasonality
        hours_in_week = 24 * 7
        weekly_pattern = 10 * np.sin(2 * np.pi * np.arange(len(timestamps)) / hours_in_week)
        
        # Daily seasonality (more incidents at night, rush hours)
        daily_pattern = 15 * np.sin(2 * np.pi * np.arange(len(timestamps)) / 24 - np.pi/2)
        
        # Weekend effect
        day_of_week = np.array([ts.weekday() for ts in timestamps])
        weekend_effect = np.where(day_of_week >= 5, 5, 0)
        
        # Special events / holidays (random spikes)
        special_events = np.zeros(len(timestamps))
        n_events = 20
        event_indices = np.random.choice(len(timestamps), n_events, replace=False)
        special_events[event_indices] = np.random.uniform(20, 40, n_events)
        
        # Weather effect (random variations)
        weather_effect = np.random.normal(0, 5, len(timestamps))
        
        # Combine all effects
        ambulance_demand = (
            trend +
            weekly_pattern +
            daily_pattern +
            weekend_effect +
            special_events +
            weather_effect +
            np.random.normal(0, 3, len(timestamps))
        )
        ambulance_demand = np.clip(ambulance_demand, 10, 150).astype(int)
        
        # Hospital bed demand (correlated but different)
        hospital_demand = (
            ambulance_demand * 0.7 +
            np.random.normal(0, 5, len(timestamps))
        )
        hospital_demand = np.clip(hospital_demand, 5, 100).astype(int)
        
        # ICU demand (subset of hospital demand)
        icu_demand = (hospital_demand * 0.2 + np.random.normal(0, 2, len(timestamps)))
        icu_demand = np.clip(icu_demand, 0, 30).astype(int)
        
        # Create DataFrame
        df = pd.DataFrame({
            'timestamp': timestamps,
            'ambulance_demand': ambulance_demand,
            'hospital_demand': hospital_demand,
            'icu_demand': icu_demand,
            'hour': [ts.hour for ts in timestamps],
            'day_of_week': day_of_week,
            'day_of_month': [ts.day for ts in timestamps],
            'month': [ts.month for ts in timestamps],
            'is_weekend': (day_of_week >= 5).astype(int),
            'is_holiday': 0  # Placeholder
        })
        
        # Mark some random days as holidays
        holiday_dates = np.random.choice(self.n_days, size=10, replace=False)
        for holiday_day in holiday_dates:
            start_idx = holiday_day * 24
            end_idx = start_idx + 24
            if end_idx <= len(df):
                df.loc[start_idx:end_idx-1, 'is_holiday'] = 1
        
        logger.info(f"Generated {len(df):,} hourly records")
        logger.info(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        logger.info(f"Ambulance demand: {df['ambulance_demand'].min()} - {df['ambulance_demand'].max()}")
        
        return df


# ============================================================================
# LSTM MODEL
# ============================================================================

if TORCH_AVAILABLE:
    class TimeSeriesDataset(Dataset):
        """Time series dataset for LSTM."""
        
        def __init__(self, sequences, targets):
            self.sequences = torch.FloatTensor(sequences)
            self.targets = torch.FloatTensor(targets)
            
        def __len__(self):
            return len(self.sequences)
        
        def __getitem__(self, idx):
            return self.sequences[idx], self.targets[idx]
    
    
    class LSTMModel(nn.Module):
        """LSTM for time series prediction."""
        
        def __init__(self, input_size, hidden_size, num_layers, dropout):
            super(LSTMModel, self).__init__()
            
            self.hidden_size = hidden_size
            self.num_layers = num_layers
            
            self.lstm = nn.LSTM(
                input_size, hidden_size, num_layers,
                batch_first=True, dropout=dropout
            )
            
            self.fc = nn.Linear(hidden_size, 1)
            
        def forward(self, x):
            # x shape: (batch, seq, features)
            lstm_out, _ = self.lstm(x)
            # Take last timestep
            last_output = lstm_out[:, -1, :]
            output = self.fc(last_output)
            return output


class LSTMPredictor:
    """LSTM-based resource predictor."""
    
    def __init__(self, params: Dict = None):
        self.params = params or LSTM_PARAMS
        self.model = None
        self.scaler = MinMaxScaler()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        if not TORCH_AVAILABLE:
            logger.warning("PyTorch not available. LSTM will not be trained.")
    
    def create_sequences(self, data: np.ndarray, seq_length: int):
        """Create sequences for LSTM."""
        sequences = []
        targets = []
        
        for i in range(len(data) - seq_length):
            seq = data[i:i + seq_length]
            target = data[i + seq_length, 0]  # Predict first column (demand)
            sequences.append(seq)
            targets.append(target)
        
        return np.array(sequences), np.array(targets)
    
    def prepare_data(self, df: pd.DataFrame, target_col: str):
        """Prepare data for LSTM."""
        # Select features
        feature_cols = [
            target_col, 'hour', 'day_of_week', 'day_of_month', 'month',
            'is_weekend', 'is_holiday'
        ]
        
        # Add lagged features
        for lag in [1, 24, 168]:  # 1h, 1day, 1week
            df[f'{target_col}_lag{lag}'] = df[target_col].shift(lag)
            feature_cols.append(f'{target_col}_lag{lag}')
        
        df = df.dropna()
        
        # Scale features
        data_scaled = self.scaler.fit_transform(df[feature_cols].values)
        
        return data_scaled
    
    def train(self, df_train: pd.DataFrame, df_val: pd.DataFrame,
              target_col: str = 'ambulance_demand') -> Dict[str, float]:
        """Train LSTM model."""
        if not TORCH_AVAILABLE:
            logger.warning("Skipping LSTM training (PyTorch not available)")
            return {}
        
        logger.info("Training LSTM model...")
        logger.info(f"Using device: {self.device}")
        
        # Prepare data
        train_scaled = self.prepare_data(df_train, target_col)
        val_scaled = self.prepare_data(df_val, target_col)
        
        # Create sequences
        seq_length = self.params['sequence_length']
        X_train, y_train = self.create_sequences(train_scaled, seq_length)
        X_val, y_val = self.create_sequences(val_scaled, seq_length)
        
        logger.info(f"Train sequences: {X_train.shape}")
        logger.info(f"Val sequences: {X_val.shape}")
        
        # Create datasets and loaders
        train_dataset = TimeSeriesDataset(X_train, y_train)
        val_dataset = TimeSeriesDataset(X_val, y_val)
        
        train_loader = DataLoader(
            train_dataset,
            batch_size=self.params['batch_size'],
            shuffle=True
        )
        val_loader = DataLoader(
            val_dataset,
            batch_size=self.params['batch_size']
        )
        
        # Initialize model
        input_size = X_train.shape[2]
        self.model = LSTMModel(
            input_size,
            self.params['hidden_size'],
            self.params['num_layers'],
            self.params['dropout']
        ).to(self.device)
        
        # Loss and optimizer
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=self.params['learning_rate']
        )
        
        # Training loop
        best_val_loss = float('inf')
        
        for epoch in range(self.params['epochs']):
            self.model.train()
            train_loss = 0
            
            for sequences, targets in train_loader:
                sequences = sequences.to(self.device)
                targets = targets.to(self.device)
                
                optimizer.zero_grad()
                outputs = self.model(sequences).squeeze()
                loss = criterion(outputs, targets)
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
            
            avg_train_loss = train_loss / len(train_loader)
            
            # Validation
            self.model.eval()
            val_loss = 0
            
            with torch.no_grad():
                for sequences, targets in val_loader:
                    sequences = sequences.to(self.device)
                    targets = targets.to(self.device)
                    outputs = self.model(sequences).squeeze()
                    loss = criterion(outputs, targets)
                    val_loss += loss.item()
            
            avg_val_loss = val_loss / len(val_loader)
            
            if (epoch + 1) % 10 == 0:
                logger.info(f"Epoch [{epoch+1}/{self.params['epochs']}] "
                          f"Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}")
            
            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss
        
        metrics = {
            'best_val_loss': best_val_loss,
            'final_train_loss': avg_train_loss
        }
        
        logger.info(f"LSTM Best Validation Loss: {best_val_loss:.4f}")
        
        return metrics
    
    def predict(self, df: pd.DataFrame, target_col: str = 'ambulance_demand') -> np.ndarray:
        """Predict using LSTM."""
        if not TORCH_AVAILABLE or self.model is None:
            logger.warning("LSTM model not available, returning zeros")
            return np.zeros(len(df))
        
        self.model.eval()
        
        data_scaled = self.scaler.transform(df.values)
        seq_length = self.params['sequence_length']
        
        predictions = []
        
        with torch.no_grad():
            for i in range(len(data_scaled) - seq_length):
                seq = data_scaled[i:i + seq_length]
                seq_tensor = torch.FloatTensor(seq).unsqueeze(0).to(self.device)
                pred = self.model(seq_tensor).item()
                predictions.append(pred)
        
        # Pad beginning
        predictions = [predictions[0]] * seq_length + predictions
        
        return np.array(predictions)


# ============================================================================
# PROPHET MODEL
# ============================================================================

class ProphetPredictor:
    """Prophet-based resource predictor."""
    
    def __init__(self):
        self.model = None
        
        if not PROPHET_AVAILABLE:
            logger.warning("Prophet not available. Install with: pip install prophet")
    
    def train(self, df: pd.DataFrame, target_col: str = 'ambulance_demand') -> Dict[str, float]:
        """Train Prophet model."""
        if not PROPHET_AVAILABLE:
            logger.warning("Skipping Prophet training (not available)")
            return {}
        
        logger.info("Training Prophet model...")
        
        # Prepare data for Prophet
        df_prophet = df[['timestamp', target_col]].rename(
            columns={'timestamp': 'ds', target_col: 'y'}
        )
        
        # Initialize and train
        self.model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=True,
            seasonality_mode='additive'
        )
        
        # Add custom seasonalities
        self.model.add_seasonality(name='hourly', period=1, fourier_order=8)
        
        self.model.fit(df_prophet)
        
        logger.info("Prophet training complete")
        
        return {'status': 'trained'}
    
    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Predict using Prophet."""
        if not PROPHET_AVAILABLE or self.model is None:
            logger.warning("Prophet model not available, returning zeros")
            return np.zeros(len(df))
        
        # Prepare future dataframe
        future = pd.DataFrame({'ds': df['timestamp']})
        forecast = self.model.predict(future)
        
        return forecast['yhat'].values


# ============================================================================
# ENSEMBLE MODEL
# ============================================================================

class ResourcePredictorEnsemble:
    """Ensemble of LSTM and Prophet."""
    
    def __init__(self, weights: Dict = None):
        self.weights = weights or ENSEMBLE_WEIGHTS
        self.lstm_model = LSTMPredictor()
        self.prophet_model = ProphetPredictor()
        self.target_col = 'ambulance_demand'
        
    def train(self, df_train: pd.DataFrame, df_val: pd.DataFrame,
              target_col: str = 'ambulance_demand') -> Dict[str, Any]:
        """Train ensemble model."""
        self.target_col = target_col
        
        logger.info("=" * 70)
        logger.info("TRAINING ENSEMBLE MODEL")
        logger.info("=" * 70)
        
        results = {}
        
        # Train LSTM
        if TORCH_AVAILABLE:
            lstm_metrics = self.lstm_model.train(df_train, df_val, target_col)
            results['lstm'] = lstm_metrics
        
        # Train Prophet
        if PROPHET_AVAILABLE:
            prophet_metrics = self.prophet_model.train(df_train, target_col)
            results['prophet'] = prophet_metrics
        
        return results
    
    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Ensemble prediction."""
        predictions = np.zeros(len(df))
        total_weight = 0
        
        # LSTM predictions
        if TORCH_AVAILABLE and self.lstm_model.model is not None:
            lstm_pred = self.lstm_model.predict(df, self.target_col)
            predictions += self.weights['lstm'] * lstm_pred
            total_weight += self.weights['lstm']
        
        # Prophet predictions
        if PROPHET_AVAILABLE and self.prophet_model.model is not None:
            prophet_pred = self.prophet_model.predict(df)
            predictions += self.weights['prophet'] * prophet_pred
            total_weight += self.weights['prophet']
        
        if total_weight > 0:
            predictions /= total_weight
        
        return predictions


# ============================================================================
# EVALUATION
# ============================================================================

def evaluate_model(model: ResourcePredictorEnsemble, df_test: pd.DataFrame,
                   target_col: str = 'ambulance_demand') -> Dict[str, Any]:
    """Comprehensive model evaluation."""
    logger.info("=" * 70)
    logger.info("MODEL EVALUATION")
    logger.info("=" * 70)
    
    # Predictions
    y_pred = model.predict(df_test)
    y_true = df_test[target_col].values
    
    # Handle length mismatch
    min_len = min(len(y_pred), len(y_true))
    y_pred = y_pred[:min_len]
    y_true = y_true[:min_len]
    
    # Metrics
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1))) * 100
    r2 = r2_score(y_true, y_pred)
    
    # Normalized RMSE
    nrmse = rmse / (y_true.max() - y_true.min())
    
    logger.info(f"\nTest Set Metrics:")
    logger.info(f"  MAE:   {mae:.4f}")
    logger.info(f"  RMSE:  {rmse:.4f}")
    logger.info(f"  NRMSE: {nrmse:.4f}")
    logger.info(f"  MAPE:  {mape:.2f}%")
    logger.info(f"  R²:    {r2:.4f}")
    
    results = {
        'mae': mae,
        'rmse': rmse,
        'nrmse': nrmse,
        'mape': mape,
        'r2_score': r2
    }
    
    return results


def create_visualizations(model: ResourcePredictorEnsemble, df_test: pd.DataFrame,
                         target_col: str, save_dir: Path):
    """Create evaluation visualizations."""
    logger.info("Creating visualizations...")
    
    y_pred = model.predict(df_test)
    y_true = df_test[target_col].values
    
    # Handle length mismatch
    min_len = min(len(y_pred), len(y_true))
    y_pred = y_pred[:min_len]
    y_true = y_true[:min_len]
    timestamps = df_test['timestamp'].values[:min_len]
    
    fig = plt.figure(figsize=(16, 10))
    
    # 1. Time series prediction (first 7 days)
    ax1 = plt.subplot(2, 2, 1)
    plot_len = min(24 * 7, len(y_pred))  # 7 days
    ax1.plot(range(plot_len), y_true[:plot_len], label='Actual', linewidth=2)
    ax1.plot(range(plot_len), y_pred[:plot_len], label='Predicted', linewidth=2, alpha=0.7)
    ax1.set_xlabel('Hour', fontsize=12)
    ax1.set_ylabel('Demand', fontsize=12)
    ax1.set_title('Predictions vs Actual (First 7 Days)', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(alpha=0.3)
    
    # 2. Scatter plot
    ax2 = plt.subplot(2, 2, 2)
    ax2.scatter(y_true, y_pred, alpha=0.5, s=10)
    ax2.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()],
             'r--', lw=2, label='Perfect Prediction')
    ax2.set_xlabel('Actual Demand', fontsize=12)
    ax2.set_ylabel('Predicted Demand', fontsize=12)
    ax2.set_title('Predicted vs Actual', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(alpha=0.3)
    
    # 3. Error distribution
    ax3 = plt.subplot(2, 2, 3)
    errors = y_pred - y_true
    ax3.hist(errors, bins=50, edgecolor='black', alpha=0.7)
    ax3.axvline(errors.mean(), color='r', linestyle='--', linewidth=2,
                label=f'Mean: {errors.mean():.2f}')
    ax3.set_xlabel('Prediction Error', fontsize=12)
    ax3.set_ylabel('Frequency', fontsize=12)
    ax3.set_title('Error Distribution', fontsize=14, fontweight='bold')
    ax3.legend()
    ax3.grid(alpha=0.3)
    
    # 4. Error over time (first 30 days)
    ax4 = plt.subplot(2, 2, 4)
    plot_len = min(24 * 30, len(errors))
    ax4.plot(range(plot_len), errors[:plot_len], alpha=0.7)
    ax4.axhline(0, color='r', linestyle='--', linewidth=2)
    ax4.set_xlabel('Hour', fontsize=12)
    ax4.set_ylabel('Prediction Error', fontsize=12)
    ax4.set_title('Error Over Time (First 30 Days)', fontsize=14, fontweight='bold')
    ax4.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_dir / 'resource_predictor_evaluation.png', dpi=300)
    plt.close()
    
    logger.info(f"Saved visualizations to {save_dir}/resource_predictor_evaluation.png")


# ============================================================================
# MODEL PERSISTENCE
# ============================================================================

def save_model(model: ResourcePredictorEnsemble, metadata: Dict, save_dir: Path):
    """Save model artifacts."""
    logger.info("Saving model artifacts...")
    
    # Save LSTM model
    if TORCH_AVAILABLE and model.lstm_model.model is not None:
        torch.save(model.lstm_model.model.state_dict(),
                  save_dir / 'resource_lstm.pth')
        joblib.dump(model.lstm_model.scaler,
                   save_dir / 'resource_lstm_scaler.pkl')
    
    # Save Prophet model
    if PROPHET_AVAILABLE and model.prophet_model.model is not None:
        with open(save_dir / 'resource_prophet.json', 'w') as f:
            json.dump(model.prophet_model.model.to_json(), f)
    
    # Save metadata
    with open(save_dir / 'resource_predictor_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    
    logger.info(f"Model artifacts saved to {save_dir}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    logger.info("=" * 70)
    logger.info("ARIA RESOURCE PREDICTOR TRAINING")
    logger.info("=" * 70)
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    try:
        # Generate data
        generator = ResourceDemandDataGenerator(n_days=365)
        df = generator.generate_data()
        
        # Split data (80/10/10)
        n_total = len(df)
        n_train = int(0.8 * n_total)
        n_val = int(0.1 * n_total)
        
        df_train = df.iloc[:n_train]
        df_val = df.iloc[n_train:n_train + n_val]
        df_test = df.iloc[n_train + n_val:]
        
        logger.info(f"\nData splits:")
        logger.info(f"  Train: {len(df_train):,} hours")
        logger.info(f"  Val:   {len(df_val):,} hours")
        logger.info(f"  Test:  {len(df_test):,} hours")
        
        # Train model
        model = ResourcePredictorEnsemble()
        training_results = model.train(
            df_train, df_val,
            target_col='ambulance_demand'
        )
        
        # Evaluate
        evaluation_results = evaluate_model(model, df_test, 'ambulance_demand')
        
        # Visualizations
        create_visualizations(model, df_test, 'ambulance_demand', REPORTS_DIR)
        
        # Save model
        metadata = {
            'model_type': 'Resource Predictor (LSTM + Prophet Ensemble)',
            'training_date': datetime.now().isoformat(),
            'train_hours': len(df_train),
            'val_hours': len(df_val),
            'test_hours': len(df_test),
            'training_results': training_results,
            'test_results': evaluation_results,
            'ensemble_weights': model.weights,
            'lstm_params': LSTM_PARAMS if TORCH_AVAILABLE else None,
            'target_column': 'ambulance_demand'
        }
        
        save_model(model, metadata, MODELS_DIR)
        
        # Final summary
        duration = time.time() - start_time
        
        logger.info("=" * 70)
        logger.info("TRAINING COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Final Test NRMSE: {evaluation_results['nrmse']:.4f}")
        logger.info(f"Final Test R²: {evaluation_results['r2_score']:.4f}")
        
        if evaluation_results['nrmse'] < 0.05:
            logger.info("✅ Target NRMSE (<0.05) ACHIEVED!")
        else:
            logger.warning(f"⚠️  Target not met. Got {evaluation_results['nrmse']:.4f}, need <0.05")
        
        logger.info(f"\nModel saved to: {MODELS_DIR}")
        logger.info("=" * 70)
        
        return 0
        
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
