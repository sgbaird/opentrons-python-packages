#!/usr/bin/env python3
"""
OT-2 Prefect Client Installation and Test Script
Run this script on the OT-2 to install and test Prefect Client functionality
"""

import sys
import urllib.request
import subprocess
import tempfile
import os
import shutil

class OT2PrefectInstaller:
    def __init__(self):
        self.base_url = "https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/38bb4e2/wheels"
        self.temp_dir = None
        
    def setup_temp_dir(self):
        """Create temporary directory for downloads"""
        self.temp_dir = tempfile.mkdtemp(prefix="ot2-prefect-")
        print(f"Using temporary directory: {self.temp_dir}")
        
    def cleanup(self):
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            print("Cleaning up temporary files...")
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            
    def download_wheel(self, wheel_name):
        """Download a wheel file"""
        wheel_url = f"{self.base_url}/{wheel_name}"
        wheel_path = os.path.join(self.temp_dir, wheel_name)
        
        print(f"Downloading {wheel_name}...")
        try:
            urllib.request.urlretrieve(wheel_url, wheel_path)
            size = os.path.getsize(wheel_path)
            print(f"Downloaded {wheel_name} ({size:,} bytes)")
            return wheel_path
        except Exception as e:
            print(f"Failed to download {wheel_name}: {e}")
            return None
            
    def install_wheel(self, wheel_path):
        """Install a wheel using pip"""
        print(f"Installing {os.path.basename(wheel_path)}...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", wheel_path],
                capture_output=True, text=True, timeout=300
            )
            
            if result.returncode == 0:
                print("✅ Installation successful")
                return True
            else:
                print("❌ Installation failed:")
                print(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Installation timed out")
            return False
        except Exception as e:
            print(f"❌ Installation error: {e}")
            return False
            
    def test_import(self, module_name):
        """Test importing a module"""
        print(f"Testing import of {module_name}...")
        try:
            result = subprocess.run(
                [sys.executable, "-c", f"import {module_name}; print(f'{module_name} version: {{getattr({module_name}, '__version__', 'unknown')}}')"],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                print("✅ Import successful")
                print(result.stdout.strip())
                return True
            else:
                print("❌ Import failed:")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Import test error: {e}")
            return False
            
    def test_prefect_example(self):
        """Test a basic Prefect workflow"""
        print("Testing basic Prefect workflow...")
        
        prefect_code = '''
from prefect import flow, task
import sys

@task
def say_hello(name: str):
    message = f"Hello {name} from OT-2!"
    print(message)
    return message

@task  
def check_system():
    import platform
    info = {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python_version": sys.version
    }
    print("System Info:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    return info

@flow
def ot2_hello_world():
    hello_result = say_hello("Prefect")
    system_info = check_system()
    print("✅ Prefect workflow completed successfully!")
    return {"greeting": hello_result, "system": system_info}

if __name__ == "__main__":
    result = ot2_hello_world()
    print("Workflow result:", result)
'''
        
        try:
            result = subprocess.run(
                [sys.executable, "-c", prefect_code],
                capture_output=True, text=True, timeout=60
            )
            
            if result.returncode == 0:
                print("✅ Prefect workflow test successful")
                print("Output:")
                print(result.stdout)
                return True
            else:
                print("❌ Prefect workflow test failed:")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Prefect workflow test error: {e}")
            return False
            
    def install_prefect_stack(self):
        """Install the complete Prefect Client stack with dependencies"""
        print("Starting OT-2 Prefect Client installation...")
        print("=" * 50)
        
        # Setup
        self.setup_temp_dir()
        
        try:
            # Step 1: Install pendulum (Prefect dependency)
            print("\nStep 1: Installing pendulum (Prefect dependency)")
            pendulum_wheel = self.download_wheel("pendulum-3.1.0-cp310-cp310-linux_armv7l.whl")
            if not pendulum_wheel or not self.install_wheel(pendulum_wheel):
                print("❌ Failed to install pendulum")
                return False
                
            # Test pendulum
            if not self.test_import("pendulum"):
                print("❌ Pendulum import test failed")
                return False
                
            # Step 2: Install Prefect Client (lightweight version)
            print("\nStep 2: Installing Prefect Client (lightweight version)")
            prefect_wheel = self.download_wheel("prefect_client-3.4.6-py3-none-any.whl")
            if not prefect_wheel or not self.install_wheel(prefect_wheel):
                print("❌ Failed to install Prefect Client")
                return False
                
            # Test Prefect import
            if not self.test_import("prefect"):
                print("❌ Prefect Client import test failed")
                return False
                
            # Step 3: Test Prefect functionality
            print("\nStep 3: Testing Prefect functionality")
            if not self.test_prefect_example():
                print("❌ Prefect functionality test failed")
                return False
                
            print("\n" + "=" * 50)
            print("🎉 SUCCESS: Prefect Client is now installed and working on OT-2!")
            print("\nNext steps:")
            print("1. You can now import prefect in your Python scripts")
            print("2. Create and run Prefect flows for your OT-2 workflows")
            print("3. Note: You're using prefect-client (lightweight version)")
            print("4. Refer to Prefect documentation for advanced usage")
            
            return True
            
        finally:
            self.cleanup()

def main():
    print("OT-2 Prefect Client Installation Script")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    
    installer = OT2PrefectInstaller()
    success = installer.install_prefect_stack()
    
    if success:
        print("\n✅ Installation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Installation failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()