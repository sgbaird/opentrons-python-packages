#!/usr/bin/env bash
"""
OT-2 Remote Installation Test Script
Executes installation tests on remote OT-2 simulators via SSH

Usage: ./remote_test.sh [fresh|working|both]
"""

set -e

# Device configurations
FRESH_DEVICE="100.101.232.60"    # ot2-simulator-9d169e (fresh device)
WORKING_DEVICE="100.79.160.30"   # ot2-simulator-53ad71 (working device)
SSH_USER="root"
SSH_OPTS="-o ConnectTimeout=30 -o StrictHostKeyChecking=no"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to test device connectivity
test_connectivity() {
    local device=$1
    local name=$2
    
    log "Testing connectivity to $name ($device)"
    
    if ping -c 1 -W 5 $device &>/dev/null; then
        success "Ping successful to $name"
    else
        error "Ping failed to $name"
        return 1
    fi
    
    if ssh $SSH_OPTS $SSH_USER@$device "echo 'SSH test successful'" &>/dev/null; then
        success "SSH connection successful to $name"
        return 0
    else
        error "SSH connection failed to $name"
        return 1
    fi
}

# Function to get device info
get_device_info() {
    local device=$1
    local name=$2
    
    log "Getting device info for $name"
    
    echo "=== Device Info for $name ==="
    ssh $SSH_OPTS $SSH_USER@$device "
        echo 'Hostname:' \$(hostname)
        echo 'Architecture:' \$(uname -m)
        echo 'OS:' \$(uname -o)
        echo 'Python version:' \$(python3 --version)
        echo 'Current PATH:' \$PATH
        echo 'Current PYTHONPATH:' \$PYTHONPATH
        
        if command -v prefect &> /dev/null; then
            echo 'Prefect status: INSTALLED'
            python3 -c 'import prefect; print(f\"Prefect version: {prefect.__version__}\")' 2>/dev/null || echo 'Prefect: Import failed'
        else
            echo 'Prefect status: NOT INSTALLED'
        fi
        
        echo 'Pip packages count:' \$(pip3 list 2>/dev/null | wc -l)
    "
    echo "========================="
}

# Function to copy test script to device
copy_test_script() {
    local device=$1
    local name=$2
    
    log "Copying test script to $name"
    
    # Copy the test script
    scp $SSH_OPTS test_fresh_installation.py $SSH_USER@$device:/tmp/
    
    if [ $? -eq 0 ]; then
        success "Test script copied to $name"
        return 0
    else
        error "Failed to copy test script to $name"
        return 1
    fi
}

# Function to run installation test
run_installation_test() {
    local device=$1
    local name=$2
    local test_type=$3  # "fresh" or "verification"
    
    log "Running $test_type installation test on $name"
    
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local log_file="ot2_${name}_${test_type}_${timestamp}.json"
    
    # Create a wrapper script to ensure proper environment
    ssh $SSH_OPTS $SSH_USER@$device "cat > /tmp/run_test.sh << 'EOF'
#!/bin/bash
set -e

cd /tmp
export PYTHONPATH=\"/var/user-packages/root/.local/lib/python3.10/site-packages:\$PYTHONPATH\"

echo \"Starting installation test on \$(hostname)\"
echo \"Test type: $test_type\"
echo \"Log file: $log_file\"

python3 test_fresh_installation.py $log_file

echo \"Test completed. Retrieving log...\"
EOF"
    
    # Make script executable and run
    ssh $SSH_OPTS $SSH_USER@$device "chmod +x /tmp/run_test.sh && /tmp/run_test.sh"
    
    local exit_code=$?
    
    # Retrieve the log file
    log "Retrieving test results from $name"
    scp $SSH_OPTS $SSH_USER@$device:/tmp/$log_file ./logs/ 2>/dev/null || {
        warning "Could not retrieve log file from $name"
    }
    
    if [ $exit_code -eq 0 ]; then
        success "Installation test completed successfully on $name"
        return 0
    else
        error "Installation test failed on $name (exit code: $exit_code)"
        return 1
    fi
}

# Function to clean up test files
cleanup_device() {
    local device=$1
    local name=$2
    
    log "Cleaning up test files on $name"
    ssh $SSH_OPTS $SSH_USER@$device "
        rm -f /tmp/test_fresh_installation.py
        rm -f /tmp/run_test.sh
        rm -f /tmp/ot2_*.json
    " 2>/dev/null || warning "Cleanup may have been incomplete on $name"
}

# Function to test fresh device
test_fresh_device() {
    echo ""
    echo "🧪 TESTING FRESH DEVICE (ot2-simulator-9d169e)"
    echo "=================================================="
    
    if ! test_connectivity $FRESH_DEVICE "fresh device"; then
        error "Cannot connect to fresh device. Skipping tests."
        return 1
    fi
    
    get_device_info $FRESH_DEVICE "fresh device"
    
    if copy_test_script $FRESH_DEVICE "fresh device"; then
        run_installation_test $FRESH_DEVICE "fresh" "fresh_install"
        cleanup_device $FRESH_DEVICE "fresh device"
    fi
}

# Function to verify working device
test_working_device() {
    echo ""
    echo "🔍 VERIFYING WORKING DEVICE (ot2-simulator-53ad71)"
    echo "=================================================="
    
    if ! test_connectivity $WORKING_DEVICE "working device"; then
        error "Cannot connect to working device. Skipping tests."
        return 1
    fi
    
    get_device_info $WORKING_DEVICE "working device"
    
    if copy_test_script $WORKING_DEVICE "working device"; then
        # Run only verification phase on working device
        ssh $SSH_OPTS $SSH_USER@$WORKING_DEVICE "
            cd /tmp
            export PYTHONPATH=\"/var/user-packages/root/.local/lib/python3.10/site-packages:\$PYTHONPATH\"
            
            # Quick verification test
            python3 -c '
import sys
sys.path.insert(0, \"/var/user-packages/root/.local/lib/python3.10/site-packages\")

try:
    import prefect
    print(f\"✅ Prefect {prefect.__version__} is working\")
    
    from prefect import flow, task
    print(\"✅ Flow/task decorators available\")
    
    # Test simple flow
    @task
    def test_task():
        return \"Working!\"
    
    @flow
    def test_flow():
        result = test_task()
        return result
    
    result = test_flow()
    print(f\"✅ Flow execution successful: {result}\")
    
except Exception as e:
    print(f\"❌ Error: {e}\")
    sys.exit(1)
'
        "
        cleanup_device $WORKING_DEVICE "working device"
    fi
}

# Create logs directory
mkdir -p logs

# Main execution
case "${1:-both}" in
    "fresh")
        test_fresh_device
        ;;
    "working")
        test_working_device
        ;;
    "both")
        test_working_device
        test_fresh_device
        ;;
    *)
        echo "Usage: $0 [fresh|working|both]"
        echo "  fresh   - Test fresh installation on ot2-simulator-9d169e"
        echo "  working - Verify working installation on ot2-simulator-53ad71"
        echo "  both    - Test both devices (default)"
        exit 1
        ;;
esac

echo ""
echo "🏁 Testing complete. Check logs/ directory for detailed results."