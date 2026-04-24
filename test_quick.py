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
summary = data.get('data', {}).get('summary', {})

print('📊 TEST RESULTS:')
print(f"Current rows: {summary.get('total_current_rows', 'N/A')}")
print(f"Previous rows: {summary.get('total_previous_rows', 'N/A')}")
print(f"Exact matches: {summary.get('exact_matches_count', 'N/A')}")
print(f"Fuzzy matches: {summary.get('suggested_matches_count', 'N/A')}")
print(f"Unmatched current: {summary.get('unmatched_current_count', 'N/A')}")
print(f"Unmatched previous: {summary.get('unmatched_previous_count', 'N/A')}")
