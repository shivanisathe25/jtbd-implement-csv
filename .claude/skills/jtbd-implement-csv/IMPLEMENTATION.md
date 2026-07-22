# Implementation Summary: jtbd-implement-csv

This document summarizes the implementation following the project conventions outlined in the feature request discussion.

## Design Decisions

### 1. Python Script for Procedural Logic

**Location:** `skills/jtbd-implement-csv/scripts/parse_csv.py`

**Responsibilities:**
- CSV parsing and validation
- Path computation (relative → absolute)
- Title extraction from existing files
- Content type detection
- Title format validation with suggestions
- Diff generation (current vs CSV)
- Structured JSON output to stdout

**Why:**
- Separates procedural logic from orchestration
- Testable independently of Claude
- Follows project convention: "procedural logic should live in a Python script"

### 2. SKILL.md as Orchestrator

**Responsibilities:**
- User interaction (prompts, confirmations)
- Invoking the Python script via `uv run --script`
- Parsing JSON output
- File updates (applying title changes)
- docs-writer agent spawning for missing files
- xref and topicmap updates
- Staged confirmations (before xref/topicmap changes)

**Why:**
- No inline conditionals in SKILL.md
- Acts on structured data from Python script
- Handles Claude-specific operations (agents, file edits, user prompts)

### 3. PEP 723 Inline Metadata

**Script header:**
```python
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
```

**Why:**
- Self-contained script with explicit Python version requirement
- Uses only stdlib (csv, json, os, pathlib, typing)
- No external dependencies needed
- Invoked via `uv run --script` per convention

### 4. Staged Confirmation UX

**User is prompted before:**
1. Creating missing files (yes/no/cancel)
2. Updating cross-references (yes/review/skip)
3. Updating topicmap entries (yes/review/skip)

**Why:**
- Follows the approved UX design: "staged confirmation UX should stay as-is"
- Gives user control over each update phase
- Review mode shows changes before applying

## File Structure

```
jtbd-implement-csv/
├── SKILL.md              # Main orchestration logic
├── EXAMPLE.md            # Complete usage walkthrough
├── IMPLEMENTATION.md     # This file
└── scripts/
    ├── parse_csv.py      # CSV parsing & validation (PEP 723)
    └── README.md         # Script documentation & JSON schema
```

## JSON Interface

### Input (Command Line)

```bash
uv run --script parse_csv.py <csv_path> <repo_root> [categories]
```

### Output (stdout)

**Success:**
```json
{
  "categories": ["What's new", "Discover", ...],
  "files": [
    {
      "path": "assemblies/builds-configure.adoc",
      "full_path": "/absolute/path/to/file.adoc",
      "category": "What's new",
      "current_title": "Configure OpenShift Builds",
      "csv_title": "Configure build settings and pipelines",
      "level": "L1",
      "content_type": "ASSEMBLY",
      "needs_update": true,
      "validation": {
        "valid": true,
        "message": "Valid format",
        "suggestion": null
      }
    }
  ],
  "missing_files": [
    {
      "path": "modules/con-security.adoc",
      "full_path": "/absolute/path/to/file.adoc",
      "category": "Discover",
      "csv_title": "Security model overview",
      "level": "L3",
      "content_type": "CONCEPT"
    }
  ]
}
```

**Error:**
```json
{
  "error": "CSV file not found: /path/to/file.csv"
}
```

## Title Validation Rules

| Content Type | Expected Format | Example Valid | Example Invalid |
|--------------|----------------|---------------|-----------------|
| CONCEPT | Noun phrase | "Security model overview" | "Configuring security" |
| PROCEDURE | Imperative verb | "Configure authentication" | "Configuration of authentication" |
| REFERENCE | Noun form | "API endpoint reference" | "Referencing API endpoints" |

Invalid titles trigger `validation.valid: false` with a suggested correction in `validation.suggestion`.

## Workflow Stages

1. **Discovery:** Python script analyzes CSV and files → JSON
2. **Planning:** SKILL.md displays comparison table, prompts user
3. **Creation:** docs-writer agent creates missing files (if user approves)
4. **Title Updates:** SKILL.md applies title changes from JSON
5. **Xref Updates:** Staged confirmation → update display text only
6. **Topicmap Updates:** Staged confirmation → update assembly names
7. **Summary:** Report all changes made

## Key Features

- ✅ No inline conditionals in SKILL.md
- ✅ All procedural logic in Python script
- ✅ PEP 723 metadata for script dependencies
- ✅ Structured JSON interface (stdin/stdout)
- ✅ Staged confirmations for xref/topicmap
- ✅ Title validation with suggestions
- ✅ Batch processing support
- ✅ Missing file creation via docs-writer
- ✅ Review mode for xref/topicmap changes

## Testing the Implementation

### Manual Test

```bash
# 1. Create a test CSV
cat > /tmp/test-mapping.csv <<EOF
Category,L1 Job Title,L2 Section Title,L3 Topic Title,Full .adoc filename path,Content Type
What's new,Review release updates,,,assemblies/release-notes.adoc,ASSEMBLY
What's new,,,Release notes for version 1.0,modules/rn-1-0.adoc,CONCEPT
EOF

# 2. Run the script
uv run --script ~/.claude/skills/jtbd-implement-csv/scripts/parse_csv.py \
  /tmp/test-mapping.csv \
  /path/to/docs/repo \
  "What's new"

# 3. Verify JSON output
# Should show categories, files array, missing_files array
```

### Integration Test

```bash
# In a docs repo with a git branch
/jtbd-implement-csv

# Follow prompts:
# 1. Provide CSV path
# 2. Select categories
# 3. Confirm file creation
# 4. Review xref updates
# 5. Review topicmap updates

# Verify:
git diff  # Check title changes, xref updates, topicmap updates
```

## Future Enhancements (Optional)

- Add `--dry-run` flag to script for validation-only mode
- Support for DITA XML format (currently AsciiDoc only)
- Parallel processing for large CSV files
- CSV schema validation (ensure required columns exist)
- More sophisticated title validation (style guide compliance)

## Comparison with Existing Skills

- **jtbd-implement-decisions:** Interactive resolution of REC-N recommendations (different workflow)
- **jtbd-header-rewriter:** Single module at a time, no CSV, no xref/topicmap updates

**No overlap confirmed** ✓

## Maintainer Notes

- Script uses only Python stdlib (no `pip install` needed)
- SKILL.md can be extended to support DITA without changing the script
- JSON schema is stable and versioned implicitly by the script
- Staged confirmations can be disabled via skill parameter (future)
