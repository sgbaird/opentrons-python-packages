#!/usr/bin/env python3
"""Simple Prefect tutorial flow example"""
from prefect import flow, task
from datetime import datetime
import socket
import sys

@task
def get_system_info():
    return {
        "hostname": socket.gethostname(),
        "timestamp": datetime.now().isoformat(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "prefect_version": __import__("prefect").__version__
    }

@task
def simple_calculation(x, y):
    """Simple calculation task"""
    return x + y

@flow(name="Simple Tutorial Flow")
def tutorial_flow():
    """Simple Prefect tutorial flow"""
    print("Starting tutorial flow")
    system_info = get_system_info()
    print(f"System info: {system_info}")
    result = simple_calculation(10, 20)
    print(f"Calculation result: {result}")
    return {
        "status": "success",
        "system_info": system_info,
        "calculation_result": result,
        "message": "Tutorial flow completed successfully"
    }

if __name__ == "__main__":
    result = tutorial_flow()
    print(f"Flow completed: {result}")
    print("Check your Prefect Cloud dashboard to see this flow run!")