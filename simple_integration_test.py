#!/usr/bin/env python3
"""
Simple test to debug Prefect + opentrons.simulate integration.
"""

import sys
import subprocess
sys.path.insert(0, "/var/user-packages/root/.local/lib/python3.10/site-packages")

def test_opentrons_protocol():
    """Test opentrons.simulate using system pydantic v1."""
    protocol_code = '''
import opentrons.simulate
protocol = opentrons.simulate.get_protocol_api("2.16")
protocol.home()
plate = protocol.load_labware("nest_96_wellplate_200ul_flat", "2")
tiprack = protocol.load_labware("opentrons_96_tiprack_1000ul", location="1")
p1000 = protocol.load_instrument("p1000_single_gen2", "right", tip_racks=[tiprack])
p1000.transfer(100, plate["A1"], plate["A2"])
print("SUCCESS: OT-2 protocol executed with opentrons.simulate!")
'''
    
    cmd = [sys.executable, "-c", protocol_code]
    env = {"PYTHONPATH": "/usr/lib/python3.10/site-packages"}
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=60)
        if result.returncode == 0:
            return True, "OT-2 protocol executed successfully"
        else:
            return False, result.stderr.strip()
    except Exception as e:
        return False, str(e)

def test_prefect_simple():
    """Test basic Prefect functionality."""
    print("Testing basic Prefect import...")
    try:
        import prefect
        print(f"✅ Prefect version: {prefect.__version__}")
        
        # Test accessing flow and task
        print("Testing flow and task access...")
        flow_decorator = prefect.flow
        task_decorator = prefect.task
        print("✅ Flow and task decorators accessed successfully!")
        
        # Create simple workflow
        @task_decorator
        def simple_task():
            return "Hello from Prefect task!"
        
        @flow_decorator
        def simple_flow():
            result = simple_task()
            return f"Flow result: {result}"
        
        # Execute flow
        result = simple_flow()
        print(f"✅ Flow executed: {result}")
        return True, "Prefect working"
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False, str(e)

def main():
    print("🧪 Simple Integration Test")
    print("=" * 40)
    
    # Test 1: Prefect
    print("\n1. Testing Prefect...")
    success, msg = test_prefect_simple()
    print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'} - {msg}")
    
    if not success:
        return
    
    # Test 2: OpenTrons
    print("\n2. Testing opentrons.simulate...")
    success, msg = test_opentrons_protocol()
    print(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'} - {msg}")
    
    if success:
        print("\n🎉 BOTH SYSTEMS WORKING!")
        print("✅ opentrons.simulate: Works with pydantic v1 (system environment)")
        print("✅ Prefect: Works with pydantic v2 (user environment)")
        print("✅ Solution: Use subprocess isolation for opentrons.simulate calls")

if __name__ == "__main__":
    main()