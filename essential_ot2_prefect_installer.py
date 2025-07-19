#!/usr/bin/env python3
"""
Essential OT-2 Prefect Installation Script
Simplified, focused installer for Prefect 3.3.4 on OT-2 simulators.
"""

import sys
import os
import subprocess
import time

def run_command(cmd, description="", timeout=300):
    """Run a command with proper error handling"""
    print(f"🔧 {description}")
    print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - Timeout")
        return False
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False

def install_prefect():
    """Install Prefect 3.3.4 with essential configuration"""
    
    print("🚀 Essential OT-2 Prefect Installation")
    print("=" * 50)
    
    # Create user packages directory
    if not run_command("mkdir -p /var/user-packages/root/.local/lib/python3.10/site-packages", 
                      "Creating package directory"):
        return False
    
    # Install Prefect wheel
    if not run_command("python3 -m pip install --user --target /var/user-packages/root/.local/lib/python3.10/site-packages prefect==3.3.4", 
                      "Installing Prefect 3.3.4"):
        return False
    
    # Set up environment
    bashrc_content = '''
# Prefect Environment Setup
export PATH="/var/user-packages/root/.local/bin:$PATH"
export PYTHONPATH="/var/user-packages/root/.local/lib/python3.10/site-packages:$PYTHONPATH"
'''
    
    with open("/root/.bashrc", "a") as f:
        f.write(bashrc_content)
    
    print("✅ Environment configured")
    
    # Verify installation
    os.environ['PYTHONPATH'] = "/var/user-packages/root/.local/lib/python3.10/site-packages"
    try:
        import prefect
        print(f"✅ Prefect {prefect.__version__} installed successfully")
        return True
    except ImportError:
        print("❌ Prefect import failed")
        return False

def setup_cloud_config(api_url=None, api_key=None):
    """Set up Prefect Cloud configuration"""
    
    if api_url:
        os.environ['PREFECT_API_URL'] = api_url
        with open("/root/.bashrc", "a") as f:
            f.write(f'\nexport PREFECT_API_URL="{api_url}"\n')
        print(f"✅ API URL configured: {api_url}")
    
    if api_key:
        os.environ['PREFECT_API_KEY'] = api_key
        with open("/root/.bashrc", "a") as f:
            f.write(f'\nexport PREFECT_API_KEY="{api_key}"\n')
        print("✅ API Key configured")

def main():
    """Main installation process"""
    
    if len(sys.argv) > 1:
        device = sys.argv[1]
        print(f"Installing on device: {device}")
        
        # SSH installation command
        ssh_cmd = f"""ssh -o ConnectTimeout=20 -o StrictHostKeyChecking=no root@{device} '
python3 - << "EOF"
{open(__file__).read()}
EOF
'"""
        
        return subprocess.call(ssh_cmd, shell=True)
    
    else:
        # Local installation
        success = install_prefect()
        
        if success:
            print("\n🎉 Installation completed successfully!")
            print("\nNext steps:")
            print("1. source ~/.bashrc")
            print("2. python3 simple_prefect_cli.py config set PREFECT_API_URL=<your-url>")
            print("3. python3 simple_prefect_cli.py config set PREFECT_API_KEY=<your-key>")
            return 0
        else:
            print("\n❌ Installation failed")
            return 1

if __name__ == "__main__":
    sys.exit(main())