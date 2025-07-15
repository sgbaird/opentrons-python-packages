#!/usr/bin/env python3
"""
Refined script to create a focused CSV of OT2-related commands and build processes.
Filters out noise and focuses on actual execution commands.
"""

import csv
import re
from pathlib import Path
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_relevant_command(command: str) -> bool:
    """
    Determine if a command is relevant for OT2 analysis.
    Focus on actual execution, build, and test commands.
    """
    # Remove commands that are just logging/metadata
    irrelevant_patterns = [
        r'^command:\s*(view|help)$',
        r'Invoking tool:.*search_repository',
        r'Python package that you want',
        r'^Git URL:',
        r'^\s*#.*',  # Comments
        r'echo\s+"[^"]*"',  # Simple echo statements
        r'^\s*\[36;1m.*\[0m',  # Color codes
    ]
    
    for pattern in irrelevant_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return False
    
    # Focus on commands that actually do something
    relevant_patterns = [
        r'\.\/build-packages',
        r'python\s+.*\.(py|sh)',
        r'docker\s+(run|build|pull)',
        r'poetry\s+(run|install|poe)',
        r'pip\s+(install|build)',
        r'npm\s+(install|run|build)',
        r'curl\s+.*\.(tar\.gz|zip)',
        r'tar\s+-',
        r'git\s+(clone|pull|push|checkout)',
        r'mkdir|cp|mv',
        r'Building\s+package',
        r'^python\s+setup\.py',
        r'Building.*wheel',
        r'Compiling',
        r'Testing',
        r'Running.*test',
    ]
    
    for pattern in relevant_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    
    return False

def clean_command(command: str) -> str:
    """Clean up command text to make it more readable."""
    # Remove color codes and escape sequences
    command = re.sub(r'\[[\d;]*m', '', command)
    command = re.sub(r'\\\\?\[0m', '', command)
    
    # Remove extra whitespace
    command = ' '.join(command.split())
    
    # Truncate very long commands
    if len(command) > 200:
        command = command[:197] + "..."
    
    return command.strip()

def categorize_command(command: str) -> str:
    """Categorize the command type."""
    cmd_lower = command.lower()
    
    if 'build-packages' in cmd_lower or 'building package' in cmd_lower:
        return 'Package Build'
    elif 'docker' in cmd_lower:
        return 'Docker Operation'
    elif 'python' in cmd_lower and '.py' in cmd_lower:
        return 'Python Execution'
    elif any(x in cmd_lower for x in ['poetry', 'pip', 'npm']):
        return 'Package Management'
    elif any(x in cmd_lower for x in ['git', 'curl', 'wget']):
        return 'Source Retrieval'
    elif any(x in cmd_lower for x in ['tar', 'unzip', 'mkdir', 'cp', 'mv']):
        return 'File Operations'
    elif any(x in cmd_lower for x in ['test', 'lint', 'format']):
        return 'Quality Assurance'
    elif any(x in cmd_lower for x in ['compiling', 'linking', 'building']):
        return 'Compilation'
    else:
        return 'Other'

def process_csv_file(input_file: str, output_file: str):
    """Process the original CSV and create a refined version."""
    commands_data = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            command = row['command']
            
            # Skip irrelevant commands
            if not is_relevant_command(command):
                continue
            
            # Clean up the command
            clean_cmd = clean_command(command)
            
            # Skip if cleaning made it too short or empty
            if len(clean_cmd) < 5:
                continue
            
            commands_data.append({
                'log_file': row['log_file'],
                'command': clean_cmd,
                'status': row['status'],
                'category': categorize_command(clean_cmd),
                'context': row['context'][:300] + "..." if len(row['context']) > 300 else row['context']
            })
    
    # Remove duplicates while preserving order
    seen = set()
    unique_commands = []
    for cmd in commands_data:
        cmd_key = (cmd['command'], cmd['status'])
        if cmd_key not in seen:
            seen.add(cmd_key)
            unique_commands.append(cmd)
    
    # Write refined CSV
    fieldnames = ['log_file', 'category', 'command', 'status', 'context']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unique_commands)
    
    logger.info(f"Refined CSV created: {output_file}")
    logger.info(f"Commands after filtering: {len(unique_commands)}")
    
    # Print category summary
    category_counts = {}
    status_counts = {}
    
    for cmd in unique_commands:
        category = cmd['category']
        status = cmd['status']
        
        category_counts[category] = category_counts.get(category, 0) + 1
        status_counts[status] = status_counts.get(status, 0) + 1
    
    logger.info("\nCategory Summary:")
    for category, count in sorted(category_counts.items()):
        logger.info(f"  {category}: {count}")
    
    logger.info("\nStatus Summary:")
    for status, count in sorted(status_counts.items()):
        logger.info(f"  {status}: {count}")

def main():
    """Main function."""
    script_dir = Path(__file__).parent
    input_file = script_dir / "job_logs_commands_analysis.csv"
    output_file = script_dir / "ot2_commands_summary.csv"
    
    if not input_file.exists():
        logger.error(f"Input file not found: {input_file}")
        logger.info("Please run analyze_job_logs.py first to generate the source data.")
        return
    
    logger.info("Creating refined OT2 commands summary...")
    process_csv_file(str(input_file), str(output_file))
    logger.info("Analysis complete!")

if __name__ == "__main__":
    main()
