#!/usr/bin/env python3
"""
ARIA Hospital Ranker - LambdaMART Learning-to-Rank
===================================================
Rank hospitals based on suitability for emergency cases.

Author: ARIA ML Team
Date: August 2026
Version: 1.0

Model Details:
- Algorithm: LightGBM LambdaMART
- Purpose: Rank hospitals by suitability
- Target: NDCG@10 > 0.8

Usage:
    python hospital_ranker.py
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
import lightgbm as lgb

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
DATA_DIR_RAW = BASE_DIR / "data" / "raw"
DATA_DIR_PROCESSED = BASE_DIR / "data" / "processed"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

# Create directories
MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Logging setup
LOG_FILE = LOGS_DIR / "hospital_ranker_training.log"
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
LGBM_PARAMS = {
    'objective': 'lambdarank',
    'metric': 'ndcg',
    'ndcg_eval_at': [5, 10, 20],
    'num_leaves': 31,
    'learning_rate': 0.05,
    'feature_fraction': 0.8,
    'bagging_fraction': 0.8,
    'bagging_freq': 5,
    'verbose': -1,
    'num_boost_round': 500
}

# ============================================================================
# DATA GENERATION
# ============================================================================

class HospitalRankingDataGenerator:
    """Generate synthetic hospital ranking data."""
    
    def __init__(self, hospitals_file: Path, n_queries: int = 10000):
        self.hospitals_file = hospitals_file
        self.n_queries = n_queries
        self.random_state = 42
        np.random.seed(self.random_state)
        
    def load_hospitals(self) -> pd.DataFrame:
        """Load hospital data."""
        logger.info(f"Loading hospitals from {self.hospitals_file}")
        
        if not self.hospitals_file.exists():
            logger.warning("Hospital file not found. Generating synthetic hospitals.")
            return self._generate_synthetic_hospitals()
        
        df = pd.read_csv(self.hospitals_file, low_memory=False)
        logger.info(f"Loaded {len(df):,} hospitals")
        
        # Clean real data
        df = df.dropna(subset=['latitude', 'longitude'])
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        df = df[(df['latitude'].between(-90, 90)) & (df['longitude'].between(-90, 90))]
        
        # Sample hospitals for faster training (take 1000 random hospitals)
        if len(df) > 1000:
            df = df.sample(n=1000, random_state=42)
            logger.info(f"Sampled {len(df)} hospitals for training")
        
        # Convert beds columns
        df['total_beds'] = pd.to_numeric(df.get('beds', 0), errors='coerce').fillna(50)
        df['icu_beds'] = pd.to_numeric(df.get('icu_beds', 0), errors='coerce').fillna(5)
        
        # Create emergency/trauma flags
        df['emergency_dept'] = df.get('emergency_services', 'Unknown').astype(str).str.lower().isin(['yes', 'true', '1']).astype(int)
        df['trauma_center'] = 0  # Default, can be enhanced
        df['rating'] = 3.5  # Default rating
        df['wait_time_avg'] = 60.0  # Default wait time
        
        # Calculate available beds (assume 30% available)
        df['available_beds'] = (df['total_beds'] * 0.3).astype(int)
        df['icu_available'] = (df['icu_beds'] * 0.3).astype(int)
        
        logger.info(f"After cleaning: {len(df):,} hospitals")
        
        return df
    
    def _generate_synthetic_hospitals(self, n_hospitals: int = 100) -> pd.DataFrame:
        """Generate synthetic hospital data."""
        logger.info(f"Generating {n_hospitals} synthetic hospitals...")
        
        hospital_ids = [f"HOSP_{i:04d}" for i in range(n_hospitals)]
        
        # Generate features
        data = {
            'hospital_id': hospital_ids,
            'name': [f"Hospital {i}" for i in range(n_hospitals)],
            'latitude': np.random.uniform(18.0, 19.5, n_hospitals),
            'longitude': np.random.uniform(72.5, 73.5, n_hospitals),
            'total_beds': np.random.randint(50, 500, n_hospitals),
            'icu_beds': np.random.randint(5, 50, n_hospitals),
            'trauma_center': np.random.choice([0, 1], n_hospitals, p=[0.7, 0.3]),
            'emergency_dept': np.random.choice([0, 1], n_hospitals, p=[0.1, 0.9]),
            'rating': np.random.uniform(2.5, 5.0, n_hospitals),
            'wait_time_avg': np.random.uniform(15, 120, n_hospitals)
        }
        
        df = pd.DataFrame(data)
        
        # Calculate available beds
        df['available_beds'] = (df['total_beds'] * np.random.uniform(0.1, 0.4, n_hospitals)).astype(int)
        df['icu_available'] = (df['icu_beds'] * np.random.uniform(0.1, 0.5, n_hospitals)).astype(int)
        
        return df
    
    def generate_queries(self, hospitals: pd.DataFrame) -> pd.DataFrame:
        """Generate emergency queries with hospital rankings."""
        logger.info(f"Generating {self.n_queries:,} emergency queries...")
        
        queries = []
        
        for query_id in tqdm(range(self.n_queries), desc="Generating queries"):
            # Random incident location
            incident_lat = np.random.uniform(18.0, 19.5)
            incident_lon = np.random.uniform(72.5, 73.5)
            
            # Random severity
            severity = np.random.choice(['LOW', 'MODERATE', 'CRITICAL'], p=[0.3, 0.5, 0.2])
            
            # Required specialty
            specialties = ['GENERAL', 'CARDIOLOGY', 'TRAUMA', 'NEUROLOGY', 'ORTHOPEDIC']
            required_specialty = np.random.choice(specialties)
            
            # Time of day
            hour = np.random.randint(0, 24)
            
            # For each hospital, calculate features and relevance
            for _, hospital in hospitals.iterrows():
                # Distance (Euclidean approximation)
                distance = np.sqrt(
                    (hospital['latitude'] - incident_lat) ** 2 +
                    (hospital['longitude'] - incident_lon) ** 2
                ) * 111  # Rough km conversion
                
                # Calculate relevance score (0-4)
                relevance = self._calculate_relevance(
                    hospital, distance, severity, required_specialty
                )
                
                query = {
                    'query_id': query_id,
                    'hospital_id': hospital['hospital_id'],
                    'incident_lat': incident_lat,
                    'incident_lon': incident_lon,
                    'severity': severity,
                    'required_specialty': required_specialty,
                    'hour': hour,
                    'distance_km': distance,
                    'total_beds': hospital['total_beds'],
                    'available_beds': hospital['available_beds'],
                    'icu_beds': hospital['icu_beds'],
                    'icu_available': hospital['icu_available'],
                    'trauma_center': hospital['trauma_center'],
                    'emergency_dept': hospital['emergency_dept'],
                    'rating': hospital['rating'],
                    'wait_time_avg': hospital['wait_time_avg'],
                    'relevance': relevance
                }
                
                queries.append(query)
        
        df = pd.DataFrame(queries)
        
        logger.info(f"Generated {len(df):,} query-hospital pairs")
        logger.info(f"Unique queries: {df['query_id'].nunique():,}")
        logger.info(f"Avg hospitals per query: {len(df) / df['query_id'].nunique():.1f}")
        
        return df
    
    def _calculate_relevance(self, hospital: pd.Series, distance: float,
                            severity: str, specialty: str) -> int:
        """Calculate relevance score (0-4) for hospital given emergency."""
        score = 0.0
        
        # Distance factor (closer is better)
        if distance < 2:
            score += 2.0
        elif distance < 5:
            score += 1.5
        elif distance < 10:
            score += 1.0
        elif distance < 20:
            score += 0.5
        
        # Bed availability
        if hospital['available_beds'] > 10:
            score += 1.0
        elif hospital['available_beds'] > 5:
            score += 0.5
        
        # Critical cases need ICU
        if severity == 'CRITICAL':
            if hospital['icu_available'] > 0:
                score += 1.5
            else:
                score -= 1.0
        
        # Trauma center for trauma cases
        if specialty == 'TRAUMA' and hospital['trauma_center'] == 1:
            score += 1.0
        
        # Emergency department
        if hospital['emergency_dept'] == 1:
            score += 0.5
        
        # Rating
        score += (hospital['rating'] - 3.0) / 2.0  # Normalized contribution
        
        # Wait time (lower is better)
        if hospital['wait_time_avg'] < 30:
            score += 0.5
        elif hospital['wait_time_avg'] > 90:
            score -= 0.5
        
        # Convert to 0-4 scale
        relevance = np.clip(int(np.round(score)), 0, 4)
        
        return relevance


# ============================================================================
# FEATURE ENGINEERING
# ============================================================================

class HospitalRankingFeatures:
    """Feature engineering for hospital ranking."""
    
    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.feature_names = []
        
    def create_features(self, df: pd.DataFrame, fit: bool = False) -> pd.DataFrame:
        """Create ranking features."""
        df = df.copy()
        
        # Distance features
        df['log_distance'] = np.log1p(df['distance_km'])
        df['distance_squared'] = df['distance_km'] ** 2
        df['is_nearby'] = (df['distance_km'] < 5).astype(int)
        
        # Capacity features
        df['bed_utilization'] = df['available_beds'] / (df['total_beds'] + 1)
        df['icu_utilization'] = df['icu_available'] / (df['icu_beds'] + 1)
        df['has_available_beds'] = (df['available_beds'] > 0).astype(int)
        df['has_icu_available'] = (df['icu_available'] > 0).astype(int)
        
        # Quality features
        df['rating_normalized'] = (df['rating'] - 2.5) / 2.5
        df['wait_time_normalized'] = (df['wait_time_avg'] - 60) / 60
        
        # Temporal features
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['is_night'] = ((df['hour'] >= 22) | (df['hour'] <= 6)).astype(int)
        
        # Encode categorical
        if fit:
            self.label_encoders['severity'] = LabelEncoder()
            df['severity_encoded'] = self.label_encoders['severity'].fit_transform(df['severity'])
            
            self.label_encoders['specialty'] = LabelEncoder()
            df['specialty_encoded'] = self.label_encoders['specialty'].fit_transform(df['required_specialty'])
        else:
            df['severity_encoded'] = self.label_encoders['severity'].transform(df['severity'])
            df['specialty_encoded'] = self.label_encoders['specialty'].transform(df['required_specialty'])
        
        # Interaction features
        df['distance_x_severity'] = df['distance_km'] * df['severity_encoded']
        df['distance_x_beds'] = df['distance_km'] * df['available_beds']
        df['rating_x_distance'] = df['rating'] * (1 / (df['distance_km'] + 1))
        
        # Critical care score
        df['critical_care_score'] = (
            df['icu_available'] * 2 +
            df['trauma_center'] * 1.5 +
            df['emergency_dept'] * 1.0
        )
        
        # Overall hospital score
        df['hospital_score'] = (
            df['rating'] * 0.3 +
            (5 - df['wait_time_avg'] / 30) * 0.2 +
            df['bed_utilization'] * 0.2 +
            df['emergency_dept'] * 0.3
        )
        
        # Select features
        feature_cols = [
            'distance_km', 'log_distance', 'distance_squared', 'is_nearby',
            'available_beds', 'icu_available', 'bed_utilization', 'icu_utilization',
            'has_available_beds', 'has_icu_available',
            'trauma_center', 'emergency_dept',
            'rating', 'rating_normalized', 'wait_time_avg', 'wait_time_normalized',
            'hour_sin', 'hour_cos', 'is_night',
            'severity_encoded', 'specialty_encoded',
            'distance_x_severity', 'distance_x_beds', 'rating_x_distance',
            'critical_care_score', 'hospital_score'
        ]
        
        if fit:
            self.feature_names = feature_cols
        
        return df[feature_cols]


# ============================================================================
# RANKING METRICS
# ============================================================================

def calculate_ndcg(y_true: np.ndarray, y_pred: np.ndarray, k: int = 10) -> float:
    """Calculate NDCG@k."""
    # Sort by predicted scores
    order = np.argsort(y_pred)[::-1][:k]
    y_true_sorted = y_true[order]
    
    # DCG
    dcg = np.sum((2 ** y_true_sorted - 1) / np.log2(np.arange(2, len(y_true_sorted) + 2)))
    
    # IDCG
    ideal_order = np.argsort(y_true)[::-1][:k]
    y_true_ideal = y_true[ideal_order]
    idcg = np.sum((2 ** y_true_ideal - 1) / np.log2(np.arange(2, len(y_true_ideal) + 2)))
    
    if idcg == 0:
        return 0.0
    
    return dcg / idcg


def calculate_map(y_true: np.ndarray, y_pred: np.ndarray, k: int = 10) -> float:
    """Calculate MAP@k."""
    order = np.argsort(y_pred)[::-1][:k]
    y_true_sorted = y_true[order]
    
    relevant = (y_true_sorted >= 3).astype(int)  # Threshold for relevance
    
    if relevant.sum() == 0:
        return 0.0
    
    precisions = []
    num_relevant = 0
    
    for i, rel in enumerate(relevant):
        if rel:
            num_relevant += 1
            precision = num_relevant / (i + 1)
            precisions.append(precision)
    
    return np.mean(precisions) if precisions else 0.0


# ============================================================================
# HOSPITAL RANKER MODEL
# ============================================================================

class HospitalRankerModel:
    """LambdaMART-based hospital ranker."""
    
    def __init__(self, params: Dict = None):
        self.params = params or LGBM_PARAMS
        self.model = None
        self.feature_engineer = HospitalRankingFeatures()
        
    def train(self, df_train: pd.DataFrame, df_val: pd.DataFrame) -> Dict[str, float]:
        """Train LambdaMART ranker."""
        logger.info("Training Hospital Ranker...")
        
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
        
        # Create LightGBM datasets with group information
        train_group = df_train.groupby('query_id').size().values
        val_group = df_val.groupby('query_id').size().values
        
        lgb_train = lgb.Dataset(
            X_train, y_train,
            group=train_group,
            free_raw_data=False
        )
        
        lgb_val = lgb.Dataset(
            X_val, y_val,
            group=val_group,
            reference=lgb_train,
            free_raw_data=False
        )
        
        # Train model
        self.model = lgb.train(
            self.params,
            lgb_train,
            valid_sets=[lgb_val],
            num_boost_round=self.params['num_boost_round'],
            callbacks=[lgb.early_stopping(stopping_rounds=50)]
        )
        
        # Evaluate
        y_pred_val = self.model.predict(X_val)
        
        # Calculate metrics per query
        ndcg_scores = []
        map_scores = []
        
        for query_id in np.unique(query_val):
            mask = query_val == query_id
            y_true_q = y_val[mask]
            y_pred_q = y_pred_val[mask]
            
            ndcg = calculate_ndcg(y_true_q, y_pred_q, k=10)
            map_score = calculate_map(y_true_q, y_pred_q, k=10)
            
            ndcg_scores.append(ndcg)
            map_scores.append(map_score)
        
        metrics = {
            'ndcg@10': np.mean(ndcg_scores),
            'map@10': np.mean(map_scores),
            'ndcg_std': np.std(ndcg_scores)
        }
        
        logger.info(f"\nValidation Metrics:")
        logger.info(f"  NDCG@10: {metrics['ndcg@10']:.4f} ± {metrics['ndcg_std']:.4f}")
        logger.info(f"  MAP@10:  {metrics['map@10']:.4f}")
        
        return metrics
    
    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Predict ranking scores."""
        X = self.feature_engineer.create_features(df, fit=False)
        return self.model.predict(X)
    
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

def evaluate_model(model: HospitalRankerModel, df_test: pd.DataFrame) -> Dict[str, Any]:
    """Comprehensive model evaluation."""
    logger.info("=" * 70)
    logger.info("MODEL EVALUATION")
    logger.info("=" * 70)
    
    # Predictions
    y_pred = model.predict(df_test)
    y_test = df_test['relevance'].values
    query_test = df_test['query_id'].values
    
    # Calculate metrics per query
    ndcg_5_scores = []
    ndcg_10_scores = []
    ndcg_20_scores = []
    map_scores = []
    
    for query_id in np.unique(query_test):
        mask = query_test == query_id
        y_true_q = y_test[mask]
        y_pred_q = y_pred[mask]
        
        ndcg_5 = calculate_ndcg(y_true_q, y_pred_q, k=5)
        ndcg_10 = calculate_ndcg(y_true_q, y_pred_q, k=10)
        ndcg_20 = calculate_ndcg(y_true_q, y_pred_q, k=20)
        map_score = calculate_map(y_true_q, y_pred_q, k=10)
        
        ndcg_5_scores.append(ndcg_5)
        ndcg_10_scores.append(ndcg_10)
        ndcg_20_scores.append(ndcg_20)
        map_scores.append(map_score)
    
    results = {
        'ndcg@5': np.mean(ndcg_5_scores),
        'ndcg@10': np.mean(ndcg_10_scores),
        'ndcg@20': np.mean(ndcg_20_scores),
        'map@10': np.mean(map_scores),
        'num_queries': len(np.unique(query_test))
    }
    
    logger.info(f"\nTest Set Metrics ({results['num_queries']} queries):")
    logger.info(f"  NDCG@5:  {results['ndcg@5']:.4f}")
    logger.info(f"  NDCG@10: {results['ndcg@10']:.4f}")
    logger.info(f"  NDCG@20: {results['ndcg@20']:.4f}")
    logger.info(f"  MAP@10:  {results['map@10']:.4f}")
    
    return results


def create_visualizations(model: HospitalRankerModel, df_test: pd.DataFrame,
                         save_dir: Path):
    """Create evaluation visualizations."""
    logger.info("Creating visualizations...")
    
    fig = plt.figure(figsize=(16, 10))
    
    # 1. Feature Importance
    ax1 = plt.subplot(2, 2, 1)
    feature_importance = model.get_feature_importance()
    top_features = feature_importance.head(15)
    ax1.barh(range(len(top_features)), top_features['importance'].values)
    ax1.set_yticks(range(len(top_features)))
    ax1.set_yticklabels(top_features['feature'].values, fontsize=8)
    ax1.set_xlabel('Importance', fontsize=12)
    ax1.set_title('Top 15 Feature Importance', fontsize=14, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    
    # 2. Score Distribution by Relevance
    ax2 = plt.subplot(2, 2, 2)
    scores = model.predict(df_test)
    for relevance in sorted(df_test['relevance'].unique()):
        mask = df_test['relevance'] == relevance
        ax2.hist(scores[mask], bins=30, alpha=0.5, label=f'Relevance {relevance}')
    ax2.set_xlabel('Prediction Score', fontsize=12)
    ax2.set_ylabel('Frequency', fontsize=12)
    ax2.set_title('Score Distribution by Relevance', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(alpha=0.3)
    
    # 3. Distance vs Score (colored by relevance)
    ax3 = plt.subplot(2, 2, 3)
    scatter = ax3.scatter(
        df_test['distance_km'], scores,
        c=df_test['relevance'], cmap='RdYlGn',
        alpha=0.5, s=10
    )
    plt.colorbar(scatter, ax=ax3, label='Relevance')
    ax3.set_xlabel('Distance (km)', fontsize=12)
    ax3.set_ylabel('Ranking Score', fontsize=12)
    ax3.set_title('Distance vs Score (by Relevance)', fontsize=14, fontweight='bold')
    ax3.grid(alpha=0.3)
    
    # 4. NDCG by Query
    ax4 = plt.subplot(2, 2, 4)
    ndcg_scores = []
    for query_id in df_test['query_id'].unique()[:100]:  # First 100 queries
        mask = df_test['query_id'] == query_id
        y_true = df_test[mask]['relevance'].values
        y_pred = scores[mask]
        ndcg = calculate_ndcg(y_true, y_pred, k=10)
        ndcg_scores.append(ndcg)
    
    ax4.plot(ndcg_scores, alpha=0.7)
    ax4.axhline(np.mean(ndcg_scores), color='r', linestyle='--', 
                label=f'Mean: {np.mean(ndcg_scores):.3f}')
    ax4.set_xlabel('Query Index', fontsize=12)
    ax4.set_ylabel('NDCG@10', fontsize=12)
    ax4.set_title('NDCG@10 per Query (first 100)', fontsize=14, fontweight='bold')
    ax4.legend()
    ax4.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_dir / 'hospital_ranker_evaluation.png', dpi=300)
    plt.close()
    
    logger.info(f"Saved visualizations to {save_dir}/hospital_ranker_evaluation.png")


# ============================================================================
# MODEL PERSISTENCE
# ============================================================================

def save_model(model: HospitalRankerModel, metadata: Dict, save_dir: Path):
    """Save model artifacts."""
    logger.info("Saving model artifacts...")
    
    # Save model
    model.model.save_model(str(save_dir / 'hospital_ranker.txt'))
    
    # Save feature engineer
    joblib.dump(model.feature_engineer, save_dir / 'hospital_ranker_features.pkl')
    
    # Save metadata
    with open(save_dir / 'hospital_ranker_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    
    logger.info(f"Model artifacts saved to {save_dir}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    logger.info("=" * 70)
    logger.info("ARIA HOSPITAL RANKER TRAINING")
    logger.info("=" * 70)
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    try:
        # Generate data
        generator = HospitalRankingDataGenerator(
            hospitals_file=DATA_DIR_RAW / 'hospitals_raw.csv',
            n_queries=1000  # Reduced to 1K for faster training
        )
        
        hospitals = generator.load_hospitals()
        df = generator.generate_queries(hospitals)
        
        # Split by queries (80/10/10)
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
        
        # Train model
        model = HospitalRankerModel()
        training_results = model.train(df_train, df_val)
        
        # Evaluate
        evaluation_results = evaluate_model(model, df_test)
        
        # Visualizations
        create_visualizations(model, df_test, REPORTS_DIR)
        
        # Feature importance
        feature_importance = model.get_feature_importance()
        logger.info("\nTop 10 Important Features:")
        for idx, row in feature_importance.head(10).iterrows():
            logger.info(f"  {row['feature']}: {row['importance']:.2f}")
        
        # Save model
        metadata = {
            'model_type': 'Hospital Ranker (LambdaMART)',
            'training_date': datetime.now().isoformat(),
            'train_queries': len(train_queries),
            'val_queries': len(val_queries),
            'test_queries': len(test_queries),
            'training_results': training_results,
            'test_results': evaluation_results,
            'lgbm_params': LGBM_PARAMS,
            'feature_names': model.feature_engineer.feature_names
        }
        
        save_model(model, metadata, MODELS_DIR)
        
        # Final summary
        duration = time.time() - start_time
        
        logger.info("=" * 70)
        logger.info("TRAINING COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Final Test NDCG@10: {evaluation_results['ndcg@10']:.4f}")
        
        if evaluation_results['ndcg@10'] >= 0.8:
            logger.info("✅ Target NDCG@10 (>0.8) ACHIEVED!")
        else:
            logger.warning(f"⚠️  Target not met. Got {evaluation_results['ndcg@10']:.4f}, need >0.8")
        
        logger.info(f"\nModel saved to: {MODELS_DIR}")
        logger.info("=" * 70)
        
        return 0
        
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
