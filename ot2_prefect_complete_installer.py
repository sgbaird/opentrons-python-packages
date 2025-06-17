#!/usr/bin/env python3
"""
Complete Prefect Installation Script for OT-2
Resolves package version conflicts and installs all dependencies
"""

import subprocess
import sys
import os


def run_command(cmd, check=True):
    """Run command and return result"""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=check)
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        if result.stderr:
            print(f"Error: {result.stderr.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        if check:
            raise
        return e


def install_wheel(url, force=True, user=True):
    """Install a wheel with force and user flags"""
    cmd = [sys.executable, '-m', 'pip', 'install']
    
    if force:
        cmd.extend(['--force-reinstall', '--no-deps'])
    
    if user:
        cmd.append('--user')
    
    cmd.append(url)
    
    return run_command(cmd, check=False)


def main():
    print("=== OT-2 Complete Prefect Installation ===")
    print("Resolving package conflicts and installing all dependencies\n")
    
    # Base URL for wheels
    base_url = "https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/wheels/"
    
    # Core wheels to install with force upgrade
    wheels = [
        # Core dependencies that need force upgrade
        "ujson-5.10.0-py3-none-linux_armv7l.whl",
        "pendulum-3.1.0-cp310-cp310-linux_armv7l.whl", 
        "prefect_client-3.4.6-py3-none-any.whl",
    ]
    
    print("Phase 1: Installing core wheels with force upgrade...")
    for wheel in wheels:
        url = base_url + wheel
        print(f"\nInstalling {wheel}...")
        result = install_wheel(url, force=True, user=True)
        if result.returncode != 0:
            print(f"Warning: Failed to install {wheel}")
    
    print("\nPhase 2: Testing installation...")
    
    # Test core imports
    tests = [
        ("pendulum", "import pendulum; print('Pendulum version:', pendulum.__version__)"),
        ("ujson", "import ujson; print('ujson version:', ujson.__version__)"),
        ("prefect", "import prefect; print('Prefect version:', prefect.__version__)"),
        ("prefect.flow", "from prefect import flow; print('Flow import: SUCCESS')"),
        ("prefect.task", "from prefect import task; print('Task import: SUCCESS')"),
    ]
    
    for name, test_code in tests:
        print(f"\nTesting {name}...")
        result = run_command([sys.executable, '-c', test_code], check=False)
        if result.returncode == 0:
            print(f"✅ {name} working")
        else:
            print(f"❌ {name} failed")
    
    print("\nPhase 3: Testing flow creation...")
    flow_test = '''
from prefect import flow, task

@task
def say_hello(name: str):
    return f"Hello {name}!"

@flow 
def hello_flow(name: str = "OT-2"):
    message = say_hello(name)
    print(message)
    return message

if __name__ == "__main__":
    result = hello_flow()
    print(f"Flow result: {result}")
'''
    
    print("Creating and running test flow...")
    result = run_command([sys.executable, '-c', flow_test], check=False)
    if result.returncode == 0:
        print("✅ Flow creation and execution: SUCCESS")
        print("🎉 PREFECT FULLY WORKING ON OT-2!")
    else:
        print("❌ Flow creation failed")
        print("Attempting fallback installation...")
        
        # Fallback: try installing specific dependencies
        print("\nPhase 4: Installing additional dependencies...")
        additional_deps = [
            "pydantic>=2.0",
            "typing-extensions>=4.10.0"
        ]
        
        for dep in additional_deps:
            print(f"Installing {dep}...")
            cmd = [sys.executable, '-m', 'pip', 'install', '--user', '--upgrade', dep]
            result = run_command(cmd, check=False)
        
        # Re-test flow creation
        print("\nRe-testing flow creation...")
        result = run_command([sys.executable, '-c', flow_test], check=False)
        if result.returncode == 0:
            print("✅ Flow creation: SUCCESS after fallback")
            print("🎉 PREFECT FULLY WORKING ON OT-2!")
        else:
            print("❌ Flow creation still failing")
            print("Manual intervention may be required")


if __name__ == "__main__":
    main()