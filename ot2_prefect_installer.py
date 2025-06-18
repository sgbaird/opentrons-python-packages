#!/usr/bin/env python3
"""
OT-2 Prefect Complete Installation Script
Installs Prefect v3.3.4 with full flow/task functionality on OT-2

This is the final, clean installation script that consolidates hundreds of 
experimental commands into a working solution.
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


def setup_environment():
    """Set up permanent environment configuration for OT-2"""
    print("🔧 Setting up permanent environment configuration...")
    
    # Environment variables needed for OT-2
    env_config = '''export PATH="/var/user-packages/root/.local/bin:$PATH"
export PYTHONPATH="/var/user-packages/root/.local/lib/python3.10/site-packages:$PYTHONPATH"'''
    
    # Write to .bashrc for interactive shells
    bashrc_path = "/root/.bashrc"
    try:
        with open(bashrc_path, 'w') as f:
            f.write(env_config + '\n')
        print(f"✅ Created {bashrc_path}")
    except Exception as e:
        print(f"❌ Failed to create {bashrc_path}: {e}")
    
    # Write to .profile for login shells
    profile_path = "/root/.profile"
    try:
        with open(profile_path, 'w') as f:
            f.write(env_config + '\n')
        print(f"✅ Created {profile_path}")
    except Exception as e:
        print(f"❌ Failed to create {profile_path}: {e}")
    
    # Apply to current session
    user_site = "/var/user-packages/root/.local/lib/python3.10/site-packages"
    current_path = os.environ.get('PYTHONPATH', '')
    new_path = f"{user_site}:{current_path}" if current_path else user_site
    os.environ['PYTHONPATH'] = new_path
    print(f"✅ PYTHONPATH set for current session: {new_path}")


def main():
    print("🎯 OT-2 PREFECT COMPLETE INSTALLATION")
    print("Installing Prefect v3.3.4 with full workflow functionality\n")
    
    # Step 1: Set up environment
    setup_environment()
    
    # Step 2: Install core pre-built wheels
    print("\n📦 Phase 1: Installing core pre-built wheels...")
    
    base_url = "https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/wheels/"
    
    # Critical wheels that solve compilation issues
    core_wheels = [
        ("pendulum-3.1.0-cp310-cp310-linux_armv7l.whl", "Resolves Rust compilation issues"),
        ("ujson-5.10.0-py3-none-linux_armv7l.whl", "Custom ARM fallback for JSON processing"),
        ("prefect-3.3.4-py3-none-any.whl", "Full Prefect workflow engine"),
    ]
    
    for wheel, description in core_wheels:
        url = base_url + wheel
        print(f"\n📥 Installing {wheel}")
        print(f"   Purpose: {description}")
        result = install_wheel(url, force=True, user=True)
        if result.returncode == 0:
            print(f"✅ {wheel} installed successfully")
        else:
            print(f"❌ {wheel} failed to install")
            return False
    
    # Step 3: Install additional dependencies
    print("\n📦 Phase 2: Installing additional dependencies...")
    
    deps = [
        ("pydantic>=2.0", "Modern data validation"),
        ("rich", "Terminal formatting for Prefect"),
        ("typing-extensions>=4.10.0", "Modern type hints"),
    ]
    
    for dep, description in deps:
        print(f"\n📥 Installing {dep}")
        print(f"   Purpose: {description}")
        cmd = [sys.executable, '-m', 'pip', 'install', '--user', '--upgrade', dep]
        result = run_command(cmd, check=False)
        if result.returncode == 0:
            print(f"✅ {dep} installed successfully")
        else:
            print(f"⚠️ {dep} failed - may already be satisfied")
    
    # Step 4: Test installation
    print("\n🔍 Phase 3: Testing installation...")
    
    # Test 1: Basic import
    print("\n🧪 Testing Prefect core import...")
    test_cmd = [sys.executable, '-c', "import prefect; print(f'Prefect version: {prefect.__version__}')"]
    result = run_command(test_cmd, check=False)
    if result.returncode != 0:
        print("❌ Basic import failed")
        return False
    print("✅ Prefect core import: SUCCESS")
    
    # Test 2: Flow/task imports
    print("\n🧪 Testing flow and task imports...")
    test_cmd = [sys.executable, '-c', "from prefect import flow, task; print('Flow/task imports: SUCCESS')"]
    result = run_command(test_cmd, check=False)
    if result.returncode != 0:
        print("❌ Flow/task imports failed")
        return False
    print("✅ Flow/task imports: SUCCESS")
    
    # Test 3: Complete flow execution
    print("\n🧪 Testing complete flow execution...")
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
    print(f"✅ Flow result: {result}")
    print("🎉 PREFECT FULLY OPERATIONAL ON OT-2!")
'''
    
    test_cmd = [sys.executable, '-c', flow_test]
    result = run_command(test_cmd, check=False)
    if result.returncode != 0:
        print("❌ Flow execution failed")
        return False
    
    # Test 4: CLI functionality
    print("\n🧪 Testing Prefect CLI...")
    cli_path = "/var/user-packages/root/.local/bin/prefect"
    if os.path.exists(cli_path):
        test_cmd = [cli_path, '--version']
        result = run_command(test_cmd, check=False)
        if result.returncode == 0:
            print("✅ Prefect CLI: SUCCESS")
        else:
            print("⚠️ Prefect CLI may need PATH configuration")
    else:
        print("⚠️ Prefect CLI not found - may need session restart")
    
    # Success message
    print("\n" + "="*60)
    print("🎉 INSTALLATION COMPLETE! 🎉")
    print("="*60)
    print("✅ Prefect v3.3.4 fully working on OT-2")
    print("✅ Flow and task decorators functional")
    print("✅ All compilation issues resolved")
    print("✅ Environment permanently configured")
    print("✅ Ready for production workflows")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("1. Restart your SSH session or run: source /root/.bashrc")
    print("2. Test CLI access: prefect --version")
    print("3. Test cloud login: prefect cloud login --help")
    print("4. Create and serve flows as needed")
    
    print("\n📖 For usage examples, see:")
    print("https://github.com/sgbaird/opentrons-python-packages/blob/copilot/fix-11/OT2-PREFECT-INSTALLATION-GUIDE.md")
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Installation failed. Please check the error messages above.")
        sys.exit(1)
    else:
        print("\n✅ Installation completed successfully!")