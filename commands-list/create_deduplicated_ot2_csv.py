#!/usr/bin/env python3
"""
Enhanced script to create a deduplicated CSV of OT2 commands with better duplicate handling.
This version removes exact duplicates and consolidates similar commands with different statuses.
"""

import csv
import re
from pathlib import Path
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def normalize_command(command: str) -> str:
    """Normalize command for better duplicate detection."""
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
    
    # Remove variable parts that make commands look different
    command = re.sub(r'\$\{\{[^}]+\}\}', '<VAR>', command)  # GitHub Actions variables
    command = re.sub(r'/tmp/[a-zA-Z0-9_-]+', '/tmp/<TEMP>', command)  # Temp files
    command = re.sub(r'--verbose', '', command)  # Remove verbose flags for comparison
    command = re.sub(r'2>&1', '', command)  # Remove redirections
    
    # Clean up extra whitespace and quotes
    command = ' '.join(command.split())
    command = command.strip('"\'')
    
    return command.strip()

def get_command_priority(status: str, context: str) -> int:
    """Get priority for command status - lower number = higher priority."""
    if status.lower() == 'success':
        return 1
    elif status.lower() == 'failed':
        return 2
    else:
        # Check context for implicit success/failure
        context_lower = context.lower()
        if any(word in context_lower for word in ['success', 'completed', 'finished']):
            return 3
        elif any(word in context_lower for word in ['error', 'failed', 'exception']):
            return 4
        else:
            return 5

def is_actual_executable_command(command: str) -> bool:
    """Check if this is an actual executable command, not descriptive text."""
    # Skip very short commands
    if len(command.strip()) < 5:
        return False
    
    # Skip pure descriptions and text
    descriptive_patterns = [
        r'^[A-Z][a-z].*\.$',  # Sentences starting with capital and ending with period
        r'^(The|This|It|Building|Creating|Installing)\s+',  # Common descriptive starts
        r'should|would|could|might|may be',  # Modal verbs
        r'is a|are a|will be|has been',  # Description phrases
        r'^\s*-\s+',  # List items
        r'^\s*\*\s+',  # Bullet points
    ]
    
    for pattern in descriptive_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return False
    
    # Focus on actual executable commands
    executable_patterns = [
        r'^\w+\s+',  # Starts with a command word
        r'\./[\w-]+',  # Local executables
        r'^(python|docker|git|npm|pip|poetry|curl|tar|mkdir|cp|mv|cd)\s+',
        r'--[\w-]+',  # Command line flags
        r'^[a-zA-Z0-9_-]+\.(py|sh|pl)(\s|$)',  # Script files
    ]
    
    for pattern in executable_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    
    return False

def deduplicate_commands(commands: List[Dict]) -> List[Dict]:
    """Remove duplicates, keeping the best example of each command."""
    # Group commands by normalized version
    command_groups = {}
    
    for cmd in commands:
        normalized = normalize_command(cmd['command'])
        if normalized not in command_groups:
            command_groups[normalized] = []
        command_groups[normalized].append(cmd)
    
    # For each group, pick the best representative
    deduplicated = []
    
    for normalized_cmd, group in command_groups.items():
        if not is_actual_executable_command(normalized_cmd):
            continue
            
        # Sort by priority (success > failed > unknown)
        group.sort(key=lambda x: get_command_priority(x['status'], x['context']))
        
        # Take the best one (first after sorting)
        best_cmd = group[0]
        
        # Clean up the original command for final output
        clean_cmd = normalize_command(best_cmd['command'])
        
        # Truncate very long commands
        if len(clean_cmd) > 120:
            clean_cmd = clean_cmd[:117] + "..."
        
        deduplicated.append({
            'command': clean_cmd,
            'success': best_cmd['status']
        })
    
    return deduplicated

def process_to_deduplicated_csv(input_file: str, output_file: str):
    """Create a deduplicated CSV with unique commands only."""
    all_commands = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        all_commands = list(reader)
    
    logger.info(f"Starting with {len(all_commands)} total commands")
    
    # Deduplicate commands
    deduplicated_commands = deduplicate_commands(all_commands)
    
    # Sort alphabetically for easier reading
    deduplicated_commands.sort(key=lambda x: x['command'].lower())
    
    # Write final CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['command', 'success']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(deduplicated_commands)
    
    logger.info(f"Deduplicated CSV created: {output_file}")
    logger.info(f"Commands after deduplication: {len(deduplicated_commands)}")
    
    # Print status summary
    status_counts = {}
    for cmd in deduplicated_commands:
        status = cmd['success']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    logger.info("\nStatus Summary (after deduplication):")
    for status, count in sorted(status_counts.items()):
        logger.info(f"  {status}: {count}")

def main():
    """Main function."""
    script_dir = Path(__file__).parent
    input_file = script_dir / "ot2_commands_summary.csv"
    output_file = script_dir / "ot2_commands_deduplicated.csv"
    
    if not input_file.exists():
        logger.error(f"Input file not found: {input_file}")
        logger.info("Please run create_ot2_summary.py first to generate the source data.")
        return
    
    logger.info("Creating deduplicated OT2 commands CSV...")
    process_to_deduplicated_csv(str(input_file), str(output_file))
    logger.info("Deduplication complete!")

if __name__ == "__main__":
    main()
