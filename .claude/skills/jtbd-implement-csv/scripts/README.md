# JTBD Implement CSV - Scripts

This directory contains Python scripts for CSV parsing, validation, and diff generation used by the `jtbd-implement-csv` skill.

## parse_csv.py

Parses JTBD CSV mapping file and generates structured update plan.

### Usage

```bash
uv run --script parse_csv.py <csv_path> <repo_root> [category1,category2,...]
```

**Arguments:**
- `csv_path`: Path to the CSV file (e.g., `~/Downloads/Job Mapping for Category template.csv`)
- `repo_root`: Root directory of the documentation repository (e.g., `$(pwd)`)
- `categories` (optional): Comma-separated category names (default: `all`)

### Example

```bash
# Parse all categories
uv run --script parse_csv.py \
  ~/Downloads/Job\ Mapping.csv \
  /path/to/docs/repo \
  all

# Parse specific categories
uv run --script parse_csv.py \
  ~/Downloads/Job\ Mapping.csv \
  /path/to/docs/repo \
  "What's new,Discover,Plan"
```

### Output Format (JSON)

**Success:**
```json
{
  "categories": ["What's new", "Discover", "Plan", ...],
  "files": [
    {
      "path": "assemblies/builds-configure.adoc",
      "full_path": "/full/path/to/assemblies/builds-configure.adoc",
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
      "path": "modules/con-security-model.adoc",
      "full_path": "/full/path/to/modules/con-security-model.adoc",
      "category": "Plan",
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

### CSV Format Expected

The script expects a CSV with these columns:
- `Category`: JTBD category name
- `L1 Job Title`: Assembly-level title
- `L2 Section Title`: Section heading title
- `L3 Topic Title`: Module-level title
- `Full .adoc filename path`: Relative path from repo root
- `Content Type`: CONCEPT, PROCEDURE, or REFERENCE

### Title Validation Rules

| Content Type | Expected Format | Example |
|--------------|----------------|---------|
| CONCEPT | Noun phrase | "Security model overview" |
| PROCEDURE | Imperative verb | "Configure authentication" |
| REFERENCE | Noun form | "API endpoint reference" |

Invalid titles will have `validation.valid: false` with a suggested correction.

### Dependencies

Uses Python stdlib only:
- `csv`: CSV parsing
- `json`: JSON output
- `os`, `pathlib`: File system operations
- `typing`: Type hints

No external dependencies required (PEP 723 block has empty `dependencies: []`).
