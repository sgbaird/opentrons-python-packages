#!/usr/bin/env bash
"""
Fresh Device Installation Command Tracker
Tracks every command sent to ot2-simulator-9d169e with detailed logging

This script will meticulously document every interaction with the fresh device
as requested in the issue description.
"""

set -e

FRESH_DEVICE="100.101.232.60"  # ot2-simulator-9d169e
SSH_USER="root"
SSH_OPTS="-o ConnectTimeout=30 -o StrictHostKeyChecking=no"
LOG_FILE="fresh_device_commands_$(date +%Y%m%d_%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Initialize log file
cat > "$LOG_FILE" << EOF
OT-2 Fresh Device Installation Command Log
==========================================
Device: ot2-simulator-9d169e ($FRESH_DEVICE)
Start Time: $(date)
Purpose: Test and refine Prefect installation instructions

Command Format:
[TIMESTAMP] COMMAND: <command>
[TIMESTAMP] RESULT: <exit_code> 
[TIMESTAMP] STDOUT: <output>
[TIMESTAMP] STDERR: <errors>
[TIMESTAMP] NOTES: <observations>

EOF

log_command() {
    local cmd="$1"
    local description="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo -e "${CYAN}[$timestamp]${NC} ${BLUE}EXECUTING:${NC} $description"
    echo -e "${CYAN}[$timestamp]${NC} ${YELLOW}COMMAND:${NC} $cmd"
    
    # Log to file
    {
        echo "[$timestamp] PHASE: $description"
        echo "[$timestamp] COMMAND: $cmd"
    } >> "$LOG_FILE"
    
    # Execute command and capture all output
    local exit_code=0
    local stdout_file=$(mktemp)
    local stderr_file=$(mktemp)
    
    if [[ "$cmd" == ssh* ]]; then
        # For SSH commands, execute directly
        eval "$cmd" > "$stdout_file" 2> "$stderr_file" || exit_code=$?
    else
        # For local commands
        bash -c "$cmd" > "$stdout_file" 2> "$stderr_file" || exit_code=$?
    fi
    
    local stdout_content=$(cat "$stdout_file")
    local stderr_content=$(cat "$stderr_file")
    
    # Display results
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✅ SUCCESS${NC} (exit code: $exit_code)"
    else
        echo -e "${RED}❌ FAILED${NC} (exit code: $exit_code)"
    fi
    
    if [ -n "$stdout_content" ]; then
        echo -e "${GREEN}STDOUT:${NC}"
        echo "$stdout_content" | head -20  # Show first 20 lines
        if [ $(echo "$stdout_content" | wc -l) -gt 20 ]; then
            echo "... (output truncated, see log file for full output)"
        fi
    fi
    
    if [ -n "$stderr_content" ]; then
        echo -e "${RED}STDERR:${NC}"
        echo "$stderr_content" | head -10  # Show first 10 lines of errors
        if [ $(echo "$stderr_content" | wc -l) -gt 10 ]; then
            echo "... (error output truncated, see log file for full output)"
        fi
    fi
    
    # Log to file
    {
        echo "[$timestamp] EXIT_CODE: $exit_code"
        echo "[$timestamp] STDOUT_START"
        echo "$stdout_content"
        echo "[$timestamp] STDOUT_END"
        echo "[$timestamp] STDERR_START"
        echo "$stderr_content"
        echo "[$timestamp] STDERR_END"
        echo "[$timestamp] STATUS: $([ $exit_code -eq 0 ] && echo "SUCCESS" || echo "FAILED")"
        echo "[$timestamp] ---"
        echo ""
    } >> "$LOG_FILE"
    
    # Cleanup temp files
    rm -f "$stdout_file" "$stderr_file"
    
    # Brief pause for readability
    sleep 1
    
    return $exit_code
}

test_connectivity() {
    echo ""
    echo "🔌 TESTING CONNECTIVITY TO FRESH DEVICE"
    echo "========================================"
    
    log_command "ping -c 3 $FRESH_DEVICE" "Test ping connectivity"
    local ping_result=$?
    
    if [ $ping_result -eq 0 ]; then
        log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'echo \"SSH test successful\" && hostname'" "Test SSH connectivity"
        return $?
    else
        echo -e "${RED}❌ Device not reachable via ping. Cannot proceed.${NC}"
        echo "[$timestamp] ERROR: Device not reachable via ping" >> "$LOG_FILE"
        return 1
    fi
}

baseline_check() {
    echo ""
    echo "📋 BASELINE SYSTEM CHECK"
    echo "========================"
    
    log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'hostname'" "Get hostname"
    log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'uname -a'" "Get system info"
    log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'python3 --version'" "Check Python version"
    log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'which python3'" "Locate Python executable"
    log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'pip3 --version'" "Check pip version"
    log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'echo \$PATH'" "Check current PATH"
    log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'echo \$PYTHONPATH'" "Check current PYTHONPATH"
    log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'pip3 list | wc -l'" "Count installed packages"
    log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'df -h /'" "Check disk space"
    log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'free -h'" "Check memory"
    
    # Critical test: Is Prefect already installed?
    log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'python3 -c \"import prefect; print(f\\\"Prefect {prefect.__version__} already installed\\\")\"'" "Check if Prefect is pre-installed"
    local prefect_preinstalled=$?
    
    if [ $prefect_preinstalled -eq 0 ]; then
        echo -e "${YELLOW}⚠️ WARNING: Prefect appears to be already installed on this 'fresh' device${NC}"
        echo "[$timestamp] WARNING: Prefect already installed on supposedly fresh device" >> "$LOG_FILE"
    else
        echo -e "${GREEN}✅ Confirmed: Fresh device has no Prefect installation${NC}"
        echo "[$timestamp] CONFIRMED: Fresh device ready for installation" >> "$LOG_FILE"
    fi
    
    return 0
}

test_automated_installation() {
    echo ""
    echo "🤖 TESTING AUTOMATED INSTALLATION"
    echo "=================================="
    
    # Step 1: Download installer
    log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'curl -L https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/ot2_prefect_final_installer.py -o installer.py'" "Download automated installer"
    
    if [ $? -eq 0 ]; then
        # Verify download
        log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'ls -la installer.py'" "Verify installer downloaded"
        log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'head -5 installer.py'" "Check installer content"
        
        # Run installer
        echo -e "${BLUE}Running automated installer (this may take several minutes)...${NC}"
        log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'python3 installer.py'" "Execute automated installer"
        local install_result=$?
        
        if [ $install_result -eq 0 ]; then
            echo -e "${GREEN}✅ Automated installation completed successfully${NC}"
            
            # Test the installation
            log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'source /root/.bashrc && python3 -c \"import prefect; print(f\\\"Prefect {prefect.__version__} installed\\\")\"'" "Verify Prefect installation"
            log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'source /root/.bashrc && prefect --version'" "Test Prefect CLI"
            
            return 0
        else
            echo -e "${RED}❌ Automated installation failed${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Could not download installer${NC}"
        return 1
    fi
}

test_manual_installation() {
    echo ""
    echo "🔧 TESTING MANUAL INSTALLATION (FALLBACK)"
    echo "=========================================="
    
    # Environment setup
    echo -e "${BLUE}Setting up environment...${NC}"
    
    log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'cat > /root/.bashrc << \\\"EOF\\\"
export PATH=\\\"/var/user-packages/root/.local/bin:\\\$PATH\\\"
export PYTHONPATH=\\\"/var/user-packages/root/.local/lib/python3.10/site-packages:\\\$PYTHONPATH\\\"
EOF'" "Create .bashrc configuration"
    
    log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'cat > /root/.profile << \\\"EOF\\\"
export PATH=\\\"/var/user-packages/root/.local/bin:\\\$PATH\\\"
export PYTHONPATH=\\\"/var/user-packages/root/.local/lib/python3.10/site-packages:\\\$PYTHONPATH\\\"
EOF'" "Create .profile configuration"
    
    log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'source /root/.bashrc && echo \"PYTHONPATH: \$PYTHONPATH\"'" "Verify environment setup"
    
    # Try requirements files
    echo -e "${BLUE}Trying requirements files...${NC}"
    
    log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'curl -L https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/requirements.txt -o requirements.txt'" "Download requirements.txt"
    
    if [ $? -eq 0 ]; then
        log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'source /root/.bashrc && pip3 install -r requirements.txt --target /var/user-packages/root/.local/lib/python3.10/site-packages/'" "Install from requirements.txt"
        local req_result=$?
        
        if [ $req_result -ne 0 ]; then
            echo -e "${YELLOW}Requirements.txt failed, trying frozen requirements...${NC}"
            
            log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'curl -L https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/requirements-frozen.txt -o requirements-frozen.txt'" "Download requirements-frozen.txt"
            
            log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'source /root/.bashrc && pip3 install -r requirements-frozen.txt --target /var/user-packages/root/.local/lib/python3.10/site-packages/'" "Install from requirements-frozen.txt"
            local frozen_result=$?
            
            if [ $frozen_result -ne 0 ]; then
                echo -e "${YELLOW}Frozen requirements failed, trying wheel installation...${NC}"
                
                # Install core wheels
                BASE_URL="https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/wheels/"
                
                log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'source /root/.bashrc && python3 -m pip install --user --force-reinstall --no-deps ${BASE_URL}pendulum-3.1.0-cp310-cp310-linux_armv7l.whl'" "Install pendulum wheel"
                
                log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'source /root/.bashrc && python3 -m pip install --user --force-reinstall --no-deps ${BASE_URL}ujson-5.10.0-py3-none-linux_armv7l.whl'" "Install ujson wheel"
                
                log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'source /root/.bashrc && python3 -m pip install --user --force-reinstall --no-deps ${BASE_URL}prefect-3.3.4-py3-none-any.whl'" "Install Prefect wheel"
                
                # Install additional dependencies
                log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'source /root/.bashrc && python3 -m pip install --user --upgrade pydantic>=2.0 rich typing-extensions>=4.10.0'" "Install additional dependencies"
            fi
        fi
    fi
}

test_installation_verification() {
    echo ""
    echo "✅ TESTING INSTALLATION VERIFICATION"
    echo "===================================="
    
    # Test basic import
    log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'source /root/.bashrc && python3 -c \"import prefect; print(f\\\"Prefect version: {prefect.__version__}\\\")\"'" "Test Prefect import"
    local import_result=$?
    
    # Test flow/task decorators
    log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'source /root/.bashrc && python3 -c \"from prefect import flow, task; print(\\\"Flow/task imports: SUCCESS\\\")\"'" "Test flow/task imports"
    local decorators_result=$?
    
    # Test complete flow
    if [ $decorators_result -eq 0 ]; then
        log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'source /root/.bashrc && python3 -c \"
from prefect import flow, task

@task
def say_hello(name: str):
    return f\\\"Hello {name}!\\\"

@flow 
def hello_flow(name: str = \\\"OT-2\\\"):
    message = say_hello(name)
    print(message)
    return message

if __name__ == \\\"__main__\\\":
    result = hello_flow()
    print(f\\\"✅ Flow result: {result}\\\")
    print(\\\"🎉 PREFECT FULLY WORKING ON OT-2!\\\")
\"'" "Test complete flow execution"
        local flow_result=$?
    fi
    
    # Test CLI
    log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'source /root/.bashrc && prefect --version'" "Test Prefect CLI"
    local cli_result=$?
    
    # Test cloud login help
    log_command "ssh $SSH_OPTS $SSH_USER@$FRESH_DEVICE 'source /root/.bashrc && prefect cloud login --help'" "Test cloud login help"
    
    # Generate final assessment
    local overall_success=1
    if [ $import_result -eq 0 ] && [ $decorators_result -eq 0 ] && [ ${flow_result:-1} -eq 0 ] && [ $cli_result -eq 0 ]; then
        overall_success=0
    fi
    
    return $overall_success
}

generate_final_report() {
    echo ""
    echo "📊 FINAL INSTALLATION REPORT"
    echo "============================"
    
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    {
        echo ""
        echo "[$timestamp] ==============================================="
        echo "[$timestamp] FINAL INSTALLATION SUMMARY"
        echo "[$timestamp] ==============================================="
        echo "[$timestamp] Device: ot2-simulator-9d169e ($FRESH_DEVICE)"
        echo "[$timestamp] Test completed at: $timestamp"
    } >> "$LOG_FILE"
    
    echo -e "${BLUE}📁 Complete command log saved to: ${NC}$LOG_FILE"
    echo ""
    echo "This log contains:"
    echo "  - Every command sent to the fresh device"
    echo "  - Complete output and error messages"
    echo "  - Timestamps for all interactions"
    echo "  - Success/failure status for each step"
    echo ""
    echo "You can use this log to:"
    echo "  1. Understand exactly what worked and what didn't"
    echo "  2. Refine the installation guide"
    echo "  3. Identify unnecessary steps"
    echo "  4. Create a minimal, working installation procedure"
}

main() {
    echo "🧪 OT-2 Fresh Device Installation Test"
    echo "======================================"
    echo "Device: ot2-simulator-9d169e"
    echo "Purpose: Test and refine Prefect installation instructions"
    echo "Log file: $LOG_FILE"
    echo ""
    
    # Test connectivity first
    if ! test_connectivity; then
        echo -e "${RED}❌ Cannot connect to fresh device. Test aborted.${NC}"
        generate_final_report
        exit 1
    fi
    
    # Baseline check
    baseline_check
    
    # Try automated installation first
    if test_automated_installation; then
        echo -e "${GREEN}✅ Automated installation successful${NC}"
        
        # Verify it works
        if test_installation_verification; then
            echo -e "${GREEN}🎉 INSTALLATION TEST COMPLETELY SUCCESSFUL!${NC}"
            generate_final_report
            exit 0
        else
            echo -e "${YELLOW}⚠️ Automated installation completed but verification failed${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ Automated installation failed, trying manual installation${NC}"
        
        # Try manual installation as fallback
        test_manual_installation
        
        # Verify manual installation
        if test_installation_verification; then
            echo -e "${GREEN}🎉 MANUAL INSTALLATION SUCCESSFUL!${NC}"
            generate_final_report
            exit 0
        else
            echo -e "${RED}❌ Manual installation also failed${NC}"
        fi
    fi
    
    generate_final_report
    echo -e "${RED}❌ Installation test completed with issues. Check log file for details.${NC}"
    exit 1
}

# Create logs directory
mkdir -p logs
cd logs

# Run main function
main "$@"