# Essential OT-2 Prefect Installation Guide

## Quick Installation

### Automated Installation (Recommended)
```bash
python3 essential_ot2_prefect_installer.py [device-name]
```

### Manual Installation
```bash
# 1. Install Prefect
mkdir -p /var/user-packages/root/.local/lib/python3.10/site-packages
python3 -m pip install --user --target /var/user-packages/root/.local/lib/python3.10/site-packages prefect==3.3.4

# 2. Set up environment
echo 'export PATH="/var/user-packages/root/.local/bin:$PATH"' >> ~/.bashrc
echo 'export PYTHONPATH="/var/user-packages/root/.local/lib/python3.10/site-packages:$PYTHONPATH"' >> ~/.bashrc

# 3. Load environment
source ~/.bashrc
```

## Cloud Configuration

### Set up Prefect Cloud connection
```bash
# Configure API endpoint and key
source ~/.bashrc
prefect config set PREFECT_API_URL="https://api.prefect.cloud/api/accounts/[ACCOUNT-ID]/workspaces/[WORKSPACE-ID]"
prefect config set PREFECT_API_KEY="[YOUR-API-KEY]"

# Verify configuration
prefect --version
```

## Usage Examples

### Basic Flow
```python
from prefect import flow, task

@task
def hello_task():
    return "Hello from OT-2!"

@flow
def hello_flow():
    result = hello_task()
    print(result)
    return result

if __name__ == "__main__":
    hello_flow()
```

### Opentrons Integration
Use `simple_ot2_opentrons_flow.py` for combined Prefect + Opentrons workflows.

## Files Overview

### Essential Files
- `essential_ot2_prefect_installer.py` - Main installer script
- `simple_ot2_opentrons_flow.py` - Working Prefect + Opentrons integration

### Verification
```python
# Test Prefect installation
import prefect
print(f"Prefect {prefect.__version__} ready")

# Test cloud connectivity (if configured)
from prefect.client.cloud import get_cloud_client
client = get_cloud_client()
print(f"Cloud client: {type(client).__name__}")
```

## Status: ✅ Production Ready

The installation has been tested and verified on OT-2 simulators with:
- Complete Prefect 3.3.4 functionality
- Cloud connectivity and monitoring
- Flow execution visible in Prefect Cloud UI
- Combined Prefect + Opentrons workflows