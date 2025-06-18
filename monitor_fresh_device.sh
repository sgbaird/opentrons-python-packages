#!/usr/bin/env bash
"""
Fresh Device Monitor
Monitors ot2-simulator-9d169e and automatically runs installation test when it comes online
"""

set -e

FRESH_DEVICE="100.101.232.60"  # ot2-simulator-9d169e
SSH_USER="root"
SSH_OPTS="-o ConnectTimeout=10 -o StrictHostKeyChecking=no"
MONITOR_LOG="fresh_device_monitor.log"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${BLUE}[$timestamp]${NC} $1"
    echo "[$timestamp] $1" >> "$MONITOR_LOG"
}

check_device() {
    # Quick ping test
    if ping -c 1 -W 5 $FRESH_DEVICE &>/dev/null; then
        # Try SSH connection
        if ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE "echo 'online'" &>/dev/null; then
            return 0  # Device is online and accessible
        fi
    fi
    return 1  # Device is offline
}

run_installation_test() {
    log "${GREEN}🎉 Fresh device is online! Starting installation test...${NC}"
    
    # Run the comprehensive installation test
    if [ -f "./test_fresh_device.sh" ]; then
        log "Running installation test script..."
        ./test_fresh_device.sh
        local test_result=$?
        
        if [ $test_result -eq 0 ]; then
            log "${GREEN}✅ Installation test completed successfully!${NC}"
        else
            log "${RED}❌ Installation test completed with issues (exit code: $test_result)${NC}"
        fi
        
        return $test_result
    else
        log "${RED}❌ Test script not found: ./test_fresh_device.sh${NC}"
        return 1
    fi
}

main() {
    echo "🔍 Fresh Device Monitor Started"
    echo "==============================="
    echo "Target: ot2-simulator-9d169e ($FRESH_DEVICE)"
    echo "Monitoring for device to come online..."
    echo "Press Ctrl+C to stop monitoring"
    echo ""
    
    log "Monitor started for ot2-simulator-9d169e ($FRESH_DEVICE)"
    
    local check_count=0
    local last_status="unknown"
    
    while true; do
        check_count=$((check_count + 1))
        
        if check_device; then
            if [ "$last_status" != "online" ]; then
                # Device just came online
                log "${GREEN}✅ Device is now ONLINE!${NC}"
                last_status="online"
                
                # Wait a moment for full boot
                log "Waiting 10 seconds for device to fully initialize..."
                sleep 10
                
                # Run the installation test
                run_installation_test
                
                log "${GREEN}🏁 Installation test completed. Monitor will continue...${NC}"
                echo ""
                echo "Monitor will continue checking device status."
                echo "To run another test when device cycles, keep monitoring..."
            fi
            
            # Device is online, check less frequently
            sleep 60  # Check every minute when online
        else
            if [ "$last_status" != "offline" ]; then
                # Device just went offline
                log "${YELLOW}📡 Device is OFFLINE${NC}"
                last_status="offline"
            fi
            
            # Show periodic status when offline
            if [ $((check_count % 10)) -eq 0 ]; then
                log "${YELLOW}Still waiting... (check #$check_count)${NC}"
            fi
            
            # Check more frequently when offline
            sleep 30  # Check every 30 seconds when offline
        fi
    done
}

# Handle Ctrl+C gracefully
trap 'echo -e "\n${YELLOW}Monitor stopped by user${NC}"; log "Monitor stopped by user"; exit 0' INT

# Create logs directory
mkdir -p logs
cd logs

# Run monitor
main "$@"