"""
Platform abstraction layer for cross-platform (Windows/Linux) support
Handles platform-specific tool paths and operations
"""
import platform
import os
from pathlib import Path


class PlatformTools:
    """Provides platform-specific tool paths and utilities"""
    
    def __init__(self):
        self.os_type = platform.system()  # 'Windows', 'Linux', 'Darwin'
        self.is_windows = self.os_type == 'Windows'
        self.is_linux = self.os_type == 'Linux'
    
    def get_decoder_path(self):
        """Get path to binary decoder tool"""
        if self.is_windows:
            return os.path.join('exes', 'Decoder.exe')
        elif self.is_linux:
            return os.path.join('exes', 'decoder')  # Linux binary
        else:
            raise OSError(f"Unsupported platform: {self.os_type}")
    
    def get_trc_extractor_path(self):
        """Get path to TRC extraction tool"""
        if self.is_windows:
            return os.path.join('exes', 'ExtractTrcFiles.exe')
        elif self.is_linux:
            return os.path.join('exes', 'extract_trc')
        else:
            raise OSError(f"Unsupported platform: {self.os_type}")
    
    def get_geckodriver_path(self):
        """Get path to geckodriver for Selenium"""
        if self.is_windows:
            return os.path.join('exes', 'geckodriver.exe')
        elif self.is_linux:
            return os.path.join('exes', 'geckodriver')
        else:
            raise OSError(f"Unsupported platform: {self.os_type}")
    
    def get_dlt_converter_path(self):
        """Get path to DLT converter tool"""
        if self.is_windows:
            # Windows may use dlt-convert.exe or rely on installed version
            return 'dlt-convert.exe'
        elif self.is_linux:
            # Linux typically uses system-installed dlt-convert
            return 'dlt-convert'
        else:
            raise OSError(f"Unsupported platform: {self.os_type}")
    
    def get_gdb_path(self):
        """Get path to GDB debugger (Linux) or equivalent debugger"""
        if self.is_linux:
            return 'gdb'  # System-installed
        elif self.is_windows:
            # Windows can use cdb.exe (part of Debugging Tools for Windows)
            return 'cdb.exe'
        else:
            raise OSError(f"Unsupported platform: {self.os_type}")
    
    def normalize_path(self, path):
        """Convert any path to OS-appropriate format"""
        # Replace backslashes with forward slashes, then use os.path.normpath
        normalized = path.replace('\\', os.sep).replace('/', os.sep)
        return os.path.normpath(normalized)
    
    def join_path(self, *parts):
        """Join path components in OS-appropriate way"""
        return os.path.join(*parts)
    
    def ensure_dir_exists(self, path):
        """Create directory if it doesn't exist"""
        os.makedirs(path, exist_ok=True)
        return path


# Global instance
platform_tools = PlatformTools()
