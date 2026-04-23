# Frontend Integration Guide - Quick Start

## API Ready Status

✅ Backend is ready to accept two large Excel files and perform matching
✅ File size limit: 100 MB per file  
✅ Support for 1500+ projects per file
✅ All 37 tests passing

---

## Step 1: Build File Upload Form

Create a form with two file inputs:

```html
<form id="reconciliationForm">
  <div>
    <label>Current Year Sheet (Ref Summary):</label>
    <input type="file" name="current_year_file" accept=".xlsx,.xls,.xlsm" required>
    <span id="file1-size"></span>
  </div>
  
  <div>
    <label>Previous Year Sheet (Summary):</label>
    <input type="file" name="previous_year_file" accept=".xlsx,.xls,.xlsm" required>
    <span id="file2-size"></span>
  </div>
  
  <button type="submit">Process Files</button>
  <progress id="progress" hidden></progress>
</form>
```

---

## Step 2: Validate Files on Frontend

```javascript
function validateFiles() {
  const form = document.getElementById('reconciliationForm');
  const file1 = form.elements['current_year_file'].files[0];
  const file2 = form.elements['previous_year_file'].files[0];
  
  const maxSize = 100 * 1024 * 1024; // 100 MB
  
  if (file1.size > maxSize || file2.size > maxSize) {
    alert('File size exceeds 100 MB limit');
    return false;
  }
  
  if (!['.xlsx', '.xls', '.xlsm'].includes(getFileExtension(file1.name))) {
    alert('Invalid file format. Use Excel files (.xlsx, .xls, .xlsm)');
    return false;
  }
  
  // Show file sizes
  document.getElementById('file1-size').textContent = 
    `(${formatBytes(file1.size)})`;
  document.getElementById('file2-size').textContent = 
    `(${formatBytes(file2.size)})`;
  
  return true;
}

function getFileExtension(filename) {
  return '.' + filename.split('.').pop().toLowerCase();
}

function formatBytes(bytes) {
  return (bytes / 1024 / 1024).toFixed(2) + ' MB';
}
```

---

## Step 3: Submit Files to Backend

```javascript
document.getElementById('reconciliationForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  if (!validateFiles()) return;
  
  const form = document.getElementById('reconciliationForm');
  const formData = new FormData(form);
  
  // Show progress
  document.getElementById('progress').removeAttribute('hidden');
  
  try {
    const response = await fetch('/api/v1/process', {
      method: 'POST',
      body: formData
      // Don't set Content-Type - browser will set it with boundary
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Processing failed');
    }
    
    const result = await response.json();
    displayResults(result);
    
  } catch (error) {
    alert('Error: ' + error.message);
    console.error(error);
  } finally {
    document.getElementById('progress').setAttribute('hidden', '');
  }
});
```

---

## Step 4: Display Matching Results

```javascript
function displayResults(data) {
  if (!data.success) {
    alert('Error: ' + data.error);
    return;
  }
  
  const summary = data.summary;
  
  // Show summary
  const html = `
    <div class="results-summary">
      <h2>Matching Results</h2>
      
      <div class="stats">
        <div class="stat">
          <strong>${summary.exact_matches}</strong>
          <span>Exact Matches</span>
        </div>
        <div class="stat">
          <strong>${summary.suggested_fuzzy_matches}</strong>
          <span>Suggested Matches (Fuzzy)</span>
        </div>
        <div class="stat">
          <strong>${summary.ambiguous_fuzzy_matches}</strong>
          <span>Ambiguous (Manual Review)</span>
        </div>
        <div class="stat warning">
          <strong>${summary.unmatched_current + summary.unmatched_previous}</strong>
          <span>Unmatched Rows</span>
        </div>
      </div>
      
      <div class="match-rate">
        Match Rate: ${calculateMatchRate(summary)}%
      </div>
      
      <div class="tabs">
        <button onclick="showTab('exact')">Exact Matches (${summary.exact_matches})</button>
        <button onclick="showTab('suggested')">Suggested (${summary.suggested_fuzzy_matches})</button>
        <button onclick="showTab('unmatched')">Unmatched (${summary.unmatched_current + summary.unmatched_previous})</button>
        <button onclick="showTab('issues')">Issues (${summary.validation_issues})</button>
      </div>
      
      <div id="exact" class="tab-content" style="display:block;">
        ${renderExactMatches(data.exact_matches)}
      </div>
      
      <div id="suggested" class="tab-content" style="display:none;">
        ${renderSuggestedMatches(data.suggested_matches)}
      </div>
      
      <div id="unmatched" class="tab-content" style="display:none;">
        ${renderUnmatchedRows(data)}
      </div>
      
      <div id="issues" class="tab-content" style="display:none;">
        ${renderValidationIssues(data.validation_issues)}
      </div>
      
      <button onclick="proceedToReconcile()" class="btn-primary">
        Approve & Proceed to Reconciliation
      </button>
    </div>
  `;
  
  document.body.appendChild(document.createElement('div')).innerHTML = html;
}

function calculateMatchRate(summary) {
  const total = summary.total_current_rows + summary.total_previous_rows;
  const matched = summary.exact_matches + summary.suggested_fuzzy_matches;
  return ((matched / total) * 100).toFixed(1);
}

function renderExactMatches(matches) {
  if (!matches || matches.length === 0) return '<p>No exact matches</p>';
  
  return `
    <table class="matches-table">
      <tr>
        <th>Row #</th>
        <th>Project Name</th>
        <th>WIP Impact</th>
        <th>FAR Impact</th>
      </tr>
      ${matches.map(m => `
        <tr>
          <td>${m.current_row_number}</td>
          <td>${m.project_name}</td>
          <td class="${m.wip_impact >= 0 ? 'positive' : 'negative'}">
            ${formatCurrency(m.wip_impact)}
          </td>
          <td class="${m.far_impact >= 0 ? 'positive' : 'negative'}">
            ${formatCurrency(m.far_impact)}
          </td>
        </tr>
      `).join('')}
    </table>
  `;
}

function renderSuggestedMatches(matches) {
  if (!matches || matches.length === 0) return '<p>No suggested matches</p>';
  
  return `
    <div class="suggested-list">
      ${matches.map(m => `
        <div class="suggestion" data-current="${m.current_row_number}" data-previous="${m.suggested_previous_row_number}">
          <strong>${m.current_project_name}</strong>
          <span class="confidence">${(m.confidence * 100).toFixed(0)}% match</span>
          ➜
          <strong>${m.suggested_project_name}</strong>
          <div class="action-buttons">
            <button onclick="approveSuggestion(this)" class="btn-approve">Approve</button>
            <button onclick="rejectSuggestion(this)" class="btn-reject">Reject</button>
          </div>
        </div>
      `).join('')}
    </div>
  `;
}

function renderUnmatchedRows(data) {
  const current = data.unmatched_current_rows || [];
  const previous = data.unmatched_previous_rows || [];
  
  return `
    <div class="unmatched-section">
      <h4>From Current Year (${current.length})</h4>
      <ul>
        ${current.map(r => `<li>${r.project_name} (Row ${r.row_number})</li>`).join('')}
      </ul>
      
      <h4>From Previous Year (${previous.length})</h4>
      <ul>
        ${previous.map(r => `<li>${r.project_name} (Row ${r.row_number})</li>`).join('')}
      </ul>
    </div>
  `;
}

function renderValidationIssues(issues) {
  if (!issues || issues.length === 0) return '<p>No validation issues</p>';
  
  return `
    <div class="issues-list">
      ${issues.map(issue => `
        <div class="issue">
          <strong>Row ${issue.row_number}: ${issue.project_name}</strong>
          <span class="issue-type">${issue.issue_type}</span>
          <p>${issue.description}</p>
        </div>
      `).join('')}
    </div>
  `;
}

function formatCurrency(value) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2
  }).format(value);
}
```

---

## Step 5: Proceed to Reconciliation

```javascript
async function proceedToReconcile() {
  // Collect approved matches
  const approvedMatches = [];
  
  // Get exact matches (all approved)
  const exactMatches = document.querySelectorAll('[data-exact="true"]');
  exactMatches.forEach(el => {
    approvedMatches.push({
      current_row_number: parseInt(el.dataset.current),
      previous_row_number: parseInt(el.dataset.previous),
      match_type: 'exact'
    });
  });
  
  // Get approved suggestions
  const approved = document.querySelectorAll('[data-suggestion-approved="true"]');
  approved.forEach(el => {
    approvedMatches.push({
      current_row_number: parseInt(el.dataset.current),
      previous_row_number: parseInt(el.dataset.previous),
      match_type: 'approved_suggestion'
    });
  });
  
  try {
    const response = await fetch('/api/v1/reconcile', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        approved_matches: approvedMatches,
        manual_overrides: {}
      })
    });
    
    const result = await response.json();
    displayReconciliationResults(result);
    
  } catch (error) {
    alert('Error during reconciliation: ' + error.message);
  }
}

function displayReconciliationResults(data) {
  const html = `
    <div class="reconciliation-results">
      <h2>Reconciliation Complete</h2>
      
      <div class="totals">
        <div class="total-item">
          <label>Total Matched Rows:</label>
          <value>${data.total_matched}</value>
        </div>
        <div class="total-item">
          <label>Total WIP Impact:</label>
          <value class="wip">${formatCurrency(data.total_wip_impact)}</value>
        </div>
        <div class="total-item">
          <label>Total FAR Impact:</label>
          <value class="far">${formatCurrency(data.total_far_impact)}</value>
        </div>
      </div>
      
      <button onclick="generateExport()" class="btn-primary btn-large">
        Download Excel Report
      </button>
    </div>
  `;
  
  document.body.appendChild(document.createElement('div')).innerHTML = html;
}
```

---

## Step 6: Generate Excel Export

```javascript
async function generateExport() {
  // Use last reconciliation result
  const reconciliationData = window.lastReconciliationData;
  
  try {
    const response = await fetch('/api/v1/export', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(reconciliationData)
    });
    
    if (!response.ok) throw new Error('Export failed');
    
    // Download file
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `reconciliation-${new Date().toISOString().split('T')[0]}.xlsx`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
    
  } catch (error) {
    alert('Error generating export: ' + error.message);
  }
}
```

---

## Error Handling

All errors follow this format:

```json
{
  "success": false,
  "error": "Short error message",
  "details": "Optional detailed explanation"
}
```

Handle errors appropriately:

```javascript
if (!response.ok) {
  const error = await response.json();
  console.error('API Error:', error);
  
  switch (response.status) {
    case 400:
      alert('Invalid input: ' + error.error);
      break;
    case 413:
      alert('File too large. Max 100 MB per file.');
      break;
    case 500:
      alert('Server error. Check logs.');
      break;
    default:
      alert('Error: ' + error.error);
  }
  
  return false;
}
```

---

## Testing with Sample Data

Two test files available in `app/sheets/`:
1. Ref_summary_sheet (1,555 projects)
2. SUMMARY_sheet (1,629 projects)

Use these to test the frontend integration.

---

## Performance Notes

- **Processing time**: 20-40 seconds for large files
- **Show progress indicator** while processing
- **Max file size**: 100 MB per file
- **Recommended file size**: < 50 MB for best performance

---

## Backend Health Check

Before starting, verify backend is running:

```javascript
async function checkBackend() {
  try {
    const response = await fetch('/health');
    const data = await response.json();
    console.log('Backend status:', data);
    return data.status === 'ok';
  } catch (error) {
    console.error('Backend not available');
    return false;
  }
}
```

---

## What Happens Inside the API

1. **Parse Files** (5-10 sec)
   - Extract headers and data
   - Normalize project names
   - Validate required columns

2. **Normalize Data** (2-3 sec)
   - Clean whitespace
   - Handle blanks/dashes
   - Parse numbers

3. **Match Rows** (15-25 sec)
   - Exact matching (normalized names)
   - Fuzzy matching (80% similarity)
   - Detect ambiguous matches

4. **Calculate Impacts** (< 1 sec)
   - WIP: current_closing - previous_closing
   - FAR: current_transfer - previous_transfer

5. **Return Results** (< 1 sec)
   - JSON with all matches and summaries
   - Ready for frontend display

---

**Backend is ready! Connect your frontend and start reconciling.** 🚀
