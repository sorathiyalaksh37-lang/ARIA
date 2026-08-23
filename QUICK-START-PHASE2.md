# 🚀 ARIA Phase 2: Quick Start Guide

**Get started with ML models in 5 minutes!**

---

## ⚡ Quick Setup

```bash
# 1. Navigate to project
cd /Users/lakshsorathiya/ARIA

# 2. Install ML dependencies
pip install -r requirements.txt

# 3. Train a model (pick one)
python ml_scripts/triage_classifier.py
```

---

## 🎯 5 Models Available

| Model | Command | Time | Output |
|-------|---------|------|--------|
| 🏥 **Triage** | `python ml_scripts/triage_classifier.py` | ~5 min | Severity classifier |
| 🚑 **ETA** | `python ml_scripts/eta_predictor.py` | ~2 min | Arrival time predictor |
| 🏥 **Hospital** | `python ml_scripts/hospital_ranker.py` | ~3 min | Hospital ranker |
| 📈 **Resource** | `python ml_scripts/resource_predictor.py` | ~10 min | Demand forecaster |
| 🗺️ **Hotspot** | `python ml_scripts/hotspot_predictor.py` | ~1 min | Hotspot detector |

---

## 📊 Quick Test

```bash
# Train the fastest model (Hotspot - 1 minute)
python ml_scripts/hotspot_predictor.py

# Check results
ls -lh models/hotspot_*
ls -lh reports/hotspot_*
cat logs/hotspot_predictor_training.log
```

---

## 🔍 What Gets Created

### After Training:
```
models/
  └── [model_name]_*.pkl        # Trained model files

reports/
  └── [model_name]_evaluation.png  # Visualization

logs/
  └── [model_name]_training.log    # Training log
```

---

## 💡 Usage Example

```python
import joblib
import pandas as pd

# Load trained model
model = joblib.load('models/eta_predictor.pkl')
scaler = joblib.load('models/eta_predictor_scaler.pkl')

# Prepare input
data = pd.DataFrame({
    'distance_km': [5.2],
    'traffic_level': ['HIGH'],
    'hour': [8],
    'weather': ['CLEAR'],
    # ... other features
})

# Predict
eta = model.predict(data)
print(f"Estimated arrival: {eta[0]:.1f} minutes")
```

---

## 📚 Full Documentation

- **[PHASE2-ML-MODELS.md](./docs/PHASE2-ML-MODELS.md)** — Complete guide (500+ lines)
- **[PHASE2-COMPLETE-SUMMARY.md](./PHASE2-COMPLETE-SUMMARY.md)** — Summary report

---

## 🆘 Troubleshooting

### Missing Dependencies?
```bash
pip install scikit-learn xgboost lightgbm torch transformers prophet optuna shap
```

### Out of Memory?
- Start with smaller models: ETA, Hotspot
- Skip BERT/LSTM if needed (models have fallbacks)

### Want to Skip Long Training?
- Models work with synthetic data by default
- No external data needed for testing

---

## ✅ Validation Checklist

- [ ] Python 3.9+ installed
- [ ] Dependencies installed (`pip list | grep xgboost`)
- [ ] Models directory exists (`mkdir -p models reports logs`)
- [ ] Ran at least one training script
- [ ] Generated model artifacts in `models/`
- [ ] Evaluation plots in `reports/`

---

## 🎯 Next Steps

1. ✅ Train all 5 models
2. ✅ Review visualizations in `reports/`
3. ✅ Check training logs
4. ⏳ Phase 3: Build FastAPI service
5. ⏳ Integrate with real data

---

**Questions?** Check the full docs in `docs/PHASE2-ML-MODELS.md`

*Last updated: August 22, 2026*
