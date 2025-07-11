#!/usr/bin/env python3
"""
Create regex fallback wheel for OT-2 environments where C compilation fails.

This creates a minimal regex implementation that provides the regex interface
using Python's standard library re module for basic functionality.
"""

import os
import tempfile
import subprocess
import shutil
from pathlib import Path

def create_regex_fallback():
    """Create a minimal regex fallback wheel"""
    
    # Create temporary directory for wheel building
    with tempfile.TemporaryDirectory() as tmpdir:
        pkg_dir = Path(tmpdir) / "regex_package"
        pkg_dir.mkdir()
        
        # Create minimal regex.py
        regex_py = pkg_dir / "regex.py"
        regex_py.write_text('''"""
Minimal regex fallback for ARM environments where compilation fails.
Provides regex interface using standard library re for basic functionality.
"""
import re
import warnings

# Show warning when using fallback
warnings.warn("Using regex fallback implementation with standard re module. "
              "Some advanced regex features may not be available.", 
              RuntimeWarning, stacklevel=2)

# Map regex functions to standard re equivalents
compile = re.compile
search = re.search
match = re.match
fullmatch = re.fullmatch
split = re.split
findall = re.findall
finditer = re.finditer
sub = re.sub
subn = re.subn
escape = re.escape
purge = re.purge

# regex flags - map to standard re flags where possible
A = ASCII = re.ASCII
I = IGNORECASE = re.IGNORECASE
L = LOCALE = re.LOCALE
M = MULTILINE = re.MULTILINE
S = DOTALL = re.DOTALL
X = VERBOSE = re.VERBOSE

# Additional regex-specific flags that don't exist in re
# Set to 0 so they can be used but have no effect
FULLCASE = 0
POSIX = 0
UNICODE = 0
V0 = 0
V1 = 0
VERSION0 = 0
VERSION1 = 0

# regex exceptions - use standard re exceptions
error = re.error

# Version info
__version__ = "2024.7.24"

class Pattern:
    """Wrapper for re.Pattern to provide regex interface"""
    def __init__(self, pattern):
        self._pattern = pattern
    
    def __getattr__(self, name):
        return getattr(self._pattern, name)

def regex_compile(pattern, flags=0, **kwargs):
    """Compile regex pattern with fallback to re.compile"""
    # Filter out regex-specific flags that don't exist in re
    re_flags = flags
    for flag in [FULLCASE, POSIX, UNICODE, V0, V1, VERSION0, VERSION1]:
        re_flags &= ~flag
    
    compiled = re.compile(pattern, re_flags)
    return Pattern(compiled)

# Override compile to use our wrapper
compile = regex_compile
''')
        
        # Create setup.py
        setup_py = pkg_dir / "setup.py"
        setup_py.write_text('''from setuptools import setup

setup(
    name="regex",
    version="2024.7.24", 
    py_modules=["regex"],
    description="Minimal regex fallback for ARM environments",
    long_description="Fallback regex implementation using standard library re",
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers", 
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8", 
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
''')
        
        # Build the wheel
        print("Building regex fallback wheel...")
        old_cwd = os.getcwd()
        try:
            os.chdir(pkg_dir)
            result = subprocess.run([
                "python3", "setup.py", "bdist_wheel", 
                "--plat-name", "linux_armv7l"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Find the created wheel
                dist_dir = pkg_dir / "dist"
                wheels = list(dist_dir.glob("*.whl"))
                if wheels:
                    wheel_path = wheels[0]
                    print(f"✅ Created wheel: {wheel_path.name}")
                    
                    # Copy to current directory
                    output_path = Path(old_cwd) / wheel_path.name
                    shutil.copy2(wheel_path, output_path)
                    print(f"✅ Copied to: {output_path}")
                    return output_path
                else:
                    print("❌ No wheel file found in dist/")
                    return None
            else:
                print(f"❌ Build failed: {result.stderr}")
                return None
                
        finally:
            os.chdir(old_cwd)

if __name__ == "__main__":
    wheel_path = create_regex_fallback()
    if wheel_path:
        print(f"\n🎉 regex fallback wheel created successfully: {wheel_path}")
        print("\nTest the wheel:")
        print(f"pip install {wheel_path}")
        print('python3 -c "import regex; print(regex.search(r\'test\', \'testing\'))"')
    else:
        print("\n❌ Failed to create regex fallback wheel")