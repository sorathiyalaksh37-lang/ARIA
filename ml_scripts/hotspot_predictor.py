#!/usr/bin/env python3
"""
ARIA Hotspot Predictor - DBSCAN + Isolation Forest
===================================================
Identify emergency incident hotspots and anomalies.

Author: ARIA ML Team
Date: August 2026
Version: 1.0

Model Details:
- Algorithm: DBSCAN (clustering) + Isolation Forest (anomalies)
- Purpose: Identify high-incident zones and unusual patterns
- Target: Precision > 0.7 for hotspot detection

Usage:
    python hotspot_predictor.py
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

# ML Libraries
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from scipy.spatial import ConvexHull

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
DATA_DIR = BASE_DIR / "data" / "processed"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

# Create directories
MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Logging setup
LOG_FILE = LOGS_DIR / "hotspot_predictor_training.log"
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
DBSCAN_PARAMS = {
    'eps': 0.5,  # in km (adjusted for coordinate scale)
    'min_samples': 10,
    'metric': 'euclidean'
}

ISOLATION_FOREST_PARAMS = {
    'n_estimators': 100,
    'contamination': 0.1,  # 10% anomalies
    'random_state': 42
}

# ============================================================================
# DATA LOADING
# ============================================================================

class HotspotDataLoader:
    """Load and prepare incident data for hotspot detection."""
    
    def __init__(self, data_path: Path):
        self.data_path = data_path
        
    def load_data(self) -> pd.DataFrame:
        """Load incident data."""
        logger.info(f"Loading data from {self.data_path}")
        
        if not self.data_path.exists():
            logger.warning("Data file not found. Generating synthetic data.")
            return self._generate_synthetic_data()
        
        df = pd.read_csv(self.data_path)
        logger.info(f"Loaded {len(df):,} records")
        
        # Parse timestamp and extract hour if not present
        if 'timestamp' in df.columns and 'hour' not in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            
        # Ensure day_of_week exists
        if 'day_of_week' not in df.columns and 'timestamp' in df.columns:
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            
        # Create is_weekend if not present
        if 'is_weekend' not in df.columns and 'day_of_week' in df.columns:
            # Map day names to numeric if needed
            day_mapping = {'MON': 0, 'TUE': 1, 'WED': 2, 'THU': 3, 'FRI': 4, 'SAT': 5, 'SUN': 6}
            if df['day_of_week'].dtype == 'object':
                df['day_of_week'] = df['day_of_week'].map(day_mapping)
            df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
            
        # Ensure severity_encoded exists
        if 'severity_encoded' not in df.columns and 'severity' in df.columns:
            severity_map = {'LOW': 1, 'MODERATE': 2, 'HIGH': 2, 'CRITICAL': 3}
            df['severity_encoded'] = df['severity'].map(severity_map).fillna(2)
        
        return df
    
    def _generate_synthetic_data(self, n_records: int = 10000) -> pd.DataFrame:
        """Generate synthetic incident data."""
        logger.info(f"Generating {n_records:,} synthetic incidents...")
        
        np.random.seed(42)
        
        # Mumbai coordinates (approximate)
        mumbai_lat_range = (18.90, 19.30)
        mumbai_lon_range = (72.80, 72.95)
        
        # Create hotspot centers
        n_hotspots = 5
        hotspot_centers = [
            (19.07, 72.87),  # South Mumbai
            (19.12, 72.88),  # Central Mumbai
            (19.18, 72.85),  # Andheri
            (19.23, 72.87),  # Borivali
            (19.08, 72.91),  # Eastern suburbs
        ]
        
        # Generate incidents (70% in hotspots, 30% random)
        incidents = []
        
        for i in range(n_records):
            if np.random.rand() < 0.7:
                # Hotspot incident
                center = hotspot_centers[np.random.randint(0, n_hotspots)]
                latitude = np.random.normal(center[0], 0.01)
                longitude = np.random.normal(center[1], 0.01)
            else:
                # Random incident
                latitude = np.random.uniform(*mumbai_lat_range)
                longitude = np.random.uniform(*mumbai_lon_range)
            
            # Timestamp (last 30 days)
            days_ago = np.random.randint(0, 30)
            hour = np.random.randint(0, 24)
            timestamp = datetime.now() - timedelta(days=days_ago, hours=hour)
            
            # Severity
            severity = np.random.choice(['LOW', 'MODERATE', 'CRITICAL'], p=[0.4, 0.4, 0.2])
            
            # Type
            incident_type = np.random.choice([
                'ACCIDENT', 'MEDICAL', 'FIRE', 'CRIME', 'OTHER'
            ], p=[0.3, 0.4, 0.1, 0.15, 0.05])
            
            incidents.append({
                'incident_id': f'INC_{i:06d}',
                'latitude': latitude,
                'longitude': longitude,
                'timestamp': timestamp,
                'severity': severity,
                'incident_type': incident_type,
                'hour': hour,
                'day_of_week': timestamp.weekday(),
                'is_weekend': 1 if timestamp.weekday() >= 5 else 0
            })
        
        df = pd.DataFrame(incidents)
        
        logger.info(f"Generated {len(df):,} synthetic incidents")
        logger.info(f"Lat range: [{df['latitude'].min():.4f}, {df['latitude'].max():.4f}]")
        logger.info(f"Lon range: [{df['longitude'].min():.4f}, {df['longitude'].max():.4f}]")
        
        return df


# ============================================================================
# FEATURE ENGINEERING
# ============================================================================

class HotspotFeatureEngineer:
    """Create features for hotspot detection."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        
    def create_spatial_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create spatial and temporal features."""
        df = df.copy()
        
        # Temporal patterns
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        # Density features (count nearby incidents)
        df['nearby_count'] = self._calculate_nearby_counts(df)
        
        # Severity encoding
        severity_map = {'LOW': 1, 'MODERATE': 2, 'CRITICAL': 3}
        df['severity_encoded'] = df['severity'].map(severity_map)
        
        return df
    
    def _calculate_nearby_counts(self, df: pd.DataFrame, radius_km: float = 0.5) -> np.ndarray:
        """Calculate number of incidents within radius."""
        counts = []
        
        # Convert radius to approximate degrees
        radius_deg = radius_km / 111.0
        
        for idx, row in df.iterrows():
            lat, lon = row['latitude'], row['longitude']
            
            # Calculate distances
            lat_diff = df['latitude'] - lat
            lon_diff = df['longitude'] - lon
            distances = np.sqrt(lat_diff**2 + lon_diff**2)
            
            # Count nearby (excluding self)
            count = ((distances < radius_deg) & (distances > 0)).sum()
            counts.append(count)
        
        return np.array(counts)


# ============================================================================
# HOTSPOT DETECTOR (DBSCAN)
# ============================================================================

class DBSCANHotspotDetector:
    """DBSCAN-based hotspot detector."""
    
    def __init__(self, params: Dict = None):
        self.params = params or DBSCAN_PARAMS
        self.model = None
        self.cluster_centers = None
        self.cluster_info = {}
        
    def fit(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Fit DBSCAN to detect hotspots."""
        logger.info("Detecting hotspots with DBSCAN...")
        
        # Extract spatial coordinates
        X = df[['latitude', 'longitude']].values
        
        # Fit DBSCAN
        self.model = DBSCAN(**self.params)
        labels = self.model.fit_predict(X)
        
        # Analyze clusters
        unique_labels = set(labels)
        n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
        n_noise = list(labels).count(-1)
        
        logger.info(f"Found {n_clusters} hotspot clusters")
        logger.info(f"Noise points: {n_noise} ({n_noise/len(df)*100:.1f}%)")
        
        # Calculate cluster statistics
        self.cluster_centers = {}
        self.cluster_info = {}
        
        for label in unique_labels:
            if label == -1:
                continue
            
            mask = labels == label
            cluster_points = X[mask]
            
            # Center (centroid)
            center = cluster_points.mean(axis=0)
            self.cluster_centers[label] = center
            
            # Statistics
            cluster_df = df[mask]
            
            self.cluster_info[label] = {
                'size': int(mask.sum()),
                'center_lat': float(center[0]),
                'center_lon': float(center[1]),
                'severity_distribution': cluster_df['severity'].value_counts().to_dict(),
                'avg_severity': float(cluster_df['severity_encoded'].mean()) if 'severity_encoded' in cluster_df.columns else None,
                'incident_types': cluster_df['incident_type'].value_counts().to_dict() if 'incident_type' in cluster_df.columns else {}
            }
        
        # Evaluation metrics
        if n_clusters > 1:
            # Silhouette score (exclude noise)
            mask_valid = labels != -1
            if mask_valid.sum() > 0:
                silhouette = silhouette_score(X[mask_valid], labels[mask_valid])
                ch_score = calinski_harabasz_score(X[mask_valid], labels[mask_valid])
            else:
                silhouette = 0
                ch_score = 0
        else:
            silhouette = 0
            ch_score = 0
        
        metrics = {
            'n_clusters': n_clusters,
            'n_noise': n_noise,
            'noise_ratio': n_noise / len(df),
            'silhouette_score': silhouette,
            'calinski_harabasz_score': ch_score
        }
        
        logger.info(f"Silhouette Score: {silhouette:.4f}")
        logger.info(f"Calinski-Harabasz Score: {ch_score:.2f}")
        
        # Log top clusters
        sorted_clusters = sorted(self.cluster_info.items(), 
                                key=lambda x: x[1]['size'], reverse=True)
        
        logger.info("\nTop 5 Hotspots:")
        for label, info in sorted_clusters[:5]:
            logger.info(f"  Cluster {label}: {info['size']} incidents at "
                       f"({info['center_lat']:.4f}, {info['center_lon']:.4f})")
        
        return metrics
    
    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Assign new points to nearest cluster."""
        X = df[['latitude', 'longitude']].values
        
        if not self.cluster_centers:
            return np.full(len(X), -1)
        
        # Assign to nearest cluster
        labels = []
        
        for point in X:
            min_dist = float('inf')
            best_label = -1
            
            for label, center in self.cluster_centers.items():
                dist = np.linalg.norm(point - center)
                if dist < min_dist:
                    min_dist = dist
                    best_label = label
            
            # If too far, mark as noise
            if min_dist > self.params['eps']:
                best_label = -1
            
            labels.append(best_label)
        
        return np.array(labels)


# ============================================================================
# ANOMALY DETECTOR (ISOLATION FOREST)
# ============================================================================

class IsolationForestAnomalyDetector:
    """Isolation Forest-based anomaly detector."""
    
    def __init__(self, params: Dict = None):
        self.params = params or ISOLATION_FOREST_PARAMS
        self.model = None
        self.feature_engineer = HotspotFeatureEngineer()
        
    def fit(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Fit Isolation Forest to detect anomalies."""
        logger.info("Training Isolation Forest for anomaly detection...")
        
        # Feature engineering
        df_features = self.feature_engineer.create_spatial_features(df)
        
        # Select features for anomaly detection
        feature_cols = [
            'latitude', 'longitude',
            'hour_sin', 'hour_cos', 'day_sin', 'day_cos',
            'nearby_count', 'severity_encoded', 'is_weekend'
        ]
        
        X = df_features[feature_cols].values
        
        # Scale features
        X_scaled = self.feature_engineer.scaler.fit_transform(X)
        
        # Fit Isolation Forest
        self.model = IsolationForest(**self.params)
        predictions = self.model.fit_predict(X_scaled)
        
        # Analyze results
        n_anomalies = (predictions == -1).sum()
        n_normal = (predictions == 1).sum()
        
        logger.info(f"Detected {n_anomalies} anomalies ({n_anomalies/len(df)*100:.1f}%)")
        logger.info(f"Normal points: {n_normal} ({n_normal/len(df)*100:.1f}%)")
        
        # Anomaly scores
        scores = self.model.decision_function(X_scaled)
        
        metrics = {
            'n_anomalies': int(n_anomalies),
            'n_normal': int(n_normal),
            'anomaly_ratio': float(n_anomalies / len(df)),
            'mean_score': float(scores.mean()),
            'std_score': float(scores.std()),
            'min_score': float(scores.min()),
            'max_score': float(scores.max())
        }
        
        logger.info(f"Anomaly Score Range: [{scores.min():.4f}, {scores.max():.4f}]")
        
        return metrics
    
    def predict(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Predict anomalies (labels and scores)."""
        df_features = self.feature_engineer.create_spatial_features(df)
        
        feature_cols = [
            'latitude', 'longitude',
            'hour_sin', 'hour_cos', 'day_sin', 'day_cos',
            'nearby_count', 'severity_encoded', 'is_weekend'
        ]
        
        X = df_features[feature_cols].values
        X_scaled = self.feature_engineer.scaler.transform(X)
        
        predictions = self.model.predict(X_scaled)
        scores = self.model.decision_function(X_scaled)
        
        return predictions, scores


# ============================================================================
# COMBINED HOTSPOT PREDICTOR
# ============================================================================

class HotspotPredictor:
    """Combined hotspot and anomaly predictor."""
    
    def __init__(self):
        self.dbscan_detector = DBSCANHotspotDetector()
        self.anomaly_detector = IsolationForestAnomalyDetector()
        
    def fit(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train both detectors."""
        logger.info("=" * 70)
        logger.info("TRAINING HOTSPOT PREDICTOR")
        logger.info("=" * 70)
        
        results = {}
        
        # DBSCAN for hotspots
        dbscan_metrics = self.dbscan_detector.fit(df)
        results['hotspot_detection'] = dbscan_metrics
        
        # Isolation Forest for anomalies
        anomaly_metrics = self.anomaly_detector.fit(df)
        results['anomaly_detection'] = anomaly_metrics
        
        return results
    
    def predict_hotspots(self, df: pd.DataFrame) -> np.ndarray:
        """Predict hotspot cluster labels."""
        return self.dbscan_detector.predict(df)
    
    def predict_anomalies(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Predict anomalies (labels and scores)."""
        return self.anomaly_detector.predict(df)
    
    def get_hotspot_info(self) -> Dict:
        """Get information about detected hotspots."""
        return self.dbscan_detector.cluster_info


# ============================================================================
# EVALUATION
# ============================================================================

def evaluate_model(model: HotspotPredictor, df: pd.DataFrame) -> Dict[str, Any]:
    """Evaluate hotspot predictor."""
    logger.info("=" * 70)
    logger.info("MODEL EVALUATION")
    logger.info("=" * 70)
    
    # Hotspot predictions
    hotspot_labels = model.predict_hotspots(df)
    
    # Anomaly predictions
    anomaly_labels, anomaly_scores = model.predict_anomalies(df)
    
    # Analyze results
    n_hotspots = len(set(hotspot_labels)) - (1 if -1 in hotspot_labels else 0)
    n_in_hotspots = (hotspot_labels != -1).sum()
    n_anomalies = (anomaly_labels == -1).sum()
    
    logger.info(f"\nHotspot Detection:")
    logger.info(f"  Total hotspots: {n_hotspots}")
    logger.info(f"  Incidents in hotspots: {n_in_hotspots} ({n_in_hotspots/len(df)*100:.1f}%)")
    
    logger.info(f"\nAnomaly Detection:")
    logger.info(f"  Anomalies detected: {n_anomalies} ({n_anomalies/len(df)*100:.1f}%)")
    logger.info(f"  Anomaly score range: [{anomaly_scores.min():.4f}, {anomaly_scores.max():.4f}]")
    
    # Calculate precision for hotspots (if we have ground truth)
    # For synthetic data, we consider high-density clusters as true hotspots
    high_density_threshold = 10
    df['nearby_count'] = model.anomaly_detector.feature_engineer._calculate_nearby_counts(df)
    true_hotspot = df['nearby_count'] >= high_density_threshold
    predicted_hotspot = hotspot_labels != -1
    
    if predicted_hotspot.sum() > 0:
        precision = (true_hotspot & predicted_hotspot).sum() / predicted_hotspot.sum()
        recall = (true_hotspot & predicted_hotspot).sum() / true_hotspot.sum() if true_hotspot.sum() > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    else:
        precision = recall = f1 = 0
    
    logger.info(f"\nHotspot Detection Metrics:")
    logger.info(f"  Precision: {precision:.4f}")
    logger.info(f"  Recall:    {recall:.4f}")
    logger.info(f"  F1-Score:  {f1:.4f}")
    
    results = {
        'n_hotspots': n_hotspots,
        'n_in_hotspots': int(n_in_hotspots),
        'hotspot_coverage': float(n_in_hotspots / len(df)),
        'n_anomalies': int(n_anomalies),
        'anomaly_ratio': float(n_anomalies / len(df)),
        'hotspot_precision': float(precision),
        'hotspot_recall': float(recall),
        'hotspot_f1': float(f1)
    }
    
    return results


# ============================================================================
# VISUALIZATION
# ============================================================================

def create_visualizations(model: HotspotPredictor, df: pd.DataFrame, save_dir: Path):
    """Create visualizations."""
    logger.info("Creating visualizations...")
    
    # Get predictions
    hotspot_labels = model.predict_hotspots(df)
    anomaly_labels, anomaly_scores = model.predict_anomalies(df)
    
    fig = plt.figure(figsize=(16, 12))
    
    # 1. Hotspot map
    ax1 = plt.subplot(2, 2, 1)
    scatter = ax1.scatter(
        df['longitude'], df['latitude'],
        c=hotspot_labels, cmap='tab10',
        alpha=0.6, s=20
    )
    
    # Plot cluster centers
    for label, center in model.dbscan_detector.cluster_centers.items():
        ax1.plot(center[1], center[0], 'r*', markersize=20, markeredgecolor='black')
        ax1.text(center[1], center[0], f'H{label}', fontsize=10, fontweight='bold')
    
    ax1.set_xlabel('Longitude', fontsize=12)
    ax1.set_ylabel('Latitude', fontsize=12)
    ax1.set_title('Hotspot Detection (DBSCAN)', fontsize=14, fontweight='bold')
    plt.colorbar(scatter, ax=ax1, label='Cluster')
    ax1.grid(alpha=0.3)
    
    # 2. Anomaly map
    ax2 = plt.subplot(2, 2, 2)
    colors = ['blue' if label == 1 else 'red' for label in anomaly_labels]
    ax2.scatter(
        df['longitude'], df['latitude'],
        c=colors, alpha=0.5, s=20
    )
    ax2.set_xlabel('Longitude', fontsize=12)
    ax2.set_ylabel('Latitude', fontsize=12)
    ax2.set_title('Anomaly Detection (Isolation Forest)', fontsize=14, fontweight='bold')
    ax2.legend(['Normal', 'Anomaly'])
    ax2.grid(alpha=0.3)
    
    # 3. Hotspot sizes
    ax3 = plt.subplot(2, 2, 3)
    hotspot_info = model.get_hotspot_info()
    if hotspot_info:
        sizes = [info['size'] for info in hotspot_info.values()]
        labels_list = list(hotspot_info.keys())
        ax3.bar(range(len(sizes)), sizes)
        ax3.set_xticks(range(len(sizes)))
        ax3.set_xticklabels([f'H{l}' for l in labels_list])
        ax3.set_xlabel('Hotspot', fontsize=12)
        ax3.set_ylabel('Number of Incidents', fontsize=12)
        ax3.set_title('Hotspot Sizes', fontsize=14, fontweight='bold')
        ax3.grid(axis='y', alpha=0.3)
    
    # 4. Anomaly score distribution
    ax4 = plt.subplot(2, 2, 4)
    ax4.hist(anomaly_scores[anomaly_labels == 1], bins=30, alpha=0.7, label='Normal')
    ax4.hist(anomaly_scores[anomaly_labels == -1], bins=30, alpha=0.7, label='Anomaly')
    ax4.set_xlabel('Anomaly Score', fontsize=12)
    ax4.set_ylabel('Frequency', fontsize=12)
    ax4.set_title('Anomaly Score Distribution', fontsize=14, fontweight='bold')
    ax4.legend()
    ax4.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_dir / 'hotspot_predictor_evaluation.png', dpi=300)
    plt.close()
    
    logger.info(f"Saved visualizations to {save_dir}/hotspot_predictor_evaluation.png")


# ============================================================================
# MODEL PERSISTENCE
# ============================================================================

def save_model(model: HotspotPredictor, metadata: Dict, save_dir: Path):
    """Save model artifacts."""
    logger.info("Saving model artifacts...")
    
    # Save DBSCAN model
    joblib.dump(model.dbscan_detector, save_dir / 'hotspot_dbscan.pkl')
    
    # Save Isolation Forest model
    joblib.dump(model.anomaly_detector, save_dir / 'hotspot_isolation_forest.pkl')
    
    # Save hotspot info - convert keys to strings for JSON serialization
    hotspot_info = model.get_hotspot_info()
    hotspot_info_serializable = {str(k): v for k, v in hotspot_info.items()}
    
    with open(save_dir / 'hotspot_info.json', 'w') as f:
        json.dump(hotspot_info_serializable, f, indent=2, default=str)
    
    # Save metadata
    with open(save_dir / 'hotspot_predictor_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    
    logger.info(f"Model artifacts saved to {save_dir}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    logger.info("=" * 70)
    logger.info("ARIA HOTSPOT PREDICTOR TRAINING")
    logger.info("=" * 70)
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    try:
        # Load data
        data_loader = HotspotDataLoader(DATA_DIR / 'incidents_processed.csv')
        df = data_loader.load_data()
        
        # Train model
        model = HotspotPredictor()
        training_results = model.fit(df)
        
        # Evaluate
        evaluation_results = evaluate_model(model, df)
        
        # Visualizations
        create_visualizations(model, df, REPORTS_DIR)
        
        # Save model
        # Convert all nested dict keys to strings for JSON serialization
        def convert_keys_to_str(obj):
            """Recursively convert dict keys to strings."""
            if isinstance(obj, dict):
                return {str(k): convert_keys_to_str(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_keys_to_str(item) for item in obj]
            else:
                return obj
        
        metadata = {
            'model_type': 'Hotspot Predictor (DBSCAN + Isolation Forest)',
            'training_date': datetime.now().isoformat(),
            'n_incidents': len(df),
            'training_results': convert_keys_to_str(training_results),
            'evaluation_results': convert_keys_to_str(evaluation_results),
            'dbscan_params': DBSCAN_PARAMS,
            'isolation_forest_params': ISOLATION_FOREST_PARAMS,
            'hotspot_info': convert_keys_to_str(model.get_hotspot_info())
        }
        
        save_model(model, metadata, MODELS_DIR)
        
        # Final summary
        duration = time.time() - start_time
        
        logger.info("=" * 70)
        logger.info("TRAINING COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Hotspots detected: {evaluation_results['n_hotspots']}")
        logger.info(f"Hotspot Precision: {evaluation_results['hotspot_precision']:.4f}")
        
        if evaluation_results['hotspot_precision'] >= 0.7:
            logger.info("✅ Target precision (>0.7) ACHIEVED!")
        else:
            logger.warning(f"⚠️  Target not met. Got {evaluation_results['hotspot_precision']:.4f}, need >0.7")
        
        logger.info(f"\nModel saved to: {MODELS_DIR}")
        logger.info("=" * 70)
        
        return 0
        
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
