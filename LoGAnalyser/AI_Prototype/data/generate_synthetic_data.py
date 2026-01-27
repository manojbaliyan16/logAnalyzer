"""
Generate synthetic log data for demo purposes
Simulates various error patterns found in automotive EM logs
"""

import random
import pandas as pd
from datetime import datetime, timedelta
import os

# Error patterns and their characteristics
ERROR_PATTERNS = {
    'Thread Crash': {
        'keywords': ['Crashed Thread', 'Stack Backtrace', 'codeCache', 'thread', 'crashed', 'SIGSEGV', 'signal'],
        'severity': 'CRITICAL',
        'components': ['macchina', 'AuthManager', 'RemoteServices', 'LifecycleMonitor']
    },
    'Application Crash': {
        'keywords': ['segmentation fault', 'core dump', 'fatal error', 'abort', 'terminated'],
        'severity': 'CRITICAL',
        'components': ['Application', 'Service', 'Process']
    },
    'Memory Leak': {
        'keywords': ['heap', 'malloc', 'free', 'memory', 'allocation', 'leak', 'OOM'],
        'severity': 'HIGH',
        'components': ['Navigation', 'Audio', 'Multimedia']
    },
    'Watchdog Timeout': {
        'keywords': ['watchdog', 'timeout', 'reset', 'wdt', 'deadlock', 'hang'],
        'severity': 'CRITICAL',
        'components': ['Kernel', 'System', 'Power']
    },
    'CAN Bus Error': {
        'keywords': ['CAN', 'bus', 'communication', 'frame', 'error', 'arbitration'],
        'severity': 'MEDIUM',
        'components': ['CAN', 'Communication', 'Network']
    },
    'SW Update Failure': {
        'keywords': ['update', 'flash', 'upgrade', 'version', 'installation', 'failed'],
        'severity': 'HIGH',
        'components': ['SW_SWUPDATE', 'System']
    },
    'Kernel Panic': {
        'keywords': ['panic', 'kernel', 'crash', 'exception', 'fault', 'abort'],
        'severity': 'CRITICAL',
        'components': ['Kernel', 'System']
    },
    'File System Error': {
        'keywords': ['filesystem', 'mount', 'disk', 'inode', 'corrupt', 'read'],
        'severity': 'MEDIUM',
        'components': ['FileSystem', 'Storage']
    },
    'Network Timeout': {
        'keywords': ['network', 'socket', 'timeout', 'connection', 'refused', 'tcp'],
        'severity': 'LOW',
        'components': ['Network', 'Communication']
    },
    'Hardware Fault': {
        'keywords': ['hardware', 'sensor', 'gpio', 'i2c', 'spi', 'fault'],
        'severity': 'HIGH',
        'components': ['Hardware', 'Sensors']
    },
    'Unknown Issue': {
        'keywords': ['error', 'failed', 'exception', 'warning', 'issue'],
        'severity': 'MEDIUM',
        'components': ['Unknown']
    },
    'No Issue': {
        'keywords': ['normal', 'success', 'ok', 'completed', 'running'],
        'severity': 'LOW',
        'components': ['System']
    }
}

SW_VERSIONS = ['AIVI_SW5244', 'AIVI_SW5250', 'PIVI_SW4100', 'PIVI_SW4110']
PLATFORMS = ['gen3', 'gen4']

def generate_log_content(error_type, sw_version, platform):
    """Generate realistic log content based on error type"""
    
    pattern = ERROR_PATTERNS[error_type]
    keywords = pattern['keywords']
    component = random.choice(pattern['components'])
    
    # Base log structure
    timestamp = datetime.now() - timedelta(days=random.randint(0, 30))
    ts_str = timestamp.strftime('%d.%m.%y %H:%M:%S')
    
    log_lines = [
        f"[{ts_str}] ERRMEM: VERSIONINFO: {sw_version}",
        f"[{ts_str}] Platform: {platform}",
        f"[{ts_str}] Component: {component}",
    ]
    
    # Add error-specific content
    if error_type == 'Thread Crash':
        modules = ['com.stla.AuthManager.so', 'com.stellantis.RemoteServices.so', 
                   'io.macchina.LifecycleMonitor.so', 'stla.app.spaak.so']
        module = random.choice(modules)
        thread_names = ['APPFWK_SUPV_MAI', 'macchina', 'AUTH_HANDLER', 'LIFECYCLE_MON']
        thread = random.choice(thread_names)
        log_lines.extend([
            f"[{ts_str}] ERROR: Crashed Thread name:: {thread}",
            f"[{ts_str}] ERROR: Stack Backtrace:",
            f"[{ts_str}] ERROR: /mnt/application-sw/mnt_app_root/usr/local/macchina/bin/macchina(+0x826c) [0x555bff826c]",
            f"[{ts_str}] ERROR: linux-vdso.so.1(__kernel_rt_sigreturn+0) [0x7fb506b84c]",
            f"[{ts_str}] ERROR: /tmpMCH/codeCache/{module}(_ZN4Stla7AuthMgr7AuthMgr+0x{random.randint(100, 999):03x}) [0x7eea7c1fac]",
            f"[{ts_str}] ERROR: /tmpMCH/codeCache/{module}(_ZNSt16_Sp_counted_base+0x50) [0x7fb44af260]",
            f"[{ts_str}] CRITICAL: Thread {thread} {random.choice(keywords)}",
        ])
    
    elif error_type == 'Application Crash':
        log_lines.extend([
            f"[{ts_str}] CRITICAL: Application crashed unexpectedly",
            f"[{ts_str}] ERROR: segmentation fault (core dumped)",
            f"[{ts_str}] TRACE: Signal SIGSEGV received",
            f"[{ts_str}] ERROR: Process terminated with code {random.randint(134, 139)}",
            f"[{ts_str}] ERROR: {random.choice(keywords).upper()} in application",
        ])
    
    elif error_type == 'Memory Leak':
        log_lines.extend([
            f"[{ts_str}] WARNING: High memory usage detected",
            f"[{ts_str}] ERROR: Heap allocation failed in {component}",
            f"[{ts_str}] TRACE: malloc returned NULL",
            f"[{ts_str}] INFO: Available memory: 128 KB / 2048 KB",
            f"[{ts_str}] ERROR: Memory leak suspected in navigation module",
            f"[{ts_str}] TRACE: {random.choice(keywords).upper()} - size: {random.randint(100, 5000)} bytes"
        ])
    
    elif error_type == 'Watchdog Timeout':
        log_lines.extend([
            f"[{ts_str}] WARNING: Task execution time exceeded threshold",
            f"[{ts_str}] ERROR: WATCHDOG_RESET triggered",
            f"[{ts_str}] TRACE: System reset due to watchdog timeout",
            f"[{ts_str}] INFO: Last task: {component}_handler",
            f"[{ts_str}] CRITICAL: System {random.choice(keywords).upper()}",
        ])
    
    elif error_type == 'CAN Bus Error':
        log_lines.extend([
            f"[{ts_str}] WARNING: CAN bus error detected",
            f"[{ts_str}] ERROR: Frame transmission failed on CAN2",
            f"[{ts_str}] TRACE: Bus-off state entered",
            f"[{ts_str}] INFO: Error counter: {random.randint(10, 255)}",
            f"[{ts_str}] ERROR: {random.choice(keywords).upper()} on CAN interface",
        ])
    
    elif error_type == 'SW Update Failure':
        log_lines.extend([
            f"[{ts_str}] INFO: Starting software update",
            f"[{ts_str}] WARNING: Update verification failed",
            f"[{ts_str}] ERROR: Flash write error at block {random.randint(100, 999)}",
            f"[{ts_str}] TRACE: Rolling back to previous version",
            f"[{ts_str}] CRITICAL: Software {random.choice(keywords).upper()}",
        ])
    
    elif error_type == 'Kernel Panic':
        log_lines.extend([
            f"[{ts_str}] CRITICAL: Kernel panic detected",
            f"[{ts_str}] ERROR: Unable to handle kernel NULL pointer dereference",
            f"[{ts_str}] TRACE: Exception at address 0x{random.randint(1000, 9999):04X}",
            f"[{ts_str}] ERROR: CPU {random.randint(0, 3)} {random.choice(keywords).upper()}",
            f"[{ts_str}] CRITICAL: System halted",
        ])
    
    else:
        # Generic error log
        for _ in range(random.randint(3, 6)):
            keyword = random.choice(keywords)
            log_lines.append(f"[{ts_str}] ERROR: {keyword.upper()} in {component}")
    
    # Add some noise (normal operations)
    noise_lines = [
        f"[{ts_str}] INFO: System running normally",
        f"[{ts_str}] DEBUG: Processing event queue",
        f"[{ts_str}] INFO: Component initialized successfully",
    ]
    log_lines.extend(random.sample(noise_lines, k=random.randint(1, 3)))
    
    # Shuffle to make it realistic
    random.shuffle(log_lines[3:])  # Keep header lines at top
    
    return '\n'.join(log_lines)

def generate_metadata():
    """Generate additional metadata for each log"""
    return {
        'has_missing_blocks': random.choice([True, False]),
        'has_overwritten': random.choice([True, False]),
        'log_size': random.randint(500, 50000),
    }

def generate_dataset(num_samples=1000):
    """Generate complete synthetic dataset"""
    
    print(f"Generating {num_samples} synthetic log samples...")
    
    data = []
    
    for i in range(num_samples):
        if i % 100 == 0:
            print(f"Generated {i}/{num_samples} samples...")
        
        # Random error type (weighted distribution)
        error_types = list(ERROR_PATTERNS.keys())
        # Weights: Thread Crash, App Crash, Memory Leak, Watchdog, CAN, SW Update, Kernel Panic, File System, Network, Hardware, Unknown, No Issue
        weights = [0.12, 0.08, 0.12, 0.12, 0.08, 0.08, 0.05, 0.08, 0.08, 0.05, 0.08, 0.06]
        error_type = random.choices(error_types, weights=weights)[0]
        
        sw_version = random.choice(SW_VERSIONS)
        platform = random.choice(PLATFORMS)
        
        log_content = generate_log_content(error_type, sw_version, platform)
        metadata = generate_metadata()
        
        data.append({
            'log_id': f'LOG_{i:05d}',
            'log_content': log_content,
            'root_cause': error_type,
            'severity': ERROR_PATTERNS[error_type]['severity'],
            'sw_version': sw_version,
            'platform': platform,
            'has_missing_blocks': metadata['has_missing_blocks'],
            'has_overwritten': metadata['has_overwritten'],
            'log_size': metadata['log_size'],
            'component': random.choice(ERROR_PATTERNS[error_type]['components'])
        })
    
    df = pd.DataFrame(data)
    
    # Save to CSV
    output_path = 'data/synthetic_logs.csv'
    os.makedirs('data', exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"\n✓ Dataset saved to {output_path}")
    print(f"\nDataset Statistics:")
    print(f"Total samples: {len(df)}")
    print(f"\nRoot Cause Distribution:")
    print(df['root_cause'].value_counts())
    print(f"\nSeverity Distribution:")
    print(df['severity'].value_counts())
    print(f"\nPlatform Distribution:")
    print(df['platform'].value_counts())
    
    return df

if __name__ == '__main__':
    df = generate_dataset(1000)
    
    # Generate some sample log files
    print("\nGenerating sample log files...")
    os.makedirs('data/sample_logs', exist_ok=True)
    
    for i in range(10):
        sample = df.iloc[i]
        filename = f"data/sample_logs/{sample['log_id']}_{sample['root_cause'].replace(' ', '_')}.log"
        with open(filename, 'w') as f:
            f.write(sample['log_content'])
    
    print(f"✓ Sample log files saved to data/sample_logs/")
