#!/usr/bin/env python3
"""
GitHub Actions Log Downloader

This script helps download and organize all GitHub Actions logs for analysis.
Works with the GitHub API to fetch workflow runs and their logs.

Usage:
    python3 download_github_logs.py --repo sgbaird/opentrons-python-packages --output logs/
"""

import os
import sys
import json
import argparse
import requests
import zipfile
from pathlib import Path
from typing import List, Dict
from datetime import datetime

class GitHubLogsDownloader:
    def __init__(self, repo: str, token: str = None):
        self.repo = repo
        self.token = token
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'OT2-Log-Downloader'
        }
        if token:
            self.headers['Authorization'] = f'token {token}'
        
        self.base_url = 'https://api.github.com'
    
    def get_workflow_runs(self, workflow_name: str = None) -> List[Dict]:
        """Get all workflow runs for the repository"""
        url = f"{self.base_url}/repos/{self.repo}/actions/runs"
        params = {'per_page': 100}
        
        if workflow_name:
            # First get workflow ID
            workflows_url = f"{self.base_url}/repos/{self.repo}/actions/workflows"
            response = requests.get(workflows_url, headers=self.headers)
            if response.status_code == 200:
                workflows = response.json()['workflows']
                for workflow in workflows:
                    if workflow_name.lower() in workflow['name'].lower():
                        params['workflow_id'] = workflow['id']
                        break
        
        all_runs = []
        page = 1
        
        while True:
            params['page'] = page
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                print(f"Error fetching runs: {response.status_code}")
                break
            
            data = response.json()
            runs = data.get('workflow_runs', [])
            
            if not runs:
                break
                
            all_runs.extend(runs)
            page += 1
            
            print(f"Fetched page {page-1}, total runs: {len(all_runs)}")
            
            # Stop if we've fetched all pages
            if len(runs) < params['per_page']:
                break
        
        return all_runs
    
    def download_run_logs(self, run_id: int, output_dir: Path) -> bool:
        """Download logs for a specific run"""
        url = f"{self.base_url}/repos/{self.repo}/actions/runs/{run_id}/logs"
        
        response = requests.get(url, headers=self.headers, stream=True)
        
        if response.status_code != 200:
            print(f"Error downloading logs for run {run_id}: {response.status_code}")
            return False
        
        # Save as zip file first
        zip_path = output_dir / f"run_{run_id}_logs.zip"
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Extract the zip file
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                extract_dir = output_dir / f"run_{run_id}"
                extract_dir.mkdir(exist_ok=True)
                zip_ref.extractall(extract_dir)
            
            # Remove the zip file
            zip_path.unlink()
            return True
            
        except Exception as e:
            print(f"Error extracting logs for run {run_id}: {e}")
            return False
    
    def download_all_logs(self, output_dir: Path, workflow_name: str = None, limit: int = None):
        """Download all available logs"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Fetching workflow runs for {self.repo}...")
        runs = self.get_workflow_runs(workflow_name)
        
        if limit:
            runs = runs[:limit]
        
        print(f"Found {len(runs)} runs to download")
        
        metadata = []
        successful_downloads = 0
        
        for i, run in enumerate(runs):
            run_id = run['id']
            run_number = run['run_number']
            status = run['status']
            conclusion = run['conclusion']
            created_at = run['created_at']
            workflow_name = run['name']
            
            print(f"Downloading {i+1}/{len(runs)}: Run #{run_number} (ID: {run_id})")
            
            if self.download_run_logs(run_id, output_dir):
                successful_downloads += 1
                metadata.append({
                    'run_id': run_id,
                    'run_number': run_number,
                    'status': status,
                    'conclusion': conclusion,
                    'created_at': created_at,
                    'workflow_name': workflow_name,
                    'downloaded': True
                })
            else:
                metadata.append({
                    'run_id': run_id,
                    'run_number': run_number,
                    'status': status,
                    'conclusion': conclusion,
                    'created_at': created_at,
                    'workflow_name': workflow_name,
                    'downloaded': False
                })
        
        # Save metadata
        metadata_file = output_dir / 'download_metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump({
                'downloaded_at': datetime.now().isoformat(),
                'repo': self.repo,
                'total_runs': len(runs),
                'successful_downloads': successful_downloads,
                'runs': metadata
            }, f, indent=2)
        
        print(f"\nDownload complete!")
        print(f"Successfully downloaded: {successful_downloads}/{len(runs)} runs")
        print(f"Logs saved to: {output_dir}")
        print(f"Metadata saved to: {metadata_file}")
        
        return successful_downloads

def create_analysis_script(output_dir: Path):
    """Create a helper script to run the log analysis"""
    script_content = f"""#!/bin/bash
# Auto-generated script to analyze downloaded logs

echo "Starting log analysis..."

python3 extract_installation_commands.py \\
    --logs-dir "{output_dir}" \\
    --output-dir "extracted_commands"

echo "Analysis complete! Check the extracted_commands/ directory for results."
"""
    
    script_path = output_dir.parent / 'analyze_logs.sh'
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    os.chmod(script_path, 0o755)
    print(f"Created analysis script: {script_path}")

def main():
    parser = argparse.ArgumentParser(description='Download GitHub Actions logs for analysis')
    parser.add_argument('--repo', default='sgbaird/opentrons-python-packages',
                       help='GitHub repository (owner/repo)')
    parser.add_argument('--output-dir', type=Path, default=Path('github_action_logs'),
                       help='Output directory for logs')
    parser.add_argument('--workflow', 
                       help='Filter by workflow name (e.g., "copilot")')
    parser.add_argument('--limit', type=int,
                       help='Limit number of runs to download')
    parser.add_argument('--token', 
                       help='GitHub token (or set GITHUB_TOKEN env var)')
    
    args = parser.parse_args()
    
    # Get token from argument or environment
    token = args.token or os.getenv('GITHUB_TOKEN')
    
    if not token:
        print("Warning: No GitHub token provided. Rate limiting may apply.")
        print("Set GITHUB_TOKEN environment variable or use --token flag for better access.")
    
    downloader = GitHubLogsDownloader(args.repo, token)
    
    try:
        downloaded_count = downloader.download_all_logs(
            args.output_dir, 
            args.workflow, 
            args.limit
        )
        
        if downloaded_count > 0:
            create_analysis_script(args.output_dir)
            
        return 0
        
    except KeyboardInterrupt:
        print("\nDownload interrupted by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == '__main__':
    exit(main())