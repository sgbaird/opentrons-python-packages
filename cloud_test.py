#!/usr/bin/env python3
"""Test Prefect Cloud connectivity"""
import requests
from prefect.settings import PREFECT_API_KEY, PREFECT_API_URL

api_key = PREFECT_API_KEY.value()
api_url = PREFECT_API_URL.value()

print(f"API URL: {api_url}")
print(f"API Key: {api_key[:20]}...")

headers = {"Authorization": f"Bearer {api_key}"}
try:
    response = requests.get(f"{api_url}/flows", headers=headers, timeout=10)
    if response.status_code == 200:
        print("✅ Cloud connectivity successful")
    elif response.status_code == 401:
        print("❌ Authentication failed - check API key")
    else:
        print(f"⚠️ API responded with status {response.status_code}")
except Exception as e:
    print(f"❌ Connection error: {e}")