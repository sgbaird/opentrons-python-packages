#!/usr/bin/env python3
"""
Simple Prefect CLI for OT-2 ARM environments.
Provides essential CLI functionality without the complexity.
"""

import sys
import os
import subprocess

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 simple_prefect_cli.py <command>")
        return 1
    
    command = sys.argv[1]
    
    if command == "--version":
        try:
            import prefect
            print(prefect.__version__)
            return 0
        except ImportError:
            print("Prefect not installed")
            return 1
    
    elif command == "config":
        if len(sys.argv) >= 4 and sys.argv[2] == "set":
            key_value = sys.argv[3]
            if "=" in key_value:
                key, value = key_value.split("=", 1)
                if key == "PREFECT_API_URL":
                    os.environ[key] = value
                    # Persist to .bashrc
                    with open("/root/.bashrc", "a") as f:
                        f.write(f'\nexport {key}="{value}"\n')
                    print(f"Set {key}")
                elif key == "PREFECT_API_KEY":
                    os.environ[key] = value
                    # Persist to .bashrc
                    with open("/root/.bashrc", "a") as f:
                        f.write(f'\nexport {key}="{value}"\n')
                    print(f"Set {key}")
        return 0
    
    elif command == "cloud" and len(sys.argv) >= 3 and sys.argv[2] == "login":
        print("Use: prefect config set PREFECT_API_URL=<url>")
        print("     prefect config set PREFECT_API_KEY=<key>")
        return 0
    
    else:
        print(f"Command '{command}' not supported in simple CLI")
        print("Supported: --version, config set, cloud login")
        return 1

if __name__ == "__main__":
    sys.exit(main())