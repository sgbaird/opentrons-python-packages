#!/usr/bin/env python3
"""
OT-2 Prefect Installation Guide Validation Script
Tests and documents each step of the installation guide to identify issues and create a refined version.

This script can be run on either a fresh or working device to validate the installation process.
"""

import subprocess
import sys
import os
import json
import time
from datetime import datetime

class InstallationGuideValidator:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "device_info": {},
            "guide_step_tests": {},
            "command_log": [],
            "issues_found": [],
            "recommendations": []
        }
        self.step_count = 0
        
    def log_step(self, step_name, command, result, expected_outcome="", notes=""):
        """Log each step of the installation guide test"""
        self.step_count += 1
        
        step_entry = {
            "step_number": self.step_count,
            "step_name": step_name,
            "command": command,
            "expected_outcome": expected_outcome,
            "actual_result": {
                "exit_code": getattr(result, 'returncode', 'N/A'),
                "stdout": getattr(result, 'stdout', str(result))[:500],  # Limit output
                "stderr": getattr(result, 'stderr', '')[:500]
            },
            "success": getattr(result, 'returncode', 1) == 0,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }
        
        self.results["command_log"].append(step_entry)
        
        # Print real-time feedback
        status = "✅" if step_entry["success"] else "❌"
        print(f"{status} Step {self.step_count}: {step_name}")
        if step_entry["actual_result"]["stdout"]:
            print(f"   → {step_entry['actual_result']['stdout'][:100]}...")
        if step_entry["actual_result"]["stderr"]:
            print(f"   ⚠️ {step_entry['actual_result']['stderr'][:100]}...")
        if notes:
            print(f"   📝 {notes}")
        
        return step_entry["success"]
    
    def run_command(self, cmd, timeout=120):
        """Execute a command and return result"""
        try:
            if isinstance(cmd, str):
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            else:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return result
        except subprocess.TimeoutExpired:
            return type('obj', (object,), {
                'returncode': -1,
                'stdout': '',
                'stderr': f'Command timed out after {timeout}s'
            })()
        except Exception as e:
            return type('obj', (object,), {
                'returncode': -1,
                'stdout': '',
                'stderr': str(e)
            })()
    
    def collect_device_info(self):
        """Collect comprehensive device information"""
        print("=" * 60)
        print("COLLECTING DEVICE INFORMATION")
        print("=" * 60)
        
        info_commands = {
            "hostname": "hostname",
            "architecture": "uname -m",
            "os_info": "uname -a",
            "python_version": "python3 --version",
            "python_path": "which python3",
            "pip_version": "pip3 --version",
            "current_path": "echo $PATH",
            "current_pythonpath": "echo $PYTHONPATH",
            "user_info": "whoami",
            "working_directory": "pwd",
            "disk_space": "df -h /",
            "memory_info": "free -h"
        }
        
        for key, cmd in info_commands.items():
            result = self.run_command(cmd)
            if result.returncode == 0:
                self.results["device_info"][key] = result.stdout.strip()
            else:
                self.results["device_info"][key] = f"Error: {result.stderr.strip()}"
        
        # Check if Prefect is already installed
        result = self.run_command("python3 -c 'import prefect; print(prefect.__version__)'")
        self.results["device_info"]["prefect_preinstalled"] = result.returncode == 0
        if result.returncode == 0:
            self.results["device_info"]["prefect_version"] = result.stdout.strip()
        
        # Print device summary
        print(f"Device: {self.results['device_info'].get('hostname', 'unknown')}")
        print(f"Architecture: {self.results['device_info'].get('architecture', 'unknown')}")
        print(f"Python: {self.results['device_info'].get('python_version', 'unknown')}")
        print(f"Prefect pre-installed: {self.results['device_info']['prefect_preinstalled']}")
        
    def test_prerequisites(self):
        """Test the prerequisites section of the guide"""
        print("\n" + "=" * 60)
        print("TESTING PREREQUISITES")
        print("=" * 60)
        
        # Test Python 3.10 requirement
        result = self.run_command("python3 --version")
        success = self.log_step(
            "Check Python 3.10",
            "python3 --version",
            result,
            "Python 3.10.x",
            "Guide requires Python 3.10"
        )
        
        if "3.10" not in result.stdout:
            self.results["issues_found"].append({
                "section": "Prerequisites",
                "issue": "Python version is not 3.10 as required by guide",
                "actual": result.stdout.strip(),
                "severity": "high"
            })
        
        # Test network connectivity
        result = self.run_command("curl -I --connect-timeout 10 https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/wheels/prefect-3.3.4-py3-none-any.whl")
        success = self.log_step(
            "Test network connectivity",
            "curl -I [wheel URL]",
            result,
            "HTTP 200 OK",
            "Required for downloading wheels"
        )
        
        if result.returncode != 0:
            self.results["issues_found"].append({
                "section": "Prerequisites", 
                "issue": "Cannot access wheel repository",
                "actual": result.stderr,
                "severity": "high"
            })
        
        # Test SSH access (we're already connected)
        self.log_step(
            "SSH access",
            "N/A - already connected",
            type('obj', (object,), {'returncode': 0, 'stdout': 'Connected', 'stderr': ''})(),
            "Successful SSH connection",
            "We're already connected via SSH"
        )
    
    def test_option1_automated_script(self):
        """Test Option 1: Automated Installation Script"""
        print("\n" + "=" * 60)
        print("TESTING OPTION 1: AUTOMATED INSTALLATION SCRIPT")
        print("=" * 60)
        
        # Step 1: Download the installer
        result = self.run_command("curl -L https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/ot2_prefect_final_installer.py -o /tmp/installer.py")
        success = self.log_step(
            "Download installer script",
            "curl -L [installer URL] -o /tmp/installer.py",
            result,
            "File downloaded successfully",
            "As per guide instructions"
        )
        
        if not success:
            self.results["issues_found"].append({
                "section": "Option 1",
                "issue": "Cannot download installer script",
                "actual": result.stderr,
                "severity": "high"
            })
            return False
        
        # Check if file was actually downloaded
        result = self.run_command("ls -la /tmp/installer.py")
        success = self.log_step(
            "Verify installer downloaded",
            "ls -la /tmp/installer.py",
            result,
            "File exists with reasonable size",
            "Confirming download"
        )
        
        # Step 2: Run the installer (but don't actually run it if Prefect is already installed)
        if self.results["device_info"]["prefect_preinstalled"]:
            # Just check that the script is valid Python
            result = self.run_command("python3 -m py_compile /tmp/installer.py")
            self.log_step(
                "Validate installer script syntax",
                "python3 -m py_compile /tmp/installer.py",
                result,
                "No syntax errors",
                "Skipping actual execution since Prefect is pre-installed"
            )
        else:
            # Actually run the installer on fresh device
            result = self.run_command("cd /tmp && python3 installer.py", timeout=600)
            success = self.log_step(
                "Run automated installer",
                "python3 installer.py",
                result,
                "Installation successful",
                "Running complete installation"
            )
        
        return True
    
    def test_option2_manual_steps(self):
        """Test Option 2: Manual Step-by-Step Installation"""
        print("\n" + "=" * 60)
        print("TESTING OPTION 2: MANUAL INSTALLATION STEPS")
        print("=" * 60)
        
        # Step 1: Set Up Environment
        print("\nTesting Step 1: Environment Setup")
        
        # Test creating .bashrc
        bashrc_content = '''export PATH="/var/user-packages/root/.local/bin:$PATH"
export PYTHONPATH="/var/user-packages/root/.local/lib/python3.10/site-packages:$PYTHONPATH"'''
        
        # Backup existing .bashrc if it exists
        result = self.run_command("cp /root/.bashrc /root/.bashrc.backup 2>/dev/null || echo 'No existing .bashrc'")
        self.log_step(
            "Backup existing .bashrc",
            "cp /root/.bashrc /root/.bashrc.backup",
            result,
            "Backup created or no existing file",
            "Safety measure"
        )
        
        # Create new .bashrc as per guide
        result = self.run_command(f'cat > /root/.bashrc.test << \'EOF\'\n{bashrc_content}\nEOF')
        success = self.log_step(
            "Create .bashrc configuration",
            "cat > /root/.bashrc << 'EOF' [content] EOF",
            result,
            "File created successfully",
            "As instructed in guide"
        )
        
        # Test .profile creation
        result = self.run_command(f'cat > /root/.profile.test << \'EOF\'\n{bashrc_content}\nEOF')
        success = self.log_step(
            "Create .profile configuration",
            "cat > /root/.profile << 'EOF' [content] EOF",
            result,
            "File created successfully",
            "As instructed in guide"
        )
        
        # Test sourcing configuration (use test files to avoid disrupting working system)
        result = self.run_command("source /root/.bashrc.test && echo $PYTHONPATH")
        success = self.log_step(
            "Test sourcing .bashrc",
            "source /root/.bashrc && echo $PYTHONPATH",
            result,
            "PYTHONPATH contains /var/user-packages",
            "Verifying environment setup"
        )
        
        if "/var/user-packages" not in result.stdout:
            self.results["issues_found"].append({
                "section": "Manual Step 1",
                "issue": "PYTHONPATH not set correctly after sourcing .bashrc",
                "actual": result.stdout,
                "severity": "medium"
            })
        
        # Step 2: Try Requirements Files
        print("\nTesting Step 2: Requirements Files")
        
        # Test downloading requirements.txt
        result = self.run_command("curl -L https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/requirements.txt -o /tmp/requirements.txt")
        success = self.log_step(
            "Download requirements.txt",
            "curl -L [requirements URL] -o requirements.txt",
            result,
            "File downloaded successfully",
            "Option A in guide"
        )
        
        # Check file content
        if success:
            result = self.run_command("head -10 /tmp/requirements.txt")
            self.log_step(
                "Inspect requirements.txt content",
                "head -10 requirements.txt",
                result,
                "Shows package list",
                "Verifying file integrity"
            )
        
        # Test downloading frozen requirements
        result = self.run_command("curl -L https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/requirements-frozen.txt -o /tmp/requirements-frozen.txt")
        success = self.log_step(
            "Download requirements-frozen.txt",
            "curl -L [frozen requirements URL] -o requirements-frozen.txt",
            result,
            "File downloaded successfully",
            "Option B in guide"
        )
        
        # Step 3: Core Dependencies Installation (test URLs)
        print("\nTesting Step 3: Core Dependencies")
        
        base_url = "https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/wheels/"
        wheels = [
            "pendulum-3.1.0-cp310-cp310-linux_armv7l.whl",
            "ujson-5.10.0-py3-none-linux_armv7l.whl", 
            "prefect-3.3.4-py3-none-any.whl"
        ]
        
        for wheel in wheels:
            url = base_url + wheel
            result = self.run_command(f"curl -I {url}")
            success = self.log_step(
                f"Check wheel availability: {wheel}",
                f"curl -I {url}",
                result,
                "HTTP 200 OK",
                "Verifying wheel accessibility"
            )
            
            if result.returncode != 0 or "200 OK" not in result.stdout:
                self.results["issues_found"].append({
                    "section": "Manual Step 3",
                    "issue": f"Wheel {wheel} not accessible",
                    "actual": result.stderr or result.stdout,
                    "severity": "high"
                })
    
    def test_verification_steps(self):
        """Test the verification steps from the guide"""
        print("\n" + "=" * 60)
        print("TESTING VERIFICATION STEPS")
        print("=" * 60)
        
        # Only test if we can source the proper environment
        source_cmd = "source /root/.bashrc 2>/dev/null || true"
        
        # Test basic import
        cmd = f"{source_cmd} && python3 -c 'import prefect; print(f\"Prefect version: {{prefect.__version__}}\")'"
        result = self.run_command(cmd)
        success = self.log_step(
            "Test Prefect basic import",
            "python3 -c 'import prefect; print(f\"Prefect version: {prefect.__version__}\")'",
            result,
            "Shows Prefect version",
            "Step 3 verification in guide"
        )
        
        # Test flow/task decorators
        cmd = f"{source_cmd} && python3 -c 'from prefect import flow, task; print(\"Flow/task imports: SUCCESS\")'"
        result = self.run_command(cmd)
        success = self.log_step(
            "Test flow/task decorators",
            "python3 -c 'from prefect import flow, task; print(\"Flow/task imports: SUCCESS\")'",
            result,
            "Shows 'Flow/task imports: SUCCESS'",
            "Step 3 verification in guide"
        )
        
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
    print(f"✅ Flow result: {result}")
    print("🎉 PREFECT FULLY WORKING ON OT-2!")
'''
        
        cmd = f"{source_cmd} && python3 -c '{flow_test}'"
        result = self.run_command(cmd)
        success = self.log_step(
            "Test complete flow execution",
            "python3 -c '[flow test code]'",
            result,
            "Shows flow execution success",
            "Step 3 verification in guide"
        )
        
        # Test CLI access
        cmd = f"{source_cmd} && prefect --version"
        result = self.run_command(cmd)
        success = self.log_step(
            "Test Prefect CLI",
            "prefect --version",
            result,
            "Shows Prefect version",
            "Step 4 verification in guide"
        )
        
        # Test cloud login help
        cmd = f"{source_cmd} && prefect cloud login --help"
        result = self.run_command(cmd)
        success = self.log_step(
            "Test cloud login help",
            "prefect cloud login --help",
            result,
            "Shows help text",
            "Step 4 verification in guide"
        )
        
        return success
    
    def test_troubleshooting_scenarios(self):
        """Test the troubleshooting scenarios in the guide"""
        print("\n" + "=" * 60)
        print("TESTING TROUBLESHOOTING SCENARIOS")
        print("=" * 60)
        
        # Test Python version check
        result = self.run_command("python3 --version")
        success = self.log_step(
            "Troubleshooting: Check Python version",
            "python3 --version",
            result,
            "Python 3.10.x",
            "From troubleshooting section"
        )
        
        # Test PYTHONPATH verification
        result = self.run_command("echo $PYTHONPATH")
        success = self.log_step(
            "Troubleshooting: Verify PYTHONPATH",
            "echo $PYTHONPATH",
            result,
            "Shows PYTHONPATH value",
            "From troubleshooting section"
        )
        
        # Test PATH verification
        result = self.run_command("echo $PATH")
        success = self.log_step(
            "Troubleshooting: Verify PATH",
            "echo $PATH",
            result,
            "Shows PATH value",
            "From troubleshooting section"
        )
        
        # Test alternative download method
        url = "https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/wheels/prefect-3.3.4-py3-none-any.whl"
        python_download = f'''python3 -c "
import urllib.request
url = '{url}'
urllib.request.urlretrieve(url, '/tmp/prefect.whl')
print('Downloaded successfully')
"'''
        
        result = self.run_command(python_download)
        success = self.log_step(
            "Troubleshooting: Alternative download method",
            "python3 -c [urllib download code]",
            result,
            "Downloaded successfully",
            "From troubleshooting section"
        )
    
    def analyze_results(self):
        """Analyze all test results and provide recommendations"""
        print("\n" + "=" * 80)
        print("ANALYSIS AND RECOMMENDATIONS")
        print("=" * 80)
        
        total_steps = len(self.results["command_log"])
        successful_steps = sum(1 for step in self.results["command_log"] if step["success"])
        success_rate = (successful_steps / total_steps * 100) if total_steps > 0 else 0
        
        print(f"Total steps tested: {total_steps}")
        print(f"Successful steps: {successful_steps}")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Issues found: {len(self.results['issues_found'])}")
        
        # Categorize issues by severity
        high_severity = [issue for issue in self.results["issues_found"] if issue["severity"] == "high"]
        medium_severity = [issue for issue in self.results["issues_found"] if issue["severity"] == "medium"]
        
        if high_severity:
            print(f"\n🚨 HIGH SEVERITY ISSUES ({len(high_severity)}):")
            for i, issue in enumerate(high_severity, 1):
                print(f"  {i}. [{issue['section']}] {issue['issue']}")
        
        if medium_severity:
            print(f"\n⚠️ MEDIUM SEVERITY ISSUES ({len(medium_severity)}):")
            for i, issue in enumerate(medium_severity, 1):
                print(f"  {i}. [{issue['section']}] {issue['issue']}")
        
        # Generate recommendations
        recommendations = []
        
        # Check for common issues
        python_version_issues = [issue for issue in self.results["issues_found"] if "Python version" in issue["issue"]]
        if python_version_issues:
            recommendations.append("Update guide to check Python version compatibility more clearly")
        
        network_issues = [issue for issue in self.results["issues_found"] if "network" in issue["issue"].lower() or "curl" in issue["issue"].lower()]
        if network_issues:
            recommendations.append("Add more robust network connectivity checking and fallback methods")
        
        wheel_issues = [issue for issue in self.results["issues_found"] if "wheel" in issue["issue"].lower()]
        if wheel_issues:
            recommendations.append("Verify all wheel URLs are correct and accessible")
        
        environment_issues = [issue for issue in self.results["issues_found"] if "PYTHONPATH" in issue["issue"] or "PATH" in issue["issue"]]
        if environment_issues:
            recommendations.append("Improve environment setup instructions with better verification steps")
        
        if success_rate > 90:
            recommendations.append("Guide appears to be working well overall")
        elif success_rate > 70:
            recommendations.append("Guide needs minor refinements")
        else:
            recommendations.append("Guide needs significant improvements")
        
        self.results["recommendations"] = recommendations
        
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        return self.results
    
    def save_results(self, filename="installation_guide_validation.json"):
        """Save detailed results to file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📁 Detailed results saved to: {filename}")
    
    def run_validation(self):
        """Run the complete validation process"""
        print("🔍 OT-2 Prefect Installation Guide Validation")
        print("=" * 80)
        
        try:
            self.collect_device_info()
            self.test_prerequisites()
            self.test_option1_automated_script()
            self.test_option2_manual_steps()
            self.test_verification_steps()
            self.test_troubleshooting_scenarios()
            
            results = self.analyze_results()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"guide_validation_{timestamp}.json"
            self.save_results(filename)
            
            return results
            
        except KeyboardInterrupt:
            print("\n⚠️ Validation interrupted by user")
            return self.results
        except Exception as e:
            print(f"\n❌ Validation failed with error: {e}")
            self.results["error"] = str(e)
            return self.results

def main():
    """Main entry point"""
    validator = InstallationGuideValidator()
    results = validator.run_validation()
    
    # Exit with appropriate code
    if results.get("error"):
        sys.exit(1)
    elif len(results.get("issues_found", [])) == 0:
        print("\n🎉 Guide validation completed successfully!")
        sys.exit(0)
    else:
        print(f"\n⚠️ Guide validation completed with {len(results['issues_found'])} issues")
        sys.exit(2)

if __name__ == "__main__":
    main()