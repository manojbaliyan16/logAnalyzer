"""
Simple demo showing AI vs Pattern-based analysis
This clearly demonstrates the difference between traditional regex and AI/ML
"""

import os
from src.pattern_analyzer import PatternAnalyzer
from src.ai_analyzer import AIAnalyzer
from src.hybrid_analyzer import HybridAnalyzer

def print_banner(text):
    """Print a clear banner"""
    print("\n" + "=" * 100)
    print(f"  {text}")
    print("=" * 100 + "\n")

def analyze_log_file(log_path):
    """Analyze a log file with all three approaches"""
    
    if not os.path.exists(log_path):
        print(f"❌ Log file not found: {log_path}")
        return
    
    # Check if model exists
    if not os.path.exists('models/ml_model.pkl'):
        print("❌ ML Model not trained!")
        print("\nPlease run: python models/train_model.py")
        return
    
    print_banner("AI-POWERED LOG ANALYZER DEMO")
    print(f"📄 Analyzing: {os.path.basename(log_path)}\n")
    
    # Read log
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        log_content = f.read()
    
    # Show snippet
    print("─" * 100)
    print("LOG SNIPPET (First 20 lines):")
    print("─" * 100)
    lines = log_content.split('\n')
    for i, line in enumerate(lines[:20], 1):
        print(f"{i:3d} | {line[:120]}")
    if len(lines) > 20:
        print(f"... ({len(lines) - 20} more lines)")
    print("─" * 100)
    
    # Initialize analyzers
    print("\n⏳ Initializing analyzers...")
    print("   [1/3] Loading Pattern-Based Analyzer (Traditional Regex)...")
    pattern_analyzer = PatternAnalyzer()
    
    print("   [2/3] Loading AI-Powered Analyzer (Machine Learning Model)...")
    ai_analyzer = AIAnalyzer()
    
    print("   [3/3] Loading Hybrid Analyzer (Pattern + AI)...")
    hybrid_analyzer = HybridAnalyzer()
    print("✓ All analyzers ready!\n")
    
    # Run analyses
    print("🔍 Running Analysis...")
    print()
    
    # 1. Pattern-Based Analysis
    print_banner("METHOD 1: PATTERN-BASED ANALYSIS (Traditional Approach)")
    print("🔧 Technology: Regular Expressions (Regex)")
    print("🎯 How it works: Matches predefined text patterns")
    print("✅ Pros: Fast, 100% accurate for known patterns")
    print("❌ Cons: Can't detect unknown issues")
    print()
    
    pattern_result = pattern_analyzer.analyze(log_content)
    
    if pattern_result['root_cause']:
        print(f"✓ DETECTED: {pattern_result['root_cause']}")
        print(f"  Confidence: {pattern_result['confidence']:.1%}")
        print(f"  Severity: {pattern_result['severity']}")
        print(f"  Explanation: {pattern_result['explanation']}")
    else:
        print("✗ NO DETECTION - Pattern not found in predefined rules")
    
    # 2. AI-Powered Analysis
    print_banner("METHOD 2: AI-POWERED ANALYSIS (Machine Learning)")
    print("🤖 Technology: Random Forest ML Model + TF-IDF")
    print("🎯 How it works: Trained on 1000 automotive logs")
    print("✅ Pros: Can detect unknown patterns, learns from data")
    print("❌ Cons: May have lower confidence on edge cases")
    print()
    
    ai_result = ai_analyzer.analyze(log_content)
    
    print(f"🤖 AI PREDICTION: {ai_result['root_cause']}")
    print(f"  Confidence: {ai_result['confidence']:.1%}")
    print(f"  Severity: {ai_result['severity']}")
    print(f"  Explanation: {ai_result['explanation']}")
    print()
    print("  Top 3 Predictions from AI Model:")
    for i, pred in enumerate(ai_result['top_3_predictions'], 1):
        print(f"    {i}. {pred['cause']:<30} ({pred['confidence']:.1%})")
    
    # 3. Hybrid Analysis
    print_banner("METHOD 3: HYBRID ANALYSIS (Best of Both Worlds)")
    print("🎯 Technology: Pattern + AI with Intelligent Fusion")
    print("🎯 How it works: Uses patterns when available, AI for unknowns")
    print("✅ Pros: 100% accuracy on known + AI for unknown patterns")
    print("✅ Recommended: Best approach for production")
    print()
    
    hybrid_result = hybrid_analyzer.analyze(log_content)
    
    print(f"🎯 HYBRID RESULT: {hybrid_result['root_cause']}")
    print(f"  Confidence: {hybrid_result['confidence']:.1%}")
    print(f"  Severity: {hybrid_result['severity']}")
    print(f"  Explanation: {hybrid_result['explanation']}")
    print(f"  Method Used: {hybrid_result.get('method', 'hybrid').upper()}")
    
    # Summary Comparison
    print_banner("COMPARISON SUMMARY")
    
    print(f"{'Method':<25} {'Detection':<35} {'Confidence':<15} {'Tech':<30}")
    print("─" * 100)
    
    pattern_detection = pattern_result['root_cause'] if pattern_result['root_cause'] else "❌ Not Detected"
    ai_detection = ai_result['root_cause']
    hybrid_detection = hybrid_result['root_cause']
    
    pattern_conf = f"{pattern_result['confidence']:.1%}" if pattern_result['root_cause'] else "N/A"
    ai_conf = f"{ai_result['confidence']:.1%}"
    hybrid_conf = f"{hybrid_result['confidence']:.1%}"
    
    print(f"🔍 Pattern-Based        {pattern_detection:<35} {pattern_conf:<15} Regex")
    print(f"🤖 AI-Powered           {ai_detection:<35} {ai_conf:<15} Random Forest + TF-IDF")
    print(f"🎯 Hybrid (Recommended) {hybrid_detection:<35} {hybrid_conf:<15} Pattern + AI Fusion")
    
    print("=" * 100)
    
    # Key Insights
    print("\n💡 KEY INSIGHTS:")
    if pattern_result['root_cause'] == ai_result['root_cause']:
        print("   ✓ Both Pattern and AI agree on the root cause")
        print("   ✓ High confidence in this detection")
    elif pattern_result['root_cause'] and not ai_result['root_cause']:
        print("   ⚠ Pattern detected issue, but AI has different prediction")
        print("   ⚠ May indicate a known pattern with unusual characteristics")
    elif not pattern_result['root_cause'] and ai_result['root_cause']:
        print("   🤖 AI detected an issue that traditional patterns missed!")
        print("   🤖 This demonstrates the power of Machine Learning")
    
    print()

def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1:
        log_path = sys.argv[1]
    else:
        log_path = "data/sample_logs/LOG_0001-AuthMgr.log"
    
    analyze_log_file(log_path)
    
    print("\n💡 USAGE:")
    print("   python demo_ai_vs_pattern.py <path_to_log_file>")
    print()
    print("📚 TO LEARN MORE:")
    print("   - See README.md for full documentation")
    print("   - See AI_INTEGRATION_GUIDE.md for AI strategy")
    print()

if __name__ == "__main__":
    main()
