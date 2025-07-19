#!/usr/bin/env python3
"""
Setup OT-2 Prefect Cloud Integration
Working around OT-2 system limitations
"""
import subprocess
import sys

def run_ssh(command, description=""):
    """Run SSH command with proper shell handling"""
    hostname = "ot2-simulator-20aceb.tail6a1dd7.ts.net"
    
    print(f"🔧 {description}")
    print(f"Command: {command}")
    
    try:
        # Use sh instead of bash, and source .bashrc manually when needed
        full_cmd = f'ssh -o ConnectTimeout=20 -o StrictHostKeyChecking=no root@{hostname} "{command}"'
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"✅ Success: {result.stdout.strip()}")
            return result.stdout.strip()
        else:
            print(f"❌ Error (code {result.returncode}): {result.stderr.strip()}")
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    print("🚀 Setting up OT-2 Prefect Cloud Integration")
    print("=" * 50)
    
    # Environment variables
    account_id = "5b838504-64cf-4297-9b35-b881ac6169b3"
    workspace_id = "d2718b4c-b49a-43ce-83c2-baf6fb3b9665"
    workspace_name = "acceleration-consortium/default"
    api_key = "pnb_KWDspVtot7vO6Tmoid7nn2NEEdD1yL4cCCRP"
    api_url = f"https://api.prefect.cloud/api/accounts/{account_id}/workspaces/{workspace_id}"
    
    print(f"Workspace: {workspace_name}")
    print(f"API URL: {api_url}")
    print()
    
    # Step 1: Ensure .bashrc has proper environment setup
    print("Step 1: Setting up environment in .bashrc")
    
    bashrc_content = '''# Prefect Environment Setup
export PATH="/var/user-packages/root/.local/bin:$PATH"
export PYTHONPATH="/var/user-packages/root/.local/lib/python3.10/site-packages:$PYTHONPATH"
'''
    
    # Check if already in .bashrc
    current_bashrc = run_ssh('cat /root/.bashrc', "Checking current .bashrc")
    if current_bashrc and "user-packages" not in current_bashrc:
        run_ssh(f'echo \'{bashrc_content}\' >> /root/.bashrc', "Adding Prefect paths to .bashrc")
    
    # Step 2: Create a startup script that sets environment permanently
    print("\nStep 2: Creating startup script for Prefect environment")
    
    startup_script = f'''#!/bin/sh
# OT-2 Prefect Environment and Cloud Setup
export PATH="/var/user-packages/root/.local/bin:$PATH"
export PYTHONPATH="/var/user-packages/root/.local/lib/python3.10/site-packages:$PYTHONPATH"
export PREFECT_API_URL="{api_url}"
export PREFECT_API_KEY="{api_key}"
'''
    
    run_ssh(f'echo \'{startup_script}\' > /root/prefect_env.sh', "Creating prefect environment script")
    run_ssh('chmod +x /root/prefect_env.sh', "Making environment script executable")
    
    # Step 3: Test Prefect availability with environment sourced
    print("\nStep 3: Testing Prefect with environment loaded")
    
    test_result = run_ssh('source /root/prefect_env.sh && python3 -c "import prefect; print(f\\"Prefect: {{prefect.__version__}}\\")"', 
                         "Testing Prefect import")
    
    if not test_result or "3.3.4" not in test_result:
        print("❌ Prefect not working, aborting")
        return
    
    # Step 4: Configure Prefect Cloud using environment variables
    print("\nStep 4: Configuring Prefect Cloud")
    
    # Test cloud connectivity
    cloud_test = '''source /root/prefect_env.sh && python3 -c "
import prefect.settings as settings
print(f'API URL: {settings.PREFECT_API_URL.value()}')
print(f'API Key: {settings.PREFECT_API_KEY.value()[:20]}...')

try:
    from prefect.client.cloud import get_cloud_client
    client = get_cloud_client()
    print(f'Cloud client: {type(client).__name__}')
except Exception as e:
    print(f'Cloud error: {e}')
"'''
    
    run_ssh(cloud_test, "Testing cloud connectivity")
    
    # Step 5: Create and run test flow
    print("\nStep 5: Creating test flow")
    
    # Create the flow file with proper escaping
    flow_script = '''source /root/prefect_env.sh && cat > /root/test_flow.py << 'FLOWEOF'
from prefect import flow, task
from datetime import datetime
import socket

@task
def get_system_info():
    return {
        "hostname": socket.gethostname(),
        "timestamp": datetime.now().isoformat(),
        "prefect_version": __import__("prefect").__version__
    }

@task
def simulate_work():
    print("Simulating OT-2 protocol...")
    import time
    time.sleep(1)
    return "Protocol completed"

@flow(name="OT-2 Cloud Test")
def ot2_test_flow():
    info = get_system_info()
    work = simulate_work()
    print(f"System: {info}")
    print(f"Work: {work}")
    return {"status": "success", "info": info, "work": work}

if __name__ == "__main__":
    result = ot2_test_flow()
    print(f"Flow result: {result}")
FLOWEOF'''
    
    run_ssh(flow_script, "Creating test flow script")
    
    # Step 6: Run the test flow
    print("\nStep 6: Running test flow")
    
    flow_result = run_ssh('source /root/prefect_env.sh && cd /root && python3 test_flow.py', 
                         "Executing test flow")
    
    # Step 7: Try to get flow run information
    print("\nStep 7: Getting flow run information")
    
    # Check if we can list flow runs
    list_runs = run_ssh('source /root/prefect_env.sh && python3 -c "from prefect.client.cloud import get_cloud_client; client = get_cloud_client(); print(\\"Cloud client ready\\")"', 
                       "Testing cloud client access")
    
    print("\n" + "=" * 50)
    print("✅ SETUP COMPLETE!")
    print("=" * 50)
    print("To use Prefect on the OT-2:")
    print("1. SSH: ssh root@ot2-simulator-20aceb.tail6a1dd7.ts.net")
    print("2. Load environment: source /root/prefect_env.sh")
    print("3. Run flows or use Prefect CLI")
    print(f"4. View in Prefect Cloud: https://app.prefect.cloud/account/{account_id}/workspace/{workspace_id}")
    print("=" * 50)

if __name__ == "__main__":
    main()