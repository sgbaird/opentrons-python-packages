#!/usr/bin/env python3
"""
GitHub Actions Log Parser and Command Extractor

This script helps extract successful installation commands from GitHub Actions logs
to retrace the "rabbit hole" installation process that eventually worked.

Usage:
    python3 extract_installation_commands.py --logs-dir /path/to/logs --output commands.csv
"""

import os
import re
import json
import csv
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Set

class LogCommandExtractor:
    def __init__(self):
        # Patterns to identify successful installations
        self.success_patterns = [
            r"Successfully installed (.+)",
            r"Successfully built (.+)", 
            r"Successfully downloaded (.+)",
            r"Requirement already satisfied: (.+)"
        ]
        
        # Patterns to identify commands that were run
        self.command_patterns = [
            r"Running command: (.+)",
            r"Executing: (.+)",
            r"\$ (.+)",
            r"bash.*?:\s*(.+)",
            r"copilot.*?:\s*(python3.*|pip.*|wget.*|curl.*|ssh.*)",
            r"command.*?:\s*(.+)",
            r"^([a-zA-Z0-9_-]+@[a-zA-Z0-9_.-]+.*?:\s*.*[pip|python|wget|curl|ssh|bash].*)",
            r"^((?:python3?|pip3?|wget|curl|ssh|bash|cat|echo|export|source)\s+.+)"
        ]
        
        # Critical package names we're tracking
        self.critical_packages = {
            'prefect', 'pendulum', 'ujson', 'pydantic', 'rich', 'typer',
            'ruamel', 'yaml', 'regex', 'dateparser', 'aiosqlite', 'alembic'
        }
        
        # Wheel URLs we've seen in successful installations
        self.wheel_urls = set()
        
        # Commands that led to success
        self.successful_command_sequences = []

    def extract_from_log(self, log_file_path: Path) -> Dict:
        """Extract commands and successes from a single log file"""
        results = {
            'file': str(log_file_path),
            'successful_installs': [],
            'commands': [],
            'wheel_urls': [],
            'critical_package_installs': [],
            'command_sequences': []
        }
        
        try:
            with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            lines = content.split('\n')
            
            current_sequence = []
            last_timestamp = None
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                # Extract timestamp if present
                timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2})', line)
                if timestamp_match:
                    last_timestamp = timestamp_match.group(1)
                
                # Check for successful installations
                for pattern in self.success_patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        packages = match.group(1)
                        results['successful_installs'].append({
                            'packages': packages,
                            'line_num': i + 1,
                            'timestamp': last_timestamp,
                            'context': self._get_context_lines(lines, i, 3)
                        })
                        
                        # Check if critical packages
                        for pkg in self.critical_packages:
                            if pkg.lower() in packages.lower():
                                results['critical_package_installs'].append({
                                    'package': pkg,
                                    'full_install': packages,
                                    'line_num': i + 1,
                                    'timestamp': last_timestamp
                                })
                
                # Extract commands
                for pattern in self.command_patterns:
                    match = re.search(pattern, line)
                    if match:
                        command = match.group(1).strip()
                        
                        # Skip empty or very short commands
                        if len(command) < 3:
                            continue
                            
                        cmd_info = {
                            'command': command,
                            'line_num': i + 1,
                            'timestamp': last_timestamp,
                            'context': self._get_context_lines(lines, i, 2)
                        }
                        
                        results['commands'].append(cmd_info)
                        current_sequence.append(cmd_info)
                        
                        # Extract wheel URLs
                        wheel_urls = re.findall(r'https?://[^\s]+\.whl', command)
                        results['wheel_urls'].extend(wheel_urls)
                        self.wheel_urls.update(wheel_urls)
                
                # If we see a success after a sequence of commands, save the sequence
                if any(re.search(pattern, line, re.IGNORECASE) for pattern in self.success_patterns):
                    if current_sequence:
                        results['command_sequences'].append({
                            'commands': current_sequence.copy(),
                            'success_line': i + 1,
                            'timestamp': last_timestamp
                        })
                        current_sequence = []
                        
        except Exception as e:
            print(f"Error processing {log_file_path}: {e}")
            
        return results

    def _get_context_lines(self, lines: List[str], current_line: int, context_size: int) -> List[str]:
        """Get surrounding lines for context"""
        start = max(0, current_line - context_size)
        end = min(len(lines), current_line + context_size + 1)
        return lines[start:end]

    def extract_from_directory(self, logs_dir: Path) -> List[Dict]:
        """Extract from all log files in directory"""
        all_results = []
        
        log_files = []
        for ext in ['*.txt', '*.log']:
            log_files.extend(logs_dir.glob(ext))
            log_files.extend(logs_dir.glob(f'**/{ext}'))
        
        print(f"Found {len(log_files)} log files to process")
        
        for log_file in log_files:
            print(f"Processing: {log_file.name}")
            results = self.extract_from_log(log_file)
            if results['successful_installs'] or results['commands']:
                all_results.append(results)
                
        return all_results

    def consolidate_successful_commands(self, all_results: List[Dict]) -> List[Dict]:
        """Consolidate all commands that led to successful installations"""
        successful_commands = []
        
        for result in all_results:
            # Commands that directly preceded successful installations
            for seq in result['command_sequences']:
                for cmd in seq['commands']:
                    cmd['source_file'] = result['file']
                    cmd['led_to_success'] = True
                    successful_commands.append(cmd)
                    
            # Also include individual successful installs with their context
            for install in result['successful_installs']:
                if install['context']:
                    for ctx_line in install['context']:
                        for pattern in self.command_patterns:
                            match = re.search(pattern, ctx_line)
                            if match:
                                successful_commands.append({
                                    'command': match.group(1).strip(),
                                    'source_file': result['file'],
                                    'led_to_success': True,
                                    'success_packages': install['packages'],
                                    'timestamp': install['timestamp']
                                })
        
        # Deduplicate while preserving order
        seen = set()
        deduplicated = []
        for cmd in successful_commands:
            cmd_text = cmd['command']
            if cmd_text not in seen and len(cmd_text) > 3:
                seen.add(cmd_text)
                deduplicated.append(cmd)
        
        return deduplicated

    def generate_installation_script(self, successful_commands: List[Dict]) -> str:
        """Generate a consolidated installation script"""
        script_lines = [
            "#!/bin/bash",
            "# Auto-generated installation script from successful GitHub Actions logs",
            f"# Generated on: {datetime.now().isoformat()}",
            f"# Based on analysis of {len(successful_commands)} successful commands",
            "",
            "set -e  # Exit on any error",
            "",
            "echo 'Starting OT-2 Prefect installation based on successful log analysis'",
            ""
        ]
        
        # Group commands by type
        env_commands = []
        pip_commands = []
        download_commands = []
        other_commands = []
        
        for cmd_info in successful_commands:
            cmd = cmd_info['command']
            
            if any(keyword in cmd.lower() for keyword in ['export', 'source', 'bashrc', 'profile']):
                env_commands.append(cmd)
            elif 'pip' in cmd.lower():
                pip_commands.append(cmd)
            elif any(keyword in cmd.lower() for keyword in ['wget', 'curl', 'download']):
                download_commands.append(cmd)
            else:
                other_commands.append(cmd)
        
        # Add environment setup
        if env_commands:
            script_lines.extend([
                "# Environment setup",
                "echo 'Setting up environment...'",
                ""
            ])
            for cmd in env_commands[:10]:  # Limit to avoid duplicates
                script_lines.append(f"echo 'Running: {cmd}'")
                script_lines.append(cmd)
                script_lines.append("")
        
        # Add downloads
        if download_commands:
            script_lines.extend([
                "# Download required files",
                "echo 'Downloading required files...'",
                ""
            ])
            for cmd in download_commands[:20]:
                script_lines.append(f"echo 'Running: {cmd}'")
                script_lines.append(cmd)
                script_lines.append("")
        
        # Add pip installations
        if pip_commands:
            script_lines.extend([
                "# Package installations",
                "echo 'Installing packages...'",
                ""
            ])
            for cmd in pip_commands[:30]:  # Most important commands
                script_lines.append(f"echo 'Running: {cmd}'")
                script_lines.append(cmd)
                script_lines.append("")
        
        script_lines.extend([
            "echo 'Installation completed!'",
            "echo 'Verifying Prefect installation...'",
            "python3 -c \"import prefect; print(f'Prefect version: {prefect.__version__}')\"",
            ""
        ])
        
        return "\n".join(script_lines)

    def save_results(self, all_results: List[Dict], successful_commands: List[Dict], output_dir: Path):
        """Save all extracted results"""
        output_dir.mkdir(exist_ok=True)
        
        # Save detailed results as JSON
        with open(output_dir / 'detailed_results.json', 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
        
        # Save successful commands as CSV
        if successful_commands:
            with open(output_dir / 'successful_commands.csv', 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['command', 'source_file', 'timestamp', 'led_to_success'])
                writer.writeheader()
                for cmd in successful_commands:
                    writer.writerow({
                        'command': cmd['command'],
                        'source_file': cmd.get('source_file', ''),
                        'timestamp': cmd.get('timestamp', ''),
                        'led_to_success': cmd.get('led_to_success', False)
                    })
        
        # Save unique wheel URLs
        with open(output_dir / 'wheel_urls.txt', 'w') as f:
            for url in sorted(self.wheel_urls):
                f.write(f"{url}\n")
        
        # Generate installation script
        script_content = self.generate_installation_script(successful_commands)
        with open(output_dir / 'consolidated_install.sh', 'w') as f:
            f.write(script_content)
        os.chmod(output_dir / 'consolidated_install.sh', 0o755)
        
        # Generate summary
        self._generate_summary(all_results, successful_commands, output_dir)

    def _generate_summary(self, all_results: List[Dict], successful_commands: List[Dict], output_dir: Path):
        """Generate a summary report"""
        total_files = len(all_results)
        total_successes = sum(len(r['successful_installs']) for r in all_results)
        total_commands = len(successful_commands)
        
        summary = [
            f"# Log Analysis Summary",
            f"Generated on: {datetime.now().isoformat()}",
            f"",
            f"## Statistics",
            f"- Log files processed: {total_files}",
            f"- Successful installations found: {total_successes}",
            f"- Successful commands extracted: {total_commands}",
            f"- Unique wheel URLs found: {len(self.wheel_urls)}",
            f"",
            f"## Critical Package Installations",
        ]
        
        # Count critical package installations
        critical_counts = {}
        for result in all_results:
            for install in result['critical_package_installs']:
                pkg = install['package']
                critical_counts[pkg] = critical_counts.get(pkg, 0) + 1
        
        for pkg, count in sorted(critical_counts.items()):
            summary.append(f"- {pkg}: {count} successful installations")
        
        summary.extend([
            f"",
            f"## Files Generated",
            f"- `detailed_results.json`: Complete extraction results",
            f"- `successful_commands.csv`: Commands that led to success", 
            f"- `wheel_urls.txt`: All wheel URLs found",
            f"- `consolidated_install.sh`: Generated installation script",
            f"",
            f"## Next Steps",
            f"1. Review the generated installation script",
            f"2. Test the script on a fresh OT-2 device",
            f"3. Refine based on any remaining issues",
        ])
        
        with open(output_dir / 'ANALYSIS_SUMMARY.md', 'w') as f:
            f.write('\n'.join(summary))

def main():
    parser = argparse.ArgumentParser(description='Extract installation commands from GitHub Actions logs')
    parser.add_argument('--logs-dir', type=Path, required=True,
                       help='Directory containing log files')
    parser.add_argument('--output-dir', type=Path, default=Path('extracted_commands'),
                       help='Output directory for results')
    
    args = parser.parse_args()
    
    if not args.logs_dir.exists():
        print(f"Error: Logs directory {args.logs_dir} does not exist")
        return 1
    
    extractor = LogCommandExtractor()
    
    print("Extracting commands from logs...")
    all_results = extractor.extract_from_directory(args.logs_dir)
    
    print("Consolidating successful commands...")
    successful_commands = extractor.consolidate_successful_commands(all_results)
    
    print("Saving results...")
    extractor.save_results(all_results, successful_commands, args.output_dir)
    
    print(f"\nAnalysis complete! Results saved to {args.output_dir}")
    print(f"Found {len(successful_commands)} commands that led to successful installations")
    print(f"Generated installation script: {args.output_dir}/consolidated_install.sh")
    
    return 0

if __name__ == '__main__':
    exit(main())