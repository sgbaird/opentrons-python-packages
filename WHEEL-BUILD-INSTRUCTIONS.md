# Essential Wheel Build Instructions

This document provides step-by-step instructions for building the three essential wheels required for Prefect on OT-2.

## Overview

The three essential wheels are:
- `pendulum-3.1.0-cp310-cp310-linux_armv7l.whl` - Date/time library (cross-compiled)
- `ujson-5.10.0-py3-none-linux_armv7l.whl` - JSON encoder/decoder (fallback implementation)
- `prefect-3.3.4-py3-none-any.whl` - Prefect workflow engine (pure Python)

## Prerequisites

- Docker for cross-compilation environment
- Python 3.10+
- Access to the build tools in this repository

## Build Environment Setup

### 1. Cross-Compilation Environment

The repository includes a cross-compilation toolchain for ARMv7l builds:

```bash
# Clone the repository
git clone https://github.com/sgbaird/opentrons-python-packages.git
cd opentrons-python-packages

# Build the cross-compilation container
cd tools
python3 -m builder.container build
```

## Building Individual Wheels

### 1. Pendulum Wheel (Cross-compiled)

Pendulum requires Rust compilation for ARMv7l architecture:

```bash
# Use the existing build script
python3 build-packages packages/pendulum/3.1.0
```

**Alternative manual build:**
```bash
# Set up cross-compilation environment
export TARGET_ARCH=armv7l
export CARGO_TARGET_ARMV7_UNKNOWN_LINUX_GNUEABIHF_LINKER=arm-linux-gnueabihf-gcc

# Clone pendulum source
git clone https://github.com/sdispater/pendulum.git
cd pendulum
git checkout 3.1.0

# Install Rust and add ARM target
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup target add armv7-unknown-linux-gnueabihf

# Build wheel with maturin
pip install maturin
maturin build --target armv7-unknown-linux-gnueabihf --release
```

### 2. Prefect Wheel (Pure Python)

Prefect is pure Python but uses the build system for consistency:

```bash
# Use the existing build script
python3 build-packages packages/prefect/3.3.4
```

**Alternative manual build:**
```bash
# Clone prefect source
git clone https://github.com/PrefectHQ/prefect.git
cd prefect
git checkout 3.3.4

# Build wheel
python3 setup.py bdist_wheel --plat-name linux_armv7l
```

### 3. ujson Wheel (Fallback Implementation)

The ujson wheel is a special case - it's a minimal fallback implementation that provides the ujson interface without C extensions:

#### Option A: Create Minimal ujson Fallback

```bash
# Create minimal ujson implementation
mkdir ujson_fallback
cd ujson_fallback

cat > ujson.py << 'EOF'
"""
Minimal ujson fallback for ARM environments where compilation fails.
Provides ujson interface using standard library json.
"""
import json

# Expose standard json functions with ujson names
dumps = json.dumps
loads = json.loads
dump = json.dump
load = json.load

# ujson-specific interface
def encode(obj, **kwargs):
    return json.dumps(obj, **kwargs)

def decode(s, **kwargs):
    return json.loads(s, **kwargs)

__version__ = "5.10.0"
EOF

cat > setup.py << 'EOF'
from setuptools import setup

setup(
    name="ujson",
    version="5.10.0",
    py_modules=["ujson"],
    description="Minimal ujson fallback for ARM",
    python_requires=">=3.7",
)
EOF

# Build the wheel
python3 setup.py bdist_wheel --plat-name linux_armv7l
```

#### Option B: Cross-compile ujson (Advanced)

```bash
# This requires setting up cross-compilation toolchain
export CC=arm-linux-gnueabihf-gcc
export CXX=arm-linux-gnueabihf-g++

git clone https://github.com/ultrajson/ultrajson.git
cd ultrajson
git checkout v5.10.0

# Install cross-compilation dependencies
sudo apt-get install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf

# Build wheel
python3 setup.py bdist_wheel --plat-name linux_armv7l
```

## Automated Build Process

For reproducible builds, use the repository's build system:

```bash
# Build all essential wheels
python3 build-packages packages/pendulum/3.1.0
python3 build-packages packages/prefect/3.3.4

# For ujson, use the fallback method above or:
# (if a build script exists)
python3 build-packages packages/ujson/5.10.0
```

## Verification

After building, verify the wheels:

```bash
# Check wheel contents
unzip -l pendulum-3.1.0-cp310-cp310-linux_armv7l.whl
unzip -l ujson-5.10.0-py3-none-linux_armv7l.whl  
unzip -l prefect-3.3.4-py3-none-any.whl

# Test installation (on ARM environment)
pip install pendulum-3.1.0-cp310-cp310-linux_armv7l.whl
python3 -c "import pendulum; print(pendulum.now())"

pip install ujson-5.10.0-py3-none-linux_armv7l.whl
python3 -c "import ujson; print(ujson.dumps({'test': True}))"

pip install prefect-3.3.4-py3-none-any.whl
python3 -c "from prefect import flow, task; print('Prefect OK')"
```

## Key Points

1. **Pendulum** requires actual cross-compilation due to Rust components
2. **Prefect** is pure Python but benefits from controlled build environment  
3. **ujson** uses a fallback implementation to avoid C compilation issues on OT-2
4. All wheels use `linux_armv7l` platform tag for OT-2 compatibility

## Troubleshooting

### Compilation Errors
- Ensure cross-compilation toolchain is properly installed
- Check that target architecture environment variables are set
- For Rust components, verify ARM target is added to rustup

### Size Issues
- If wheels are too large, check for debug symbols
- Consider using `--strip` flags during compilation
- Verify only necessary components are included

### Compatibility Issues
- Test wheels on actual OT-2 hardware or simulator
- Verify Python version compatibility (3.10)
- Check for missing shared library dependencies

This build process ensures that all essential wheels are reproducible and compatible with the OT-2's ARMv7l architecture.