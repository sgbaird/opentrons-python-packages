#!/usr/bin/env python3
"""
Quick OT-2 Prefect Installation
One-liner script for immediate Prefect installation on OT-2
"""

import subprocess
import sys
import os

def quick_install():
    print("🚀 Quick OT-2 Prefect Installation")
    
    # Set PYTHONPATH for current session
    user_site = "/var/user-packages/root/.local/lib/python3.10/site-packages"
    current_path = os.environ.get('PYTHONPATH', '')
    new_path = f"{user_site}:{current_path}" if current_path else user_site
    os.environ['PYTHONPATH'] = new_path
    
    # Install critical wheels
    base_url = "https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/wheels/"
    wheels = [
        "pendulum-3.1.0-cp310-cp310-linux_armv7l.whl",
        "ujson-5.10.0-py3-none-linux_armv7l.whl", 
        "prefect-3.3.4-py3-none-any.whl"
    ]
    
    for wheel in wheels:
        print(f"Installing {wheel}...")
        cmd = [sys.executable, '-m', 'pip', 'install', '--user', '--force-reinstall', '--no-deps', base_url + wheel]
        subprocess.run(cmd, check=True)
    
    # Install deps
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--user', 'rich', 'pydantic>=2.0'], check=True)
    
    # Test
    subprocess.run([sys.executable, '-c', "from prefect import flow, task; print('✅ Prefect working!')"], check=True)
    print("🎉 Installation complete!")

if __name__ == "__main__":
    quick_install()