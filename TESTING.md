# Testing Prefect Installation on OT-2

This minimal testing approach validates the Prefect installation instructions.

## Quick Test

```bash
python3 test_device_access.py
```

This script:
1. Tests connectivity to the fresh OT-2 device (100.101.232.60)
2. Validates Prefect installation if device is accessible

## Manual Testing

If automated test fails, manually test with:

```bash
# Test SSH connection
ssh root@100.101.232.60 "echo 'Connected'"

# Check Prefect installation
ssh root@100.101.232.60 "python3 -c 'import prefect; print(prefect.__version__)'"
ssh root@100.101.232.60 "prefect version"
```

## Installation Guide

Follow the existing installation guide: `OT2-PREFECT-INSTALLATION-GUIDE.md`