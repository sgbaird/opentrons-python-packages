#!/usr/bin/env python3
"""
Final script to create the most user-friendly CSV of OT2 commands and their success status.
This creates a simple 2-column format as requested: command and success status.
"""

import csv
import re
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_and_simplify_command(command: str) -> str:
    """Clean up command and extract the essential executable command."""
    # Remove color codes and escape sequences
    command = re.sub(r'\[[\d;]*m', '', command)
    command = re.sub(r'\\\\?\[0m', '', command)
    
    # Remove timestamps and context
    command = re.sub(r'^\d{4}-\d{2}-\d{2}T[\d:.]+Z\s+', '', command)
    
    # Extract command from common patterns
    if 'command:' in command:
        parts = command.split('command:')
        if len(parts) > 1:
            command = parts[1].strip()
    
    # Remove directory prefixes in common patterns
    command = re.sub(r'^cd [^&]+&&?\s*', '', command)
    
    # Clean up extra whitespace and quotes
    command = ' '.join(command.split())
    command = command.strip('"\'')
    
    # Truncate very long commands but keep important parts
    if len(command) > 150:
        command = command[:147] + "..."
    
    return command.strip()

def determine_success_status(status: str, command: str, context: str) -> str:
    """Determine if command was successful based on status and context."""
    status_lower = status.lower()
    context_lower = context.lower()
    
    # Check for explicit failure indicators
    failure_indicators = [
        'error', 'failed', 'failure', 'exception', 'traceback',
        'command not found', 'permission denied', 'no such file',
        'build failed', 'compilation failed'
    ]
    
    success_indicators = [
        'successfully', 'completed', 'finished', 'done',
        'build successful', 'compilation successful'
    ]
    
    if status_lower == 'failed':
        return 'Failed'
    elif status_lower == 'success':
        return 'Success'
    else:
        # Check context for success/failure indicators
        for indicator in failure_indicators:
            if indicator in context_lower:
                return 'Failed'
        
        for indicator in success_indicators:
            if indicator in context_lower:
                return 'Success'
        
        return 'Unknown'

def is_actual_command(command: str) -> bool:
    """Check if this is an actual executable command vs noise."""
    # Skip very short commands
    if len(command.strip()) < 5:
        return False
    
    # Skip pure text/descriptions
    if not any(char in command for char in ['.', '/', '-', '_']):
        return False
    
    # Focus on actual executable commands
    command_patterns = [
        r'^\w+\s+',  # Starts with a command word
        r'\./[\w-]+',  # Local executables
        r'python\s+',  # Python commands
        r'docker\s+',  # Docker commands
        r'git\s+',  # Git commands
        r'npm\s+',  # NPM commands
        r'pip\s+',  # Pip commands
        r'poetry\s+',  # Poetry commands
        r'curl\s+',  # Curl commands
        r'tar\s+',  # Tar commands
        r'mkdir\s+',  # File operations
        r'cp\s+',  # Copy commands
        r'mv\s+',  # Move commands
    ]
    
    for pattern in command_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    
    return False

def process_to_final_csv(input_file: str, output_file: str):
    """Create the final user-friendly CSV with just command and success status."""
    final_commands = []
    seen_commands = set()
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            original_command = row['command']
            status = row['status']
            context = row['context']
            
            # Clean and simplify the command
            clean_cmd = clean_and_simplify_command(original_command)
            
            # Skip if not an actual command
            if not is_actual_command(clean_cmd):
                continue
            
            # Determine success status
            success_status = determine_success_status(status, clean_cmd, context)
            
            # Avoid exact duplicates but keep different statuses
            cmd_key = clean_cmd.lower()
            if cmd_key not in seen_commands or len(seen_commands) < 500:  # Allow some variation
                seen_commands.add(cmd_key)
                final_commands.append({
                    'command': clean_cmd,
                    'success': success_status
                })
    
    # Sort by command for easier reading
    final_commands.sort(key=lambda x: x['command'].lower())
    
    # Write final CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['command', 'success']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_commands)
    
    logger.info(f"Final CSV created: {output_file}")
    logger.info(f"Total commands: {len(final_commands)}")
    
    # Print status summary
    status_counts = {}
    for cmd in final_commands:
        status = cmd['success']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    logger.info("\nSuccess Status Summary:")
    for status, count in sorted(status_counts.items()):
        logger.info(f"  {status}: {count}")

def main():
    """Main function."""
    script_dir = Path(__file__).parent
    input_file = script_dir / "ot2_commands_summary.csv"
    output_file = script_dir / "ot2_final_commands.csv"
    
    if not input_file.exists():
        logger.error(f"Input file not found: {input_file}")
        logger.info("Please run create_ot2_summary.py first to generate the source data.")
        return
    
    logger.info("Creating final user-friendly OT2 commands CSV...")
    process_to_final_csv(str(input_file), str(output_file))
    logger.info("Final CSV creation complete!")

if __name__ == "__main__":
    main()
