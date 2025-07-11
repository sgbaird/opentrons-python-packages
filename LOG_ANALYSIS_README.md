# GitHub Actions Log Analysis Tools

This directory contains tools to systematically extract and analyze the successful installation commands from GitHub Actions logs, helping to retrace the "rabbit hole" installation process that eventually worked for Prefect on OT-2 devices.

## Tools Overview

### 1. `download_github_logs.py`
Downloads all GitHub Actions logs from the repository for analysis.

```bash
# Download all copilot workflow logs
python3 download_github_logs.py --workflow copilot --output-dir github_action_logs/

# Download all logs (may be large)
python3 download_github_logs.py --output-dir all_logs/

# Download with GitHub token for better rate limits
export GITHUB_TOKEN=your_token_here
python3 download_github_logs.py --workflow copilot --output-dir github_action_logs/
```

### 2. `extract_installation_commands.py`
Analyzes log files to extract successful installation commands and generate consolidated installation scripts.

```bash
# Extract commands from downloaded logs
python3 extract_installation_commands.py --logs-dir github_action_logs/ --output-dir extracted_commands/

# Analyze logs in a specific directory
python3 extract_installation_commands.py --logs-dir /path/to/logs --output-dir results/
```

## Workflow

1. **Download logs**:
   ```bash
   python3 download_github_logs.py --workflow copilot --output-dir copilot_logs/
   ```

2. **Extract successful commands**:
   ```bash
   python3 extract_installation_commands.py --logs-dir copilot_logs/ --output-dir extracted_commands/
   ```

3. **Review results**:
   - `extracted_commands/ANALYSIS_SUMMARY.md` - Overview of findings
   - `extracted_commands/successful_commands.csv` - Commands that led to success
   - `extracted_commands/consolidated_install.sh` - Generated installation script
   - `extracted_commands/wheel_urls.txt` - All wheel URLs found

## For Manual Log Analysis

If you already have log files:

1. **Place logs in a directory**:
   ```
   my_logs/
   ├── log1.txt
   ├── log2.txt
   └── ...
   ```

2. **Run extraction**:
   ```bash
   python3 extract_installation_commands.py --logs-dir my_logs/ --output-dir results/
   ```

## Output Files

The analysis generates several output files:

- **`detailed_results.json`** - Complete extraction results with context
- **`successful_commands.csv`** - CSV of commands that led to successful installations
- **`wheel_urls.txt`** - All unique wheel URLs found in the logs
- **`consolidated_install.sh`** - Executable script with extracted commands
- **`ANALYSIS_SUMMARY.md`** - Summary report with statistics

## Understanding the Analysis

The tools look for:
- Commands that preceded successful package installations
- Critical package installations (prefect, pendulum, ujson, etc.)
- Wheel URLs used in successful installations
- Command sequences that led to success

The goal is to recreate the exact sequence of commands that eventually worked, avoiding the trial-and-error process.

## Example Usage for Current Issue

Based on the comments, to analyze all copilot logs:

```bash
# 1. Download all copilot workflow logs (68 runs mentioned)
python3 download_github_logs.py \
    --repo sgbaird/opentrons-python-packages \
    --workflow copilot \
    --output-dir copilot_action_logs/

# 2. Extract successful commands
python3 extract_installation_commands.py \
    --logs-dir copilot_action_logs/ \
    --output-dir extracted_installation_commands/

# 3. Review the generated installation script
cat extracted_installation_commands/consolidated_install.sh

# 4. Test on fresh OT-2 device
scp extracted_installation_commands/consolidated_install.sh root@ot2-device:/tmp/
ssh root@ot2-device "bash /tmp/consolidated_install.sh"
```

This systematic approach should help consolidate all the successful commands from the "rabbit hole" installation process into a reproducible script.