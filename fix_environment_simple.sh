#!/bin/bash
# Simple script to fix OT-2 environment and setup cloud tools
set -e

HOSTNAME="ot2-simulator-20aceb.tail6a1dd7.ts.net"

echo "🚀 Fixing OT-2 Environment Variables Issue"
echo "Target: $HOSTNAME"

# Function to run SSH commands with environment setup
run_ssh() {
    ssh -o ConnectTimeout=20 -o StrictHostKeyChecking=no root@$HOSTNAME "source /root/.bashrc 2>/dev/null || true; $1"
}

echo "🔧 Step 1: Creating robust environment setup script..."

# Create environment setup script
run_ssh 'cat > /root/setup_prefect_env.sh << "ENVEOF"
#!/bin/bash
# Robust Prefect Environment Setup for OT-2
export PATH="/var/user-packages/root/.local/bin:$PATH"
export PYTHONPATH="/var/user-packages/root/.local/lib/python3.10/site-packages:$PYTHONPATH"

# Verify environment is loaded
if command -v prefect >/dev/null 2>&1; then
    echo "✅ Prefect environment loaded successfully"
else
    echo "⚠️ Prefect not found in PATH"
fi
ENVEOF'

run_ssh 'chmod +x /root/setup_prefect_env.sh'

echo "🔧 Step 2: Updating shell configuration..."

# Update .bashrc to auto-load environment
run_ssh 'echo "" >> /root/.bashrc'
run_ssh 'echo "# Auto-load Prefect environment" >> /root/.bashrc'
run_ssh 'echo "if [ -f /root/setup_prefect_env.sh ]; then" >> /root/.bashrc'
run_ssh 'echo "    source /root/setup_prefect_env.sh" >> /root/.bashrc'
run_ssh 'echo "fi" >> /root/.bashrc'

# Create .bash_profile for login shells
run_ssh 'cat > /root/.bash_profile << "PROFILEEOF"
# Load .bashrc for login shells
if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi
PROFILEEOF'

echo "🌐 Step 3: Creating Prefect Cloud setup tools..."

# Create cloud setup script
run_ssh 'cat > /root/setup_cloud.sh << "CLOUDEOF"
#!/bin/bash
# Prefect Cloud Setup Script
if [ $# -ne 2 ]; then
    echo "Usage: $0 <api_key> <workspace_url>"
    echo "Example: $0 \"pnb_xxx...\" \"https://api.prefect.cloud/api/accounts/xxx/workspaces/xxx\""
    exit 1
fi

API_KEY="$1"
WORKSPACE_URL="$2"

echo "🌐 Setting up Prefect Cloud authentication..."
mkdir -p /root/.prefect

cat > /root/.prefect/profiles.toml << PROFILEEOF
active = "cloud"

[profiles.cloud]
PREFECT_API_KEY = "${API_KEY}"
PREFECT_API_URL = "${WORKSPACE_URL}"
PROFILEEOF

echo "✅ Prefect Cloud profile configured"
echo "🧪 Testing cloud connectivity..."

source /root/setup_prefect_env.sh
python3 -c "
import requests
from prefect.settings import PREFECT_API_KEY, PREFECT_API_URL

api_key = PREFECT_API_KEY.value()
api_url = PREFECT_API_URL.value()

print(f\"API URL: {api_url}\")
print(f\"API Key: {api_key[:20]}...\")

headers = {\"Authorization\": f\"Bearer {api_key}\"}
try:
    response = requests.get(f\"{api_url}/flows\", headers=headers, timeout=10)
    if response.status_code == 200:
        print(\"✅ Cloud connectivity successful\")
    elif response.status_code == 401:
        print(\"❌ Authentication failed - check API key\")
    else:
        print(f\"⚠️ API responded with status {response.status_code}\")
except Exception as e:
    print(f\"❌ Connection error: {e}\")
"

echo "🎉 Prefect Cloud setup complete!"
CLOUDEOF'

run_ssh 'chmod +x /root/setup_cloud.sh'

# Create test flow script
run_ssh 'cat > /root/test_cloud_flow.py << "TESTEOF"
#!/usr/bin/env python3
"""Test Prefect Cloud Flow"""
from prefect import flow, task
from datetime import datetime
import socket
import sys

@task
def get_system_info():
    return {
        "hostname": socket.gethostname(),
        "timestamp": datetime.now().isoformat(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "prefect_version": __import__("prefect").__version__
    }

@task
def simulate_protocol():
    print("🧪 Starting protocol simulation...")
    import time
    time.sleep(1)
    return "Protocol simulation completed successfully"

@flow(name="OT-2 Cloud Verification Flow")
def ot2_cloud_test():
    print("🚀 Starting OT-2 Cloud Test Flow")
    system_info = get_system_info()
    print(f"📊 System info: {system_info}")
    protocol_result = simulate_protocol()
    print(f"🧪 Protocol result: {protocol_result}")
    return {
        "status": "success",
        "system_info": system_info,
        "protocol_result": protocol_result,
        "message": "✅ OT-2 Prefect Cloud integration working!"
    }

if __name__ == "__main__":
    result = ot2_cloud_test()
    print(f"\n🎉 Flow completed: {result}")
    print("\n📱 Check your Prefect Cloud dashboard to see this flow run!")
TESTEOF'

run_ssh 'chmod +x /root/test_cloud_flow.py'

echo "🧪 Step 4: Testing the fixed environment..."

echo "Testing environment loading..."
run_ssh 'source /root/setup_prefect_env.sh && echo "Environment: OK"'

echo "Testing Prefect import..."
run_ssh 'source /root/setup_prefect_env.sh && python3 -c "import prefect; print(f\"Prefect: {prefect.__version__}\")"'

echo "Testing flow/task decorators..."
run_ssh 'source /root/setup_prefect_env.sh && python3 -c "from prefect import flow, task; print(\"Flow/task: OK\")"'

echo -e "\n✅ ENVIRONMENT FIXED SUCCESSFULLY!"
echo "=" * 50
echo "🎯 Next Steps:"
echo "1. Get your Prefect Cloud API key and workspace URL"
echo "2. SSH to the device: ssh root@$HOSTNAME" 
echo "3. Run: ./setup_cloud.sh 'your_api_key' 'your_workspace_url'"
echo "4. Test: python3 test_cloud_flow.py"
echo "5. Check your Prefect Cloud dashboard!"
echo "=" * 50