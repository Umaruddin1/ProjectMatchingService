#!/usr/bin/env python3
import requests
import json

response = requests.post(
    'http://localhost:8000/api/v1/process',
    files={
        'current_year_file': open('app/sheets/current_100_rows.xlsx', 'rb'),
        'previous_year_file': open('app/sheets/Book1.xlsx', 'rb'),
    }
)

data = response.json()
print("API Response keys:", list(data.keys()))
print()
if 'data' in data:
    print("data keys:", list(data['data'].keys()))
    print()
    if 'summary' in data['data']:
        print("Summary:", json.dumps(data['data']['summary'], indent=2))
else:
    print("Full response (first 500 chars):")
    print(json.dumps(data, indent=2)[:500])
