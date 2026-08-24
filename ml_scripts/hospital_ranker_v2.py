#!/usr/bin/env python3
"""
ARIA Hospital Ranker - Production LambdaMART Implementation
============================================================
Ranks hospitals by suitability for emergency cases using pairwise learning-to-rank.

Author: ARIA ML Team (Senior ML Engineer)
Date: August 2026
Version: 2.0 - Production Ready

Algorithm: LightGBM LambdaMART with Optuna hyperparameter optimization
Target: NDCG@10 > 0.8

Usage:
    python hospital_ranker_v2.py
"""

import os
import sys
import json
import logging
import warnings
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional

import numpy as np
import pandas as pd
from tqdm import tqdm

# ML Libraries
import lightgbm as lgb
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import ndcg_score

# Optimization
try:
    import optuna
    from optuna.samplers import TPESampler
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False
    print("⚠️  Optuna not available. Install with: pip install optuna")

# Geospatial calculations
from math import radians, sin, cos, sqrt, atan2

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
DATA_DIR = BASE_DIR / "data" / "raw"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

# Create directories
for directory in [MODELS_DIR, REPORTS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Logging setup
LOG_FILE = LOGS_DIR / "hospital_ranker_v2_training.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# LambdaMART hyperparameters (will be optimized)
DEFAULT_PARAMS = {
    'objective': 'lambdarank',
    'metric': 'ndcg',
    'ndcg_eval_at': [3, 5, 10],
    'num_leaves': 31,
    'learning_rate': 0.05,
    'feature_fraction': 0.8,
    'bagging_fraction': 0.8,
    'bagging_freq': 5,
    'min_child_samples': 20,
    'verbose': -1,
    'force_row_wise': True,
    'num_boost_round': 500
}

# Feature engineering constants
MAX_HOSPITALS_PER_QUERY = 20  # Top K nearest hospitals to consider
EARTH_RADIUS_KM = 6371.0

# ============================================================================
# GEOSPATIAL UTILITIES
# ============================================================================

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate haversine distance between two points in kilometers.
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
    
    Returns:
        Distance in kilometers
    """
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return EARTH_RADIUS_KM * c


# ============================================================================
# DATA LOADING
# ============================================================================

class DataLoader:
    """Load and prepare hospital and incident data."""
    
    def __init__(self, hospitals_path: Path, incidents_path: Path):
        self.hospitals_path = hospitals_path
        self.incidents_path = incidents_path
        
    def load_hospitals(self) -> pd.DataFrame:
        """Load hospital data."""
        logger.info(f"Loading hospitals from {self.hospitals_path}")
        
        df = pd.read_csv(self.hospitals_path, low_memory=False)
        logger.info(f"Loaded {len(df):,} hospitals")
        
        # Clean and validate
        df = self._clean_hospitals(df)
        
        logger.info(f"After cleaning: {len(df):,} hospitals")
        return df
    
    def _clean_hospitals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean hospital data."""
        # Remove rows with missing critical fields
        df = df.dropna(subset=['latitude', 'longitude'])
        
        # Convert numeric columns
        numeric_cols = ['latitude', 'longitude', 'beds', 'icu_beds', 'ventilators']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Filter valid coordinates
        df = df[
            (df['latitude'].between(-90, 90)) &
            (df['longitude'].between(-90, 90))
        ]
        
        # Fill missing values
        df['beds'] = df['beds'].fillna(0)
        df['icu_beds'] = df['icu_beds'].fillna(0)
        df['ventilators'] = df['ventilators'].fillna(0)
        df['emergency_services'] = df['emergency_services'].fillna('Unknown')
        df['ambulance_available'] = df['ambulance_available'].fillna('Unknown')
        
        # Create derived features
        df['has_emergency'] = df['emergency_services'].astype(str).str.lower().isin(['yes', 'true', '1']).astype(int)
        df['has_ambulance'] = df['ambulance_available'].astype(str).str.lower().isin(['yes', 'true', '1']).astype(int)
        df['has_icu'] = (df['icu_beds'] > 0).astype(int)
        df['has_ventilator'] = (df['ventilators'] > 0).astype(int)
        
        return df
    
    def load_incidents(self) -> pd.DataFrame:
        """Load incident data."""
        logger.info(f"Loading incidents from {self.incidents_path}")
        
        df = pd.read_csv(self.incidents_path, low_memory=False)
        logger.info(f"Loaded {len(df):,} incidents")
        
        # Clean and validate
        df = self._clean_incidents(df)
        
        logger.info(f"After cleaning: {len(df):,} incidents")
        return df
    
    def _clean_incidents(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean incident data."""
        # Remove rows with missing critical fields
        df = df.dropna(subset=['latitude', 'longitude', 'severity'])
        
        # Convert numeric columns
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        
        # Filter valid coordinates
        df = df[
            (df['latitude'].between(-90, 90)) &
            (df['longitude'].between(-90, 90))
        ]
        
        # Parse timestamp
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        return df


# ============================================================================
# PAIRWISE DATA GENERATION
# ============================================================================

class PairwiseDataGenerator:
    """Generate pairwise ranking data for learning-to-rank."""
    
    def __init__(self, hospitals: pd.DataFrame, incidents: pd.DataFrame):
        self.hospitals = hospitals
        self.incidents = incidents
        
    def generate(self, n_samples: int = 10000) -> pd.DataFrame:
        """
        Generate pairwise ranking data.
        
        For each incident (query), find top K nearest hospitals and create
        query-document pairs with relevance labels.
        
        Args:
            n_samples: Number of incidents to sample
        
        Returns:
            DataFrame with query-document pairs
        """
        logger.info(f"Generating pairwise data for {n_samples} incidents...")
        
        # Sample incidents
        incidents_sample = self.incidents.sample(
            min(n_samples, len(self.incidents)), 
            random_state=42
        )
        
        pairs = []
        
        for idx, incident in tqdm(incidents_sample.iterrows(), 
                                   total=len(incidents_sample), 
                                   desc="Creating pairs"):
            
            # Calculate distances to all hospitals
            distances = self.hospitals.apply(
                lambda h: haversine_distance(
                    incident['latitude'], incident['longitude'],
                    h['latitude'], h['longitude']
                ),
                axis=1
            )
            
            # Get top K nearest hospitals
            nearest_indices = distances.nsmallest(MAX_HOSPITALS_PER_QUERY).index
            
            # Create pairs for this incident
            for hospital_idx in nearest_indices:
                hospital = self.hospitals.loc[hospital_idx]
                distance = distances[hospital_idx]
                
                # Calculate relevance label (0-4 scale)
                relevance = self._calculate_relevance(
                    incident, hospital, distance
                )
                
                pair = {
                    'query_id': idx,
                    'incident_id': incident.get('incident_id', f'INC_{idx}'),
                    'hospital_id': hospital.get('hospital_id', f'HOSP_{hospital_idx}'),
                    'incident_lat': incident['latitude'],
                    'incident_lon': incident['longitude'],
                    'incident_severity': incident['severity'],
                    'hospital_lat': hospital['latitude'],
                    'hospital_lon': hospital['longitude'],
                    'distance_km': distance,
                    'hospital_beds': hospital['beds'],
                    'hospital_icu_beds': hospital['icu_beds'],
                    'hospital_ventilators': hospital['ventilators'],
                    'has_emergency': hospital['has_emergency'],
                    'has_ambulance': hospital['has_ambulance'],
                    'has_icu': hospital['has_icu'],
                    'has_ventilator': hospital['has_ventilator'],
                    'hour': incident.get('hour', 12),
                    'is_weekend': incident.get('is_weekend', 0),
                    'relevance': relevance
                }
                
                pairs.append(pair)
        
        df = pd.DataFrame(pairs)
        
        logger.info(f"Generated {len(df):,} query-hospital pairs")
        logger.info(f"Unique queries: {df['query_id'].nunique():,}")
        logger.info(f"Avg hospitals per query: {len(df) / df['query_id'].nunique():.1f}")
        logger.info(f"Relevance distribution:\n{df['relevance'].value_counts().sort_index()}")
        
        return df
    
    def _calculate_relevance(self, incident: pd.Series, hospital: pd.Series, 
                           distance: float) -> int:
        """
        Calculate relevance score (0-4) for hospital given incident.
        
        Scoring criteria:
        - Distance: Closer is better
        - Bed availability: More beds = higher score
        - ICU availability: Critical for severe cases
        - Emergency services: Required for emergencies
        - Specialty match: Bonus for matching services
        
        Returns:
            Relevance score 0-4 (4 = perfect match)
        """
        score = 0.0
        
        # 1. Distance factor (max 2 points)
        if distance < 2:
            score += 2.0
        elif distance < 5:
            score += 1.5
        elif distance < 10:
            score += 1.0
        elif distance < 20:
            score += 0.5
        
        # 2. Bed availability (max 1 point)
        beds = hospital['beds']
        if beds > 100:
            score += 1.0
        elif beds > 50:
            score += 0.7
        elif beds > 20:
            score += 0.4
        
        # 3. Critical care for severe cases (max 1 point)
        severity = incident['severity']
        if severity == 'CRITICAL':
            if hospital['has_icu'] and hospital['has_ventilator']:
                score += 1.0
            elif hospital['has_icu']:
                score += 0.5
            else:
                score -= 0.5  # Penalty for no ICU on critical case
        
        # 4. Emergency services (max 0.5 points)
        if hospital['has_emergency']:
            score += 0.5
        
        # 5. Ambulance availability (max 0.3 points)
        if hospital['has_ambulance']:
            score += 0.3
        
        # Normalize to 0-4 scale
        relevance = int(np.clip(np.round(score), 0, 4))
        
        return relevance


# ============================================================================
# FEATURE ENGINEERING
# ============================================================================

class FeatureEngineer:
    """Engineer 50+ features for hospital ranking."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_names = []
        self.label_encoders = {}
        
    def create_features(self, df: pd.DataFrame, fit: bool = False) -> pd.DataFrame:
        """
        Create comprehensive feature set for ranking.
        
        Feature categories:
        1. Distance features (5)
        2. Hospital capacity (8)
        3. Hospital quality/services (6)
        4. Temporal features (6)
        5. Severity matching (4)
        6. Interaction features (8)
        7. Derived scores (5)
        
        Total: 42+ features
        """
        df = df.copy()
        
        # ===== 1. DISTANCE FEATURES (5) =====
        df['distance_km'] = df['distance_km'].fillna(999)
        df['log_distance'] = np.log1p(df['distance_km'])
        df['distance_squared'] = df['distance_km'] ** 2
        df['is_very_close'] = (df['distance_km'] < 2).astype(int)
        df['is_nearby'] = (df['distance_km'] < 5).astype(int)
        df['is_far'] = (df['distance_km'] > 20).astype(int)
        
        # ===== 2. HOSPITAL CAPACITY (8) =====
        df['hospital_beds'] = df['hospital_beds'].fillna(0)
        df['hospital_icu_beds'] = df['hospital_icu_beds'].fillna(0)
        df['hospital_ventilators'] = df['hospital_ventilators'].fillna(0)
        
        df['log_beds'] = np.log1p(df['hospital_beds'])
        df['log_icu_beds'] = np.log1p(df['hospital_icu_beds'])
        
        # Capacity ratios
        df['icu_to_total_ratio'] = df['hospital_icu_beds'] / (df['hospital_beds'] + 1)
        df['ventilator_to_icu_ratio'] = df['hospital_ventilators'] / (df['hospital_icu_beds'] + 1)
        
        # Capacity bins
        df['is_large_hospital'] = (df['hospital_beds'] > 100).astype(int)
        df['is_medium_hospital'] = ((df['hospital_beds'] >= 50) & (df['hospital_beds'] <= 100)).astype(int)
        
        # ===== 3. HOSPITAL SERVICES (6) =====
        df['has_emergency'] = df['has_emergency'].fillna(0).astype(int)
        df['has_ambulance'] = df['has_ambulance'].fillna(0).astype(int)
        df['has_icu'] = df['has_icu'].fillna(0).astype(int)
        df['has_ventilator'] = df['has_ventilator'].fillna(0).astype(int)
        
        # Service score
        df['service_score'] = (
            df['has_emergency'] * 2 +
            df['has_ambulance'] * 1 +
            df['has_icu'] * 2 +
            df['has_ventilator'] * 1
        )
        
        # Critical care capability
        df['critical_care_capable'] = (
            (df['has_icu'] == 1) & (df['has_ventilator'] == 1)
        ).astype(int)
        
        # ===== 4. TEMPORAL FEATURES (6) =====
        df['hour'] = df['hour'].fillna(12)
        df['is_weekend'] = df['is_weekend'].fillna(0)
        
        # Cyclical encoding
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        
        # Time of day bins
        df['is_night'] = ((df['hour'] >= 22) | (df['hour'] <= 6)).astype(int)
        df['is_rush_hour'] = ((df['hour'] >= 7) & (df['hour'] <= 9) | 
                              (df['hour'] >= 17) & (df['hour'] <= 19)).astype(int)
        
        # ===== 5. SEVERITY MATCHING (4) =====
        # Encode severity
        if fit:
            self.label_encoders['severity'] = LabelEncoder()
            df['severity_encoded'] = self.label_encoders['severity'].fit_transform(
                df['incident_severity'].fillna('MODERATE')
            )
        else:
            df['severity_encoded'] = self.label_encoders['severity'].transform(
                df['incident_severity'].fillna('MODERATE')
            )
        
        # Severity flags
        df['is_critical'] = (df['incident_severity'] == 'CRITICAL').astype(int)
        df['is_moderate'] = (df['incident_severity'] == 'MODERATE').astype(int)
        df['is_low'] = (df['incident_severity'] == 'LOW').astype(int)
        
        # ===== 6. INTERACTION FEATURES (8) =====
        # Distance × Severity
        df['distance_x_severity'] = df['distance_km'] * df['severity_encoded']
        
        # Distance × Capacity
        df['distance_x_beds'] = df['distance_km'] * df['log_beds']
        df['distance_x_icu'] = df['distance_km'] * df['log_icu_beds']
        
        # Critical case × ICU availability
        df['critical_needs_icu'] = df['is_critical'] * df['has_icu']
        df['critical_lacks_icu'] = df['is_critical'] * (1 - df['has_icu'])
        
        # Distance × Services
        df['distance_x_emergency'] = df['distance_km'] * df['has_emergency']
        df['distance_x_service_score'] = df['distance_km'] * df['service_score']
        
        # Weekend × Services
        df['weekend_x_emergency'] = df['is_weekend'] * df['has_emergency']
        
        # ===== 7. DERIVED SCORES (5) =====
        # Overall hospital score (normalized)
        df['hospital_quality_score'] = (
            df['log_beds'] * 0.3 +
            df['service_score'] * 0.4 +
            df['icu_to_total_ratio'] * 0.3
        )
        
        # Suitability score
        df['suitability_score'] = (
            (1 / (df['distance_km'] + 1)) * 10 +  # Closer is better
            df['service_score'] * 2 +
            df['critical_care_capable'] * 3
        )
        
        # Capacity density (beds per km)
        df['capacity_density'] = df['hospital_beds'] / (df['distance_km'] + 1)
        
        # Emergency readiness
        df['emergency_readiness'] = (
            df['has_emergency'] * 3 +
            df['has_ambulance'] * 2 +
            df['has_icu'] * 3 +
            df['has_ventilator'] * 2
        )
        
        # Match score (for critical cases)
        df['critical_match_score'] = (
            df['is_critical'] * (
                df['has_icu'] * 5 +
                df['has_ventilator'] * 3 +
                df['has_emergency'] * 2 -
                df['distance_km'] * 0.5
            )
        )
        
        # Select feature columns
        feature_cols = [
            # Distance (6)
            'distance_km', 'log_distance', 'distance_squared', 
            'is_very_close', 'is_nearby', 'is_far',
            
            # Capacity (9)
            'hospital_beds', 'hospital_icu_beds', 'hospital_ventilators',
            'log_beds', 'log_icu_beds', 'icu_to_total_ratio', 
            'ventilator_to_icu_ratio', 'is_large_hospital', 'is_medium_hospital',
            
            # Services (6)
            'has_emergency', 'has_ambulance', 'has_icu', 'has_ventilator',
            'service_score', 'critical_care_capable',
            
            # Temporal (6)
            'hour_sin', 'hour_cos', 'is_night', 'is_rush_hour', 'is_weekend',
            'severity_encoded',
            
            # Severity (3)
            'is_critical', 'is_moderate', 'is_low',
            
            # Interactions (8)
            'distance_x_severity', 'distance_x_beds', 'distance_x_icu',
            'critical_needs_icu', 'critical_lacks_icu', 'distance_x_emergency',
            'distance_x_service_score', 'weekend_x_emergency',
            
            # Derived scores (5)
            'hospital_quality_score', 'suitability_score', 'capacity_density',
            'emergency_readiness', 'critical_match_score'
        ]
        
        if fit:
            self.feature_names = feature_cols
        
        logger.info(f"Created {len(feature_cols)} features")
        
        return df[feature_cols]


# ============================================================================
# RANKING METRICS
# ============================================================================

def calculate_ndcg_at_k(y_true: np.ndarray, y_pred: np.ndarray, k: int) -> float:
    """Calculate NDCG@k metric."""
    if len(y_true) == 0:
        return 0.0
    
    # Reshape for sklearn
    y_true_reshaped = y_true.reshape(1, -1)
    y_pred_reshaped = y_pred.reshape(1, -1)
    
    return ndcg_score(y_true_reshaped, y_pred_reshaped, k=k)


# ============================================================================
# HOSPITAL RANKER MODEL
# ============================================================================

class HospitalRanker:
    """LambdaMART-based hospital ranker with hyperparameter optimization."""
    
    def __init__(self, params: Dict = None):
        self.params = params or DEFAULT_PARAMS.copy()
        self.model = None
        self.feature_engineer = FeatureEngineer()
        self.best_params = None
        
    def train(self, df_train: pd.DataFrame, df_val: pd.DataFrame,
              optimize: bool = True, n_trials: int = 20) -> Dict[str, Any]:
        """
        Train LambdaMART ranker with optional hyperparameter optimization.
        
        Args:
            df_train: Training data
            df_val: Validation data
            optimize: Whether to run hyperparameter optimization
            n_trials: Number of Optuna trials
        
        Returns:
            Training metrics
        """
        logger.info("=" * 70)
        logger.info("TRAINING HOSPITAL RANKER")
        logger.info("=" * 70)
        
        # Feature engineering
        X_train = self.feature_engineer.create_features(df_train, fit=True)
        y_train = df_train['relevance'].values
        query_train = df_train['query_id'].values
        
        X_val = self.feature_engineer.create_features(df_val, fit=False)
        y_val = df_val['relevance'].values
        query_val = df_val['query_id'].values
        
        logger.info(f"Feature matrix shape: {X_train.shape}")
        logger.info(f"Features: {len(self.feature_engineer.feature_names)}")
        logger.info(f"Train queries: {len(np.unique(query_train)):,}")
        logger.info(f"Val queries: {len(np.unique(query_val)):,}")
        
        # Hyperparameter optimization
        if optimize and OPTUNA_AVAILABLE:
            logger.info(f"\nRunning hyperparameter optimization ({n_trials} trials)...")
            self.best_params = self._optimize_hyperparameters(
                X_train, y_train, query_train,
                X_val, y_val, query_val,
                n_trials=n_trials
            )
            self.params.update(self.best_params)
            logger.info(f"Best parameters: {self.best_params}")
        
        # Train final model
        logger.info("\nTraining final model...")
        train_group = df_train.groupby('query_id').size().values
        val_group = df_val.groupby('query_id').size().values
        
        lgb_train = lgb.Dataset(
            X_train.values, y_train,
            group=train_group,
            free_raw_data=False
        )
        
        lgb_val = lgb.Dataset(
            X_val.values, y_val,
            group=val_group,
            reference=lgb_train,
            free_raw_data=False
        )
        
        # Train
        self.model = lgb.train(
            self.params,
            lgb_train,
            valid_sets=[lgb_val],
            num_boost_round=self.params.get('num_boost_round', 500),
            callbacks=[lgb.early_stopping(stopping_rounds=50, verbose=False)]
        )
        
        # Evaluate
        y_pred_val = self.model.predict(X_val.values)
        
        # Calculate NDCG per query
        ndcg_3_scores = []
        ndcg_5_scores = []
        ndcg_10_scores = []
        
        for query_id in np.unique(query_val):
            mask = query_val == query_id
            y_true_q = y_val[mask]
            y_pred_q = y_pred_val[mask]
            
            if len(y_true_q) > 0:
                ndcg_3 = calculate_ndcg_at_k(y_true_q, y_pred_q, k=min(3, len(y_true_q)))
                ndcg_5 = calculate_ndcg_at_k(y_true_q, y_pred_q, k=min(5, len(y_true_q)))
                ndcg_10 = calculate_ndcg_at_k(y_true_q, y_pred_q, k=min(10, len(y_true_q)))
                
                ndcg_3_scores.append(ndcg_3)
                ndcg_5_scores.append(ndcg_5)
                ndcg_10_scores.append(ndcg_10)
        
        metrics = {
            'ndcg@3': float(np.mean(ndcg_3_scores)),
            'ndcg@5': float(np.mean(ndcg_5_scores)),
            'ndcg@10': float(np.mean(ndcg_10_scores)),
            'ndcg@3_std': float(np.std(ndcg_3_scores)),
            'ndcg@5_std': float(np.std(ndcg_5_scores)),
            'ndcg@10_std': float(np.std(ndcg_10_scores))
        }
        
        logger.info(f"\nValidation Metrics:")
        logger.info(f"  NDCG@3:  {metrics['ndcg@3']:.4f} ± {metrics['ndcg@3_std']:.4f}")
        logger.info(f"  NDCG@5:  {metrics['ndcg@5']:.4f} ± {metrics['ndcg@5_std']:.4f}")
        logger.info(f"  NDCG@10: {metrics['ndcg@10']:.4f} ± {metrics['ndcg@10_std']:.4f}")
        
        return metrics
    
    def _optimize_hyperparameters(self, X_train, y_train, query_train,
                                   X_val, y_val, query_val,
                                   n_trials: int = 20) -> Dict:
        """Optimize hyperparameters using Optuna."""
        
        def objective(trial):
            params = {
                'objective': 'lambdarank',
                'metric': 'ndcg',
                'ndcg_eval_at': [3],
                'num_leaves': trial.suggest_int('num_leaves', 20, 50),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
                'feature_fraction': trial.suggest_float('feature_fraction', 0.6, 1.0),
                'bagging_fraction': trial.suggest_float('bagging_fraction', 0.6, 1.0),
                'bagging_freq': trial.suggest_int('bagging_freq', 1, 7),
                'min_child_samples': trial.suggest_int('min_child_samples', 10, 50),
                'verbose': -1,
                'force_row_wise': True
            }
            
            train_group = []
            current_query = query_train[0]
            count = 0
            for q in query_train:
                if q == current_query:
                    count += 1
                else:
                    train_group.append(count)
                    current_query = q
                    count = 1
            train_group.append(count)
            
            val_group = []
            current_query = query_val[0]
            count = 0
            for q in query_val:
                if q == current_query:
                    count += 1
                else:
                    val_group.append(count)
                    current_query = q
                    count = 1
            val_group.append(count)
            
            lgb_train = lgb.Dataset(X_train.values, y_train, group=train_group)
            lgb_val = lgb.Dataset(X_val.values, y_val, group=val_group, reference=lgb_train)
            
            model = lgb.train(
                params, lgb_train,
                num_boost_round=200,
                valid_sets=[lgb_val],
                callbacks=[lgb.early_stopping(stopping_rounds=30, verbose=False)]
            )
            
            y_pred = model.predict(X_val.values)
            
            # Calculate NDCG@3
            ndcg_scores = []
            for query_id in np.unique(query_val):
                mask = query_val == query_id
                y_true_q = y_val[mask]
                y_pred_q = y_pred[mask]
                
                if len(y_true_q) > 0:
                    ndcg = calculate_ndcg_at_k(y_true_q, y_pred_q, k=min(3, len(y_true_q)))
                    ndcg_scores.append(ndcg)
            
            return np.mean(ndcg_scores)
        
        study = optuna.create_study(
            direction='maximize',
            sampler=TPESampler(seed=42)
        )
        
        study.optimize(objective, n_trials=n_trials, show_progress_bar=True)
        
        logger.info(f"Best NDCG@3: {study.best_value:.4f}")
        
        return study.best_params
    
    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Predict ranking scores."""
        X = self.feature_engineer.create_features(df, fit=False)
        return self.model.predict(X.values)
    
    def rank_hospitals(self, df: pd.DataFrame, top_k: int = 10) -> pd.DataFrame:
        """Rank hospitals for each query."""
        scores = self.predict(df)
        df = df.copy()
        df['score'] = scores
        
        # Sort by query and score
        df_ranked = df.sort_values(['query_id', 'score'], ascending=[True, False])
        
        # Get top-k per query
        df_top = df_ranked.groupby('query_id').head(top_k).reset_index(drop=True)
        
        return df_top
    
    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance."""
        importance = self.model.feature_importance(importance_type='gain')
        
        return pd.DataFrame({
            'feature': self.feature_engineer.feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)


# ============================================================================
# EVALUATION
# ============================================================================

def evaluate_model(model: HospitalRanker, df_test: pd.DataFrame) -> Dict[str, Any]:
    """Comprehensive model evaluation."""
    logger.info("=" * 70)
    logger.info("MODEL EVALUATION")
    logger.info("=" * 70)
    
    # Predictions
    y_pred = model.predict(df_test)
    y_test = df_test['relevance'].values
    query_test = df_test['query_id'].values
    
    # Calculate metrics per query
    ndcg_3_scores = []
    ndcg_5_scores = []
    ndcg_10_scores = []
    
    for query_id in np.unique(query_test):
        mask = query_test == query_id
        y_true_q = y_test[mask]
        y_pred_q = y_pred[mask]
        
        if len(y_true_q) > 0:
            ndcg_3 = calculate_ndcg_at_k(y_true_q, y_pred_q, k=min(3, len(y_true_q)))
            ndcg_5 = calculate_ndcg_at_k(y_true_q, y_pred_q, k=min(5, len(y_true_q)))
            ndcg_10 = calculate_ndcg_at_k(y_true_q, y_pred_q, k=min(10, len(y_true_q)))
            
            ndcg_3_scores.append(ndcg_3)
            ndcg_5_scores.append(ndcg_5)
            ndcg_10_scores.append(ndcg_10)
    
    results = {
        'ndcg@3': float(np.mean(ndcg_3_scores)),
        'ndcg@5': float(np.mean(ndcg_5_scores)),
        'ndcg@10': float(np.mean(ndcg_10_scores)),
        'num_queries': len(np.unique(query_test))
    }
    
    logger.info(f"\nTest Set Metrics ({results['num_queries']} queries):")
    logger.info(f"  NDCG@3:  {results['ndcg@3']:.4f}")
    logger.info(f"  NDCG@5:  {results['ndcg@5']:.4f}")
    logger.info(f"  NDCG@10: {results['ndcg@10']:.4f}")
    
    return results


# ============================================================================
# VISUALIZATION
# ============================================================================

def create_visualizations(model: HospitalRanker, df_test: pd.DataFrame, save_dir: Path):
    """Create evaluation visualizations."""
    logger.info("Creating visualizations...")
    
    fig = plt.figure(figsize=(16, 10))
    
    # 1. Feature Importance
    ax1 = plt.subplot(2, 2, 1)
    feature_importance = model.get_feature_importance()
    top_features = feature_importance.head(20)
    ax1.barh(range(len(top_features)), top_features['importance'].values, color='steelblue')
    ax1.set_yticks(range(len(top_features)))
    ax1.set_yticklabels(top_features['feature'].values, fontsize=8)
    ax1.set_xlabel('Importance (Gain)', fontsize=12)
    ax1.set_title('Top 20 Feature Importance', fontsize=14, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    ax1.invert_yaxis()
    
    # 2. Score Distribution by Relevance
    ax2 = plt.subplot(2, 2, 2)
    scores = model.predict(df_test)
    for relevance in sorted(df_test['relevance'].unique()):
        mask = df_test['relevance'] == relevance
        if mask.sum() > 0:
            ax2.hist(scores[mask], bins=30, alpha=0.6, label=f'Relevance {relevance}')
    ax2.set_xlabel('Prediction Score', fontsize=12)
    ax2.set_ylabel('Frequency', fontsize=12)
    ax2.set_title('Score Distribution by Relevance', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(alpha=0.3)
    
    # 3. Distance vs Score
    ax3 = plt.subplot(2, 2, 3)
    scatter = ax3.scatter(
        df_test['distance_km'], scores,
        c=df_test['relevance'], cmap='RdYlGn',
        alpha=0.5, s=20
    )
    plt.colorbar(scatter, ax=ax3, label='Relevance')
    ax3.set_xlabel('Distance (km)', fontsize=12)
    ax3.set_ylabel('Ranking Score', fontsize=12)
    ax3.set_title('Distance vs Score (colored by Relevance)', fontsize=14, fontweight='bold')
    ax3.grid(alpha=0.3)
    
    # 4. NDCG Distribution
    ax4 = plt.subplot(2, 2, 4)
    query_test = df_test['query_id'].values
    y_test = df_test['relevance'].values
    ndcg_scores = []
    
    for query_id in np.unique(query_test):
        mask = query_test == query_id
        y_true = y_test[mask]
        y_pred = scores[mask]
        if len(y_true) > 0:
            ndcg = calculate_ndcg_at_k(y_true, y_pred, k=min(10, len(y_true)))
            ndcg_scores.append(ndcg)
    
    ax4.hist(ndcg_scores, bins=30, edgecolor='black', alpha=0.7, color='coral')
    ax4.axvline(np.mean(ndcg_scores), color='red', linestyle='--', linewidth=2,
                label=f'Mean: {np.mean(ndcg_scores):.3f}')
    ax4.set_xlabel('NDCG@10', fontsize=12)
    ax4.set_ylabel('Number of Queries', fontsize=12)
    ax4.set_title('NDCG@10 Distribution Across Queries', fontsize=14, fontweight='bold')
    ax4.legend()
    ax4.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_dir / 'hospital_ranker_v2_report.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"Saved visualizations to {save_dir}/hospital_ranker_v2_report.png")


# ============================================================================
# MODEL PERSISTENCE
# ============================================================================

def save_model(model: HospitalRanker, metadata: Dict, save_dir: Path):
    """Save model artifacts."""
    logger.info("Saving model artifacts...")
    
    # Save LightGBM model
    model.model.save_model(str(save_dir / 'hospital_ranker.pkl'))
    
    # Save feature engineer
    joblib.dump(model.feature_engineer, save_dir / 'hospital_ranker_features.pkl')
    
    # Save scaler
    joblib.dump(model.feature_engineer.scaler, save_dir / 'hospital_ranker_scaler.pkl')
    
    # Save feature names as JSON
    with open(save_dir / 'hospital_ranker_feature_names.json', 'w') as f:
        json.dump(model.feature_engineer.feature_names, f, indent=2)
    
    # Save metadata
    with open(save_dir / 'hospital_ranker_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    
    logger.info(f"✅ Model artifacts saved to {save_dir}")
    logger.info(f"   - hospital_ranker.pkl (LightGBM model)")
    logger.info(f"   - hospital_ranker_features.pkl (Feature engineer)")
    logger.info(f"   - hospital_ranker_scaler.pkl (StandardScaler)")
    logger.info(f"   - hospital_ranker_feature_names.json (Feature list)")
    logger.info(f"   - hospital_ranker_metadata.json (Training metadata)")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    logger.info("=" * 70)
    logger.info("ARIA HOSPITAL RANKER - PRODUCTION TRAINING")
    logger.info("=" * 70)
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    try:
        # 1. Load data
        data_loader = DataLoader(
            hospitals_path=DATA_DIR / 'hospitals_raw.csv',
            incidents_path=BASE_DIR / 'data' / 'processed' / 'incidents_processed.csv'
        )
        
        hospitals = data_loader.load_hospitals()
        incidents = data_loader.load_incidents()
        
        # 2. Generate pairwise data
        pair_generator = PairwiseDataGenerator(hospitals, incidents)
        df = pair_generator.generate(n_samples=10000)  # 10K incidents
        
        # 3. Split data by queries (80/10/10)
        unique_queries = df['query_id'].unique()
        np.random.shuffle(unique_queries)
        
        n_train = int(0.8 * len(unique_queries))
        n_val = int(0.1 * len(unique_queries))
        
        train_queries = unique_queries[:n_train]
        val_queries = unique_queries[n_train:n_train + n_val]
        test_queries = unique_queries[n_train + n_val:]
        
        df_train = df[df['query_id'].isin(train_queries)]
        df_val = df[df['query_id'].isin(val_queries)]
        df_test = df[df['query_id'].isin(test_queries)]
        
        logger.info(f"\nData splits:")
        logger.info(f"  Train: {len(df_train):,} pairs ({len(train_queries):,} queries)")
        logger.info(f"  Val:   {len(df_val):,} pairs ({len(val_queries):,} queries)")
        logger.info(f"  Test:  {len(df_test):,} pairs ({len(test_queries):,} queries)")
        
        # 4. Train model with optimization
        model = HospitalRanker()
        training_results = model.train(
            df_train, df_val,
            optimize=OPTUNA_AVAILABLE,  # Only if Optuna available
            n_trials=20
        )
        
        # 5. Evaluate
        evaluation_results = evaluate_model(model, df_test)
        
        # 6. Visualizations
        create_visualizations(model, df_test, REPORTS_DIR)
        
        # 7. Feature importance
        feature_importance = model.get_feature_importance()
        logger.info("\nTop 15 Important Features:")
        for idx, row in feature_importance.head(15).iterrows():
            logger.info(f"  {row['feature']:30s}: {row['importance']:8.2f}")
        
        # 8. Save model
        metadata = {
            'model_type': 'Hospital Ranker (LambdaMART)',
            'algorithm': 'LightGBM LambdaMART',
            'training_date': datetime.now().isoformat(),
            'data_summary': {
                'n_hospitals': len(hospitals),
                'n_incidents': len(incidents),
                'n_pairs': len(df),
                'train_queries': len(train_queries),
                'val_queries': len(val_queries),
                'test_queries': len(test_queries)
            },
            'training_results': training_results,
            'test_results': evaluation_results,
            'hyperparameters': model.params,
            'best_params': model.best_params if model.best_params else None,
            'feature_names': model.feature_engineer.feature_names,
            'n_features': len(model.feature_engineer.feature_names)
        }
        
        save_model(model, metadata, MODELS_DIR)
        
        # Final summary
        duration = time.time() - start_time
        
        logger.info("=" * 70)
        logger.info("TRAINING COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Duration: {duration:.2f} seconds ({duration/60:.1f} minutes)")
        logger.info(f"Final Test NDCG@10: {evaluation_results['ndcg@10']:.4f}")
        logger.info(f"Final Test NDCG@5:  {evaluation_results['ndcg@5']:.4f}")
        logger.info(f"Final Test NDCG@3:  {evaluation_results['ndcg@3']:.4f}")
        
        if evaluation_results['ndcg@10'] >= 0.8:
            logger.info("✅ Target NDCG@10 (>0.8) ACHIEVED!")
        else:
            logger.warning(f"⚠️  Target not fully met. Got {evaluation_results['ndcg@10']:.4f}, target >0.8")
            logger.info("   This is acceptable for real-world data. Consider:")
            logger.info("   - Adding more training data")
            logger.info("   - Feature engineering improvements")
            logger.info("   - Longer hyperparameter optimization")
        
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
