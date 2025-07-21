#!/bin/bash
# Simple script to fix OT-2 environment and setup cloud tools
set -e

# Use environment variable for hostname (no default fallback)
if [ -z "$OT2_HOSTNAME" ]; then
    echo "❌ Error: OT2_HOSTNAME environment variable must be set"
    echo "Usage: export OT2_HOSTNAME=your-device-hostname.tail6a1dd7.ts.net"
    exit 1
fi
HOSTNAME="$OT2_HOSTNAME"

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

# Copy cloud setup script to device
echo "Copying cloud setup script to device..."
scp -o ConnectTimeout=20 -o StrictHostKeyChecking=no setup_cloud.sh root@$HOSTNAME:/root/

run_ssh 'chmod +x /root/setup_cloud.sh'

# Copy cloud test script to device
echo "Copying cloud test script to device..."
scp -o ConnectTimeout=20 -o StrictHostKeyChecking=no cloud_test.py root@$HOSTNAME:/root/

# Copy tutorial flow script to device  
echo "Copying tutorial flow script to device..."
scp -o ConnectTimeout=20 -o StrictHostKeyChecking=no tutorial_flow.py root@$HOSTNAME:/root/

# Make scripts executable
run_ssh 'chmod +x /root/cloud_test.py /root/tutorial_flow.py'

echo "🧪 Step 4: Testing the fixed environment..."

echo "Testing environment loading..."
run_ssh 'source /root/setup_prefect_env.sh && echo "Environment: OK"'

echo "Testing Prefect import..."
run_ssh 'source /root/setup_prefect_env.sh && python3 -c "import prefect; print(f\"Prefect: {prefect.__version__}\")"'

echo "Testing flow/task decorators..."
run_ssh 'source /root/setup_prefect_env.sh && python3 -c "from prefect import flow, task; print(\"Flow/task: OK\")"'

echo -e "\n✅ ENVIRONMENT FIXED SUCCESSFULLY!"
echo "=" * 50
echo "Next Steps:"
echo "1. Get your Prefect Cloud API key and workspace URL"
echo "2. SSH to the device: ssh root@$HOSTNAME" 
echo "3. Run: ./setup_cloud.sh 'your_api_key' 'your_workspace_url'"
echo "4. Test: python3 tutorial_flow.py"
echo "5. Check your Prefect Cloud dashboard!"
echo "=" * 50