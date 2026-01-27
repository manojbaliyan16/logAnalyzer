"""
Pattern-based log analyzer (Traditional approach)
Uses regex and keyword matching
"""

import re

class PatternAnalyzer:
    def __init__(self):
        self.patterns = {
            'Thread Crash': [
                r'Crashed Thread',
                r'Stack Backtrace:',
                r'thread.*crashed',
                r'thread.*terminated.*unexpectedly',
                r'fatal.*exception.*thread'
            ],
            'Application Crash': [
                r'application.*crash',
                r'segmentation.*fault',
                r'core.*dump',
                r'fatal.*error'
            ],
            'Watchdog Timeout': [
                r'WATCHDOG_RESET',
                r'watchdog.*timeout',
                r'wdt.*triggered'
            ],
            'CAN Bus Error': [
                r'CAN.*error',
                r'bus.*off',
                r'frame.*transmission.*failed'
            ],
            'Kernel Panic': [
                r'kernel.*panic',
                r'NULL.*pointer.*dereference',
                r'system.*halted'
            ],
            'SW Update Failure': [
                r'update.*failed',
                r'flash.*write.*error',
                r'installation.*failed'
            ]
        }
    
    def analyze(self, log_content, metadata=None):
        """
        Analyze log using pattern matching
        
        Returns:
            {
                'root_cause': str or None,
                'confidence': float,
                'matched_patterns': list,
                'method': 'pattern'
            }
        """
        
        matched_patterns = []
        
        for cause, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, log_content, re.IGNORECASE):
                    matched_patterns.append({
                        'cause': cause,
                        'pattern': pattern
                    })
        
        if matched_patterns:
            # Return first match (can be improved with voting)
            root_cause = matched_patterns[0]['cause']
            confidence = 1.0  # Pattern matching is deterministic
            
            # Extract additional context
            explanation = self._extract_crash_details(log_content, root_cause)
            if not explanation:
                explanation = f"Matched pattern: {matched_patterns[0]['pattern']}"
            
            return {
                'root_cause': root_cause,
                'confidence': confidence,
                'matched_patterns': matched_patterns,
                'method': 'pattern',
                'severity': self._infer_severity(root_cause),
                'explanation': explanation
            }
        else:
            return {
                'root_cause': None,
                'confidence': 0.0,
                'matched_patterns': [],
                'method': 'pattern',
                'severity': 'UNKNOWN',
                'explanation': 'No known patterns matched'
            }
    
    def _extract_crash_details(self, log_content, root_cause):
        """Extract specific crash details from log"""
        details = []
        
        # Check if it's a crashed thread
        if re.search(r'Crashed Thread name::', log_content, re.IGNORECASE):
            # Look for Stack Backtrace section
            backtrace_match = re.search(r'Stack Backtrace:(.*?)(?=\n\d+\s+\d{4}/\d{2}/\d{2}.*?(?:log info|log warn|log debug|$))', log_content, re.DOTALL | re.IGNORECASE)
            
            if backtrace_match:
                backtrace = backtrace_match.group(1)
                
                # Find all modules with their full names from /tmpMCH/codeCache/
                # Pattern: /tmpMCH/codeCache/<full_module_name>.so(<function>...)
                module_pattern = r'/tmpMCH/codeCache/((?:com\.|stla\.|io\.)?[^/\s]+?)\.so\(([^)]+)?\)'
                module_matches = re.findall(module_pattern, backtrace)
                
                if module_matches:
                    # Take the LAST module in stack (deepest application code)
                    # Filter out system libraries (libc, libstdc++, etc.)
                    app_modules = [(mod, func) for mod, func in module_matches 
                                   if mod.startswith(('com.', 'stla.', 'io.'))]
                    
                    if app_modules:
                        module_name, function = app_modules[-1]  # Last/deepest call
                        
                        # Try to extract readable function name
                        func_info = ""
                        if function:
                            # Extract class/method from mangled name
                            # Pattern like: _ZN4Stla7AuthMgr7AuthMgr18AuthMgr_CfgMgrTaskEv
                            class_match = re.search(r'(\w+)(?:Mgr|Manager|Service|Task|Handler)', function)
                            if class_match:
                                func_info = f" in {class_match.group(0)}"
                        
                        return f"Module '{module_name}' is crashing{func_info}"
                    else:
                        # If only system libraries, take the first app module from full log
                        module_name = module_matches[0][0]
                        return f"Module '{module_name}' is crashing"
            
            # Fallback: search entire log for modules if backtrace extraction failed
            module_matches = re.findall(r'/tmpMCH/codeCache/((?:com\.|stla\.|io\.)?[^/\s]+?)\.so', log_content)
            if module_matches:
                # Prefer modules with our prefixes
                app_modules = [m for m in module_matches if any(m.startswith(p) for p in ['com.', 'stla.', 'io.'])]
                if app_modules:
                    module_name = app_modules[-1]  # Last occurrence
                else:
                    module_name = module_matches[-1]
                return f"Module '{module_name}' is crashing"
            
            # If no module found in codeCache, extract thread name
            thread_match = re.search(r'Crashed Thread name::\s*([A-Za-z0-9_]+)', log_content)
            if thread_match:
                thread_name = thread_match.group(1)
                return f"Thread '{thread_name}' crashed but module not identified"
        
        # Fallback: check for stack backtrace with modules even without explicit crash marker
        if re.search(r'Stack Backtrace:', log_content, re.IGNORECASE):
            module_matches = re.findall(r'/tmpMCH/codeCache/((?:com\.|stla\.|io\.)?[^/\s]+?)\.so', log_content)
            if module_matches:
                app_modules = [m for m in module_matches if any(m.startswith(p) for p in ['com.', 'stla.', 'io.'])]
                module_name = app_modules[-1] if app_modules else module_matches[-1]
                return f"Module '{module_name}' is crashing"
        
        # Extract process/application name
        app_match = re.search(r'(APPFWK_[A-Z_]+|[A-Z]+MGR|[A-Za-z]+Manager)', log_content)
        if app_match:
            app_name = app_match.group(1)
            if not any(app_name in d for d in details):
                details.append(f"Component: {app_name}")
        
        # Extract error type
        error_match = re.search(r'(segmentation fault|null pointer|memory corruption|stack overflow|deadlock)', log_content, re.IGNORECASE)
        if error_match:
            error_type = error_match.group(1)
            details.append(f"Error: {error_type}")
        
        if details:
            return " - ".join(details)
        return None
    
    def _infer_severity(self, root_cause):
        """Infer severity from root cause"""
        severity_map = {
            'Thread Crash': 'CRITICAL',
            'Application Crash': 'CRITICAL',
            'Watchdog Timeout': 'CRITICAL',
            'Kernel Panic': 'CRITICAL',
            'SW Update Failure': 'HIGH',
            'CAN Bus Error': 'MEDIUM',
            'Memory Leak': 'HIGH'
        }
        return severity_map.get(root_cause, 'MEDIUM')
    
    def analyze_file(self, file_path):
        """Analyze log from file"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            log_content = f.read()
        
        return self.analyze(log_content)
