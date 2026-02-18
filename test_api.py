#!/usr/bin/env python3
"""Test API disconnections endpoint"""

import requests
import json

# Test API disconnections
url = "http://localhost:5000/api/statistics/disconnections"
params = {
    'start_date': '2026-02-17',
    'end_date': '2026-02-17'
}

print(f"Testing API: {url}")
print(f"Params: {params}")
print()

try:
    response = requests.get(url, params=params)
    print(f"Status code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
