# AI Log Analyzer Prototype

## Overview
This is a working prototype demonstrating AI integration with the EM Log Analyser system.

## Features
- ✅ Synthetic log data generation
- ✅ Simple ML model (Random Forest + TF-IDF)
- ✅ Hybrid analysis (Pattern-based + AI)
- ✅ Training pipeline
- ✅ Inference demo
- ✅ Comparison dashboard

## Project Structure
```
AI_Prototype/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── demo.py                      # Main demo script
├── data/
│   ├── generate_synthetic_data.py   # Generate sample logs
│   ├── synthetic_logs.csv           # Generated data
│   └── sample_logs/                 # Example log files
├── models/
│   ├── train_model.py              # Model training script
│   ├── ml_model.pkl                # Trained model
│   └── vectorizer.pkl              # TF-IDF vectorizer
├── src/
│   ├── pattern_analyzer.py         # Traditional pattern-based
│   ├── ai_analyzer.py              # AI-powered analyzer
│   ├── hybrid_analyzer.py          # Combined approach
│   └── utils.py                    # Helper functions
└── results/
    ├── comparison_report.html      # Results comparison
    └── metrics.json                # Performance metrics
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Synthetic Data
```bash
python data/generate_synthetic_data.py
```

### 3. Train the Model
```bash
python models/train_model.py
```

### 4. Run the Demo
```bash
python demo.py
```

## Demo Scenarios

The demo includes 5 test scenarios:

1. **Memory Leak** - AI should detect with high confidence
2. **Watchdog Timeout** - Both pattern and AI should catch
3. **Unknown Issue** - Only AI should detect
4. **CAN Bus Error** - Pattern-based should catch
5. **SW Update Failure** - AI should identify

## Expected Output

```
========================================
AI Log Analyzer Prototype Demo
========================================

[Scenario 1: Memory Leak Detection]
Pattern-Based: No match
AI Prediction: Memory Leak (92% confidence)
Winner: AI ✓

[Scenario 2: Watchdog Timeout]
Pattern-Based: WATCHDOG_RESET detected
AI Prediction: Watchdog Timeout (95% confidence)
Winner: Both agree ✓

[Overall Results]
Pattern-Based Accuracy: 60%
AI-Based Accuracy: 85%
Hybrid Accuracy: 90%
```

## Model Details

### Features Used:
- Log text (TF-IDF vectors)
- SW version encoding
- Platform type
- Log size
- Has missing blocks (boolean)
- Has overwritten blocks (boolean)

### Model: Random Forest Classifier
- 100 estimators
- Max depth: 20
- Features: TF-IDF (100 dimensions) + metadata (6 features)

### Classes:
1. Memory Leak
2. Watchdog Timeout
3. CAN Bus Error
4. SW Update Failure
5. Kernel Panic
6. File System Error
7. Network Timeout
8. Hardware Fault
9. Unknown Issue
10. No Issue

## Performance Metrics

After training on 1000 synthetic logs:
- Training Accuracy: ~95%
- Test Accuracy: ~85%
- Precision: ~83%
- Recall: ~85%
- F1 Score: ~84%

## Extending the Prototype

### Add Real Logs:
```python
from src.ai_analyzer import AIAnalyzer

analyzer = AIAnalyzer('models/ml_model.pkl', 'models/vectorizer.pkl')
result = analyzer.analyze_log_file('path/to/real/log.pro')
print(result)
```

### Retrain with Your Data:
```python
from models.train_model import train_model

# Prepare your data as CSV with columns:
# log_content, root_cause, severity, sw_version, platform
train_model('your_data.csv', output_model='models/custom_model.pkl')
```

## Next Steps for Production

1. **Replace synthetic data** with real historical tickets
2. **Upgrade to BERT** for better text understanding
3. **Add more features** (fault dates, component info)
4. **Implement feedback loop** for continuous learning
5. **Deploy as microservice** (FastAPI)
6. **Add monitoring** (MLflow, Weights & Biases)

## License
Internal prototype for demonstration purposes.
