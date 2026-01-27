"""
Analyze a custom log file using the trained AI model
"""

import os
import sys
from src.pattern_analyzer import PatternAnalyzer
from src.ai_analyzer import AIAnalyzer
from src.hybrid_analyzer import HybridAnalyzer

def print_section(title):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80 + "\n")

def print_result(name, result, color_code=""):
    """Print analysis result with detailed output"""
    reset = "\033[0m"
    
    print(f"\n{color_code}{'═' * 80}")
    print(f"  {name}")
    print(f"{'═' * 80}{reset}\n")
    
    if result['root_cause']:
        conf_str = f"{result['confidence']:.1%}"
        print(f"  ✓ Root Cause:  {result['root_cause']}")
        print(f"  ✓ Confidence:  {conf_str}")
        print(f"  ✓ Severity:    {result.get('severity', 'N/A')}")
        print(f"  ✓ Explanation: {result.get('explanation', 'N/A')}")
        
        # Show top predictions for AI analyzer
        if 'top_predictions' in result and result['top_predictions']:
            print(f"\n  Top 3 Predictions:")
            for rank, (cause, conf) in enumerate(result['top_predictions'][:3], 1):
                print(f"    {rank}. {cause:<25} ({conf:.1%})")
    else:
        print(f"  ✗ No issue detected")
    
    print()

def analyze_log_file(log_path):
    """Analyze a specific log file"""
    
    if not os.path.exists(log_path):
        print(f"❌ Log file not found: {log_path}")
        return
    
    # Check if model exists
    if not os.path.exists('models/ml_model.pkl'):
        print("❌ Model not found!")
        print("\nPlease run: python models/train_model.py")
        return
    
    print_section(f"Analyzing Custom Log File")
    print(f"File: {os.path.basename(log_path)}")
    print(f"Path: {log_path}\n")
    
    # Read log content
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        log_content = f.read()
    
    # Show log content
    print("─" * 80)
    print("LOG CONTENT:")
    print("─" * 80)
    lines = log_content.split('\n')
    for i, line in enumerate(lines[:30], 1):  # Show first 30 lines
        print(f"{i:3d} | {line}")
    if len(lines) > 30:
        print(f"... ({len(lines) - 30} more lines)")
    print("─" * 80)
    
    # Initialize analyzers
    print("\n⏳ Initializing analyzers...")
    pattern_analyzer = PatternAnalyzer()
    ai_analyzer = AIAnalyzer()
    hybrid_analyzer = HybridAnalyzer()
    print("✓ All analyzers ready")
    
    # Run analyses
    print("\n⏳ Running analysis...")
    
    # Pattern-based
    pattern_result = pattern_analyzer.analyze(log_content)
    
    # AI-based
    ai_result = ai_analyzer.analyze(log_content)
    
    # Hybrid
    hybrid_result = hybrid_analyzer.analyze(log_content)
    
    # Print results
    print_section("Analysis Results")
    
    print_result("🔍 PATTERN-BASED ANALYSIS (Traditional Regex)", pattern_result, "\033[94m")
    print_result("🤖 AI-POWERED ANALYSIS (Machine Learning)", ai_result, "\033[92m")
    print_result("🎯 HYBRID ANALYSIS (Best of Both)", hybrid_result, "\033[93m")
    
    print("=" * 80)
    print("\n✓ Analysis complete!\n")
    
    # Summary comparison
    print_section("Summary Comparison")
    print(f"{'Analyzer':<25} {'Detection':<30} {'Confidence':<15}")
    print("─" * 80)
    
    for name, result, emoji in [
        ("Pattern-Based", pattern_result, "🔍"),
        ("AI-Powered", ai_result, "🤖"),
        ("Hybrid", hybrid_result, "🎯")
    ]:
        detection = result['root_cause'] if result['root_cause'] else "No detection"
        confidence = f"{result['confidence']:.1%}" if result['root_cause'] else "N/A"
        print(f"{emoji} {name:<22} {detection:<30} {confidence:<15}")
    
    print("=" * 80 + "\n")

def main():
    """Main entry point"""
    
    # Check command line arguments
    if len(sys.argv) > 1:
        log_path = sys.argv[1]
    else:
        # Default to the AuthMgr log
        log_path = "data/sample_logs/LOG_0001-AuthMgr.log"
    
    analyze_log_file(log_path)
    
    print("\n💡 TIP: You can analyze any log file by running:")
    print(f"   python analyze_custom_log.py <path_to_your_log_file>\n")

if __name__ == "__main__":
    main()
