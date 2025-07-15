#!/usr/bin/env python3
"""
Script to analyze job logs and extract commands and their success/failure status.
Creates a CSV file with commands and their execution results.
"""

import os
import re
import csv
from pathlib import Path
from typing import List, Tuple, Dict
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_commands_from_log(log_file_path: str) -> List[Tuple[str, str, str]]:
    """
    Extract commands and their status from a single log file.
    Returns list of tuples: (command, status, context)
    """
    commands = []
    
    # Patterns to identify commands and their results
    command_patterns = [
        # Shell commands
        r'^\s*\$\s*(.+)$',
        r'^\s*>\s*(.+)$',
        r'^\s*#\s*(.+)$',
        
        # Docker commands
        r'docker\s+(run|build|pull|push)\s+(.+)',
        
        # Python/build commands
        r'python\s+(.+\.py.*)',
        r'poetry\s+(run|install|add|poe)\s+(.+)',
        r'pip\s+(install|build)\s+(.+)',
        r'\.\/build-packages\s*(.*)',
        r'npm\s+(install|run|build)\s+(.+)',
        
        # CI/CD commands
        r'(curl|wget|git|tar|unzip)\s+(.+)',
        
        # Tool invocations
        r'Invoking tool:\s*(.+)',
        r'Running:\s*(.+)',
        r'Executing:\s*(.+)',
        r'command:\s*(.+)',
        
        # Build/test commands
        r'Building\s+(.+)',
        r'Testing\s+(.+)',
        r'Compiling\s+(.+)',
    ]
    
    # Status indicators
    success_patterns = [
        r'SUCCESS',
        r'success',
        r'completed successfully',
        r'Successfully',
        r'PASSED',
        r'✓',
        r'OK',
        r'Built\s+(.+)',
        r'Completed',
        r'finished',
    ]
    
    error_patterns = [
        r'ERROR',
        r'error',
        r'FAILED',
        r'failed',
        r'Failed',
        r'Exception',
        r'Traceback',
        r'✗',
        r'FAIL',
        r'abort',
        r'killed',
    ]
    
    try:
        with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        logger.error(f"Error reading {log_file_path}: {e}")
        return []
    
    current_command = None
    command_context = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Check for command patterns
        for pattern in command_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                if current_command:
                    # Save previous command with unknown status
                    commands.append((current_command, "Unknown", ' '.join(command_context)))
                
                current_command = match.group(0)
                command_context = [line]
                break
        
        # Add context lines after a command
        if current_command and len(command_context) < 10:  # Limit context
            command_context.append(line)
        
        # Check for status indicators
        if current_command:
            status = "Unknown"
            
            # Check for success
            for pattern in success_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    status = "Success"
                    break
            
            # Check for errors (errors override success)
            for pattern in error_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    status = "Failed"
                    break
            
            # If we found a definitive status, save the command
            if status != "Unknown":
                commands.append((current_command, status, ' '.join(command_context)))
                current_command = None
                command_context = []
    
    # Save any remaining command
    if current_command:
        commands.append((current_command, "Unknown", ' '.join(command_context)))
    
    return commands

def analyze_all_logs(job_logs_dir: str) -> List[Dict[str, str]]:
    """
    Analyze all log files in the job logs directory.
    Returns list of dictionaries for CSV output.
    """
    all_commands = []
    job_logs_path = Path(job_logs_dir)
    
    if not job_logs_path.exists():
        logger.error(f"Directory {job_logs_dir} does not exist")
        return []
    
    log_files = list(job_logs_path.glob("*.txt"))
    logger.info(f"Found {len(log_files)} log files to analyze")
    
    for log_file in sorted(log_files):
        logger.info(f"Processing {log_file.name}")
        
        commands = extract_commands_from_log(str(log_file))
        
        for command, status, context in commands:
            all_commands.append({
                'log_file': log_file.name,
                'command': command.strip(),
                'status': status,
                'context': context[:500] + "..." if len(context) > 500 else context  # Truncate long context
            })
    
    return all_commands

def create_csv_report(commands: List[Dict[str, str]], output_file: str):
    """
    Create a CSV report from the extracted commands.
    """
    fieldnames = ['log_file', 'command', 'status', 'context']
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(commands)
        
        logger.info(f"CSV report created: {output_file}")
        logger.info(f"Total commands extracted: {len(commands)}")
        
        # Print summary statistics
        status_counts = {}
        for cmd in commands:
            status = cmd['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        logger.info("Status Summary:")
        for status, count in status_counts.items():
            logger.info(f"  {status}: {count}")
            
    except Exception as e:
        logger.error(f"Error creating CSV file: {e}")

def main():
    """Main function to run the analysis."""
    script_dir = Path(__file__).parent
    job_logs_dir = script_dir / "job-logs"
    output_file = script_dir / "job_logs_commands_analysis.csv"
    
    logger.info("Starting job logs analysis...")
    logger.info(f"Job logs directory: {job_logs_dir}")
    logger.info(f"Output file: {output_file}")
    
    # Analyze all logs
    commands = analyze_all_logs(str(job_logs_dir))
    
    if not commands:
        logger.warning("No commands found in log files")
        return
    
    # Create CSV report
    create_csv_report(commands, str(output_file))
    
    logger.info("Analysis complete!")

if __name__ == "__main__":
    main()
