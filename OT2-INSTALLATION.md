# Prefect Installation for OT-2

This guide explains how to install and use Prefect on the Opentrons OT-2 system.

## Quick Installation

### Method 1: All-in-One Python Script (Recommended for OT-2)

Download and run the automated installer:

```python
# Download the installer
curl -L https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/79767ae/ot2_prefect_installer.py -o ot2_prefect_installer.py

# Run the installer
python ot2_prefect_installer.py
```

This script will:
1. Download the pendulum dependency wheel
2. Install pendulum
3. Download the Prefect wheel
4. Install Prefect
5. Test both imports and run a basic workflow
6. Clean up temporary files

### Method 2: Manual Installation

If you prefer manual control:

```python
# Step 1: Download the Python installer
curl -L https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/79767ae/install.py -o install.py

# Step 2: Install pendulum (Prefect dependency)
python install.py pendulum

# Step 3: Install Prefect
python install.py prefect

# Step 4: Test the installation
python -c "import prefect; print('Prefect version:', prefect.__version__)"
```

### Method 3: Direct Wheel Installation

For systems without curl or for debugging:

```python
# Download wheels manually or use wget if available
# Then install directly:

python -m pip install pendulum-3.1.0-cp310-cp310-linux_armv7l.whl
python -m pip install prefect-3.3.4-py3-none-any.whl
```

## Available Wheels

This repository provides pre-built wheels for ARMv7l (OT-2 architecture):

- `pendulum-3.1.0-cp310-cp310-linux_armv7l.whl` (116KB)
- `prefect-3.3.4-py3-none-any.whl` (5.8MB)
- `pandas-1.5.0-cp310-cp310-linux_armv7l.whl` (14MB)

## Basic Usage Example

Once installed, you can use Prefect in your OT-2 scripts:

```python
from prefect import flow, task

@task
def prepare_plate():
    print("Preparing plate...")
    # Your OT-2 plate preparation code here
    return "Plate ready"

@task  
def run_protocol(plate_status):
    print(f"Running protocol with {plate_status}")
    # Your OT-2 protocol code here
    return "Protocol completed"

@flow
def ot2_workflow():
    plate = prepare_plate()
    result = run_protocol(plate)
    print(f"Workflow finished: {result}")
    return result

# Run the workflow
if __name__ == "__main__":
    ot2_workflow()
```

## Troubleshooting

### Import Errors

If you get import errors:

1. **Check Python version**: Ensure you're using Python 3.10
   ```python
   python --version
   ```

2. **Verify installation**: 
   ```python
   python -c "import pendulum; print('Pendulum OK')"
   python -c "import prefect; print('Prefect OK')"
   ```

3. **Check wheel compatibility**:
   ```python
   python -c "import platform; print('Architecture:', platform.machine())"
   ```
   Should show `armv7l` for OT-2

### Download Issues

If downloads fail:

1. **Check network connectivity**:
   ```python
   curl -I https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/79767ae/wheels/prefect-3.3.4-py3-none-any.whl
   ```

2. **Use alternative download method**:
   ```python
   python -c "
   import urllib.request
   urllib.request.urlretrieve(
       'https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/79767ae/wheels/prefect-3.3.4-py3-none-any.whl',
       'prefect.whl'
   )
   print('Downloaded successfully')
   "
   ```

### Permission Issues

If you get permission errors:

```python
python -m pip install --user wheel_file.whl
```

## System Requirements

- **Architecture**: ARMv7l (Raspberry Pi 3B+)
- **Python**: 3.10+
- **OS**: Opentrons custom firmware
- **Network**: Internet access for initial download
- **Storage**: ~20MB free space for all wheels

## Background

This solution addresses the complexity of installing Prefect on OT-2 systems where:

- Standard pip install fails due to compilation requirements
- pendulum (Prefect dependency) requires Rust compilation 
- ARMv7l wheels are not readily available
- Limited system tools (no git, bash, venv)

The pre-built wheels in this repository eliminate these issues by providing compatible binaries.

## Support

If you encounter issues:

1. Check that you're on an ARMv7l system (OT-2)
2. Verify Python 3.10 is being used
3. Ensure network connectivity to GitHub
4. Try the automated installer first before manual methods

For additional help, refer to the repository issues or documentation.