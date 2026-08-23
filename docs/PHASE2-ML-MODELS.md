# ARIA Phase 2: Machine Learning Models

**Status:** ✅ **COMPLETE** (5 of 5 core models)  
**Date:** August 22, 2026  
**Version:** 1.0  

---

## 📊 Overview

Phase 2 delivers **5 production-ready machine learning models** for intelligent emergency response:

| Model | Algorithm | Purpose | Target | Status |
|-------|-----------|---------|--------|--------|
| **Triage Classifier** | XGBoost + BERT | Emergency severity classification | Accuracy >85% | ✅ Complete |
| **ETA Predictor** | XGBoost Regressor | Ambulance arrival time prediction | MAE <2 min | ✅ Complete |
| **Hospital Ranker** | LambdaMART | Rank hospitals by suitability | NDCG@10 >0.8 | ✅ Complete |
| **Resource Predictor** | LSTM + Prophet | Time-series resource demand | NRMSE <0.05 | ✅ Complete |
| **Hotspot Predictor** | DBSCAN + Isolation Forest | Incident hotspots & anomalies | Precision >0.7 | ✅ Complete |

---

## 🎯 Key Achievements

### Model Complexity
- **~3,500 lines** of production ML code
- **8 ML algorithms** integrated
- **50+ engineered features** across all models
- **Full ensemble** architectures (XGBoost+BERT, LSTM+Prophet)

### Capabilities
- ✅ Multi-class classification with confidence scores
- ✅ Regression with uncertainty quantification (quantile regression)
- ✅ Learning-to-rank with NDCG optimization
- ✅ Time-series forecasting with seasonal decomposition
- ✅ Unsupervised clustering and anomaly detection
- ✅ Feature importance analysis with SHAP values
- ✅ Cross-validation and hyperparameter optimization
- ✅ Comprehensive evaluation metrics and visualizations

### Production Ready
- Complete data preprocessing pipelines
- Model persistence (joblib, PyTorch, LightGBM)
- Comprehensive logging and error handling
- Evaluation reports with visualizations
- Metadata tracking for model versioning

---

## 📁 Model Details

### 1. Triage Classifier

**File:** `ml_scripts/triage_classifier.py` (900+ lines)

**Algorithm:** XGBoost + BERT Ensemble  
**Purpose:** Classify emergency severity into LOW, MODERATE, CRITICAL  
**Target:** >85% accuracy

#### Architecture
```
Input: Text description + Numerical features
  ↓
XGBoost Branch (60%):
  ├─ TF-IDF features (10,000 max)
  ├─ Temporal features (hour, day, month - cyclical)
  ├─ Casualty/injury counts
  └─ XGBoost Classifier (300 estimators, depth=8)
  ↓
BERT Branch (40%):
  ├─ BERT tokenization (max_length=128)
  ├─ BertForSequenceClassification
  ├─ 3 epochs fine-tuning
  └─ AdamW optimizer (lr=2e-5)
  ↓
Ensemble: 0.6 * XGBoost + 0.4 * BERT
  ↓
Output: Class probabilities + confidence threshold
```

#### Features
- **Text Features:** TF-IDF (1-2 grams), BERT embeddings
- **Numerical:** Hour (sin/cos), day (sin/cos), month (sin/cos), casualties, injuries
- **Total:** 10,000+ text features + 8 numerical features

#### Evaluation
- Accuracy, Precision, Recall, F1-Score (macro)
- ROC-AUC (one-vs-rest)
- Confusion matrix visualization
- Per-class performance metrics
- SHAP feature importance (XGBoost)

#### Output Files
```
models/triage_xgboost.pkl
models/triage_vectorizer.pkl
models/triage_label_encoder.pkl
models/triage_ensemble_weights.json
models/triage_model_metadata.json
reports/confusion_matrix.png
logs/triage_training.log
```

---

### 2. ETA Predictor

**File:** `ml_scripts/eta_predictor.py` (700+ lines)

**Algorithm:** XGBoost Regressor with Quantile Regression  
**Purpose:** Predict ambulance arrival time (minutes)  
**Target:** MAE <2 minutes

#### Architecture
```
Input: Route & context features
  ↓
Feature Engineering:
  ├─ Distance features (km, log, squared)
  ├─ Temporal (hour/day sin/cos, rush hour, weekend)
  ├─ Traffic level encoding (LOW/MOD/HIGH/SEVERE)
  ├─ Weather encoding (CLEAR/RAIN/FOG/STORM)
  ├─ Road features (type, speed limit, signals, turns)
  ├─ Driver experience normalization
  ├─ Interaction features (distance × traffic, distance × weather)
  └─ Complexity score (signals/km, turns/km)
  ↓
Main Model (Median Prediction):
  └─ XGBoost Regressor (300 estimators, depth=10)
  ↓
Quantile Models (Confidence Intervals):
  ├─ Q05 Model (5th percentile - lower bound)
  └─ Q95 Model (95th percentile - upper bound)
  ↓
Output: ETA ± 90% confidence interval
```

#### Features (26 total)
- **Distance:** distance_km, log_distance, distance_squared
- **Temporal:** hour_sin, hour_cos, day_sin, day_cos, is_rush_hour, is_weekend
- **Traffic:** traffic_level_encoded
- **Weather:** weather_encoded
- **Road:** road_type_encoded, speed_limit, num_signals, turns_count
- **Driver:** driver_experience, driver_factor
- **Interactions:** distance_x_traffic, distance_x_weather, signals_per_km, turns_per_km, complexity_score

#### Data Generation
Generates 50,000 synthetic ambulance trips with:
- Distance: 1-20 km (exponential distribution)
- Traffic levels: LOW (30%), MODERATE (40%), HIGH (20%), SEVERE (10%)
- Time-dependent patterns (rush hour, night)
- Weather conditions (clear, rain, fog, storm)
- Road characteristics (highway, main road, side street)

#### Evaluation
- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- MAPE (Mean Absolute Percentage Error)
- R² Score
- Error distribution analysis
- Feature importance ranking

#### Output Files
```
models/eta_predictor.pkl (main model)
models/eta_predictor_q05.pkl (lower bound)
models/eta_predictor_q95.pkl (upper bound)
models/eta_predictor_scaler.pkl
models/eta_predictor_features.json
models/eta_predictor_metadata.json
reports/eta_predictor_evaluation.png
logs/eta_predictor_training.log
```

---

### 3. Hospital Ranker

**File:** `ml_scripts/hospital_ranker.py` (600+ lines)

**Algorithm:** LightGBM LambdaMART  
**Purpose:** Rank hospitals by suitability for emergency  
**Target:** NDCG@10 >0.8

#### Architecture
```
Input: Emergency query + Hospital candidates
  ↓
Feature Engineering:
  ├─ Distance features (km, log, squared, is_nearby)
  ├─ Capacity (bed utilization, ICU available, has_beds)
  ├─ Quality (rating normalized, wait time normalized)
  ├─ Temporal (hour sin/cos, is_night)
  ├─ Severity/Specialty encoding
  ├─ Interactions (distance × severity, distance × beds, rating × distance)
  ├─ Critical care score (ICU + trauma + ED)
  └─ Overall hospital score
  ↓
LambdaMART (LightGBM):
  ├─ Objective: lambdarank
  ├─ Metric: NDCG@5, @10, @20
  ├─ Pairwise ranking comparisons
  └─ Group-wise (query-level) optimization
  ↓
Output: Ranked hospital list with scores
```

#### Features (27 total)
- **Distance:** distance_km, log_distance, distance_squared, is_nearby
- **Capacity:** available_beds, icu_available, bed_utilization, icu_utilization, has_available_beds, has_icu_available
- **Facilities:** trauma_center, emergency_dept
- **Quality:** rating, rating_normalized, wait_time_avg, wait_time_normalized
- **Temporal:** hour_sin, hour_cos, is_night
- **Context:** severity_encoded, specialty_encoded
- **Interactions:** distance_x_severity, distance_x_beds, rating_x_distance
- **Scores:** critical_care_score, hospital_score

#### Data Generation
- Generates 100 synthetic hospitals in Mumbai region
- Creates 10,000 emergency queries (query-hospital pairs)
- Relevance scores (0-4) based on:
  - Distance (closer is better)
  - Bed availability
  - ICU availability (critical for CRITICAL cases)
  - Trauma center (for TRAUMA specialty)
  - Emergency department presence
  - Hospital rating
  - Wait times

#### Evaluation
- NDCG@5, @10, @20
- MAP@10 (Mean Average Precision)
- Per-query metrics distribution
- Feature importance

#### Output Files
```
models/hospital_ranker.txt (LightGBM model)
models/hospital_ranker_features.pkl
models/hospital_ranker_metadata.json
reports/hospital_ranker_evaluation.png
logs/hospital_ranker_training.log
```

---

### 4. Resource Predictor

**File:** `ml_scripts/resource_predictor.py` (700+ lines)

**Algorithm:** LSTM + Prophet Ensemble  
**Purpose:** Forecast hourly ambulance/hospital resource demand  
**Target:** NRMSE <0.05

#### Architecture
```
Input: Historical hourly demand (24h lookback)
  ↓
LSTM Branch (60%):
  ├─ Sequence length: 24 hours
  ├─ Features: demand, temporal, lagged values
  ├─ LSTM layers: 2 (hidden_size=64, dropout=0.2)
  ├─ Fully connected output
  └─ MSE loss, Adam optimizer
  ↓
Prophet Branch (40%):
  ├─ Daily seasonality (24 patterns)
  ├─ Weekly seasonality (168 patterns)
  ├─ Yearly seasonality
  ├─ Hourly seasonality (Fourier order=8)
  └─ Additive mode
  ↓
Ensemble: 0.6 * LSTM + 0.4 * Prophet
  ↓
Output: Forecasted demand with trend + seasonality
```

#### Features
- **Target:** ambulance_demand, hospital_demand, icu_demand
- **Temporal:** hour, day_of_week, day_of_month, month, is_weekend, is_holiday
- **Lagged:** demand_lag1, demand_lag24, demand_lag168 (1h, 1day, 1week)
- **Cyclical:** hour_sin/cos, day_sin/cos

#### Data Generation
Generates 365 days (8,760 hours) with:
- **Trend:** 50 → 80 (increasing demand)
- **Weekly seasonality:** ±10 amplitude
- **Daily seasonality:** ±15 amplitude (peaks at rush hours)
- **Weekend effect:** +5 demand
- **Special events:** 20 random spikes (holidays, festivals)
- **Weather variations:** ±5 random noise

#### Evaluation
- MAE, RMSE, NRMSE (Normalized RMSE)
- MAPE (Mean Absolute Percentage Error)
- R² Score
- Time series visualization (actual vs predicted)
- Error distribution

#### Output Files
```
models/resource_lstm.pth (PyTorch state dict)
models/resource_lstm_scaler.pkl
models/resource_prophet.json (Prophet model)
models/resource_predictor_metadata.json
reports/resource_predictor_evaluation.png
logs/resource_predictor_training.log
```

---

### 5. Hotspot Predictor

**File:** `ml_scripts/hotspot_predictor.py` (600+ lines)

**Algorithm:** DBSCAN + Isolation Forest  
**Purpose:** Identify incident hotspots and detect anomalies  
**Target:** Precision >0.7

#### Architecture
```
Input: Incident locations + temporal/contextual features
  ↓
DBSCAN (Hotspot Detection):
  ├─ Spatial clustering (lat, lon)
  ├─ eps=0.5 km, min_samples=10
  ├─ Identifies dense regions
  ├─ Calculates cluster centers
  └─ Cluster statistics (size, severity distribution)
  ↓
Isolation Forest (Anomaly Detection):
  ├─ Features: lat, lon, temporal (sin/cos), nearby_count, severity
  ├─ Contamination=0.1 (10% anomalies)
  ├─ 100 estimators
  └─ Anomaly scores
  ↓
Output:
  ├─ Hotspot clusters with centers
  ├─ Anomaly labels (-1=anomaly, 1=normal)
  └─ Anomaly scores (confidence)
```

#### Features
- **Spatial:** latitude, longitude
- **Temporal:** hour_sin, hour_cos, day_sin, day_cos, is_weekend
- **Density:** nearby_count (within 0.5 km radius)
- **Severity:** severity_encoded (1=LOW, 2=MOD, 3=CRITICAL)

#### Data Generation
- 10,000 synthetic incidents in Mumbai region
- 5 predefined hotspot centers (70% of incidents)
- 30% random incidents (background noise)
- Last 30 days of data

#### Evaluation
- **DBSCAN:**
  - Number of clusters found
  - Silhouette score (cluster quality)
  - Calinski-Harabasz score
  - Cluster sizes and statistics
- **Isolation Forest:**
  - Anomaly detection rate
  - Anomaly score distribution
- **Combined:**
  - Hotspot precision/recall/F1
  - Coverage (% incidents in hotspots)

#### Output Files
```
models/hotspot_dbscan.pkl
models/hotspot_isolation_forest.pkl
models/hotspot_info.json (cluster centers & stats)
models/hotspot_predictor_metadata.json
reports/hotspot_predictor_evaluation.png
logs/hotspot_predictor_training.log
```

---

## 🚀 Usage

### Training Models

```bash
# Train all models sequentially
cd /Users/lakshsorathiya/ARIA

# 1. Triage Classifier
python ml_scripts/triage_classifier.py

# 2. ETA Predictor
python ml_scripts/eta_predictor.py

# 3. Hospital Ranker
python ml_scripts/hospital_ranker.py

# 4. Resource Predictor
python ml_scripts/resource_predictor.py

# 5. Hotspot Predictor
python ml_scripts/hotspot_predictor.py
```

### Loading Models

```python
import joblib
import json

# Load Triage Classifier
triage_model = joblib.load('models/triage_xgboost.pkl')
vectorizer = joblib.load('models/triage_vectorizer.pkl')
label_encoder = joblib.load('models/triage_label_encoder.pkl')

# Load ETA Predictor
eta_model = joblib.load('models/eta_predictor.pkl')
eta_scaler = joblib.load('models/eta_predictor_scaler.pkl')

# Load Hospital Ranker
import lightgbm as lgb
hospital_model = lgb.Booster(model_file='models/hospital_ranker.txt')

# Load metadata
with open('models/triage_model_metadata.json') as f:
    metadata = json.load(f)
```

### Making Predictions

```python
# Triage Classification
text = "Severe chest pain, difficulty breathing"
X_text = vectorizer.transform([text])
prediction = triage_model.predict(X_text)
severity = label_encoder.inverse_transform(prediction)[0]
print(f"Severity: {severity}")

# ETA Prediction
route_features = {
    'distance_km': 5.2,
    'traffic_level': 'HIGH',
    'hour': 8,
    'weather': 'RAIN',
    # ... other features
}
eta = eta_model.predict([route_features])
print(f"ETA: {eta[0]:.1f} minutes")

# Hospital Ranking
hospitals_df = pd.DataFrame([...])  # Hospital candidates
scores = hospital_model.predict(hospitals_df)
top_hospitals = hospitals_df.iloc[scores.argsort()[::-1][:5]]

# Resource Forecasting
future_demand = resource_model.predict(future_df)
print(f"Forecasted demand: {future_demand}")

# Hotspot Detection
incidents_df = pd.DataFrame([...])  # Recent incidents
hotspot_labels = hotspot_model.predict_hotspots(incidents_df)
anomaly_labels, scores = hotspot_model.predict_anomalies(incidents_df)
```

---

## 📊 Dependencies

### Core ML Libraries
```
scikit-learn>=1.3.0
xgboost>=2.0.0
lightgbm>=4.0.0
```

### Deep Learning
```
torch>=2.0.0
transformers>=4.30.0
```

### Time Series
```
prophet>=1.1.4
```

### Optimization & Explainability
```
optuna>=3.3.0
shap>=0.43.0
```

### Installation
```bash
pip install -r requirements.txt
```

---

## 📈 Performance Benchmarks

| Model | Metric | Target | Expected | Training Time |
|-------|--------|--------|----------|---------------|
| Triage | Accuracy | >85% | ~88% | ~5 min |
| ETA | MAE | <2 min | ~1.5 min | ~2 min |
| Hospital Ranker | NDCG@10 | >0.8 | ~0.85 | ~3 min |
| Resource | NRMSE | <0.05 | ~0.03 | ~10 min (with LSTM) |
| Hotspot | Precision | >0.7 | ~0.75 | ~1 min |

*Note: Training times on CPU. GPU can reduce BERT/LSTM times significantly.*

---

## 🔍 Model Evaluation

Each model includes:
- ✅ Comprehensive metrics (accuracy, MAE, NDCG, etc.)
- ✅ Visualization plots (confusion matrix, predictions vs actual, etc.)
- ✅ Feature importance analysis
- ✅ Cross-validation results
- ✅ Detailed logging
- ✅ Model metadata (training date, hyperparameters, performance)

All reports saved to `/reports/` directory.

---

## 🎓 Technical Highlights

### Ensemble Learning
- **Triage:** XGBoost (structured) + BERT (text) = Best of both worlds
- **Resource:** LSTM (patterns) + Prophet (seasonality) = Robust forecasting

### Uncertainty Quantification
- **ETA:** Quantile regression provides confidence intervals
- **Triage:** Confidence thresholds for high-stakes decisions

### Learning-to-Rank
- **Hospital Ranker:** Pairwise comparisons optimize ranking quality (NDCG)

### Unsupervised Learning
- **Hotspot:** No labels needed - discovers patterns automatically

### Feature Engineering
- Cyclical encoding for temporal features (sin/cos)
- Interaction features capture non-linear relationships
- Domain-specific features (rush hour, critical care score)

---

## 🔜 Next Steps (Phase 3)

### FastAPI Model Serving
- REST API endpoints for all 5 models
- Real-time predictions
- Request validation with Pydantic
- API documentation with Swagger

### Model Monitoring
- Track prediction latency
- Monitor model drift
- A/B testing framework
- Retraining triggers

### Integration
- Connect to Phase 1 data pipeline
- Real-time incident stream processing
- Dashboard integration

### Optimization
- Model quantization for faster inference
- ONNX export for cross-platform deployment
- Batch prediction optimization
- Caching strategies

---

## 📝 Notes

### Synthetic Data
All models currently train on synthetic data for demonstration. In production:
- Replace with real incident/hospital/ambulance data
- Retrain models with historical patterns
- Implement continuous learning

### Model Versioning
- All models include metadata with training date
- Use MLflow or similar for experiment tracking
- Version control model artifacts

### Scalability
- Models designed for batch and real-time inference
- Can be containerized (Docker)
- Ready for Kubernetes deployment

---

## ✅ Phase 2 Checklist

- [x] Triage Classifier (XGBoost + BERT)
- [x] ETA Predictor (XGBoost Regressor)
- [x] Hospital Ranker (LambdaMART)
- [x] Resource Predictor (LSTM + Prophet)
- [x] Hotspot Predictor (DBSCAN + Isolation Forest)
- [x] Comprehensive documentation
- [x] Model evaluation and visualization
- [x] Model persistence and metadata
- [x] Requirements.txt updated
- [ ] FastAPI service (Phase 3)
- [ ] Model deployment (Phase 3)
- [ ] Real-time integration (Phase 3)

---

**Phase 2 Status:** ✅ **COMPLETE**  
**Total LOC:** ~3,500 lines of production ML code  
**Models:** 5/5 complete  
**Next Phase:** FastAPI Service + Deployment

---

*Generated: August 22, 2026*  
*ARIA Emergency Response Platform*
