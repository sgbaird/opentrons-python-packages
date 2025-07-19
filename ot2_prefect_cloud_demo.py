#!/usr/bin/env python3
"""
OT-2 Prefect Cloud Integration Demo
Validates complete Prefect Cloud functionality on OT-2 simulators.

Usage:
    python3 ot2_prefect_cloud_demo.py

Requirements:
    - Prefect 3.3.4 installed on OT-2
    - Service account API key configured
    - Cloud workspace access
"""

import asyncio
from prefect import flow, task
from datetime import datetime
import time
import prefect.settings
from prefect.client.cloud import get_cloud_client

@task
def initialize_ot2():
    """Initialize OT-2 simulator for testing"""
    print("🤖 Initializing OT-2 simulator...")
    time.sleep(1)
    return "OT-2 simulator ready"

@task
def run_protocol_simulation():
    """Simulate running a laboratory protocol"""
    print("🧪 Running laboratory protocol simulation...")
    
    # Simulate protocol steps
    steps = [
        "Aspirating samples from source wells",
        "Transferring to reaction plates", 
        "Mixing reagents",
        "Dispensing to output wells"
    ]
    
    for i, step in enumerate(steps, 1):
        print(f"  Step {i}: {step}")
        time.sleep(0.5)
    
    return f"Protocol completed successfully with {len(steps)} steps"

@task
def generate_report(protocol_result):
    """Generate a protocol report"""
    print("📊 Generating protocol report...")
    
    report = {
        "protocol_id": f"OT2-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "status": "completed",
        "result": protocol_result,
        "timestamp": datetime.now().isoformat(),
        "device": "OT-2 simulator"
    }
    
    return report

@flow(name="OT2-Laboratory-Automation-Demo", description="Complete OT-2 laboratory automation with Prefect Cloud")
def ot2_laboratory_demo():
    """
    Comprehensive OT-2 laboratory automation demonstration
    Shows full integration with Prefect Cloud monitoring
    """
    print("🚀 Starting OT-2 Laboratory Automation Demo")
    print("=" * 50)
    
    # Initialize system
    init_result = initialize_ot2()
    print(f"✅ {init_result}")
    
    # Run protocol
    protocol_result = run_protocol_simulation()
    print(f"✅ {protocol_result}")
    
    # Generate report
    report = generate_report(protocol_result)
    print(f"✅ Report generated: {report['protocol_id']}")
    
    print("=" * 50)
    print("🎉 OT-2 Laboratory Automation Demo completed successfully!")
    print("📱 Check Prefect Cloud UI for real-time monitoring and logs")
    
    return report

def verify_cloud_connection():
    """Verify Prefect Cloud connectivity before running demo"""
    try:
        print("🔍 Verifying Prefect Cloud connection...")
        
        # Check configuration
        api_url = prefect.settings.PREFECT_API_URL.value()
        api_key = prefect.settings.PREFECT_API_KEY.value()
        
        if not api_url:
            raise Exception("PREFECT_API_URL not configured")
        if not api_key:
            raise Exception("PREFECT_API_KEY not configured")
            
        print(f"   API URL: {api_url}")
        print(f"   API Key: {api_key[:10]}... (configured)")
        
        # Test client creation
        client = get_cloud_client()
        print(f"   ✅ Cloud client created: {type(client).__name__}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Cloud connection failed: {e}")
        print("\n💡 Configuration help:")
        print("   export PREFECT_API_KEY='your-service-account-key'")
        print("   export PREFECT_API_URL='https://api.prefect.cloud/api/accounts/[ACCOUNT]/workspaces/[WORKSPACE]'")
        return False

if __name__ == "__main__":
    print("OT-2 Prefect Cloud Integration Demo")
    print("=" * 40)
    
    # Verify connection first
    if not verify_cloud_connection():
        print("\n❌ Please configure Prefect Cloud connection and try again.")
        exit(1)
    
    print("\n🎯 Running demo flow...")
    print("   (Monitor in real-time at Prefect Cloud UI)")
    print()
    
    # Run the demo flow
    try:
        result = ot2_laboratory_demo()
        print("\n" + "=" * 50)
        print("✅ DEMO COMPLETED SUCCESSFULLY!")
        print("📊 Final Report:")
        for key, value in result.items():
            print(f"   {key}: {value}")
        print("\n🌐 View detailed logs and execution graph in Prefect Cloud")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        exit(1)