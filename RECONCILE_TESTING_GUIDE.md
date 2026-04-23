# Testing the /reconcile Endpoint

## Overview

The `/reconcile` endpoint takes the **output from `/process`** and returns final WIP/FAR impact calculations.

**There is NO session ID needed.** The frontend simply:
1. Calls `/process` and gets back matching results
2. Passes the full response data + approved matches to `/reconcile`
3. Gets final totals

---

## How to Test: Step-by-Step

### Step 1: Call `/process` endpoint

Upload your two files:

```bash
curl -X POST "http://localhost:8000/api/v1/process" \
  -F "current_year_file=@app/sheets/current_100_rows.xlsx" \
  -F "previous_year_file=@app/sheets/Book1.xlsx" \
  -o process_response.json
```

This returns a JSON file with:
- `current_year_rows` (list of all parsed rows)
- `previous_year_rows` (list of all parsed rows)
- `exact_matches` (confirmed matches)
- `suggested_matches` (fuzzy matches for review)
- `unmatched_current_rows` (rows with no match found)
- `unmatched_previous_rows` (rows with no match found)

### Step 2: Prepare `/reconcile` request

Create a file `reconcile_request.json` with:

```json
{
  "current_year_rows": [
    {
      "row_number": 2,
      "project_name": "T.K.MOKONYANE PS",
      "values": {
        "closing_balance": 137830,
        "additions": 0,
        "transfer": 0
      }
    },
    {
      "row_number": 3,
      "project_name": "TALEDI SUB(AIRCONS INSTALL",
      "values": {
        "closing_balance": 0,
        "additions": 471688,
        "transfer": 471688
      }
    }
  ],
  "previous_year_rows": [
    {
      "row_number": 2,
      "project_name": "T.K.MOKONYANE PS",
      "values": {
        "opening_balance": 137830,
        "additions": 0,
        "transfer": 0,
        "closing_balance": 137830
      }
    },
    {
      "row_number": 3,
      "project_name": "TALEDI SUB(AIRCONS INSTALL",
      "values": {
        "opening_balance": 0,
        "additions": 0,
        "transfer": 0,
        "closing_balance": 0
      }
    }
  ],
  "approved_matches": [
    {
      "current_row_number": 2,
      "previous_row_number": 2,
      "match_type": "exact"
    },
    {
      "current_row_number": 3,
      "previous_row_number": 3,
      "match_type": "exact"
    }
  ],
  "manual_overrides": {}
}
```

### Step 3: Call `/reconcile` endpoint

```bash
curl -X POST "http://localhost:8000/api/v1/reconcile" \
  -H "Content-Type: application/json" \
  -d @reconcile_request.json \
  -o reconcile_response.json
```

---

## What to Pass in the Body

### Request Format

```json
{
  "current_year_rows": [
    {
      "row_number": <int>,           // Row number from original file (e.g., 2, 3, 4...)
      "project_name": <string>,       // Project name
      "values": {                     // Key-value map of accounting values
        "closing_balance": <float>,
        "additions": <float>,
        "transfer": <float>,
        ...other fields
      }
    }
    // ... more rows
  ],
  "previous_year_rows": [
    {
      "row_number": <int>,
      "project_name": <string>,
      "values": {
        "opening_balance": <float>,
        "additions": <float>,
        "transfer": <float>,
        "closing_balance": <float>,
        ...other fields
      }
    }
    // ... more rows
  ],
  "approved_matches": [
    {
      "current_row_number": <int>,      // Row number from current_year_rows
      "previous_row_number": <int>,     // Row number from previous_year_rows
      "match_type": "exact"             // Or "approved_suggestion", "manual"
    }
    // ... more matches
  ],
  "manual_overrides": {}  // Optional: {current_row: previous_row} pairs
}
```

---

## Easy Way: Use /process Response Directly

The smartest way is to **copy rows directly from `/process` response**:

### Workflow

1. **Call `/process`** and save response to `process_response.json`

2. **Build reconcile request** by combining:
   - `current_year_rows` from process response
   - `previous_year_rows` from process response
   - `exact_matches` → convert to `approved_matches`
   - Optionally add user-approved `suggested_matches`

3. **Example Python code:**

```python
import json

# Read process response
with open('process_response.json') as f:
    process_data = json.load(f)

# Build reconcile request
reconcile_request = {
    "current_year_rows": process_data["current_year_rows"],
    "previous_year_rows": process_data["previous_year_rows"],
    "approved_matches": [
        {
            "current_row_number": match["current_row_number"],
            "previous_row_number": match["previous_row_number"],
            "match_type": "exact"
        }
        for match in process_data["exact_matches"]
    ] + [
        {
            "current_row_number": match["current_row_number"],
            "previous_row_number": match["suggested_previous_row_number"],
            "match_type": "approved_suggestion"
        }
        for match in process_data["suggested_matches"]
        # User can filter to only include approved suggestions
    ],
    "manual_overrides": {}
}

# Save for curl
with open('reconcile_request.json', 'w') as f:
    json.dump(reconcile_request, f, indent=2)
```

Then call:

```bash
curl -X POST "http://localhost:8000/api/v1/reconcile" \
  -H "Content-Type: application/json" \
  -d @reconcile_request.json
```

---

## Response Format

The `/reconcile` endpoint returns:

```json
{
  "success": true,
  "reconciled_matches": [
    {
      "current_row_number": 2,
      "previous_row_number": 2,
      "project_name": "T.K.MOKONYANE PS",
      "current_values": {
        "closing_balance": 137830,
        "additions": 0,
        "transfer": 0
      },
      "previous_values": {
        "opening_balance": 137830,
        "additions": 0,
        "transfer": 0,
        "closing_balance": 137830
      },
      "wip_impact": 0.0,      // Current closing - previous closing
      "far_impact": 0.0       // Current transfer - previous transfer
    },
    // ... more reconciled matches
  ],
  "unmatched_current_rows": [],
  "unmatched_previous_rows": [],
  "total_current_rows": 100,
  "total_previous_rows": 100,
  "total_matched": 50,
  "total_unmatched": 50,
  "total_wip_impact": 250000.50,    // Sum of all WIP impacts
  "total_far_impact": 125000.25     // Sum of all FAR impacts
}
```

---

## Testing with Real Data: Full Example

Save this as `test_reconcile.py` and run it:

```python
import json
import requests
import sys

BASE_URL = "http://localhost:8000"

# Step 1: Call /process
print("Step 1: Calling /process...")
with open('app/sheets/current_100_rows.xlsx', 'rb') as f1, \
     open('app/sheets/Book1.xlsx', 'rb') as f2:
    files = {
        'current_year_file': f1,
        'previous_year_file': f2
    }
    response = requests.post(f"{BASE_URL}/api/v1/process", files=files)

if response.status_code != 200:
    print(f"Error: {response.status_code}")
    print(response.json())
    sys.exit(1)

process_data = response.json()
print(f"✓ Process returned:")
print(f"  - Current year rows: {len(process_data['current_year_rows'])}")
print(f"  - Previous year rows: {len(process_data['previous_year_rows'])}")
print(f"  - Exact matches: {len(process_data['exact_matches'])}")
print(f"  - Suggested matches: {len(process_data['suggested_matches'])}")

# Step 2: Build reconcile request (approve all exact matches)
print("\nStep 2: Building reconcile request...")
reconcile_request = {
    "current_year_rows": process_data["current_year_rows"],
    "previous_year_rows": process_data["previous_year_rows"],
    "approved_matches": [
        {
            "current_row_number": match["current_row_number"],
            "previous_row_number": match["previous_row_number"],
            "match_type": "exact"
        }
        for match in process_data["exact_matches"]
    ],
    "manual_overrides": {}
}
print(f"✓ Request ready with {len(reconcile_request['approved_matches'])} approved matches")

# Step 3: Call /reconcile
print("\nStep 3: Calling /reconcile...")
response = requests.post(
    f"{BASE_URL}/api/v1/reconcile",
    json=reconcile_request
)

if response.status_code != 200:
    print(f"Error: {response.status_code}")
    print(response.json())
    sys.exit(1)

reconcile_data = response.json()
print("✓ Reconciliation complete!")
print(f"\nResults:")
print(f"  - Total matched: {reconcile_data['total_matched']}")
print(f"  - Total WIP Impact: {reconcile_data['total_wip_impact']:.2f}")
print(f"  - Total FAR Impact: {reconcile_data['total_far_impact']:.2f}")
print(f"  - Reconciled rows: {len(reconcile_data['reconciled_matches'])}")

# Save response
with open('reconcile_response.json', 'w') as f:
    json.dump(reconcile_data, f, indent=2)
print("\n✓ Response saved to reconcile_response.json")
```

Run it:

```bash
pip install requests
python test_reconcile.py
```

---

## Session ID / Authentication

**NO session ID is needed** for the current implementation.

In a production system, you might add:
- Session tokens (from login)
- API keys
- JWT tokens

But for now, just pass the data directly. The system is **stateless** - it processes each request independently.

---

## Common Issues & Solutions

### "Field required" error in reconcile request

**Problem**: You didn't include all required fields

**Solution**: Make sure your request has:
- `current_year_rows` (list, can be empty)
- `previous_year_rows` (list, can be empty)
- `approved_matches` (list, at least [])
- All rows have: `row_number`, `project_name`, `values`

### WIP/FAR impacts are 0.0

**Reason**: This is correct if:
- Previous closing balance = current closing balance (no change)
- Previous transfer = current transfer (no change)

**Example**: Row 1:
```
Current closing: 137830
Previous closing: 137830
WIP Impact: 0.0 ✓ (correct, no change)
```

### Reconcile request is too large

**Solution**: Only include rows that are actually matched
- Filter out unmatched rows if you have thousands
- Pass only the essential fields in `values`

---

## Next: Export

After reconciliation, call `/export` with the reconcile response:

```bash
curl -X POST "http://localhost:8000/api/v1/export" \
  -H "Content-Type: application/json" \
  -d @reconcile_response.json \
  -o results.xlsx
```

Downloads your final Excel report.

---

## Summary

| Step | Endpoint | Input | Output |
|------|----------|-------|--------|
| 1 | `/process` | Two Excel files | Parsed rows + matches |
| 2 | `/reconcile` | Process output + approved matches | Final WIP/FAR totals |
| 3 | `/export` | Reconcile output | Excel file |

**NO session ID needed. Just pass data along the pipeline.**
