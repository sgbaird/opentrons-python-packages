# Pre-built Python Wheels

This directory contains pre-built Python wheel files for arm7hf architecture that can be directly downloaded and installed on OT-2 systems.

## Quick Installation

Download and install directly:

```bash
# Example: Install prefect
curl -L https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/wheels/prefect-3.3.4-py3-none-any.whl -o /tmp/prefect.whl
pip install /tmp/prefect.whl

# Example: Install pandas
curl -L https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/wheels/pandas-1.5.0-cp310-cp310-linux_armv7l.whl -o /tmp/pandas.whl
pip install /tmp/pandas.whl

# Example: Install pendulum (Prefect dependency) - for ARMv7l (Opentrons OT-2)
curl -L https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/wheels/pendulum-3.1.0-cp310-cp310-linux_armv7l.whl -o /tmp/pendulum.whl
pip install /tmp/pendulum.whl

# Alternative: Direct pip install from GitHub (single command)
pip install https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/wheels/pendulum-3.1.0-cp310-cp310-linux_armv7l.whl
```

## Available Packages

- `pandas-1.5.0-cp310-cp310-linux_armv7l.whl` - Pandas data analysis library (compiled for ARMv7l/Opentrons OT-2) - 14MB
- `prefect-3.3.4-py3-none-any.whl` - Prefect workflow orchestration framework (pure Python) - 5.8MB  
- `pendulum-3.1.0-cp310-cp310-linux_armv7l.whl` - Date/time manipulation library (ARMv7l-compatible) - 113KB
- `pendulum-3.1.0-py3-none-any.whl` - Date/time manipulation library (universal Python wheel) - 109KB
- `pendulum-3.1.0-cp310-cp310-manylinux_2_17_aarch64.manylinux2014_aarch64.whl` - Date/time library (compiled for aarch64/ARM64) - 336KB

All wheels are ready for immediate download and installation.

## Purpose

These wheels are provided as a backup when CI-built artifacts are not available or accessible. They are built using the same cross-compilation process as the automated CI system.

## Updating

Wheels in this directory are updated when:
1. New package versions are added
2. CI builds complete successfully and produce new wheels
3. Manual updates are needed for critical fixes

Last updated: Simplified CI implementation
Built from: Current commit with consolidated CI workflows