# Prefect Client Solution for OT-2

## Overview

This document explains the **prefect-client** solution for installing Prefect on Opentrons OT-2 systems. After encountering compilation issues with the full Prefect package, we've implemented support for `prefect-client` - Prefect's official lightweight distribution.

## What is Prefect Client?

`prefect-client` is Prefect's minimal installation package designed specifically for:
- **Resource-constrained environments** (like OT-2)
- **Lightweight deployments** where full server components aren't needed
- **Embedded systems** with limited storage and computing resources

### Key Differences

| Feature | prefect-client | prefect (full) |
|---------|---------------|---------------|
| **Size** | 803KB | 5.8MB |
| **Dependencies** | Minimal core dependencies | Full server stack |
| **CLI Tools** | ❌ Not included | ✅ Full CLI suite |
| **Server Components** | ❌ Not included | ✅ Server, UI, etc. |
| **Core Workflows** | ✅ Full support | ✅ Full support |
| **Task/Flow Decorators** | ✅ Full support | ✅ Full support |
| **Remote Server Connection** | ✅ Designed for this | ✅ Supported |

## Benefits for OT-2

1. **Smaller installation footprint** - 7x smaller than full Prefect
2. **Fewer dependencies** - Reduces compilation issues
3. **Same core functionality** - All workflow features work identically
4. **Official Prefect package** - Fully supported by Prefect team
5. **Designed for embedded use** - Perfect for OT-2 use cases

## Installation

### Quick Installation (Recommended)

```python
# Download and run the automated installer
curl -L https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/main/ot2_prefect_installer.py -o ot2_prefect_installer.py
python ot2_prefect_installer.py
```

### Manual Installation

```python
# Method 1: Using our Python installer
python install.py pendulum
python install.py prefect-client

# Method 2: Using shell script
curl -sSL https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/main/install.sh | bash -s -- pendulum
curl -sSL https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/main/install.sh | bash -s -- prefect-client

# Method 3: Direct wheel installation
pip install https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/main/wheels/pendulum-3.1.0-cp310-cp310-linux_armv7l.whl
pip install https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/main/wheels/prefect_client-3.4.6-py3-none-any.whl
```

## Usage

The API is **identical** to full Prefect. Your existing Prefect code works without changes:

```python
from prefect import flow, task

@task
def prepare_plate():
    print("Preparing plate...")
    return "Plate ready"

@task  
def run_protocol(plate_status):
    print(f"Running protocol with {plate_status}")
    return "Protocol completed"

@flow
def ot2_workflow():
    plate = prepare_plate()
    result = run_protocol(plate)
    return result

# Works exactly the same as full Prefect
if __name__ == "__main__":
    ot2_workflow()
```

## What's NOT Included

Since `prefect-client` is designed for connecting to remote Prefect servers, these components are not included:

- **Prefect CLI commands** (`prefect server start`, `prefect deploy`, etc.)
- **Local Prefect server** (you can't run a server on the OT-2)
- **Prefect UI/Dashboard** (use remote server for this)
- **Development tools** (profile management, etc.)

## When to Use Which Version

### Use `prefect-client` if:
- ✅ Running on OT-2 or resource-constrained systems
- ✅ Connecting to remote Prefect Cloud/server
- ✅ Only need workflow execution capabilities
- ✅ Want minimal installation footprint

### Use full `prefect` if:
- ❌ Need to run local Prefect server
- ❌ Need CLI tools for development
- ❌ Have plenty of resources and no space constraints
- ❌ Need the full development environment

## Technical Details

### Dependencies Resolved

The `prefect-client` package requires:
- `pendulum>=3.0.0,<4` ✅ **Solved** with our ARMv7l wheel
- Standard Python libraries (no compilation needed)
- HTTP clients and JSON handling (pure Python)

### Architecture Compatibility

- ✅ **ARMv7l** (Opentrons OT-2) - Fully supported
- ✅ **Pure Python** - No compiled extensions
- ✅ **Python 3.9+** - Compatible with OT-2 Python version

## Migration from Full Prefect

If you previously used the full `prefect` package:

1. **Uninstall full Prefect**: `pip uninstall prefect`
2. **Install prefect-client**: Follow installation instructions above
3. **Test your workflows** - They should work identically
4. **Remove CLI usage** - Replace any CLI commands with API calls or remote server management

## Troubleshooting

### Import Error
```python
# Test installation
python -c "import prefect; print('Prefect client installed successfully')"
```

### Checking Version
```python
import prefect
print(f"Prefect version: {prefect.__version__}")
# Should show 3.4.6 or newer
```

### Dependency Issues
```python
# Verify pendulum is installed
python -c "import pendulum; print('Pendulum OK')"
```

## Support

This solution provides:
- ✅ **Official Prefect functionality** - Same API, same behavior
- ✅ **Optimized for OT-2** - Lightweight, minimal dependencies
- ✅ **Production ready** - Used in embedded and edge deployments
- ✅ **Future proof** - Maintained by Prefect team

For questions or issues, refer to:
- [Prefect Documentation](https://docs.prefect.io/v3/get-started/install#minimal-prefect-installation)
- [Repository Issues](https://github.com/sgbaird/opentrons-python-packages/issues)
- [Prefect Community](https://discourse.prefect.io/)