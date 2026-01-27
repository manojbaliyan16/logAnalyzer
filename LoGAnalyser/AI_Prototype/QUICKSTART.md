# Quick Start Guide

## Setup (5 minutes)

### Step 1: Install dependencies
```bash
cd AI_Prototype
pip install -r requirements.txt
```

### Step 2: Generate data and train model
```bash
# Generate 1000 synthetic log samples
python data/generate_synthetic_data.py

# Train the ML model (~1-2 minutes)
python models/train_model.py
```

### Step 3: Run the demo
```bash
python demo.py
```

## What to Expect

The demo will:
1. Load 5 sample log files
2. Analyze each with 3 methods:
   - Pattern-based (traditional)
   - AI-powered (ML model)
   - Hybrid (combination)
3. Show accuracy comparison
4. Declare a winner!

## Example Output

```
================================================================================
 Scenario 1: Memory Leak
================================================================================

Analyzing: LOG_00000_Memory_Leak.log

Log Snippet:
--------------------------------------------------------------------------------
[22.01.26 14:23:45] ERRMEM: VERSIONINFO: AIVI_SW5244
[22.01.26 14:23:45] Platform: gen3
[22.01.26 14:23:45] Component: Navigation
[22.01.26 14:23:45] WARNING: High memory usage detected
[22.01.26 14:23:45] ERROR: Heap allocation failed in Navigation
...
--------------------------------------------------------------------------------

Analysis Results:
--------------------------------------------------------------------------------
[Pattern-Based]
  No detection

[AI-Powered]
  Root Cause: Memory Leak
  Confidence: 92%
  Severity: HIGH
  Explanation: Detected memory allocation issues...

[Hybrid]
  Root Cause: Memory Leak
  Confidence: 92%
  Severity: HIGH
  Explanation: AI detected Memory Leak. No matching patterns found.
--------------------------------------------------------------------------------

Comparison:
  Ground Truth: Memory Leak
  Pattern Match: ✗
  AI Match: ✓
  Hybrid Match: ✓

Execution Times:
  Pattern: 0.15ms
  AI: 12.34ms
  Hybrid: 12.50ms

Press Enter to continue...
```

## Tips

- Press Ctrl+C to exit demo anytime
- Check `data/sample_logs/` for generated log files
- Model is saved in `models/ml_model.pkl`
- Retrain anytime with `python models/train_model.py`

## Next Steps

After the demo, try:
1. Analyze your own logs:
   ```python
   from src.hybrid_analyzer import HybridAnalyzer
   
   analyzer = HybridAnalyzer()
   result = analyzer.analyze_file('your_log.pro')
   print(result)
   ```

2. Generate more data:
   ```python
   python data/generate_synthetic_data.py  # Generates 1000 samples
   ```

3. Experiment with model parameters in `models/train_model.py`

Enjoy! 🚀
