#!/usr/bin/env python3
"""
OT-2 Fresh Installation Test Script
Systematically tests Prefect installation from scratch on a fresh OT-2 simulator

This script validates every step of the installation guide and documents results.
"""

import subprocess
import sys
import os
import time
import json
from datetime import datetime
from pathlib import Path

class InstallationTester:
    def __init__(self, log_file="installation_test_log.json"):
        self.log_file = log_file
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "device_info": {},
            "test_phases": {},
            "commands_executed": [],
            "final_status": {}
        }
        
    def log_command(self, command, result, phase, description=""):
        """Log every command and its result"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "phase": phase,
            "command": command,
            "description": description,
            "exit_code": result.returncode if hasattr(result, 'returncode') else 'N/A',
            "stdout": result.stdout if hasattr(result, 'stdout') else str(result),
            "stderr": result.stderr if hasattr(result, 'stderr') else "",
            "success": result.returncode == 0 if hasattr(result, 'returncode') else False
        }
        self.results["commands_executed"].append(entry)
        
        # Print real-time feedback
        status = "✅" if entry["success"] else "❌"
        print(f"{status} [{phase}] {description or command}")
        if entry["stdout"]:
            print(f"   → {entry['stdout'][:100]}{'...' if len(entry['stdout']) > 100 else ''}")
        if entry["stderr"]:
            print(f"   ⚠️ {entry['stderr'][:100]}{'...' if len(entry['stderr']) > 100 else ''}")
            
    def run_command(self, cmd, description="", timeout=120):
        """Run a command and capture result"""
        try:
            if isinstance(cmd, str):
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            else:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return result
        except subprocess.TimeoutExpired:
            return type('Result', (), {
                'returncode': -1, 
                'stdout': '', 
                'stderr': f'Command timed out after {timeout}s'
            })()
        except Exception as e:
            return type('Result', (), {
                'returncode': -1, 
                'stdout': '', 
                'stderr': str(e)
            })()
    
    def phase_1_baseline_check(self):
        """Phase 1: Check baseline system state"""
        print("=" * 60)
        print("PHASE 1: BASELINE SYSTEM CHECK")
        print("=" * 60)
        
        phase_results = {}
        
        # Basic system info
        cmd = "uname -a"
        result = self.run_command(cmd)
        self.log_command(cmd, result, "baseline", "Get system info")
        phase_results["system_info"] = result.stdout.strip()
        
        cmd = "hostname"
        result = self.run_command(cmd)
        self.log_command(cmd, result, "baseline", "Get hostname")
        phase_results["hostname"] = result.stdout.strip()
        
        # Python version
        cmd = "python3 --version"
        result = self.run_command(cmd)
        self.log_command(cmd, result, "baseline", "Check Python version")
        phase_results["python_version"] = result.stdout.strip()
        
        # Check if Prefect is already installed
        cmd = "python3 -c 'import prefect; print(f\"Already installed: {prefect.__version__}\")'"
        result = self.run_command(cmd)
        self.log_command(cmd, result, "baseline", "Check existing Prefect installation")
        phase_results["existing_prefect"] = result.returncode == 0
        
        # Check existing packages
        cmd = "pip3 list"
        result = self.run_command(cmd)
        self.log_command(cmd, result, "baseline", "List existing packages")
        phase_results["existing_packages"] = len(result.stdout.split('\n')) if result.returncode == 0 else 0
        
        # Check current PATH and PYTHONPATH
        cmd = "echo $PATH"
        result = self.run_command(cmd)
        self.log_command(cmd, result, "baseline", "Check current PATH")
        phase_results["current_path"] = result.stdout.strip()
        
        cmd = "echo $PYTHONPATH"
        result = self.run_command(cmd)
        self.log_command(cmd, result, "baseline", "Check current PYTHONPATH")
        phase_results["current_pythonpath"] = result.stdout.strip()
        
        # Check network connectivity
        cmd = "curl -I --connect-timeout 10 https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/wheels/prefect-3.3.4-py3-none-any.whl"
        result = self.run_command(cmd)
        self.log_command(cmd, result, "baseline", "Test network connectivity to wheel repository")
        phase_results["network_connectivity"] = result.returncode == 0
        
        self.results["test_phases"]["phase_1"] = phase_results
        return phase_results
    
    def phase_2_environment_setup(self):
        """Phase 2: Set up environment as per installation guide"""
        print("\n" + "=" * 60)
        print("PHASE 2: ENVIRONMENT SETUP")
        print("=" * 60)
        
        phase_results = {}
        
        # Create .bashrc configuration
        bashrc_content = """export PATH="/var/user-packages/root/.local/bin:$PATH"
export PYTHONPATH="/var/user-packages/root/.local/lib/python3.10/site-packages:$PYTHONPATH" """
        
        cmd = f"cat > /root/.bashrc << 'EOF'\n{bashrc_content}\nEOF"
        result = self.run_command(cmd)
        self.log_command(cmd, result, "environment", "Create .bashrc configuration")
        phase_results["bashrc_created"] = result.returncode == 0
        
        # Create .profile configuration
        cmd = f"cat > /root/.profile << 'EOF'\n{bashrc_content}\nEOF"
        result = self.run_command(cmd)
        self.log_command(cmd, result, "environment", "Create .profile configuration")
        phase_results["profile_created"] = result.returncode == 0
        
        # Source the configuration
        cmd = "source /root/.bashrc"
        result = self.run_command(cmd)
        self.log_command(cmd, result, "environment", "Source .bashrc configuration")
        
        # Verify environment variables are set
        cmd = "source /root/.bashrc && echo $PYTHONPATH"
        result = self.run_command(cmd)
        self.log_command(cmd, result, "environment", "Verify PYTHONPATH is set")
        phase_results["pythonpath_set"] = "/var/user-packages" in result.stdout
        
        cmd = "source /root/.bashrc && echo $PATH"
        result = self.run_command(cmd)
        self.log_command(cmd, result, "environment", "Verify PATH is set")
        phase_results["path_set"] = "/var/user-packages" in result.stdout
        
        self.results["test_phases"]["phase_2"] = phase_results
        return phase_results
    
    def phase_3_automated_installation(self):
        """Phase 3: Test automated installation script"""
        print("\n" + "=" * 60)
        print("PHASE 3: AUTOMATED INSTALLATION TEST")
        print("=" * 60)
        
        phase_results = {}
        
        # Download the installation script
        cmd = "curl -L https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/ot2_prefect_final_installer.py -o installer.py"
        result = self.run_command(cmd, timeout=60)
        self.log_command(cmd, result, "automated", "Download installation script")
        phase_results["script_downloaded"] = result.returncode == 0
        
        if result.returncode == 0:
            # Run the automated installer
            cmd = "source /root/.bashrc && python3 installer.py"
            result = self.run_command(cmd, timeout=600)  # 10 minutes timeout
            self.log_command(cmd, result, "automated", "Run automated installation script")
            phase_results["automated_install_success"] = result.returncode == 0
            
            # Test if Prefect is working after automated install
            if result.returncode == 0:
                cmd = "source /root/.bashrc && python3 -c 'import prefect; print(f\"Prefect {prefect.__version__} installed\")'"
                result = self.run_command(cmd)
                self.log_command(cmd, result, "automated", "Verify Prefect import after automated install")
                phase_results["prefect_import_success"] = result.returncode == 0
        
        self.results["test_phases"]["phase_3"] = phase_results
        return phase_results
    
    def phase_4_manual_installation_fallback(self):
        """Phase 4: Test manual installation if automated fails"""
        print("\n" + "=" * 60)
        print("PHASE 4: MANUAL INSTALLATION FALLBACK")
        print("=" * 60)
        
        phase_results = {}
        
        # Try requirements file installation first
        cmd = "curl -L https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/requirements.txt -o requirements.txt"
        result = self.run_command(cmd, timeout=60)
        self.log_command(cmd, result, "manual", "Download requirements.txt")
        
        if result.returncode == 0:
            cmd = "source /root/.bashrc && pip3 install -r requirements.txt --target /var/user-packages/root/.local/lib/python3.10/site-packages/"
            result = self.run_command(cmd, timeout=600)
            self.log_command(cmd, result, "manual", "Install from requirements.txt")
            phase_results["requirements_install"] = result.returncode == 0
            
            if result.returncode != 0:
                # Fallback to frozen requirements
                cmd = "curl -L https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/requirements-frozen.txt -o requirements-frozen.txt"
                result = self.run_command(cmd, timeout=60)
                self.log_command(cmd, result, "manual", "Download requirements-frozen.txt")
                
                if result.returncode == 0:
                    cmd = "source /root/.bashrc && pip3 install -r requirements-frozen.txt --target /var/user-packages/root/.local/lib/python3.10/site-packages/"
                    result = self.run_command(cmd, timeout=600)
                    self.log_command(cmd, result, "manual", "Install from requirements-frozen.txt")
                    phase_results["frozen_requirements_install"] = result.returncode == 0
        
        # If requirements fail, try wheel-based installation
        if not phase_results.get("requirements_install") and not phase_results.get("frozen_requirements_install"):
            # Install core wheels
            base_url = "https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/wheels/"
            wheels = [
                "pendulum-3.1.0-cp310-cp310-linux_armv7l.whl",
                "ujson-5.10.0-py3-none-linux_armv7l.whl", 
                "prefect-3.3.4-py3-none-any.whl"
            ]
            
            wheel_results = {}
            for wheel in wheels:
                cmd = f"source /root/.bashrc && python3 -m pip install --user --force-reinstall --no-deps {base_url}{wheel}"
                result = self.run_command(cmd, timeout=180)
                self.log_command(cmd, result, "manual", f"Install {wheel}")
                wheel_results[wheel] = result.returncode == 0
            
            phase_results["wheel_installs"] = wheel_results
            
            # Install additional dependencies
            deps = ["pydantic>=2.0", "rich", "typing-extensions>=4.10.0"]
            dep_results = {}
            for dep in deps:
                cmd = f"source /root/.bashrc && python3 -m pip install --user --upgrade {dep}"
                result = self.run_command(cmd, timeout=180)
                self.log_command(cmd, result, "manual", f"Install {dep}")
                dep_results[dep] = result.returncode == 0
            
            phase_results["dependency_installs"] = dep_results
        
        self.results["test_phases"]["phase_4"] = phase_results
        return phase_results
    
    def phase_5_verification(self):
        """Phase 5: Comprehensive verification of installation"""
        print("\n" + "=" * 60)
        print("PHASE 5: INSTALLATION VERIFICATION")
        print("=" * 60)
        
        phase_results = {}
        
        # Test basic Prefect import
        cmd = "source /root/.bashrc && python3 -c 'import prefect; print(f\"Prefect version: {prefect.__version__}\")'"
        result = self.run_command(cmd)
        self.log_command(cmd, result, "verification", "Test Prefect import")
        phase_results["prefect_import"] = result.returncode == 0
        
        # Test flow and task decorators
        cmd = "source /root/.bashrc && python3 -c 'from prefect import flow, task; print(\"Flow/task imports: SUCCESS\")'"
        result = self.run_command(cmd)
        self.log_command(cmd, result, "verification", "Test flow/task decorators")
        phase_results["decorators_import"] = result.returncode == 0
        
        # Test complete flow functionality
        flow_test = '''
from prefect import flow, task

@task
def say_hello(name: str):
    return f"Hello {name}!"

@flow 
def hello_flow(name: str = "OT-2"):
    message = say_hello(name)
    print(message)
    return message

if __name__ == "__main__":
    result = hello_flow()
    print(f"Flow result: {result}")
    print("🎉 PREFECT FLOW TEST COMPLETE!")
'''
        cmd = f"source /root/.bashrc && python3 -c '{flow_test}'"
        result = self.run_command(cmd, timeout=60)
        self.log_command(cmd, result, "verification", "Test complete flow execution")
        phase_results["flow_execution"] = result.returncode == 0
        
        # Test CLI availability
        cmd = "source /root/.bashrc && prefect --version"
        result = self.run_command(cmd)
        self.log_command(cmd, result, "verification", "Test Prefect CLI")
        phase_results["cli_available"] = result.returncode == 0
        
        # Test cloud login help (don't actually login)
        cmd = "source /root/.bashrc && prefect cloud login --help"
        result = self.run_command(cmd)
        self.log_command(cmd, result, "verification", "Test Prefect cloud login help")
        phase_results["cloud_login_help"] = result.returncode == 0
        
        self.results["test_phases"]["phase_5"] = phase_results
        return phase_results
    
    def generate_report(self):
        """Generate final report"""
        print("\n" + "=" * 80)
        print("FINAL INSTALLATION TEST REPORT")
        print("=" * 80)
        
        # Calculate overall success
        total_commands = len(self.results["commands_executed"])
        successful_commands = sum(1 for cmd in self.results["commands_executed"] if cmd["success"])
        
        # Phase summaries
        phase_summaries = {}
        for phase_name, phase_data in self.results["test_phases"].items():
            if isinstance(phase_data, dict):
                phase_success = sum(1 for v in phase_data.values() if v is True)
                phase_total = len([v for v in phase_data.values() if isinstance(v, bool)])
                phase_summaries[phase_name] = {
                    "success_rate": f"{phase_success}/{phase_total}" if phase_total > 0 else "N/A",
                    "percentage": round((phase_success/phase_total)*100) if phase_total > 0 else 0
                }
        
        self.results["final_status"] = {
            "total_commands": total_commands,
            "successful_commands": successful_commands,
            "command_success_rate": round((successful_commands/total_commands)*100) if total_commands > 0 else 0,
            "phase_summaries": phase_summaries,
            "overall_success": self.results["test_phases"].get("phase_5", {}).get("flow_execution", False)
        }
        
        # Print summary
        print(f"Commands executed: {successful_commands}/{total_commands} ({self.results['final_status']['command_success_rate']}% success)")
        print(f"Overall installation success: {'✅ YES' if self.results['final_status']['overall_success'] else '❌ NO'}")
        
        for phase, summary in phase_summaries.items():
            print(f"{phase}: {summary['success_rate']} ({summary['percentage']}%)")
        
        # Save detailed log
        with open(self.log_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nDetailed log saved to: {self.log_file}")
        
        return self.results
    
    def run_full_test(self):
        """Run the complete installation test suite"""
        print("🧪 Starting OT-2 Prefect Installation Test Suite")
        print(f"📝 Results will be logged to: {self.log_file}")
        
        try:
            self.phase_1_baseline_check()
            self.phase_2_environment_setup()
            self.phase_3_automated_installation()
            
            # Only run manual fallback if automated failed
            if not self.results["test_phases"]["phase_3"].get("automated_install_success"):
                self.phase_4_manual_installation_fallback()
            
            self.phase_5_verification()
            
        except KeyboardInterrupt:
            print("\n⚠️ Test interrupted by user")
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            self.results["error"] = str(e)
        
        finally:
            return self.generate_report()

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        log_file = sys.argv[1]
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"ot2_installation_test_{timestamp}.json"
    
    tester = InstallationTester(log_file)
    results = tester.run_full_test()
    
    if results["final_status"]["overall_success"]:
        print("\n🎉 INSTALLATION TEST SUCCESSFUL!")
        sys.exit(0)
    else:
        print("\n❌ INSTALLATION TEST FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()