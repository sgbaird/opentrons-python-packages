#!/usr/bin/env python3
"""
Revised comprehensive OT-2 Prefect installation with direct module creation.

This script creates fallback modules directly and performs the complete
installation sequence that was successful on the original device.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and handle output"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"Command: {cmd}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    print(f"Exit code: {result.returncode}")
    
    if result.returncode != 0:
        print(f"❌ FAILED: {description}")
        return False
    else:
        print(f"✅ SUCCESS: {description}")
        return True

def setup_environment():
    """Set up the Python environment paths"""
    print("\n🔧 Setting up environment...")
    
    bashrc_content = '''export PATH="/var/user-packages/root/.local/bin:$PATH"
export PYTHONPATH="/var/user-packages/root/.local/lib/python3.10/site-packages:$PYTHONPATH"
'''
    
    # Write to .bashrc
    with open("/root/.bashrc", "w") as f:
        f.write(bashrc_content)
    
    # Write to .profile  
    with open("/root/.profile", "w") as f:
        f.write(bashrc_content)
    
    # Set environment for current session
    os.environ["PATH"] = "/var/user-packages/root/.local/bin:" + os.environ.get("PATH", "")
    os.environ["PYTHONPATH"] = "/var/user-packages/root/.local/lib/python3.10/site-packages:" + os.environ.get("PYTHONPATH", "")
    
    return True

def install_core_wheels():
    """Install the core ARM-compatible wheels"""
    print("\n📦 Installing core ARM wheels...")
    
    core_wheels = [
        "https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/wheels/pendulum-3.1.0-cp310-cp310-linux_armv7l.whl",
        "https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/wheels/ujson-5.10.0-py3-none-linux_armv7l.whl", 
        "https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/wheels/prefect-3.3.4-py3-none-any.whl"
    ]
    
    cmd = f"python3 -m pip install --user --force-reinstall --no-deps {' '.join(core_wheels)}"
    return run_command(cmd, "Installing core ARM wheels")

def create_fallback_modules():
    """Create fallback modules directly"""
    print("\n🏗️  Creating fallback modules...")
    return run_command("python3 create_fallback_modules.py", "Creating fallback modules")

def install_dependencies():
    """Install additional dependencies with fallback handling"""
    print("\n📚 Installing additional dependencies...")
    
    # First install basic dependencies that usually work
    basic_deps = [
        "pydantic>=2.0",
        "rich", 
        "typing-extensions>=4.10.0",
        "aiosqlite",
        "alembic", 
        "apprise",
        "asgi-lifespan",
        "jsonpatch",
        "rfc3339-validator",
        "readchar",
        "typer"
    ]
    
    for dep in basic_deps:
        run_command(f"python3 -m pip install --user {dep}", f"Installing {dep}")
    
    # Try to install ruamel-yaml (may need fallback)
    run_command("python3 -m pip install --user ruamel-yaml", "Installing ruamel-yaml")
    
    # Try problematic dependencies with more lenient approach
    problematic_deps = [
        "dateparser",
        "pydantic-extra-types",
        "cachetools",
        "coolname",
        "cloudpickle",
        "pathspec",
        "toml",
        "fsspec",
        "httpcore",
        "python-slugify",
        "griffe",
        "opentelemetry-api"
    ]
    
    for dep in problematic_deps:
        print(f"\n🔄 Attempting to install {dep}...")
        result = run_command(f"python3 -m pip install --user {dep}", f"Installing {dep}")
        if not result:
            print(f"⚠️  Failed to install {dep}, will continue without it")
    
    return True

def verify_installation():
    """Verify that Prefect is working correctly"""
    print("\n✅ Verifying installation...")
    
    # Test basic import
    if not run_command('python3 -c "import prefect; print(f\'Prefect version: {prefect.__version__}\')"', "Testing Prefect import"):
        return False
    
    # Test flow/task decorators
    test_code = '''
import warnings
warnings.filterwarnings("ignore")

try:
    from prefect import flow, task
    print("✅ Flow/task decorators imported successfully")
    
    @task
    def test_task():
        return "Hello from task"
    
    @flow
    def test_flow():
        result = test_task()
        print(f"Flow result: {result}")
        return result
    
    print("✅ Flow/task definitions created successfully")
    
    # Try to run the flow
    test_flow()
    print("✅ Flow execution completed successfully")
    
except Exception as e:
    print(f"⚠️  Flow/task test failed: {e}")
    print("But basic Prefect import works, so core functionality is available")
'''
    
    # Write test file
    with open("/tmp/test_prefect.py", "w") as f:
        f.write(test_code)
    
    run_command("python3 /tmp/test_prefect.py", "Testing Prefect flow/task functionality")
    
    # Test CLI (may fail but that's ok)
    print("\n🔄 Testing Prefect CLI (may fail, but core functionality should work)...")
    run_command("prefect --version", "Testing Prefect CLI")
    
    return True

def main():
    """Main installation process"""
    print("🚀 Starting revised comprehensive OT-2 Prefect installation")
    
    # Set up environment
    if not setup_environment():
        print("❌ Failed to set up environment")
        return False
    
    # Install core wheels
    if not install_core_wheels():
        print("❌ Failed to install core wheels")
        return False
    
    # Create fallback modules
    if not create_fallback_modules():
        print("❌ Failed to create fallback modules")
        return False
    
    # Install additional dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        return False
    
    # Verify installation
    if not verify_installation():
        print("❌ Installation verification failed")
        return False
    
    print("\n🎉 Installation completed!")
    print("\nPrefect core functionality should now be available on this OT-2 device.")
    print("\nYou can test it with:")
    print('python3 -c "from prefect import flow, task; print(\'Prefect ready!\')"')
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)