"""
Log Type Handlers for different log file formats
Supports: .dlt, .txt, coredump/backtrace files
"""
import os
import subprocess
import shutil
from pathlib import Path
from Utils.platform_tools import platform_tools


class DLTLogHandler:
    """Handler for .dlt (Diagnostic Log and Trace) files"""
    
    def __init__(self, dlt_file_path):
        self.dlt_file = dlt_file_path
        self.dlt_converter = platform_tools.get_dlt_converter_path()
    
    def convert_to_text(self, output_path=None):
        """
        Convert .dlt to readable text format
        
        Args:
            output_path: Where to save converted file. If None, uses <input>.txt
        
        Returns:
            Path to converted text file
        """
        if output_path is None:
            output_path = self.dlt_file + '.txt'
        
        try:
            # Method 1: Try using dlt-convert command line tool
            cmd = [self.dlt_converter, '-a', self.dlt_file, '-o', output_path]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✓ Successfully converted {self.dlt_file} to text format")
            return output_path
        
        except FileNotFoundError:
            print(f"Warning: dlt-convert not found. Trying python-dlt library...")
            # Method 2: Try using python-dlt library
            try:
                return self._convert_with_python_dlt(output_path)
            except ImportError:
                print("Error: python-dlt library not installed. Install with: pip install python-dlt")
                raise
        
        except subprocess.CalledProcessError as e:
            print(f"Error converting DLT file: {e.stderr}")
            # Try python library as fallback
            return self._convert_with_python_dlt(output_path)
    
    def _convert_with_python_dlt(self, output_path):
        """Fallback method using python-dlt library"""
        try:
            import dlt
            # Read DLT file and convert to text
            # Note: Actual implementation depends on python-dlt API
            with open(output_path, 'w', encoding='utf-8') as out_f:
                # Simplified - actual implementation may vary
                out_f.write(f"# Converted from {self.dlt_file}\n")
                # TODO: Implement actual python-dlt parsing
            return output_path
        except Exception as e:
            print(f"Error using python-dlt: {e}")
            raise
    
    def extract_traces(self):
        """
        Extract trace patterns from DLT file
        Returns path to converted text file for analysis
        """
        text_log = self.convert_to_text()
        return text_log
    
    def validate(self):
        """Check if DLT file is valid"""
        if not os.path.exists(self.dlt_file):
            return False, "File does not exist"
        
        # Check file size
        file_size = os.path.getsize(self.dlt_file)
        if file_size == 0:
            return False, "File is empty"
        
        # Basic DLT file header check (DLT files start with "DLT\x01")
        try:
            with open(self.dlt_file, 'rb') as f:
                header = f.read(4)
                if header[:3] == b'DLT':
                    return True, "Valid DLT file"
                else:
                    return False, "Invalid DLT header"
        except Exception as e:
            return False, f"Error reading file: {e}"


class TextLogHandler:
    """Handler for plain .txt log files"""
    
    def __init__(self, txt_file_path):
        self.txt_file = txt_file_path
    
    def validate_format(self):
        """
        Check if text log is in expected format
        Returns (bool, str): (is_valid, message)
        """
        if not os.path.exists(self.txt_file):
            return False, "File does not exist"
        
        # Check file size
        file_size = os.path.getsize(self.txt_file)
        if file_size == 0:
            return False, "File is empty"
        
        try:
            # Try to read first few lines to check encoding and format
            with open(self.txt_file, 'r', encoding='utf-8', errors='ignore') as f:
                first_lines = [f.readline() for _ in range(5)]
                
            # Check if file has content
            if not any(line.strip() for line in first_lines):
                return False, "File appears to be empty or contains only whitespace"
            
            return True, "Valid text log file"
        
        except Exception as e:
            # Try with different encoding
            try:
                with open(self.txt_file, 'r', encoding='latin-1', errors='ignore') as f:
                    first_lines = [f.readline() for _ in range(5)]
                return True, "Valid text log file (alternate encoding)"
            except:
                return False, f"Error reading file: {e}"
    
    def extract_traces(self):
        """
        Text files can be processed directly
        Returns the file path itself
        """
        is_valid, message = self.validate_format()
        if is_valid:
            return self.txt_file
        else:
            raise ValueError(f"Invalid text file: {message}")
    
    def normalize_encoding(self, output_path=None):
        """
        Normalize encoding to UTF-8 if needed
        
        Args:
            output_path: Where to save normalized file. If None, overwrites original
        
        Returns:
            Path to normalized file
        """
        if output_path is None:
            output_path = self.txt_file + '.normalized.txt'
        
        try:
            # Read with fallback encodings
            content = None
            for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
                try:
                    with open(self.txt_file, 'r', encoding=encoding, errors='ignore') as f:
                        content = f.read()
                    break
                except:
                    continue
            
            if content:
                # Write as UTF-8
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return output_path
            else:
                raise ValueError("Could not read file with any known encoding")
        
        except Exception as e:
            print(f"Error normalizing encoding: {e}")
            raise


class CoredumpHandler:
    """Handler for coredump and backtrace files"""
    
    def __init__(self, core_file_path, binary_path=None):
        self.core_file = core_file_path
        self.binary_path = binary_path
        self.debugger = platform_tools.get_gdb_path()
    
    def extract_backtrace(self, output_path=None):
        """
        Extract backtrace from coredump using gdb (Linux) or cdb (Windows)
        
        Args:
            output_path: Where to save backtrace. If None, uses <input>.backtrace.txt
        
        Returns:
            Path to backtrace text file
        """
        if output_path is None:
            output_path = self.core_file + '.backtrace.txt'
        
        if platform_tools.is_linux:
            return self._extract_with_gdb(output_path)
        elif platform_tools.is_windows:
            return self._extract_with_cdb(output_path)
        else:
            raise OSError(f"Unsupported platform for coredump analysis: {platform_tools.os_type}")
    
    def _extract_with_gdb(self, output_path):
        """Extract backtrace using GDB (Linux)"""
        try:
            # Build GDB command
            if self.binary_path:
                # With binary for symbol resolution
                cmd = [
                    'gdb',
                    '-batch',
                    '-ex', 'thread apply all bt full',  # Get full backtrace for all threads
                    '-ex', 'info registers',  # Get register info
                    '-ex', 'quit',
                    self.binary_path,
                    self.core_file
                ]
            else:
                # Without binary (limited info)
                cmd = [
                    'gdb',
                    '-batch',
                    '-ex', 'bt',
                    '-ex', 'quit',
                    '-c', self.core_file
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # Write output
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# Backtrace extracted from: {self.core_file}\n")
                f.write(f"# Binary: {self.binary_path if self.binary_path else 'Not specified'}\n")
                f.write("=" * 80 + "\n\n")
                f.write(result.stdout)
                if result.stderr:
                    f.write("\n\n# STDERR:\n")
                    f.write(result.stderr)
            
            print(f"✓ Successfully extracted backtrace to {output_path}")
            return output_path
        
        except subprocess.TimeoutExpired:
            print("Error: GDB command timed out")
            raise
        except FileNotFoundError:
            print("Error: GDB not found. Install with: sudo apt-get install gdb")
            raise
        except Exception as e:
            print(f"Error extracting backtrace with GDB: {e}")
            raise
    
    def _extract_with_cdb(self, output_path):
        """Extract backtrace using CDB (Windows Debugger)"""
        try:
            # Windows debugger command
            cmd = [
                'cdb',
                '-z', self.core_file,  # Dump file
                '-c', 'kv; q'  # Stack trace and quit
            ]
            
            if self.binary_path:
                cmd.extend(['-y', os.path.dirname(self.binary_path)])  # Symbol path
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # Write output
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# Backtrace extracted from: {self.core_file}\n")
                f.write("=" * 80 + "\n\n")
                f.write(result.stdout)
            
            print(f"✓ Successfully extracted backtrace to {output_path}")
            return output_path
        
        except FileNotFoundError:
            print("Error: CDB not found. Install Debugging Tools for Windows")
            raise
        except Exception as e:
            print(f"Error extracting backtrace with CDB: {e}")
            raise
    
    def analyze_crash(self):
        """
        Analyze crash signature and stack trace
        Returns path to analyzed backtrace file
        """
        backtrace_file = self.extract_backtrace()
        return backtrace_file
    
    def validate(self):
        """Check if coredump file is valid"""
        if not os.path.exists(self.core_file):
            return False, "File does not exist"
        
        file_size = os.path.getsize(self.core_file)
        if file_size == 0:
            return False, "File is empty"
        
        # Check if it's likely a core dump (basic check)
        try:
            with open(self.core_file, 'rb') as f:
                header = f.read(4)
                # ELF core dumps start with 0x7f 'E' 'L' 'F'
                if header == b'\x7fELF':
                    return True, "Valid ELF core dump"
                # Windows minidumps start with 'MDMP'
                elif header == b'MDMP':
                    return True, "Valid Windows minidump"
                else:
                    # Could still be valid, just different format
                    return True, "File appears to be a dump file"
        except Exception as e:
            return False, f"Error reading file: {e}"


# Helper function to determine log type and get appropriate handler
def get_log_handler(file_path):
    """
    Factory function to get appropriate log handler based on file extension
    
    Args:
        file_path: Path to log file
    
    Returns:
        Appropriate handler instance (DLTLogHandler, TextLogHandler, or CoredumpHandler)
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.dlt':
        return DLTLogHandler(file_path)
    elif file_ext == '.txt':
        return TextLogHandler(file_path)
    elif file_ext in ['.core', '.dump', '.dmp']:
        return CoredumpHandler(file_path)
    elif 'backtrace' in file_path.lower() or 'coredump' in file_path.lower():
        return CoredumpHandler(file_path)
    else:
        raise ValueError(f"Unsupported log file type: {file_ext}")
