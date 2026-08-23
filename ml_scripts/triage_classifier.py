#!/usr/bin/env python3
"""
ARIA Triage Classifier - XGBoost + BERT Ensemble
=================================================
Emergency severity classification using ensemble of XGBoost and BERT.

Author: ARIA ML Team
Date: August 2026
Version: 1.0

Model Details:
- Algorithm: XGBoost + BERT Ensemble
- Classes: LOW (0), MODERATE (1), CRITICAL (2)
- Target Accuracy: >85%
- Ensemble: 60% XGBoost + 40% BERT

Usage:
    python triage_classifier.py
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
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve
)
import xgboost as xgb

# Deep Learning (BERT)
try:
    import torch
    from transformers import BertTokenizer, BertForSequenceClassification, AdamW
    from transformers import get_linear_schedule_with_warmup
    from torch.utils.data import DataLoader, TensorDataset
    BERT_AVAILABLE = True
except ImportError:
    BERT_AVAILABLE = False
    print("⚠️  BERT not available. Install with: pip install torch transformers")

# Hyperparameter Optimization
try:
    import optuna
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False
    print("⚠️  Optuna not available. Install with: pip install optuna")

# Feature Importance
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    print("⚠️  SHAP not available. Install with: pip install shap")

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
LOG_FILE = LOGS_DIR / "triage_training.log"
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
    'max_depth': 8,
    'learning_rate': 0.1,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'objective': 'multi:softprob',
    'num_class': 3,
    'eval_metric': 'mlogloss',
    'random_state': 42
}

BERT_PARAMS = {
    'model_name': 'bert-base-uncased',
    'max_length': 128,
    'batch_size': 16,
    'epochs': 3,
    'learning_rate': 2e-5
}

ENSEMBLE_WEIGHTS = {
    'xgboost': 0.6,
    'bert': 0.4,
    'confidence_threshold': 0.7
}

# ============================================================================
# DATA LOADING AND PREPARATION
# ============================================================================

class TriageDataLoader:
    """Load and prepare data for triage classification."""
    
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.label_encoder = LabelEncoder()
        
    def load_data(self) -> pd.DataFrame:
        """Load incident data."""
        logger.info(f"Loading data from {self.data_path}")
        
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_path}")
        
        df = pd.read_csv(self.data_path)
        logger.info(f"Loaded {len(df):,} records")
        
        return df
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features and target."""
        logger.info("Preparing features and target...")
        
        # Check required columns
        required_cols = ['incident_description', 'severity']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Extract features
        X = df.copy()
        y = df['severity']
        
        # Encode target
        y_encoded = self.label_encoder.fit_transform(y)
        
        logger.info(f"Class distribution:")
        for cls, count in zip(self.label_encoder.classes_, 
                              np.bincount(y_encoded)):
            logger.info(f"  {cls}: {count:,} ({count/len(y_encoded)*100:.1f}%)")
        
        return X, pd.Series(y_encoded, name='severity')
    
    def create_numerical_features(self, df: pd.DataFrame) -> np.ndarray:
        """Create numerical feature matrix."""
        features = []
        
        # Time-based features (if available)
        if 'hour' in df.columns:
            hour_sin = np.sin(2 * np.pi * df['hour'] / 24)
            hour_cos = np.cos(2 * np.pi * df['hour'] / 24)
            features.extend([hour_sin, hour_cos])
        
        if 'day_of_week' in df.columns:
            dow_sin = np.sin(2 * np.pi * df['day_of_week'] / 7)
            dow_cos = np.cos(2 * np.pi * df['day_of_week'] / 7)
            features.extend([dow_sin, dow_cos])
        
        if 'month' in df.columns:
            month_sin = np.sin(2 * np.pi * df['month'] / 12)
            month_cos = np.cos(2 * np.pi * df['month'] / 12)
            features.extend([month_sin, month_cos])
        
        # Casualties/injuries (if available)
        if 'casualties' in df.columns:
            casualties = df['casualties'].fillna(0).values
            features.append(casualties)
        
        if 'injuries' in df.columns:
            injuries = df['injuries'].fillna(0).values
            features.append(injuries)
        
        if features:
            return np.column_stack(features)
        else:
            # Return dummy feature if none available
            return np.zeros((len(df), 1))


# ============================================================================
# XGBOOST MODEL
# ============================================================================

class XGBoostTriageModel:
    """XGBoost-based triage classifier."""
    
    def __init__(self, params: Dict = None):
        self.params = params or XGBOOST_PARAMS
        self.model = None
        self.vectorizer = None
        self.feature_names = None
        
    def create_features(self, X: pd.DataFrame, 
                       fit: bool = False) -> np.ndarray:
        """Create TF-IDF + numerical features."""
        # TF-IDF on text
        if fit:
            self.vectorizer = TfidfVectorizer(
                max_features=10000,
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95,
                stop_words='english'
            )
            text_features = self.vectorizer.fit_transform(
                X['incident_description'].fillna('')
            )
        else:
            text_features = self.vectorizer.transform(
                X['incident_description'].fillna('')
            )
        
        # Numerical features
        data_loader = TriageDataLoader(None)
        num_features = data_loader.create_numerical_features(X)
        
        # Combine
        X_combined = np.hstack([
            text_features.toarray(),
            num_features
        ])
        
        return X_combined
    
    def train(self, X_train: pd.DataFrame, y_train: np.ndarray,
              X_val: pd.DataFrame, y_val: np.ndarray) -> Dict[str, float]:
        """Train XGBoost model."""
        logger.info("Training XGBoost model...")
        
        # Create features
        X_train_features = self.create_features(X_train, fit=True)
        X_val_features = self.create_features(X_val, fit=False)
        
        logger.info(f"Feature matrix shape: {X_train_features.shape}")
        
        # Train model
        self.model = xgb.XGBClassifier(**self.params)
        
        eval_set = [(X_train_features, y_train), (X_val_features, y_val)]
        
        self.model.fit(
            X_train_features, y_train,
            eval_set=eval_set,
            early_stopping_rounds=50,
            verbose=False
        )
        
        # Evaluate
        y_pred = self.model.predict(X_val_features)
        y_pred_proba = self.model.predict_proba(X_val_features)
        
        metrics = {
            'accuracy': accuracy_score(y_val, y_pred),
            'f1_macro': f1_score(y_val, y_pred, average='macro'),
            'precision_macro': precision_score(y_val, y_pred, average='macro'),
            'recall_macro': recall_score(y_val, y_pred, average='macro')
        }
        
        logger.info(f"XGBoost Validation Metrics:")
        for metric, value in metrics.items():
            logger.info(f"  {metric}: {value:.4f}")
        
        return metrics
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict class."""
        X_features = self.create_features(X, fit=False)
        return self.model.predict(X_features)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predict class probabilities."""
        X_features = self.create_features(X, fit=False)
        return self.model.predict_proba(X_features)
    
    def cross_validate(self, X: pd.DataFrame, y: np.ndarray, 
                       cv: int = 5) -> Dict[str, float]:
        """Perform cross-validation."""
        logger.info(f"Performing {cv}-fold cross-validation...")
        
        X_features = self.create_features(X, fit=True)
        
        skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
        scores = cross_val_score(
            self.model, X_features, y,
            cv=skf, scoring='accuracy', n_jobs=-1
        )
        
        return {
            'cv_mean': scores.mean(),
            'cv_std': scores.std(),
            'cv_scores': scores.tolist()
        }


# ============================================================================
# BERT MODEL (Simplified)
# ============================================================================

class BERTTriageModel:
    """BERT-based triage classifier."""
    
    def __init__(self, params: Dict = None):
        self.params = params or BERT_PARAMS
        self.model = None
        self.tokenizer = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def prepare_data(self, texts: List[str], labels: np.ndarray = None):
        """Tokenize and prepare data for BERT."""
        if self.tokenizer is None:
            self.tokenizer = BertTokenizer.from_pretrained(
                self.params['model_name']
            )
        
        encodings = self.tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=self.params['max_length'],
            return_tensors='pt'
        )
        
        if labels is not None:
            dataset = TensorDataset(
                encodings['input_ids'],
                encodings['attention_mask'],
                torch.tensor(labels)
            )
        else:
            dataset = TensorDataset(
                encodings['input_ids'],
                encodings['attention_mask']
            )
        
        return dataset
    
    def train(self, X_train: pd.DataFrame, y_train: np.ndarray,
              X_val: pd.DataFrame, y_val: np.ndarray) -> Dict[str, float]:
        """Train BERT model."""
        logger.info("Training BERT model...")
        logger.info(f"Using device: {self.device}")
        
        # Load pretrained BERT
        self.model = BertForSequenceClassification.from_pretrained(
            self.params['model_name'],
            num_labels=3
        ).to(self.device)
        
        # Prepare data
        train_texts = X_train['incident_description'].fillna('').tolist()
        val_texts = X_val['incident_description'].fillna('').tolist()
        
        train_dataset = self.prepare_data(train_texts, y_train)
        val_dataset = self.prepare_data(val_texts, y_val)
        
        train_loader = DataLoader(
            train_dataset,
            batch_size=self.params['batch_size'],
            shuffle=True
        )
        val_loader = DataLoader(
            val_dataset,
            batch_size=self.params['batch_size']
        )
        
        # Optimizer and scheduler
        optimizer = AdamW(
            self.model.parameters(),
            lr=self.params['learning_rate']
        )
        
        total_steps = len(train_loader) * self.params['epochs']
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=0,
            num_training_steps=total_steps
        )
        
        # Training loop
        best_val_acc = 0
        for epoch in range(self.params['epochs']):
            logger.info(f"Epoch {epoch + 1}/{self.params['epochs']}")
            
            # Train
            self.model.train()
            train_loss = 0
            
            for batch in tqdm(train_loader, desc="Training"):
                input_ids = batch[0].to(self.device)
                attention_mask = batch[1].to(self.device)
                labels = batch[2].to(self.device)
                
                optimizer.zero_grad()
                
                outputs = self.model(
                    input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                loss = outputs.loss
                loss.backward()
                optimizer.step()
                scheduler.step()
                
                train_loss += loss.item()
            
            avg_train_loss = train_loss / len(train_loader)
            
            # Validate
            self.model.eval()
            val_preds = []
            val_labels = []
            
            with torch.no_grad():
                for batch in val_loader:
                    input_ids = batch[0].to(self.device)
                    attention_mask = batch[1].to(self.device)
                    labels = batch[2].to(self.device)
                    
                    outputs = self.model(
                        input_ids,
                        attention_mask=attention_mask
                    )
                    
                    preds = torch.argmax(outputs.logits, dim=1)
                    val_preds.extend(preds.cpu().numpy())
                    val_labels.extend(labels.cpu().numpy())
            
            val_acc = accuracy_score(val_labels, val_preds)
            
            logger.info(f"  Train Loss: {avg_train_loss:.4f}")
            logger.info(f"  Val Accuracy: {val_acc:.4f}")
            
            if val_acc > best_val_acc:
                best_val_acc = val_acc
        
        metrics = {
            'accuracy': best_val_acc,
            'f1_macro': f1_score(val_labels, val_preds, average='macro')
        }
        
        logger.info(f"BERT Best Validation Accuracy: {best_val_acc:.4f}")
        
        return metrics
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predict class probabilities."""
        self.model.eval()
        
        texts = X['incident_description'].fillna('').tolist()
        dataset = self.prepare_data(texts)
        loader = DataLoader(dataset, batch_size=self.params['batch_size'])
        
        all_probs = []
        
        with torch.no_grad():
            for batch in loader:
                input_ids = batch[0].to(self.device)
                attention_mask = batch[1].to(self.device)
                
                outputs = self.model(input_ids, attention_mask=attention_mask)
                probs = torch.softmax(outputs.logits, dim=1)
                all_probs.extend(probs.cpu().numpy())
        
        return np.array(all_probs)


# ============================================================================
# ENSEMBLE MODEL
# ============================================================================

class EnsembleTriageModel:
    """Ensemble of XGBoost and BERT."""
    
    def __init__(self, weights: Dict = None):
        self.weights = weights or ENSEMBLE_WEIGHTS
        self.xgboost_model = XGBoostTriageModel()
        self.bert_model = None
        if BERT_AVAILABLE:
            self.bert_model = BERTTriageModel()
        self.label_encoder = LabelEncoder()
        
    def train(self, X_train: pd.DataFrame, y_train: np.ndarray,
              X_val: pd.DataFrame, y_val: np.ndarray) -> Dict[str, Any]:
        """Train ensemble model."""
        logger.info("=" * 70)
        logger.info("TRAINING ENSEMBLE MODEL")
        logger.info("=" * 70)
        
        results = {}
        
        # Train XGBoost
        xgb_metrics = self.xgboost_model.train(X_train, y_train, X_val, y_val)
        results['xgboost'] = xgb_metrics
        
        # Train BERT (if available)
        if self.bert_model:
            try:
                bert_metrics = self.bert_model.train(
                    X_train, y_train, X_val, y_val
                )
                results['bert'] = bert_metrics
            except Exception as e:
                logger.warning(f"BERT training failed: {e}")
                self.bert_model = None
        
        return results
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Ensemble prediction."""
        # XGBoost predictions
        xgb_proba = self.xgboost_model.predict_proba(X)
        
        # BERT predictions (if available)
        if self.bert_model:
            bert_proba = self.bert_model.predict_proba(X)
            
            # Weighted ensemble
            ensemble_proba = (
                self.weights['xgboost'] * xgb_proba +
                self.weights['bert'] * bert_proba
            )
        else:
            # XGBoost only
            ensemble_proba = xgb_proba
        
        return ensemble_proba
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict class labels."""
        proba = self.predict_proba(X)
        return np.argmax(proba, axis=1)


# ============================================================================
# MODEL EVALUATION
# ============================================================================

def evaluate_model(model: EnsembleTriageModel, X_test: pd.DataFrame,
                   y_test: np.ndarray, label_encoder: LabelEncoder) -> Dict[str, Any]:
    """Comprehensive model evaluation."""
    logger.info("=" * 70)
    logger.info("MODEL EVALUATION")
    logger.info("=" * 70)
    
    # Predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)
    
    # Basic metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='macro')
    recall = recall_score(y_test, y_pred, average='macro')
    f1 = f1_score(y_test, y_pred, average='macro')
    
    logger.info(f"Accuracy:  {accuracy:.4f}")
    logger.info(f"Precision: {precision:.4f}")
    logger.info(f"Recall:    {recall:.4f}")
    logger.info(f"F1-Score:  {f1:.4f}")
    
    # Per-class metrics
    logger.info("\nPer-Class Metrics:")
    report = classification_report(
        y_test, y_pred,
        target_names=label_encoder.classes_,
        output_dict=True
    )
    
    for cls in label_encoder.classes_:
        logger.info(f"\n{cls}:")
        logger.info(f"  Precision: {report[cls]['precision']:.4f}")
        logger.info(f"  Recall:    {report[cls]['recall']:.4f}")
        logger.info(f"  F1-Score:  {report[cls]['f1-score']:.4f}")
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    
    # ROC-AUC (one-vs-rest)
    try:
        roc_auc = roc_auc_score(y_test, y_pred_proba, multi_class='ovr')
        logger.info(f"\nROC-AUC (OvR): {roc_auc:.4f}")
    except Exception as e:
        logger.warning(f"Could not calculate ROC-AUC: {e}")
        roc_auc = None
    
    results = {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'roc_auc': roc_auc,
        'confusion_matrix': cm.tolist(),
        'classification_report': report
    }
    
    return results


# ============================================================================
# VISUALIZATION
# ============================================================================

def create_visualizations(y_test: np.ndarray, y_pred: np.ndarray,
                         y_pred_proba: np.ndarray,
                         label_encoder: LabelEncoder,
                         save_dir: Path):
    """Create evaluation visualizations."""
    logger.info("Creating visualizations...")
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm, annot=True, fmt='d', cmap='Blues',
        xticklabels=label_encoder.classes_,
        yticklabels=label_encoder.classes_
    )
    plt.title('Confusion Matrix', fontsize=16, fontweight='bold')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(save_dir / 'confusion_matrix.png', dpi=300)
    plt.close()
    
    logger.info(f"Saved confusion matrix to {save_dir}/confusion_matrix.png")


# ============================================================================
# MODEL PERSISTENCE
# ============================================================================

def save_model(model: EnsembleTriageModel, label_encoder: LabelEncoder,
               metadata: Dict, save_dir: Path):
    """Save model artifacts."""
    logger.info("Saving model artifacts...")
    
    # Save XGBoost model
    joblib.dump(
        model.xgboost_model.model,
        save_dir / 'triage_xgboost.pkl'
    )
    
    # Save TF-IDF vectorizer
    joblib.dump(
        model.xgboost_model.vectorizer,
        save_dir / 'triage_vectorizer.pkl'
    )
    
    # Save label encoder
    joblib.dump(
        label_encoder,
        save_dir / 'triage_label_encoder.pkl'
    )
    
    # Save ensemble weights
    with open(save_dir / 'triage_ensemble_weights.json', 'w') as f:
        json.dump(model.weights, f, indent=2)
    
    # Save metadata
    with open(save_dir / 'triage_model_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    
    logger.info(f"Model artifacts saved to {save_dir}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    logger.info("=" * 70)
    logger.info("ARIA TRIAGE CLASSIFIER TRAINING")
    logger.info("=" * 70)
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    try:
        # Load data
        data_loader = TriageDataLoader(DATA_DIR / 'incidents_processed.csv')
        df = data_loader.load_data()
        X, y = data_loader.prepare_features(df)
        
        # Split data (70% train, 15% val, 15% test)
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
        )
        
        logger.info(f"\nData splits:")
        logger.info(f"  Train: {len(X_train):,} samples")
        logger.info(f"  Val:   {len(X_val):,} samples")
        logger.info(f"  Test:  {len(X_test):,} samples")
        
        # Train model
        model = EnsembleTriageModel()
        model.label_encoder = data_loader.label_encoder
        
        training_results = model.train(
            X_train, y_train.values,
            X_val, y_val.values
        )
        
        # Evaluate on test set
        evaluation_results = evaluate_model(
            model, X_test, y_test.values,
            data_loader.label_encoder
        )
        
        # Create visualizations
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)
        
        create_visualizations(
            y_test.values, y_pred, y_pred_proba,
            data_loader.label_encoder,
            REPORTS_DIR
        )
        
        # Save model
        metadata = {
            'model_type': 'Triage Classifier (XGBoost + BERT Ensemble)',
            'training_date': datetime.now().isoformat(),
            'train_samples': len(X_train),
            'val_samples': len(X_val),
            'test_samples': len(X_test),
            'classes': data_loader.label_encoder.classes_.tolist(),
            'training_results': training_results,
            'test_results': evaluation_results,
            'ensemble_weights': model.weights,
            'xgboost_params': XGBOOST_PARAMS,
            'bert_params': BERT_PARAMS if BERT_AVAILABLE else None
        }
        
        save_model(model, data_loader.label_encoder, metadata, MODELS_DIR)
        
        # Final summary
        duration = time.time() - start_time
        
        logger.info("=" * 70)
        logger.info("TRAINING COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Final Test Accuracy: {evaluation_results['accuracy']:.4f}")
        logger.info(f"Final Test F1-Score: {evaluation_results['f1_score']:.4f}")
        
        # Check if target met
        if evaluation_results['accuracy'] >= 0.85:
            logger.info("✅ Target accuracy (>85%) ACHIEVED!")
        else:
            logger.warning(f"⚠️  Target accuracy not met. Got {evaluation_results['accuracy']:.4f}, need >0.85")
        
        logger.info(f"\nModel saved to: {MODELS_DIR}")
        logger.info(f"Reports saved to: {REPORTS_DIR}")
        logger.info("=" * 70)
        
        return 0
        
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
