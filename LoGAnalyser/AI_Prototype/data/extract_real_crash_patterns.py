"""
Extract crash patterns from real AuthMgr.log file and generate training data
This creates realistic training samples based on actual log data
"""

import os
import re
import pandas as pd
import random
from datetime import datetime

def extract_crash_segments(log_file_path, output_csv='data/real_crash_training.csv'):
    """Extract crash segments from real log file"""
    
    print(f"Reading log file: {log_file_path}")
    print("This may take a minute for large files...")
    
    with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
        log_content = f.read()
    
    print(f"✓ Loaded {len(log_content):,} characters")
    
    # Split into lines for processing
    lines = log_content.split('\n')
    print(f"✓ Total lines: {len(lines):,}")
    
    # Find all crash incidents
    crash_segments = []
    
    # Pattern: Find "Crashed Thread name::" and extract surrounding context
    crash_pattern = re.compile(r'Crashed Thread name::', re.IGNORECASE)
    
    print("\n🔍 Searching for crash patterns...")
    
    for i, line in enumerate(lines):
        if crash_pattern.search(line):
            # Extract context: 50 lines before crash, 100 lines after (including stack trace)
            start_idx = max(0, i - 50)
            end_idx = min(len(lines), i + 100)
            
            segment_lines = lines[start_idx:end_idx]
            segment_text = '\n'.join(segment_lines)
            
            # Extract module name from this segment
            module_match = re.search(r'/tmpMCH/codeCache/((?:com\.|stla\.|io\.)?[^/\s]+?)\.so', segment_text)
            module_name = module_match.group(1) if module_match else "Unknown"
            
            # Extract thread name
            thread_match = re.search(r'Crashed Thread name::\s*([A-Za-z0-9_]+)', line)
            thread_name = thread_match.group(1) if thread_match else "Unknown"
            
            crash_segments.append({
                'log_content': segment_text,
                'root_cause': 'Thread Crash',
                'severity': 'CRITICAL',
                'module': module_name,
                'thread': thread_name,
                'line_number': i
            })
            
            print(f"  Found crash #{len(crash_segments)}: Thread={thread_name}, Module={module_name} at line {i:,}")
    
    print(f"\n✓ Found {len(crash_segments)} crash incidents")
    
    # Extract normal operation segments (no crashes)
    print("\n🔍 Extracting normal operation segments...")
    
    normal_segments = []
    sample_count = min(len(crash_segments) * 2, 100)  # 2x crashes or max 100
    
    for _ in range(sample_count):
        # Random position avoiding crashes
        random_start = random.randint(0, len(lines) - 150)
        
        # Check if this segment contains a crash
        segment_lines = lines[random_start:random_start + 150]
        segment_text = '\n'.join(segment_lines)
        
        if 'Crashed Thread' not in segment_text and 'Stack Backtrace' not in segment_text:
            normal_segments.append({
                'log_content': segment_text,
                'root_cause': 'No Issue',
                'severity': 'LOW',
                'module': 'N/A',
                'thread': 'N/A',
                'line_number': random_start
            })
    
    print(f"✓ Extracted {len(normal_segments)} normal operation segments")
    
    # Combine all segments
    all_segments = crash_segments + normal_segments
    
    # Create DataFrame
    df = pd.DataFrame(all_segments)
    
    # Add metadata
    df['log_id'] = [f'REAL_{i:05d}' for i in range(len(df))]
    df['sw_version'] = 'REAL_LOG'
    df['platform'] = 'gen3'
    df['has_missing_blocks'] = False
    df['has_overwritten'] = False
    df['log_size'] = df['log_content'].apply(len)
    
    # Shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Save
    df.to_csv(output_csv, index=False)
    print(f"\n✓ Saved {len(df)} training samples to {output_csv}")
    
    # Statistics
    print("\n" + "=" * 80)
    print("TRAINING DATA STATISTICS")
    print("=" * 80)
    print(f"\nTotal samples: {len(df)}")
    print(f"\nRoot Cause Distribution:")
    print(df['root_cause'].value_counts())
    print(f"\nAverage log segment size: {df['log_size'].mean():.0f} characters")
    print(f"Total data size: {df['log_size'].sum() / 1024 / 1024:.2f} MB")
    
    return df

def combine_with_synthetic(real_csv='data/real_crash_training.csv', 
                           synthetic_csv='data/synthetic_logs.csv',
                           output_csv='data/combined_training.csv'):
    """Combine real crash data with synthetic data for comprehensive training"""
    
    print("\n" + "=" * 80)
    print("COMBINING REAL + SYNTHETIC DATA")
    print("=" * 80)
    
    # Load real data
    if os.path.exists(real_csv):
        df_real = pd.read_csv(real_csv)
        print(f"\n✓ Loaded {len(df_real)} real log samples")
    else:
        print(f"\n❌ Real data not found: {real_csv}")
        return None
    
    # Load synthetic data
    if os.path.exists(synthetic_csv):
        df_synthetic = pd.read_csv(synthetic_csv)
        print(f"✓ Loaded {len(df_synthetic)} synthetic samples")
        
        # Filter out synthetic crashes (we have real ones now)
        df_synthetic = df_synthetic[~df_synthetic['root_cause'].isin(['Thread Crash', 'Application Crash'])]
        print(f"✓ Kept {len(df_synthetic)} non-crash synthetic samples")
    else:
        print(f"⚠ Synthetic data not found: {synthetic_csv}")
        df_synthetic = pd.DataFrame()
    
    # Combine
    df_combined = pd.concat([df_real, df_synthetic], ignore_index=True)
    
    # Shuffle
    df_combined = df_combined.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Save
    df_combined.to_csv(output_csv, index=False)
    print(f"\n✓ Combined dataset saved to {output_csv}")
    
    # Statistics
    print("\n" + "=" * 80)
    print("COMBINED DATASET STATISTICS")
    print("=" * 80)
    print(f"\nTotal samples: {len(df_combined)}")
    print(f"\nRoot Cause Distribution:")
    print(df_combined['root_cause'].value_counts())
    print(f"\nSeverity Distribution:")
    print(df_combined['severity'].value_counts())
    
    return df_combined

def main():
    """Main entry point"""
    import os
    
    log_file = 'data/sample_logs/AuthMgr.log'
    
    if not os.path.exists(log_file):
        print(f"❌ Log file not found: {log_file}")
        print("\nPlease ensure AuthMgr.log is in data/sample_logs/")
        return
    
    # Extract crash patterns from real log
    df_real = extract_crash_segments(log_file)
    
    # Combine with synthetic data
    df_combined = combine_with_synthetic()
    
    print("\n" + "=" * 80)
    print("✓ TRAINING DATA PREPARATION COMPLETE!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Review the extracted crash patterns")
    print("2. Run: python models/train_model.py")
    print("3. Test with: python demo_ai_vs_pattern.py")
    print()

if __name__ == "__main__":
    main()
