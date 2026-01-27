"""
Demo script showcasing AI-enhanced log analysis
Run this after training the model
"""

import os
import pandas as pd
from src.pattern_analyzer import PatternAnalyzer
from src.ai_analyzer import AIAnalyzer
from src.hybrid_analyzer import HybridAnalyzer
import time

def print_section(title):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80 + "\n")

def print_result(name, result, color_code=""):
    """Print analysis result"""
    reset = "\033[0m"
    
    if result['root_cause']:
        conf_str = f"{result['confidence']:.0%}"
        print(f"{color_code}[{name}]{reset}")
        print(f"  Root Cause: {result['root_cause']}")
        print(f"  Confidence: {conf_str}")
        print(f"  Severity: {result.get('severity', 'N/A')}")
        print(f"  Explanation: {result.get('explanation', 'N/A')}")
    else:
        print(f"{color_code}[{name}]{reset}")
        print("  No detection")

def run_demo():
    """Run the demo"""
    
    print_section("AI Log Analyzer Prototype Demo")
    
    # Check if model exists
    if not os.path.exists('models/ml_model.pkl'):
        print("❌ Model not found!")
        print("\nPlease run the following commands first:")
        print("1. python data/generate_synthetic_data.py")
        print("2. python models/train_model.py")
        return
    
    # Initialize analyzers
    print("Initializing analyzers...")
    pattern_analyzer = PatternAnalyzer()
    ai_analyzer = AIAnalyzer()
    hybrid_analyzer = HybridAnalyzer()
    print("✓ All analyzers ready\n")
    
    # Load sample logs
    sample_logs_dir = 'data/sample_logs'
    
    if not os.path.exists(sample_logs_dir):
        print(f"❌ Sample logs not found in {sample_logs_dir}")
        print("\nPlease run: python data/generate_synthetic_data.py")
        return
    
    sample_files = [f for f in os.listdir(sample_logs_dir) if f.endswith('.log')][:5]
    
    # Statistics
    pattern_correct = 0
    ai_correct = 0
    hybrid_correct = 0
    total = len(sample_files)
    
    # Analyze each sample
    for i, filename in enumerate(sample_files, 1):
        file_path = os.path.join(sample_logs_dir, filename)
        
        # Extract ground truth from filename
        ground_truth = filename.split('_', 2)[2].replace('.log', '').replace('_', ' ')
        
        print_section(f"Scenario {i}: {ground_truth}")
        print(f"Analyzing: {filename}\n")
        
        # Read log
        with open(file_path, 'r') as f:
            log_content = f.read()
        
        # Show log snippet
        print("Log Snippet:")
        print("-" * 80)
        lines = log_content.split('\n')
        for line in lines[3:8]:  # Show 5 lines
            print(line)
        if len(lines) > 8:
            print("...")
        print("-" * 80 + "\n")
        
        # Run analyses
        start_time = time.time()
        
        # Pattern-based
        pattern_result = pattern_analyzer.analyze(log_content)
        pattern_time = time.time() - start_time
        
        # AI-based
        start_time = time.time()
        ai_result = ai_analyzer.analyze(log_content)
        ai_time = time.time() - start_time
        
        # Hybrid
        start_time = time.time()
        hybrid_result = hybrid_analyzer.analyze(log_content)
        hybrid_time = time.time() - start_time
        
        # Print results
        print("Analysis Results:")
        print("-" * 80)
        print_result("Pattern-Based", pattern_result, "\033[94m")  # Blue
        print()
        print_result("AI-Powered", ai_result, "\033[92m")  # Green
        print()
        print_result("Hybrid", hybrid_result, "\033[93m")  # Yellow
        print("-" * 80)
        
        # Check correctness
        pattern_match = pattern_result['root_cause'] == ground_truth if pattern_result['root_cause'] else False
        ai_match = ai_result['root_cause'] == ground_truth
        hybrid_match = hybrid_result['root_cause'] == ground_truth
        
        if pattern_match:
            pattern_correct += 1
        if ai_match:
            ai_correct += 1
        if hybrid_match:
            hybrid_correct += 1
        
        # Show winner
        print("\nComparison:")
        print(f"  Ground Truth: {ground_truth}")
        print(f"  Pattern Match: {'✓' if pattern_match else '✗'}")
        print(f"  AI Match: {'✓' if ai_match else '✗'}")
        print(f"  Hybrid Match: {'✓' if hybrid_match else '✗'}")
        
        print(f"\nExecution Times:")
        print(f"  Pattern: {pattern_time*1000:.2f}ms")
        print(f"  AI: {ai_time*1000:.2f}ms")
        print(f"  Hybrid: {hybrid_time*1000:.2f}ms")
        
        input("\nPress Enter to continue...")
    
    # Final summary
    print_section("Summary Report")
    
    print("Accuracy Comparison:")
    print("-" * 80)
    print(f"Pattern-Based Accuracy: {pattern_correct}/{total} ({pattern_correct/total:.0%})")
    print(f"AI-Powered Accuracy:    {ai_correct}/{total} ({ai_correct/total:.0%})")
    print(f"Hybrid Accuracy:        {hybrid_correct}/{total} ({hybrid_correct/total:.0%})")
    
    # Determine winner
    print("\n" + "=" * 80)
    if hybrid_correct >= max(pattern_correct, ai_correct):
        print("🏆 WINNER: Hybrid Approach")
        print("   The combination of pattern-based and AI provides the best results!")
    elif ai_correct > pattern_correct:
        print("🏆 WINNER: AI-Powered Approach")
        print("   AI successfully detected issues missed by pattern matching!")
    else:
        print("🏆 WINNER: Pattern-Based Approach")
        print("   Traditional patterns performed well for these known issues!")
    print("=" * 80)
    
    # Recommendations
    print("\n📊 Key Insights:")
    print("-" * 80)
    if ai_correct > pattern_correct:
        print("✓ AI detected issues that pattern matching missed")
    if hybrid_correct >= ai_correct:
        print("✓ Hybrid approach provides safety net with pattern validation")
    if pattern_correct == total:
        print("✓ All issues were known patterns - good pattern coverage")
    else:
        print(f"✓ {total - pattern_correct} issues were not in pattern database - AI added value")
    
    print("\n💡 Recommendations:")
    print("-" * 80)
    print("1. Use hybrid approach in production for best coverage")
    print("2. Collect more real data to improve AI accuracy")
    print("3. Update pattern database with newly discovered issues")
    print("4. Monitor AI confidence scores - retrain if dropping")
    print("5. Implement feedback loop for continuous learning")
    
    print("\n" + "=" * 80)
    print("Demo Complete! Thank you for using AI Log Analyzer Prototype.")
    print("=" * 80 + "\n")

if __name__ == '__main__':
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
