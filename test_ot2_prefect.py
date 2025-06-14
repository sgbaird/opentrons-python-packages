#!/usr/bin/env python3
"""
Direct OT-2 Prefect Test Script

Run this script directly on the OT-2 device to install and test Prefect.
This script bypasses the need for external SSH connections.

Usage: python test_ot2_prefect.py
"""

import sys
import urllib.request
import subprocess
import tempfile
import os
import shutil
import platform

def print_system_info():
    """Print system information for debugging"""
    print("=" * 60)
    print("OT-2 SYSTEM INFORMATION")
    print("=" * 60)
    print(f"Platform: {platform.platform()}")
    print(f"Machine: {platform.machine()}")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {os.getcwd()}")
    print("=" * 60)

def download_file(url, local_path):
    """Download a file from URL"""
    print(f"Downloading: {url}")
    try:
        urllib.request.urlretrieve(url, local_path)
        size = os.path.getsize(local_path)
        print(f"✅ Downloaded {os.path.basename(local_path)} ({size:,} bytes)")
        return True
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def run_command(cmd, description, timeout=300):
    """Run a command and return success status"""
    print(f"\n{description}")
    print(f"Command: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        
        if result.returncode == 0:
            print("✅ Success")
            if result.stdout.strip():
                print("Output:", result.stdout.strip())
            return True
        else:
            print("❌ Failed")
            if result.stderr.strip():
                print("Error:", result.stderr.strip())
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ Command timed out after {timeout} seconds")
        return False
    except Exception as e:
        print(f"❌ Command error: {e}")
        return False

def test_prefect_workflow():
    """Test a comprehensive Prefect workflow"""
    print("\n" + "=" * 60)
    print("TESTING PREFECT WORKFLOW")
    print("=" * 60)
    
    workflow_code = '''
import sys
import platform
from prefect import flow, task

@task
def check_ot2_system():
    """Check OT-2 system information"""
    info = {
        "platform": platform.platform(),
        "machine": platform.machine(), 
        "python_version": sys.version,
        "prefect_available": True
    }
    print("🤖 OT-2 System Check:")
    for key, value in info.items():
        print(f"   {key}: {value}")
    return info

@task
def simulate_plate_prep():
    """Simulate plate preparation"""
    print("🧪 Simulating plate preparation...")
    # This would be actual OT-2 protocol code
    steps = [
        "Loading tips",
        "Aspirating samples", 
        "Dispensing to wells",
        "Ejecting tips"
    ]
    
    for i, step in enumerate(steps, 1):
        print(f"   Step {i}: {step}")
    
    return {"steps_completed": len(steps), "status": "success"}

@task
def analyze_results(prep_result):
    """Analyze the preparation results"""
    print("📊 Analyzing results...")
    if prep_result["status"] == "success":
        analysis = {
            "total_steps": prep_result["steps_completed"],
            "success_rate": 100.0,
            "recommendations": ["All steps completed successfully", "Ready for next protocol"]
        }
    else:
        analysis = {
            "total_steps": prep_result["steps_completed"],
            "success_rate": 0.0,
            "recommendations": ["Check equipment", "Retry protocol"]
        }
    
    print(f"   Success rate: {analysis['success_rate']}%")
    for rec in analysis["recommendations"]:
        print(f"   📝 {rec}")
    
    return analysis

@flow
def ot2_protocol_workflow():
    """Main OT-2 protocol workflow using Prefect"""
    print("🚀 Starting OT-2 Protocol Workflow")
    
    # Check system
    system_info = check_ot2_system()
    
    # Run protocol steps
    prep_result = simulate_plate_prep() 
    
    # Analyze results
    analysis = analyze_results(prep_result)
    
    # Combine results
    workflow_result = {
        "system": system_info,
        "preparation": prep_result,
        "analysis": analysis,
        "workflow_status": "completed"
    }
    
    print("✅ OT-2 Workflow completed successfully!")
    return workflow_result

if __name__ == "__main__":
    try:
        result = ot2_protocol_workflow()
        print("\\n📋 WORKFLOW SUMMARY:")
        print(f"   System: {result['system']['machine']}")
        print(f"   Steps completed: {result['preparation']['steps_completed']}")
        print(f"   Success rate: {result['analysis']['success_rate']}%")
        print(f"   Status: {result['workflow_status']}")
        print("\\n🎉 Prefect is working perfectly on OT-2!")
    except Exception as e:
        print(f"\\n❌ Workflow failed: {e}")
        sys.exit(1)
'''
    
    print("Running comprehensive Prefect workflow test...")
    try:
        result = subprocess.run(
            [sys.executable, "-c", workflow_code],
            capture_output=True, text=True, timeout=120
        )
        
        if result.returncode == 0:
            print("✅ Prefect workflow test PASSED")
            print("\nWorkflow Output:")
            print("-" * 40)
            print(result.stdout)
            print("-" * 40)
            return True
        else:
            print("❌ Prefect workflow test FAILED")
            print("Error output:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Workflow test error: {e}")
        return False

def main():
    """Main test function"""
    print_system_info()
    
    # Check if we're on the right architecture
    if platform.machine() != "armv7l":
        print(f"⚠️  WARNING: This script is designed for ARMv7l (OT-2)")
        print(f"   Current architecture: {platform.machine()}")
        print("   Continuing anyway for testing...")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix="ot2-prefect-test-")
    print(f"\nUsing temporary directory: {temp_dir}")
    
    try:
        base_url = "https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/main/wheels"
        
        # Download and install pendulum
        print("\n" + "=" * 60)
        print("STEP 1: INSTALLING PENDULUM")
        print("=" * 60)
        
        pendulum_url = f"{base_url}/pendulum-3.1.0-cp310-cp310-linux_armv7l.whl"
        pendulum_path = os.path.join(temp_dir, "pendulum.whl")
        
        if not download_file(pendulum_url, pendulum_path):
            print("❌ Failed to download pendulum wheel")
            return False
            
        if not run_command([sys.executable, "-m", "pip", "install", pendulum_path], 
                          "Installing pendulum"):
            print("❌ Failed to install pendulum")
            return False
            
        # Test pendulum import
        if not run_command([sys.executable, "-c", "import pendulum; print(f'Pendulum version: {pendulum.__version__}')"],
                          "Testing pendulum import"):
            print("❌ Pendulum import failed")
            return False
        
        # Download and install Prefect
        print("\n" + "=" * 60)
        print("STEP 2: INSTALLING PREFECT")
        print("=" * 60)
        
        prefect_url = f"{base_url}/prefect-3.3.4-py3-none-any.whl"
        prefect_path = os.path.join(temp_dir, "prefect.whl")
        
        if not download_file(prefect_url, prefect_path):
            print("❌ Failed to download Prefect wheel")
            return False
            
        if not run_command([sys.executable, "-m", "pip", "install", prefect_path],
                          "Installing Prefect"):
            print("❌ Failed to install Prefect")
            return False
            
        # Test Prefect import
        if not run_command([sys.executable, "-c", "import prefect; print(f'Prefect version: {prefect.__version__}')"],
                          "Testing Prefect import"):
            print("❌ Prefect import failed")
            return False
        
        # Run comprehensive workflow test
        print("\n" + "=" * 60)
        print("STEP 3: TESTING PREFECT FUNCTIONALITY")
        print("=" * 60)
        
        if not test_prefect_workflow():
            print("❌ Prefect workflow test failed")
            return False
        
        # Final success message
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("✅ Prefect is successfully installed and working on OT-2")
        print("✅ All dependencies are satisfied")
        print("✅ Workflow execution is functional")
        print("\n📚 Next steps:")
        print("   1. You can now use Prefect in your OT-2 protocols")
        print("   2. Import with: from prefect import flow, task")
        print("   3. Create workflows for your laboratory automation")
        print("   4. Refer to Prefect docs for advanced features")
        
        return True
        
    finally:
        # Cleanup
        print(f"\n🧹 Cleaning up temporary files in {temp_dir}")
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    print("OT-2 Prefect Installation and Test Script")
    print("==========================================")
    
    success = main()
    
    if success:
        print("\n✅ TEST COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n❌ TEST FAILED - Check errors above")
        sys.exit(1)