# Accounting Reconciliation Service

A FastAPI backend for Excel-based accounting reconciliation workflow.

## Features

- **Two-File Excel Upload**: Upload separate current year and previous year Excel files
- **Data Validation**: Validate required headers and formula calculations
- **Intelligent Matching**: Exact and fuzzy matching of project names across files
- **Impact Calculation**: Automated WIP (Work-in-Progress) and FAR (Fixed Asset Retirement) impact calculations
- **Excel Export**: Generate detailed reconciliation reports as Excel workbooks

## Tech Stack

- **Python 3.11**
- **FastAPI** - Modern async web framework
- **Pydantic** - Data validation with Python type hints
- **OpenPyXL** - Excel file handling
- **FuzzyWuzzy** - Fuzzy string matching
- **Pytest** - Unit testing

## Project Structure

```
app/
├── main.py                 # FastAPI application entry point
├── api/
│   └── v1/
│       ├── endpoints/
│       │   ├── process.py     # Upload and process endpoint
│       │   ├── reconcile.py   # Reconciliation endpoint
│       │   └── export.py      # Export endpoint
│       └── __init__.py
├── schemas/
│   ├── common.py           # Common response schemas
│   ├── process.py          # Process request/response schemas
│   ├── reconcile.py        # Reconcile request/response schemas
│   └── export.py           # Export schemas
├── services/
│   ├── file_validation_service.py    # File validation
│   ├── excel_parser_service.py       # Excel parsing
│   ├── normalization_service.py      # Data normalization
│   ├── matching_service.py           # Matching logic
│   ├── reconciliation_service.py     # Impact calculations
│   └── export_service.py             # Excel export generation
├── core/
│   ├── config.py           # Application configuration
│   ├── logging_config.py   # Logging setup
│   └── exceptions.py       # Custom exceptions
└── utils/
    ├── number_parser.py    # Numeric value parsing
    ├── text_normalizer.py  # Text normalization
    └── excel_helpers.py    # Excel utilities

tests/
├── test_number_parser.py    # Number parsing tests
├── test_normalization.py    # Text normalization tests
├── test_matching.py         # Matching logic tests
├── test_reconciliation.py   # Reconciliation tests
└── test_excel_parser.py     # Excel parsing tests
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### 1. POST `/api/v1/process`

Upload and process two separate Excel files (current year and previous year).

**Request:**
- `current_year_file`: Excel file (.xlsx) containing current year data
- `previous_year_file`: Excel file (.xlsx) containing previous year data

**Response:**
```json
{
  "success": true,
  "current_year_rows": [...],
  "previous_year_rows": [...],
  "exact_matches": [...],
  "suggested_matches": [...],
  "unmatched_current_rows": [...],
  "unmatched_previous_rows": [...],
  "validation_issues": [...],
  "impact_preview": [...],
  "summary": {
    "total_current_rows": 10,
    "total_previous_rows": 10,
    "exact_matches": 8,
    "suggested_fuzzy_matches": 1,
    "ambiguous_fuzzy_matches": 0,
    "unmatched_current": 1,
    "unmatched_previous": 1,
    "validation_issues": 0
  }
}
```

### 2. POST `/api/v1/reconcile`

Finalize matches and calculate impacts.

**Request:**
```json
{
  "approved_matches": [
    {
      "current_row_number": 2,
      "previous_row_number": 2,
      "match_type": "approved"
    }
  ],
  "manual_overrides": {}
}
```

**Response:**
```json
{
  "success": true,
  "reconciled_matches": [...],
  "total_matched": 8,
  "total_wip_impact": 50000.00,
  "total_far_impact": 25000.00
}
```

### 3. POST `/api/v1/export`

Generate Excel export with reconciliation results.

**Request:**
```json
{
  "reconciled_matches": [...],
  "unmatched_current_rows": [...],
  "unmatched_previous_rows": [...],
  "validation_issues": [...],
  "summary": {...}
}
```

**Response:** Excel file download

## Data Processing Rules

### Required Headers

**Current Year Sheet:**
- Project Name
- As of 31 Mar
- Additions
- Transfer
- As on 31 Mar

**Previous Year Sheet:**
- Project Name
- Opening Balance
- Additions
- Transfer
- Closing Balance

### Numeric Parsing

- Blank values → 0
- `-` → 0
- Numbers with commas are supported
- Whitespace is trimmed

### Formula Validation

**Current Year:**
```
As of 31 Mar + Additions - Transfer = As on 31 Mar
```

**Previous Year:**
```
Opening Balance + Additions - Transfer = Closing Balance
```

### Matching Strategy

1. **Exact Match**: Normalized project names must be identical
2. **Fuzzy Match**: Uses token_set_ratio with 80% threshold
   - 1 candidate → suggested match
   - 2+ candidates → ambiguous (manual review needed)

### Impact Calculations

**WIP Impact:**
```
Current Year Closing Balance - Previous Year Closing Balance
```

**FAR Impact:**
```
Current Year Transfer - Previous Year Transfer
```

## Configuration

Edit `app/core/config.py` to customize:
- `FUZZY_MATCH_THRESHOLD` (default: 0.80)
- `MAX_UPLOAD_SIZE` (default: 10 MB)
- Sheet name variations
- Required headers


## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_matching.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Test Coverage (37 tests)

- Excel parsing and robust header detection ✅
- Text normalization and fuzzy matching ✅
- Numeric value parsing (blanks, dashes, commas) ✅
- Formula validation ✅
- WIP and FAR impact calculations ✅
- Two-file upload and reconciliation ✅

### Real-World File Testing

The system has been tested with real-world accounting Excel files:
- **December file**: 1,557 rows with 98 year-based columns
- **March file**: 883 rows with date-based headers
- Successfully handles complex formatting and data structures
- Robust header detection skips leading blank rows and metadata



## Error Handling

The API returns proper HTTP status codes:
- `200` - Success
- `400` - Bad request (file validation, parsing, validation errors)
- `500` - Internal server error

Error responses include:
- `success`: false
- `error`: Short error message
- `details`: Optional detailed explanation

## Logging

Console logging is configured with format:
```
%(asctime)s | %(levelname)s | %(name)s | %(message)s
```

Important events logged:
- File upload received
- Parsing started/completed
- Row counts extracted
- Matching results
- Reconciliation completion
- Export generation
- Processing failures

## Development

The project uses:
- **FastAPI** with async/await
- **Pydantic** for data validation
- **OpenPyXL** for Excel handling
- **FuzzyWuzzy** for string matching
- **Pytest** for unit testing

No database required - all processing is in-memory with optional file-based output.

## License

Proprietary - Internal Use Only
