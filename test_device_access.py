#!/usr/bin/env python3
"""
Minimal test to verify device access and validate Prefect installation.
"""

import subprocess
import sys

def test_device_connectivity():
    """Test if we can connect to the fresh OT-2 device."""
    devices = ["100.101.232.60", "ot2-simulator-9d169e.tail6a1dd7.ts.net"]
    
    for device in devices:
        print(f"Testing connectivity to {device}...")
        
        # Test SSH directly (ping might be blocked)
        try:
            result = subprocess.run(['ssh', '-o', 'ConnectTimeout=10', '-o', 'StrictHostKeyChecking=no',
                                   f'root@{device}', 'echo "Connected"'], 
                                  capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                print("✓ SSH connection successful")
                return device
            else:
                print(f"✗ SSH connection failed: {result.stderr.strip()}")
                continue
        except subprocess.TimeoutExpired:
            print("✗ SSH timeout")
            continue
    
    return None

def validate_prefect_installation(device_ip):
    """Validate Prefect installation on the device."""
    commands = [
        "python3 -c 'import prefect; print(f\"Prefect {prefect.__version__} installed\")'",
        "prefect version",
        "python3 -c 'from prefect import flow, task; print(\"Prefect decorators working\")'"
    ]
    
    for cmd in commands:
        try:
            result = subprocess.run(['ssh', '-o', 'ConnectTimeout=10', 
                                   f'root@{device_ip}', cmd], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"✓ {cmd[:50]}... - {result.stdout.strip()}")
            else:
                print(f"✗ {cmd[:50]}... - Failed: {result.stderr.strip()}")
                return False
        except subprocess.TimeoutExpired:
            print(f"✗ {cmd[:50]}... - Timeout")
            return False
    
    return True

if __name__ == "__main__":
    device = test_device_connectivity()
    if device:
        print(f"\nDevice {device} accessible. Testing Prefect installation...")
        if validate_prefect_installation(device):
            print("\n✓ All tests passed!")
            sys.exit(0)
        else:
            print("\n✗ Prefect validation failed")
            sys.exit(1)
    else:
        print("\n✗ Cannot connect to any device")
        sys.exit(1)