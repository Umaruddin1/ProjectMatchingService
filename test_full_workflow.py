#!/usr/bin/env python3
"""
End-to-end workflow test: /process -> /reconcile -> /export
"""
import requests
import json

API = "http://localhost:8000/api/v1"

print("=" * 70)
print("FULL WORKFLOW TEST")
print("=" * 70)

# Step 1: Process files
print("\n1️⃣  TESTING /process endpoint...")
with open(r"app/sheets/current_100_rows.xlsx", "rb") as cf:
    with open(r"app/sheets/Book1.xlsx", "rb") as pf:
        files = {
            "current_year_file": ("current.xlsx", cf),
            "previous_year_file": ("previous.xlsx", pf),
        }
        process_response = requests.post(f"{API}/process", files=files)

if process_response.status_code == 200:
    process_data = process_response.json()
    print(f"   ✅ Status: {process_response.status_code}")
    print(f"   📊 Summary:")
    summary = process_data.get("summary", {})
    print(f"      Current rows: {summary.get('total_current_rows')}")
    print(f"      Previous rows: {summary.get('total_previous_rows')}")
    print(f"      Exact matches: {summary.get('exact_matches')}")
    print(f"      Fuzzy matches: {summary.get('suggested_fuzzy_matches')}")
    print(f"      Unmatched: {summary.get('unmatched_current')} current, {summary.get('unmatched_previous')} previous")
else:
    print(f"   ❌ Failed: {process_response.status_code}")
    print(f"   {process_response.text}")
    exit(1)

# Step 2: Reconcile with some approved matches
print("\n2️⃣  TESTING /reconcile endpoint...")
exact_matches = process_data.get("exact_matches", [])
if len(exact_matches) > 0:
    # Approve first 5 exact matches
    approved = exact_matches[:5]
    approved_list = [
        {
            "current_row_number": m["current_row_number"],
            "previous_row_number": m["previous_row_number"],
            "match_type": "exact"
        }
        for m in approved
    ]
    
    reconcile_request = {
        "current_year_rows": process_data.get("current_year_rows", []),
        "previous_year_rows": process_data.get("previous_year_rows", []),
        "approved_matches": approved_list,
        "manual_overrides": {}
    }
    
    reconcile_response = requests.post(
        f"{API}/reconcile",
        json=reconcile_request
    )
    
    if reconcile_response.status_code == 200:
        reconcile_data = reconcile_response.json()
        print(f"   ✅ Status: {reconcile_response.status_code}")
        print(f"   📊 Reconciled:")
        print(f"      Total matched: {reconcile_data.get('total_matched')}")
        print(f"      WIP Impact: {reconcile_data.get('total_wip_impact')}")
        print(f"      FAR Impact: {reconcile_data.get('total_far_impact')}")
    else:
        print(f"   ❌ Failed: {reconcile_response.status_code}")
        print(f"   {reconcile_response.text}")
        exit(1)
else:
    print("   ⚠️  No exact matches to test reconcile")
    reconcile_data = {"reconciled_matches": []}

# Step 3: Export
print("\n3️⃣  TESTING /export endpoint...")
export_request = {
    "reconciled_matches": reconcile_data.get("reconciled_matches", []),
    "unmatched_current_rows": reconcile_data.get("unmatched_current_rows", []),
    "unmatched_previous_rows": reconcile_data.get("unmatched_previous_rows", []),
    "validation_issues": process_data.get("validation_issues", []),
    "summary": {
        "total_matched": reconcile_data.get("total_matched", 0),
        "total_wip_impact": reconcile_data.get("total_wip_impact", 0),
        "total_far_impact": reconcile_data.get("total_far_impact", 0),
    }
}

export_response = requests.post(f"{API}/export", json=export_request)

if export_response.status_code == 200:
    print(f"   ✅ Status: {export_response.status_code}")
    file_size = len(export_response.content)
    print(f"   📄 File size: {file_size / 1024:.1f} KB")
    print(f"   📥 Would download as: reconciliation_{int(__import__('time').time())}.xlsx")
else:
    print(f"   ❌ Failed: {export_response.status_code}")
    print(f"   {export_response.text}")
    exit(1)

print("\n" + "=" * 70)
print("✅ FULL WORKFLOW TEST PASSED")
print("=" * 70)
print("\nAll three endpoints working correctly:")
print("  ✅ /api/v1/process  - Upload & parse")
print("  ✅ /api/v1/reconcile - Reconcile matches")
print("  ✅ /api/v1/export    - Generate Excel")
