# Quick Start Guide

## Installation

```bash
# Navigate to project directory
cd ProjectMatchingService

# Install dependencies
pip install -r requirements.txt
```

## Running Tests

```bash
# Run all unit tests
pytest tests/ -v

# Run specific test file
pytest tests/test_matching.py -v

# Quick test summary
pytest tests/ -q
```

## Starting the Server

```bash
# Start the FastAPI server (default: http://127.0.0.1:8000)
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## API Documentation

Once the server is running:
- **Interactive Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **OpenAPI JSON**: http://127.0.0.1:8000/openapi.json

## Testing with Sample Data

1. The project includes a `sample_reconciliation.xlsx` file for testing.
2. Upload it via the Swagger UI or use curl:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/process" \
  -F "file=@sample_reconciliation.xlsx"
```

## Project Architecture

### Three Main APIs

1. **POST /api/v1/process** - Upload and analyze Excel workbook
   - Input: Excel file with current year and previous year sheets
   - Output: JSON with parsed rows, matches, validation issues, impact preview

2. **POST /api/v1/reconcile** - Finalize matching and calculate impacts
   - Input: Approved matches from process endpoint
   - Output: Final reconciled matches with WIP/FAR impacts

3. **POST /api/v1/export** - Generate Excel export
   - Input: Final reconciliation data
   - Output: Excel file for download

### Key Services

- **FileValidationService**: Validates uploaded files
- **ExcelParserService**: Parses and maps Excel sheets to data
- **NormalizationService**: Normalizes project names and validates formulas
- **MatchingService**: Performs exact and fuzzy matching
- **ReconciliationService**: Calculates WIP and FAR impacts
- **ExportService**: Generates Excel output

### Utilities

- **number_parser**: Handles numeric value parsing (blanks, dashes, commas)
- **text_normalizer**: Normalizes project names for matching
- **excel_helpers**: Utility functions for Excel processing

## Configuration

Edit `app/core/config.py` to customize:
- Fuzzy matching threshold (default: 0.80 / 80%)
- Maximum upload file size (default: 10 MB)
- Sheet name variations to detect
- Required column headers

## Data Processing Flow

1. **File Upload** → Validation (size, type)
2. **Sheet Detection** → Find current year and previous year sheets
3. **Header Mapping** → Normalize and map column headers
4. **Data Parsing** → Extract and parse numeric values
5. **Formula Validation** → Check accounting formulas
6. **Normalization** → Normalize project names
7. **Matching** → Exact + fuzzy matching
8. **Impact Calculation** → WIP and FAR impacts
9. **Export** → Generate Excel workbook

## Error Handling

- **400 Bad Request**: File validation, parsing, or data validation errors
- **422 Unprocessable Entity**: Missing required parameters
- **500 Internal Server Error**: Unexpected server errors

All errors include descriptive messages to help diagnose issues.

## Example Workflow

```bash
# 1. Start server
python -m uvicorn app.main:app --reload

# 2. Upload file (in another terminal)
curl -F "file=@sample_reconciliation.xlsx" \
  http://127.0.0.1:8000/api/v1/process > process_response.json

# 3. Review matches in process_response.json
# 4. Create reconciliation request with approved matches
curl -X POST http://127.0.0.1:8000/api/v1/reconcile \
  -H "Content-Type: application/json" \
  -d @reconcile_request.json > reconcile_response.json

# 5. Export results
curl -X POST http://127.0.0.1:8000/api/v1/export \
  -H "Content-Type: application/json" \
  -d @reconcile_response.json \
  -o results.xlsx
```

## Troubleshooting

### Server won't start
- Check Python version (requires 3.11+): `python --version`
- Verify dependencies: `pip list | grep -E fastapi|pydantic`
- Check port availability: `netstat -tuln | grep 8000`

### File upload fails
- Ensure file is Excel format (.xlsx)
- File size must be under 10 MB
- Verify file isn't corrupted: try opening in Excel

### Matching not working
- Check project names are consistent between sheets
- Verify header names match expected format
- Review validation issues in response

### No fuzzy matches found
- Increase `FUZZY_MATCH_THRESHOLD` if too strict
- Check project name normalization
- Ensure project names have enough similarity (80%+ by default)

## Development Notes

- **No Database**: All processing is in-memory for simplicity
- **Async/Await**: FastAPI handles concurrent requests efficiently
- **File-based Output**: Excel exports are written to disk
- **Console Logging**: All events logged to stdout for debugging
- **Stateless API**: Each request is independent; no session state

## Performance Considerations

- File parsing: ~100ms for typical 100-row workbook
- Fuzzy matching: O(n*m) where n=current rows, m=previous rows
- Excel export: ~500ms for typical output
- Maximum file size: 10 MB (configurable)

## Future Enhancements

- Database support for persistent results
- Background task processing for large files
- WebSocket support for real-time progress
- Advanced matching algorithms
- User authentication and authorization
- Results caching
- Batch processing
