#!/usr/bin/env python3
"""
Prefect Serve Deployment with Opentrons Integration
Runs the flow via serve and allows remote execution
"""

import os

# Set up Prefect Cloud configuration
os.environ['PREFECT_API_URL'] = 'https://api.prefect.cloud/api/accounts/5b838504-64cf-4297-9b35-b881ac6169b3/workspaces/d2718b4c-b49a-43ce-83c2-baf6fb3b9665'

from simple_ot2_opentrons_flow import ot2_laboratory_flow

print("🚀 Starting Prefect Serve for OT-2 Opentrons Integration")
print("=" * 60)

if __name__ == "__main__":
    # Create and run serve deployment
    print("🔧 Creating serve deployment...")
    
    # Use flow.serve() to create a deployment
    print("✅ Starting serve deployment...")
    ot2_laboratory_flow.serve(
        name="ot2-opentrons-serve",
        description="OT-2 Laboratory automation with Opentrons API integration",
        tags=["ot2", "opentrons", "laboratory", "automation"],
        version="1.0.0"
    )