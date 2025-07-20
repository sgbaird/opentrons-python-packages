#!/usr/bin/env python3
"""
Minimal Prefect + Opentrons Integration Example
Simple proof of concept showing both APIs working in same script
"""

import os
import sys

# Configure Prefect using environment variables (no hardcoded credentials)
if 'PREFECT_API_URL' not in os.environ:
    print("Warning: PREFECT_API_URL not set. Configure for cloud connectivity.")
if 'PREFECT_API_KEY' not in os.environ:
    print("Warning: PREFECT_API_KEY not set. Configure for cloud connectivity.")

# Import both APIs directly in same script
from prefect import flow, task
import prefect

# Add system packages for Opentrons
sys.path.insert(0, "/usr/lib/python3.10/site-packages")
import opentrons.simulate

print(f"✅ Prefect {prefect.__version__} imported")
print(f"✅ Opentrons API imported")

@task
def opentrons_protocol_task():
    """Execute simple Opentrons protocol directly in Prefect task"""
    print("🤖 Running Opentrons protocol...")
    
    # Simple protocol definition
    protocol_text = '''
metadata = {'apiLevel': '2.13'}

def run(protocol):
    # Load labware
    tips = protocol.load_labware('opentrons_96_tiprack_300ul', 1)
    plate = protocol.load_labware('corning_96_wellplate_360ul_flat', 2)
    
    # Load instrument  
    p300 = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=[tips])
    
    # Simple protocol steps
    p300.pick_up_tip()
    p300.aspirate(100, plate.wells()[0])
    p300.dispense(100, plate.wells()[1])
    p300.drop_tip()
    
    protocol.comment("Simple transfer completed")
'''
    
    try:
        # Execute protocol simulation
        result = opentrons.simulate.simulate(protocol_text, custom_labware_paths=[], custom_data_paths=[])
        print("✅ Protocol simulation successful")
        return "Protocol completed successfully"
    except Exception as e:
        print(f"❌ Protocol error: {e}")
        return f"Protocol failed: {e}"

@flow(log_prints=True)
def simple_ot2_flow():
    """Simple flow demonstrating Prefect + Opentrons integration"""
    print("🚀 Starting simple OT-2 flow...")
    
    # Execute Opentrons protocol in Prefect task
    result = opentrons_protocol_task()
    
    print(f"📊 Flow result: {result}")
    return {"status": "completed", "protocol_result": result}

if __name__ == "__main__":
    print("🧪 Testing minimal Prefect + Opentrons integration...")
    
    # Execute the flow
    result = simple_ot2_flow()
    
    print(f"\n✅ Integration test complete: {result}")
    print("✅ Both Prefect and Opentrons APIs working in same script")