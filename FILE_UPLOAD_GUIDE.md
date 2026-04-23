# File Upload Configuration Guide

## Large File Support Update

The API has been configured to handle large Excel files with 1500+ rows and thousands of columns.

### Configuration Changes

**Max Upload Size**: Increased from 10 MB to **100 MB**
- Location: `app/core/config.py`
- Setting: `MAX_UPLOAD_SIZE = 100 * 1024 * 1024`

**Supported File Formats**:
- `.xlsx` (Excel 2007+)
- `.xls` (Excel 97-2003)
- `.xlsm` (Excel with Macros)

### File Size Recommendations

| Scenario | Recommended Size | Limit |
|----------|-----------------|-------|
| Small workbooks (<100 rows) | < 1 MB | 100 MB |
| Medium workbooks (100-1000 rows) | 1-20 MB | 100 MB |
| Large workbooks (1000+ rows) | 20-50 MB | 100 MB |
| Very large workbooks (2000+ rows) | 50-100 MB | 100 MB |

### Current Production Specifications

Based on testing with actual files:
- **Ref_summary_sheet**: ~1,555 projects (no year columns)
- **SUMMARY_sheet**: ~1,629 projects (with 2020/21 data)
- **Combined size**: ~5-10 MB per file
- **Processing time**: < 30 seconds per file

## Frontend Integration

### Uploading Two Files

Use multipart form data with two file fields:

```javascript
const formData = new FormData();
formData.append('current_year_file', refSummarySheetFile);  // First file
formData.append('previous_year_file', summarySheetFile);    // Second file

const response = await fetch('/api/v1/process', {
  method: 'POST',
  body: formData
});
```

### API Endpoint

**Endpoint**: `POST /api/v1/process`

**Request**:
- `current_year_file`: File upload (first sheet - e.g., Ref_summary_sheet)
- `previous_year_file`: File upload (second sheet - e.g., SUMMARY_sheet)

**Response** (ProcessResponse):
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
    "total_current_rows": 1555,
    "total_previous_rows": 1629,
    "exact_matches": 1234,
    "suggested_fuzzy_matches": 50,
    "ambiguous_fuzzy_matches": 12,
    "unmatched_current": 200,
    "unmatched_previous": 250,
    "validation_issues": 5
  }
}
```

## Performance Considerations

### Memory Usage
- Peak memory: ~200-300 MB for 2000+ row files
- Streaming: Files are saved to temp disk, not loaded entirely into RAM
- Cleanup: Temporary files are automatically deleted after processing

### Processing Time
- Parsing: ~5-10 seconds per file
- Normalization: ~2-3 seconds
- Matching (exact): ~5-10 seconds
- Matching (fuzzy): ~10-20 seconds depending on ambiguity
- **Total**: 20-40 seconds for typical 1500+ row files

### Optimization Tips
1. Use file pre-validation on frontend (file type, size warning)
2. Implement progress indicators for uploads (large files)
3. Cache sheet column mappings if uploading same format repeatedly
4. For very large files (>50 MB), consider chunked uploads on frontend

## Troubleshooting

### "File too large" Error
- Check file size: Should be < 100 MB
- Verify in browser before upload
- Clear unnecessary data from Excel (hidden sheets, images, etc.)

### "Invalid file type" Error
- Only `.xlsx`, `.xls`, `.xlsm` are supported
- Convert the file to Excel format if needed
- Check file extension matches actual format

### Timeout During Processing
- Check logs for parsing errors
- Verify both files have proper headers
- Ensure columns match expected schema
- Try with smaller test file first

### Out of Memory
- Should not occur with current 100 MB limit
- If it does, check server RAM availability
- Consider increasing server memory allocation

## File Format Requirements

### File Structure
Both uploaded files should:
1. Have headers in the first or second row
2. Include "Project Name" column (case-insensitive)
3. Have consistent column order across both files
4. Avoid hidden columns/rows in critical areas

### Headers Supported
- **Project Name** (required in both files)
- Case/spacing variations handled automatically

### Data Types
- Text: Project names, project codes
- Numbers: Opening Balance, Additions, Transfer, Closing Balance
- Blanks: Treated as 0
- `-` character: Treated as 0
- Numbers with commas: Parsed correctly (1,000 → 1000)

## Running Tests with Large Files

Test files available in `app/sheets/`:
1. Ref_summary_sheet (1,555 projects)
2. SUMMARY_sheet (1,629 projects)

To run matching tests:
```bash
pytest tests/test_matching.py -v
```

To test with actual files:
```python
# See verify_startup.py for example
python verify_startup.py
```

## Deployment

### Docker (if used)
Ensure host has sufficient disk space for temporary files:
```dockerfile
# Example: /tmp mount should have at least 200 MB free
```

### Local Development
No additional setup needed. FastAPI automatically respects `MAX_UPLOAD_SIZE` from config.

### Environment Variables
To override upload size at runtime (if needed):
```bash
# Currently no override available; edit config.py directly
# Future: MAX_UPLOAD_SIZE_MB environment variable
```

## Security Notes

- File size limit prevents disk exhaustion attacks
- File type validation prevents non-Excel uploads
- No stored disk cache; temporary files cleaned up immediately
- No file access from other API endpoints (isolation)

## Support

For issues with large file uploads:
1. Check `app/core/config.py` for current limits
2. Review logs in console output
3. See `EXCEL_DIAGNOSTIC_REPORT.md` for data structure reference
4. Consult `TESTING_REPORT.md` for verified file formats
