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
summary = data.get('summary', {})

print('📊 MATCHING STATISTICS:')
print(f"Total current rows: {summary.get('total_current_rows', 'N/A')}")
print(f"Total previous rows: {summary.get('total_previous_rows', 'N/A')}")
print(f"Exact matches: {summary.get('exact_matches', 'N/A')}")
print(f"Fuzzy matches: {summary.get('suggested_fuzzy_matches', 'N/A')}")
print(f"Ambiguous fuzzy: {summary.get('ambiguous_fuzzy_matches', 'N/A')}")
print(f"Unmatched current: {summary.get('unmatched_current', 'N/A')}")
print(f"Unmatched previous: {summary.get('unmatched_previous', 'N/A')}")
print(f"Validation issues: {summary.get('validation_issues', 'N/A')}")
