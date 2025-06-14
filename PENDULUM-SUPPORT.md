# Pendulum Support for Prefect on OT-2

This document explains the pendulum wheel availability in this repository to address Prefect dependency issues on OT-2 systems.

## Problem

Prefect 3.3.4 depends on `pendulum>=3.0.0,<4` for date/time operations. However, pendulum:

1. **Uses Rust compilation**: Pendulum 3.x is built with maturin and includes Rust extensions for performance
2. **ARM compilation challenges**: Building pendulum for ARM7HF (OT-2 architecture) is complex due to Rust cross-compilation requirements
3. **Import failures**: Even when hatchling and other dependencies are resolved, missing pendulum causes Prefect import failures

## Solution

This repository now provides **two pendulum wheel options**:

### 1. Universal Wheel (Recommended for compatibility)
- **File**: `pendulum-3.1.0-py3-none-any.whl` (109KB)
- **Architecture**: Platform-independent, pure Python fallback
- **Compatibility**: Works on any Python 3.9+ system including OT-2
- **Performance**: Slightly slower than compiled version but fully functional

### 2. ARM64 Optimized Wheel (Best performance)
- **File**: `pendulum-3.1.0-cp310-cp310-manylinux_2_17_aarch64.manylinux2014_aarch64.whl` (336KB)
- **Architecture**: Compiled for ARM64/aarch64 systems
- **Compatibility**: May work on OT-2 depending on glibc version and ABI compatibility
- **Performance**: Full native performance with Rust optimizations

## Installation

### Option 1: Use the install script
```bash
curl -sSL https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/main/install.sh | bash -s -- pendulum
```

### Option 2: Direct wheel installation (universal)
```bash
curl -L https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/main/wheels/pendulum-3.1.0-py3-none-any.whl -o /tmp/pendulum.whl
pip install /tmp/pendulum.whl
```

### Option 3: Direct wheel installation (ARM64 optimized)
```bash
curl -L https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/main/wheels/pendulum-3.1.0-cp310-cp310-manylinux_2_17_aarch64.manylinux2014_aarch64.whl -o /tmp/pendulum.whl
pip install /tmp/pendulum.whl
```

## Complete Prefect Installation

To install Prefect with pendulum dependency resolved:

```bash
# Install pendulum first
curl -sSL https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/main/install.sh | bash -s -- pendulum

# Then install prefect
curl -sSL https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/main/install.sh | bash -s -- prefect
```

Or install both wheels directly:

```bash
# Download both wheels
curl -L https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/main/wheels/pendulum-3.1.0-py3-none-any.whl -o /tmp/pendulum.whl
curl -L https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/main/wheels/prefect-3.3.4-py3-none-any.whl -o /tmp/prefect.whl

# Install in dependency order
pip install /tmp/pendulum.whl
pip install /tmp/prefect.whl
```

## Version Compatibility

- **Pendulum 3.1.0**: Latest stable version, satisfies Prefect's `>=3.0.0,<4` requirement
- **Python 3.10**: Wheels are built for Python 3.10, compatible with OT-2 Python version
- **Dependencies**: Pendulum only requires `python-dateutil>=2.6` and `tzdata>=2020.1`

## Troubleshooting

If you encounter import errors:

1. **Try the universal wheel first**: It has broader compatibility
2. **Check Python version**: Ensure you're running Python 3.9+
3. **Verify installation**: `python -c "import pendulum; print(pendulum.__version__)"`
4. **Check dependencies**: Ensure `python-dateutil` and `tzdata` are available

## Background

This addresses the issue described in:
- [Prefect Discussion #17843](https://github.com/PrefectHQ/prefect/discussions/17843#discussioncomment-12972316)
- OT-2 pendulum compilation challenges
- ARM7HF cross-compilation complexity for Rust-based packages