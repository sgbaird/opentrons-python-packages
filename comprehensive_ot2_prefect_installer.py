#!/usr/bin/env python3
"""
Comprehensive OT-2 Prefect installation with fallback modules.

This script creates all necessary fallback wheels and performs the complete
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

def create_fallback_wheels():
    """Create all necessary fallback wheels"""
    print("\n🏗️  Creating fallback wheels...")
    
    # Build regex fallback
    if not run_command("python3 create_regex_fallback.py", "Building regex fallback wheel"):
        return False
    
    # Build ruamel.yaml.clib fallback
    if not run_command("python3 create_ruamel_yaml_clib_fallback.py", "Building ruamel.yaml.clib fallback wheel"):
        return False
    
    # Build ujson fallback
    if not run_command("python3 create_ujson_fallback.py", "Building ujson fallback wheel"):
        return False
    
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
    
    # Source the environment
    run_command("source /root/.bashrc", "Sourcing environment")
    
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

def install_fallback_wheels():
    """Install the locally created fallback wheels"""
    print("\n🔄 Installing fallback wheels...")
    
    # Find the created wheels
    wheels = []
    for pattern in ["regex-*-linux_armv7l.whl", "ruamel.yaml.clib-*-linux_armv7l.whl", "ujson-*-linux_armv7l.whl"]:
        found = list(Path(".").glob(pattern))
        wheels.extend(found)
    
    if not wheels:
        print("❌ No fallback wheels found to install")
        return False
    
    for wheel in wheels:
        if not run_command(f"python3 -m pip install --user --force-reinstall --no-deps {wheel}", f"Installing {wheel.name}"):
            return False
    
    return True

def install_dependencies():
    """Install additional dependencies"""
    print("\n📚 Installing additional dependencies...")
    
    deps = [
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
        "typer",
        "ruamel-yaml",
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
    
    # Install in smaller batches to avoid conflicts
    for dep in deps:
        if not run_command(f"python3 -m pip install --user {dep}", f"Installing {dep}"):
            print(f"⚠️  Warning: Failed to install {dep}, continuing...")
    
    return True

def verify_installation():
    """Verify that Prefect is working correctly"""
    print("\n✅ Verifying installation...")
    
    # Test basic import
    if not run_command('python3 -c "import prefect; print(f\'Prefect version: {prefect.__version__}\')"', "Testing Prefect import"):
        return False
    
    # Test flow/task decorators
    test_code = '''
from prefect import flow, task

@task
def test_task():
    return "Hello from task"

@flow
def test_flow():
    result = test_task()
    print(f"Flow result: {result}")
    return result

if __name__ == "__main__":
    test_flow()
'''
    
    # Write test file
    with open("/tmp/test_prefect.py", "w") as f:
        f.write(test_code)
    
    if not run_command("python3 /tmp/test_prefect.py", "Testing Prefect flow/task functionality"):
        return False
    
    # Test CLI
    if not run_command("prefect --version", "Testing Prefect CLI"):
        return False
    
    return True

def main():
    """Main installation process"""
    print("🚀 Starting comprehensive OT-2 Prefect installation with fallbacks")
    
    # Create fallback wheels first
    if not create_fallback_wheels():
        print("❌ Failed to create fallback wheels")
        return False
    
    # Set up environment
    if not setup_environment():
        print("❌ Failed to set up environment")
        return False
    
    # Install core wheels
    if not install_core_wheels():
        print("❌ Failed to install core wheels")
        return False
    
    # Install fallback wheels
    if not install_fallback_wheels():
        print("❌ Failed to install fallback wheels")
        return False
    
    # Install additional dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        return False
    
    # Verify installation
    if not verify_installation():
        print("❌ Installation verification failed")
        return False
    
    print("\n🎉 Installation completed successfully!")
    print("\nPrefect is now ready to use on this OT-2 device.")
    print("\nYou can test it with:")
    print("python3 -c \"from prefect import flow, task; print('Prefect ready!')\"")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)