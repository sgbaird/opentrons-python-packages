#!/usr/bin/env python3
"""
Test Prefect serve/deployment functionality with Opentrons integration
This script will:
1. Start a Prefect server
2. Create and deploy the flow 
3. Run the deployment remotely
4. Monitor execution
"""

import sys
import time
import subprocess
import threading
from pathlib import Path

print("🚀 Testing Prefect Serve/Deployment with Opentrons Integration")
print("=" * 70)

def run_serve_in_background():
    """Run prefect serve in background"""
    print("🔧 Starting Prefect serve in background...")
    
    # Source environment and run serve
    cmd = """
source ~/.bashrc
cd /root
python3 -c "
from prefect_opentrons_flow_with_serve import laboratory_automation_flow
from prefect import serve

# Create the serve deployment
serve_deployment = serve(
    laboratory_automation_flow.to_deployment(
        name='ot2-lab-serve',
        description='OT-2 Lab Automation via Serve',
        tags=['ot2', 'serve', 'opentrons']
    ),
    host='0.0.0.0',
    port=4200
)

print('🚀 Starting serve...')
serve_deployment.serve()
"
"""
    
    try:
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Monitor output
        for line in process.stdout:
            print(f"[SERVE] {line.strip()}")
            
    except Exception as e:
        print(f"❌ Serve failed: {e}")

def test_deployment_run():
    """Test running the deployment"""
    print("\n🧪 Testing deployment execution...")
    
    time.sleep(5)  # Wait for serve to start
    
    cmd = """
source ~/.bashrc
cd /root

# Test direct flow execution first
echo "=== TESTING DIRECT FLOW ==="
python3 -c "
from prefect_opentrons_flow_with_serve import laboratory_automation_flow
result = laboratory_automation_flow()
print(f'Direct flow result: {result}')
"

echo -e "\n=== TESTING DEPLOYMENT RUN ==="
# Try to trigger deployment run
python3 -c "
import requests
import time

# Test if serve is running
try:
    response = requests.get('http://localhost:4200/health', timeout=5)
    print(f'Serve health check: {response.status_code}')
except Exception as e:
    print(f'Serve not ready: {e}')

# Try to run deployment
try:
    from prefect.deployments import run_deployment
    run_result = run_deployment('OT2-Lab-Automation/ot2-lab-serve')
    print(f'Deployment run result: {run_result}')
except Exception as e:
    print(f'Deployment run failed: {e}')
"
"""
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        print(f"Exit code: {result.returncode}")
    except subprocess.TimeoutExpired:
        print("⚠️ Test timed out after 120 seconds")
    except Exception as e:
        print(f"❌ Test failed: {e}")

def main():
    """Main test function"""
    
    # Create the flow file on the remote device first
    upload_script = f"""
cat > /root/prefect_opentrons_flow_with_serve.py << 'EOF'
{open('prefect_opentrons_flow_with_serve.py').read()}
EOF
chmod +x /root/prefect_opentrons_flow_with_serve.py
echo "✅ Flow script uploaded to OT-2"
"""
    
    print("📤 Uploading flow script to OT-2...")
    subprocess.run(f"ssh root@ot2-simulator-20aceb.tail6a1dd7.ts.net '{upload_script}'", shell=True)
    
    # Start serve in background thread
    serve_thread = threading.Thread(target=run_serve_in_background, daemon=True)
    serve_thread.start()
    
    # Wait a bit then test deployment
    time.sleep(3)
    test_deployment_run()
    
    print("\n" + "=" * 70)
    print("🎯 SERVE/DEPLOYMENT TEST COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()