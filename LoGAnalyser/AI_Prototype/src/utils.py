"""
Utility functions for the prototype
"""

import json
import os

def save_results(results, output_path='results/analysis_results.json'):
    """Save analysis results to JSON"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

def load_results(input_path='results/analysis_results.json'):
    """Load analysis results from JSON"""
    with open(input_path, 'r') as f:
        return json.load(f)

def format_confidence(confidence):
    """Format confidence as percentage"""
    return f"{confidence:.0%}"

def get_color_code(confidence):
    """Get terminal color code based on confidence"""
    if confidence >= 0.8:
        return '\033[92m'  # Green
    elif confidence >= 0.5:
        return '\033[93m'  # Yellow
    else:
        return '\033[91m'  # Red

def reset_color():
    """Reset terminal color"""
    return '\033[0m'

def print_colored(text, confidence):
    """Print text with color based on confidence"""
    color = get_color_code(confidence)
    reset = reset_color()
    print(f"{color}{text}{reset}")
