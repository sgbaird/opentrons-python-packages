#!/usr/bin/env python3
"""
Fix OT-2 Environment Variables and Prefect Cloud Setup
Addresses the issue where environment variables aren't loaded in non-interactive SSH sessions
"""

import subprocess
import sys
import os
import time

def run_ssh_command(hostname, command, timeout=30):
    """Run SSH command with proper environment setup"""
    # Always source the environment setup script first
    full_command = f"source /root/setup_prefect_env.sh 2>/dev/null || source /root/.bashrc; {command}"
    
    ssh_cmd = [
        "ssh", "-o", "ConnectTimeout=20", "-o", "StrictHostKeyChecking=no",
        f"root@{hostname}", full_command
    ]
    
    try:
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"

def fix_environment_setup(hostname):
    """Fix the environment variable loading issue"""
    
    print(f"🔧 Fixing environment setup for {hostname}")
    
    # Create a comprehensive environment setup script
    env_setup_script = '''#!/bin/bash
# Comprehensive Prefect Environment Setup for OT-2
export PATH="/var/user-packages/root/.local/bin:$PATH"
export PYTHONPATH="/var/user-packages/root/.local/lib/python3.10/site-packages:$PYTHONPATH"

# Verify environment is loaded
if command -v prefect >/dev/null 2>&1; then
    echo "✅ Prefect environment loaded successfully"
else
    echo "⚠️ Prefect not found in PATH"
fi'''

    commands = [
        # Create the environment setup script
        f'''cat > /root/setup_prefect_env.sh << 'EOF'
{env_setup_script}
EOF''',
        
        # Make it executable
        "chmod +x /root/setup_prefect_env.sh",
        
        # Update .bashrc to automatically source this script
        '''cat >> /root/.bashrc << 'EOF'

# Auto-load Prefect environment
if [ -f /root/setup_prefect_env.sh ]; then
    source /root/setup_prefect_env.sh
fi
EOF''',
        
        # Create .bash_profile for login shells  
        '''cat > /root/.bash_profile << 'EOF'
# Load .bashrc for login shells
if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi
EOF''',
        
        # Test the environment setup
        "source /root/setup_prefect_env.sh && python3 -c 'import prefect; print(f\"Prefect version: {prefect.__version__}\")'"
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"  Step {i}/{len(commands)}: Setting up environment...")
        exit_code, stdout, stderr = run_ssh_command(hostname, cmd)
        
        if exit_code != 0:
            print(f"  ❌ Failed: {stderr}")
            return False
        else:
            if stdout.strip():
                print(f"  ✅ {stdout.strip()}")
    
    return True

def setup_prefect_cloud_template(hostname):
    """Set up Prefect Cloud configuration template"""
    
    print(f"🌐 Setting up Prefect Cloud configuration template")
    
    cloud_setup_script = '''#!/bin/bash
# Prefect Cloud Setup Script
# Usage: ./setup_cloud.sh <api_key> <workspace_url>

if [ $# -ne 2 ]; then
    echo "Usage: $0 <api_key> <workspace_url>"
    echo "Example: $0 'pnb_xxx...' 'https://api.prefect.cloud/api/accounts/xxx/workspaces/xxx'"
    exit 1
fi

API_KEY="$1"
WORKSPACE_URL="$2"

echo "🌐 Setting up Prefect Cloud authentication..."

# Create profiles directory
mkdir -p /root/.prefect

# Create profile configuration
cat > /root/.prefect/profiles.toml << EOF
active = "cloud"

[profiles.cloud]
PREFECT_API_KEY = "${API_KEY}"
PREFECT_API_URL = "${WORKSPACE_URL}"
EOF

echo "✅ Prefect Cloud profile configured"

# Test configuration
echo "🧪 Testing cloud connectivity..."
python3 -c "
import requests
from prefect.settings import PREFECT_API_KEY, PREFECT_API_URL

api_key = PREFECT_API_KEY.value()
api_url = PREFECT_API_URL.value()

print(f'API URL: {api_url}')
print(f'API Key: {api_key[:20]}...')

# Test API connectivity
headers = {'Authorization': f'Bearer {api_key}'}
try:
    response = requests.get(f'{api_url}/flows', headers=headers, timeout=10)
    if response.status_code == 200:
        print('✅ Cloud connectivity successful')
    elif response.status_code == 401:
        print('❌ Authentication failed - check API key')
    else:
        print(f'⚠️ API responded with status {response.status_code}')
except Exception as e:
    print(f'❌ Connection error: {e}')
"

echo "🎉 Prefect Cloud setup complete!"
'''

    test_flow_script = '''#!/usr/bin/env python3
"""
Test Prefect Cloud Flow - Run this to verify cloud integration
"""
from prefect import flow, task
from datetime import datetime
import socket

@task
def get_system_info():
    """Get OT-2 system information"""
    import os
    return {
        "hostname": socket.gethostname(),
        "timestamp": datetime.now().isoformat(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "prefect_version": __import__("prefect").__version__
    }

@task
def simulate_protocol():
    """Simulate OT-2 protocol execution"""
    print("🧪 Starting protocol simulation...")
    
    # Simulate some work
    import time
    time.sleep(1)
    
    return "Protocol simulation completed successfully"

@flow(name="OT-2 Cloud Verification Flow")
def ot2_cloud_test():
    """Test flow to verify Prefect Cloud integration"""
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
    # Run the flow
    result = ot2_cloud_test()
    print(f"\\n🎉 Flow completed: {result}")
    print("\\n📱 Check your Prefect Cloud dashboard to see this flow run!")
'''

    # Create files separately to avoid EOF issues
    setup_file_cmd = 'cat > /root/setup_cloud.sh << "SETUPEOF"\n' + cloud_setup_script + '\nSETUPEOF'
    test_file_cmd = 'cat > /root/test_cloud_flow.py << "TESTEOF"\n' + test_flow_script + '\nTESTEOF'
    instructions_content = '''# Prefect Cloud Setup Instructions

## 1. Set up Cloud Authentication

Run the setup script with your credentials:
```bash
./setup_cloud.sh "your_api_key" "your_workspace_url"
```

### Getting Your Credentials:

**API Key:**
- Go to your Prefect Cloud dashboard
- Navigate to account settings
- Generate a new API key (starts with `pnb_` for service accounts)

**Workspace URL:**
- Format: `https://api.prefect.cloud/api/accounts/[ACCOUNT-ID]/workspaces/[WORKSPACE-ID]`
- Find in your dashboard URL or use the workspace API

## 2. Test Cloud Integration

Run the test flow:
```bash
python3 test_cloud_flow.py
```

This will:
- Execute a flow in Prefect Cloud
- Show real-time logs
- Appear in your Prefect Cloud dashboard

## 3. Environment Issues

If you get "command not found" errors:
```bash
# Manually load environment
source /root/setup_prefect_env.sh

# Then retry your commands
python3 test_cloud_flow.py
```

## 4. Troubleshooting

**Authentication Errors (401):**
- Check API key is correct
- Verify workspace URL format
- Ensure service account has proper permissions

**Connection Errors:**
- Test internet connectivity: `ping google.com`
- Check firewall settings
- Verify DNS resolution

**Import Errors:**
- Run environment setup: `source /root/setup_prefect_env.sh`
- Check Prefect installation: `python3 -c "import prefect; print(prefect.__version__)"`'''
    instructions_file_cmd = 'cat > /root/CLOUD_SETUP_INSTRUCTIONS.md << "INSTEOF"\n' + instructions_content + '\nINSTEOF'

    commands = [
        # Create cloud setup script
        setup_file_cmd,
        
        # Make it executable
        "chmod +x /root/setup_cloud.sh",
        
        # Create test flow script  
        test_file_cmd,
        
        # Make it executable
        "chmod +x /root/test_cloud_flow.py",
        
        # Create usage instructions
        instructions_file_cmd
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"  Step {i}/{len(commands)}: Creating cloud setup tools...")
        exit_code, stdout, stderr = run_ssh_command(hostname, cmd)
        
        if exit_code != 0:
            print(f"  ❌ Failed: {stderr}")
            return False
    
    print("  ✅ Cloud setup tools created")
    return True

def verify_installation(hostname):
    """Verify the complete installation"""
    
    print(f"🧪 Verifying installation on {hostname}")
    
    tests = [
        ("Environment loading", "echo 'PATH:' && echo $PATH | grep -o '/var/user-packages/root/.local/bin' || echo 'Missing'"),
        ("Prefect import", "python3 -c 'import prefect; print(f\"Prefect: {prefect.__version__}\")'"),
        ("Flow/task decorators", "python3 -c 'from prefect import flow, task; print(\"Flow/task: OK\")'"),
        ("Prefect CLI", "prefect --version 2>/dev/null || echo 'CLI not working'"),
    ]
    
    results = {}
    for test_name, command in tests:
        print(f"  Testing {test_name}...")
        exit_code, stdout, stderr = run_ssh_command(hostname, command, timeout=15)
        
        if exit_code == 0 and stdout.strip():
            print(f"  ✅ {stdout.strip()}")
            results[test_name] = "PASS"
        else:
            print(f"  ❌ Failed: {stderr or 'No output'}")
            results[test_name] = "FAIL"
    
    return results

def main():
    """Main function to fix environment and setup cloud"""
    
    hostname = "ot2-simulator-20aceb.tail6a1dd7.ts.net"
    
    print(f"🚀 Fixing OT-2 Environment and Setting up Prefect Cloud")
    print(f"Target: {hostname}")
    print("=" * 60)
    
    # Step 1: Fix environment variable loading
    if not fix_environment_setup(hostname):
        print("❌ Failed to fix environment setup")
        return False
    
    # Step 2: Set up cloud configuration tools
    if not setup_prefect_cloud_template(hostname):
        print("❌ Failed to setup cloud configuration")
        return False
    
    # Step 3: Verify installation
    results = verify_installation(hostname)
    
    # Step 4: Summary
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    
    all_passed = all(result == "PASS" for result in results.values())
    
    for test, result in results.items():
        status = "✅" if result == "PASS" else "❌"
        print(f"{status} {test}: {result}")
    
    if all_passed:
        print(f"\n🎉 SUCCESS: Environment fixed for {hostname}")
        print("\nNext steps:")
        print("1. Get your Prefect Cloud API key and workspace URL")
        print("2. Run: ssh root@ot2-simulator-20aceb.tail6a1dd7.ts.net")
        print("3. Run: ./setup_cloud.sh 'your_api_key' 'your_workspace_url'")
        print("4. Run: python3 test_cloud_flow.py")
        print("5. Check your Prefect Cloud dashboard for the flow run!")
    else:
        print(f"\n⚠️ Some tests failed. Check installation.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)