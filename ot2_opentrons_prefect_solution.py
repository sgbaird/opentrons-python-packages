#!/usr/bin/env python3
"""
OT-2 + Prefect Integration with opentrons.simulate Support

This script demonstrates how to successfully combine Prefect flows with 
opentrons.simulate by using environment isolation to handle pydantic 
version conflicts.

Key insight: 
- opentrons.simulate requires pydantic v1 (system environment)
- Prefect requires pydantic v2 (user environment)
- Solution: Use subprocess isolation to run each with appropriate pydantic version

Author: GitHub Copilot
Date: 2025-01-18
Device: ot2-simulator-9d169e.tail6a1dd7.ts.net
"""

import sys
import subprocess
import json
import time
from typing import Dict, Any, Tuple

# Ensure user packages are prioritized for Prefect
sys.path.insert(0, "/var/user-packages/root/.local/lib/python3.10/site-packages")

def execute_ot2_protocol_with_opentrons_simulate() -> Tuple[bool, str]:
    """
    Execute OT-2 protocol using opentrons.simulate in isolated environment.
    Uses system pydantic v1 for compatibility.
    """
    protocol_code = '''
import opentrons.simulate

print("🤖 Executing OT-2 Protocol with opentrons.simulate")

# Create protocol API
protocol = opentrons.simulate.get_protocol_api("2.16")

# Home the robot
protocol.home()

# Load labware
plate = protocol.load_labware("nest_96_wellplate_200ul_flat", "2")
tiprack = protocol.load_labware("opentrons_96_tiprack_1000ul", location="1")

# Load pipette
p1000 = protocol.load_instrument("p1000_single_gen2", "right", tip_racks=[tiprack])

# Execute transfer
p1000.transfer(100, plate["A1"], plate["A2"])

print("✅ SUCCESS: Complete OT-2 protocol executed with opentrons.simulate!")
print("Result: Transferred 100μL from A1 to A2")
'''
    
    cmd = [sys.executable, "-c", protocol_code]
    
    # Use system environment with pydantic v1
    env = {"PYTHONPATH": "/usr/lib/python3.10/site-packages"}
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            env=env, 
            timeout=120  # Allow time for protocol execution
        )
        
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, f"Error: {result.stderr.strip()}"
            
    except subprocess.TimeoutExpired:
        return False, "Protocol execution timed out"
    except Exception as e:
        return False, f"Execution failed: {str(e)}"

def create_prefect_workflow():
    """
    Create Prefect workflow that orchestrates OT-2 protocol execution.
    Uses user environment with pydantic v2.
    """
    from prefect import flow, task
    
    @task
    def ot2_protocol_task():
        """Prefect task that executes OT-2 protocol via opentrons.simulate."""
        print("🧪 Starting OT-2 protocol execution...")
        success, output = execute_ot2_protocol_with_opentrons_simulate()
        
        if not success:
            raise RuntimeError(f"OT-2 protocol failed: {output}")
            
        return {
            "status": "success",
            "output": output,
            "method": "opentrons.simulate"
        }
    
    @flow(name="ot2-opentrons-simulate-prefect-flow")
    def ot2_prefect_integration_flow():
        """
        Complete Prefect flow that orchestrates OT-2 protocol using opentrons.simulate.
        Demonstrates successful integration of both systems.
        """
        print("🌊 Starting Prefect Flow: OT-2 + opentrons.simulate Integration")
        
        # Execute OT-2 protocol task
        protocol_result = ot2_protocol_task()
        
        # Flow completion
        flow_result = {
            "flow_status": "completed",
            "protocol_result": protocol_result,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "integration": "prefect + opentrons.simulate",
            "pydantic_solution": "environment_isolation"
        }
        
        print("🎉 Flow completed successfully!")
        return flow_result
    
    return ot2_prefect_integration_flow

def main():
    """Main integration test and demonstration."""
    print("🧪 OT-2 + Prefect + opentrons.simulate Integration Test")
    print("=" * 60)
    print("Device: ot2-simulator-9d169e.tail6a1dd7.ts.net")
    print(f"Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("Solution: Environment isolation for pydantic compatibility")
    print("=" * 60)
    print()
    
    # Test 1: Verify Prefect is available
    print("1. Testing Prefect availability...")
    try:
        import prefect
        print(f"   ✅ Prefect {prefect.__version__} imported successfully")
    except Exception as e:
        print(f"   ❌ Prefect import failed: {e}")
        return
    
    # Test 2: Test opentrons.simulate in isolation
    print("\n2. Testing opentrons.simulate with environment isolation...")
    success, output = execute_ot2_protocol_with_opentrons_simulate()
    if success:
        print("   ✅ opentrons.simulate executed successfully!")
        print(f"   Output preview: {output.split(chr(10))[-2] if chr(10) in output else output}")
    else:
        print(f"   ❌ opentrons.simulate failed: {output}")
        return
    
    # Test 3: Create and execute combined workflow
    print("\n3. Executing combined Prefect + opentrons.simulate workflow...")
    try:
        workflow = create_prefect_workflow()
        result = workflow()
        
        print("   ✅ Combined workflow executed successfully!")
        print(f"   Flow Status: {result['flow_status']}")
        print(f"   Protocol Status: {result['protocol_result']['status']}")
        print(f"   Integration Method: {result['integration']}")
        
    except Exception as e:
        print(f"   ❌ Combined workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Success summary
    print("\n" + "=" * 60)
    print("🎉 INTEGRATION SUCCESS!")
    print("=" * 60)
    print("✅ Prefect flows can orchestrate OT-2 protocols")
    print("✅ opentrons.simulate works perfectly with pydantic v1") 
    print("✅ Environment isolation resolves pydantic conflicts")
    print("✅ Both systems work together seamlessly")
    print()
    print("Key insight: Use subprocess isolation to handle pydantic version conflicts")
    print("- opentrons.simulate: system environment (pydantic v1)")
    print("- Prefect: user environment (pydantic v2)")
    print("=" * 60)

if __name__ == "__main__":
    main()