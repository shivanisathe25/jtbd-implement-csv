# jtbd-implement-csv

## Overview

A Claude Code skill that updates existing JTBD (Jobs-to-be-Done) titles in Red Hat product documentation from CSV mapping files. Handles batch processing, title validation, cross-reference updates, and topicmap synchronization with staged user confirmations.

## What It Does

✅ **Title Updates:**
- Updates L1/L2/L3 titles in existing AsciiDoc files from CSV
- Validates title formats (CONCEPT, PROCEDURE, REFERENCE)
- Suggests corrections for invalid formats
- Batch processes multiple categories at once

✅ **Cross-Reference Updates:**
- Updates xref display text to match new titles
- Preserves anchor IDs (keeps `[id="..."]` unchanged)
- Skips custom display text
- Staged confirmation with review mode

✅ **Topicmap Synchronization:**
- Auto-updates `_topic_maps/_topic_map.yml` with new assembly titles
- Validates YAML syntax
- Staged confirmation with review mode

✅ **Missing File Creation:**
- Detects files referenced in CSV but missing from repo
- Creates them via docs-writer agent
- Prompts for user confirmation

## What It Does NOT Do

❌ Change filenames  
❌ Change anchor IDs  
❌ Update external references outside the repo  
❌ Overwrite content (only updates titles and structure)

## Prerequisites

- Claude Code installed and configured
- JTBD CSV mapping file (format: "Job Mapping for Category template.csv")
- Red Hat product documentation repository cloned locally
- Python 3.11+ with `uv` installed (for script execution)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/shivanisathe25/create-jobs-skill.git
cd create-jobs-skill
```

2. Copy skill to Claude Code global skills directory:
```bash
mkdir -p ~/.claude/skills/jtbd-implement-csv
cp -r .claude/skills/jtbd-implement-csv/* ~/.claude/skills/jtbd-implement-csv/
```

3. Verify installation:
```bash
ls ~/.claude/skills/jtbd-implement-csv/SKILL.md
ls ~/.claude/skills/jtbd-implement-csv/scripts/parse_csv.py
```

## Usage

Navigate to your documentation repository, then run:

```bash
cd /path/to/your/docs-repo
/jtbd-implement-csv
```

The skill will prompt you for:
1. **CSV file path** (or auto-search ~/Downloads)
2. **Category selection** (single, multiple, or "all")
3. **Missing file creation** (yes/no/cancel)
4. **Xref updates** (yes/review/skip)
5. **Topicmap updates** (yes/review/skip)

## Example Session

```
User: /jtbd-implement-csv

Claude: Please provide the path to the CSV file.
User: ~/Downloads/Job Mapping for Category template.csv

Claude: Which category titles do you want to update?
        Options:
        - Enter one category (e.g., "What's new")
        - Enter multiple (e.g., "What's new, Discover, Plan")
        - Type "all" for batch mode
User: What's new, Discover

Claude: Files found for categories: What's new, Discover

        ✓ Files to update: 5
        ❌ Missing files: 2

        Title comparison from CSV:

        | File | Current Title | CSV Title | Level | Validation | Needs Update? |
        |------|--------------|-----------|-------|-----------|---------------|
        | assemblies/builds-release-notes.adoc | "Builds release notes" | "Review release updates to plan cluster upgrades" | L1 | ✓ Valid | ✓ YES |
        | modules/proc-setup.adoc | "Setting up builds" | "Setup builds" | L3 | ⚠️ Should be "Set up builds" | ✓ YES |

        Missing files detected: 2
          - modules/con-security-model.adoc (L3 CONCEPT) - "Security model overview"
          - modules/ref-api-endpoints.adoc (L3 REFERENCE) - "API endpoint reference"

        Create missing files? (yes/no/cancel)
User: yes

Claude: [Spawns docs-writer agents, creates files]

        Updating titles...
        ✓ 5 titles updated (2 with suggested corrections applied)

        Update xref display text? (yes/review/skip)
User: review

Claude: Found 8 cross-references to update:

        assemblies/overview.adoc:
          xref:builds-release-notes_{context}[Builds release notes]
          → xref:builds-release-notes_{context}[Review release updates to plan cluster upgrades]

        [... 7 more xrefs ...]

        Apply these xref updates? (yes/no)
User: yes

Claude: ✓ 8 xrefs updated

        Update topicmap? (yes/review/skip)
User: yes

Claude: ✓ 1 topicmap entry updated
        ✓ YAML validation passed

        ✓ Implementation Complete

        Titles updated: 5
          - assemblies/builds-release-notes.adoc (L1)
          - modules/proc-setup.adoc (L3)
          - modules/con-security.adoc (L3)
          - modules/ref-config.adoc (L3)
          - modules/proc-install.adoc (L3)

        Cross-references updated: 8
          - 3 xrefs in assemblies/overview.adoc
          - 5 xrefs across 3 other files

        Topicmap entries updated: 1
          - _topic_maps/_topic_map.yml (1 assembly name)

        Files created: 2
          - modules/con-security-model.adoc (L3 CONCEPT)
          - modules/ref-api-endpoints.adoc (L3 REFERENCE)

        Next steps:
        1. Review: git diff
        2. Test documentation build
        3. Commit when satisfied
```

## Workflow Details

### 1. CSV Analysis (Python Script)

The skill uses `scripts/parse_csv.py` (PEP 723) to:
- Parse CSV and extract L1/L2/L3 titles
- Compare with current titles in files
- Validate title formats against content types
- Detect missing files
- Output structured JSON

**Invocation:**
```bash
uv run --script scripts/parse_csv.py <csv_path> <repo_root> [categories]
```

**JSON Output:**
```json
{
  "categories": ["What's new", "Discover", ...],
  "files": [
    {
      "path": "assemblies/builds.adoc",
      "current_title": "Configure Builds",
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
  "missing_files": [...]
}
```

### 2. Title Format Validation

| Content Type | Expected Format | ✅ Valid Example | ❌ Invalid Example |
|--------------|----------------|------------------|-------------------|
| **CONCEPT** | Noun phrase | "Security model overview" | "Configuring security" |
| **PROCEDURE** | Imperative verb | "Configure authentication" | "Configuration of authentication" |
| **REFERENCE** | Noun form | "API endpoint reference" | "Referencing API endpoints" |

Invalid titles trigger a validation warning with suggested corrections.

### 3. Staged Confirmations

User is prompted before:
1. **Creating missing files** → yes/no/cancel
2. **Updating cross-references** → yes/review/skip
3. **Updating topicmap** → yes/review/skip

**Review mode** shows all changes before applying.

### 4. Cross-Reference Updates

Updates only display text in `[...]`, preserves IDs:

```asciidoc
// Before
See xref:config-options_{context}[Configuration options] for details.

// After
See xref:config-options_{context}[Build configuration reference] for details.
```

**Rules:**
- Updates display text matching old title
- Skips custom display text
- Skips commented-out xrefs
- Keeps anchor IDs unchanged

### 5. Topicmap Updates

Updates assembly `Name:` fields in `_topic_maps/_topic_map.yml`:

```yaml
# Before
Topics:
- Name: Builds release notes
  File: builds-release-notes

# After
Topics:
- Name: Review release updates to plan cluster upgrades
  File: builds-release-notes
```

Validates YAML syntax after updates.

## Technical Implementation

### Architecture

**Python Script (PEP 723):**
- `scripts/parse_csv.py` - CSV parsing, validation, diff generation
- Uses Python stdlib only (csv, json, os, pathlib, typing)
- Outputs structured JSON to stdout
- No external dependencies

**SKILL.md (Orchestration):**
- Invokes Python script via `uv run --script`
- Parses JSON output
- Handles user interaction (prompts, confirmations)
- Performs file updates (titles, xrefs, topicmap)
- Spawns docs-writer agent for missing files
- No inline conditionals (logic in Python script)

### Design Principles

1. **Separation of concerns:** Procedural logic in Python, orchestration in SKILL.md
2. **Structured interface:** JSON contract between script and skill
3. **User control:** Staged confirmations for sensitive operations
4. **Validation first:** Check before update, suggest corrections
5. **No destructive actions:** Preserve content, only update titles

## CSV Format

The skill expects a CSV with these columns:

- `Category` - JTBD category name (e.g., "What's new", "Discover")
- `L1 Job Title` - Assembly-level title
- `L2 Section Title` - Section heading title
- `L3 Topic Title` - Module-level title
- `Full .adoc filename path` - Relative path from repo root (e.g., `modules/proc-setup.adoc`)
- `Content Type` - CONCEPT, PROCEDURE, or REFERENCE

**Example:**
```csv
Category,L1 Job Title,L2 Section Title,L3 Topic Title,Full .adoc filename path,Content Type
What's new,Review release updates,,,assemblies/release-notes.adoc,ASSEMBLY
What's new,,,Release notes for version 1.0,modules/rn-1-0.adoc,CONCEPT
Discover,,,Security model overview,modules/con-security.adoc,CONCEPT
```

## Key Features

- ✅ **Batch processing** - Multiple categories in one run
- ✅ **Title validation** - Format checking with suggestions
- ✅ **Staged confirmations** - User control before xref/topicmap updates
- ✅ **Review mode** - Preview changes before applying
- ✅ **Missing file creation** - Via docs-writer agent
- ✅ **YAML validation** - Prevents topicmap syntax errors
- ✅ **No destructive actions** - Preserves all content and IDs
- ✅ **PEP 723 compliance** - Self-contained Python script
- ✅ **No external dependencies** - Uses Python stdlib only

## Documentation

- **SKILL.md** - Complete workflow documentation
- **QUICKSTART.md** - One-page reference guide
- **EXAMPLE.md** - Step-by-step walkthrough
- **IMPLEMENTATION.md** - Design decisions & rationale
- **scripts/README.md** - Script API & JSON schema
- **REVIEW_CHECKLIST.md** - Quality assurance checklist

## Verification Commands

After running the skill:

```bash
# Review all changes
git diff

# Check updated titles
grep "^= " assemblies/*.adoc modules/*.adoc

# Verify xref updates
grep -r "xref:" --include="*.adoc" | grep -i "build"

# Validate topicmap YAML
python3 -c "import yaml; yaml.safe_load_all(open('_topic_maps/_topic_map.yml'))"

# Test documentation build
./build.sh  # or your build command
```

## Troubleshooting

**CSV not found**  
→ Provide explicit path or copy to ~/Downloads

**Category not in CSV**  
→ Check spelling matches CSV exactly (case-sensitive)

**Title validation warning**  
→ Choose option 1 to apply suggested correction

**YAML syntax error after topicmap update**  
→ Check indentation, script validates before writing

**Xref not updated**  
→ Custom display text is intentionally skipped

**Script execution error**  
→ Ensure `uv` is installed: `pip install uv`

## Related Skills

This skill is part of the jtbd-tools suite. Related skills:
- **jtbd-implement-decisions** - Interactive resolution of REC-N recommendations
- **jtbd-header-rewriter** - Single module title updates (no CSV, no batch)

**No overlap** - Each skill handles a different workflow.

## Contributing

Issues and pull requests welcome!

**For bug reports:**
- Include CSV structure (sanitized)
- Attach error messages
- Provide repo structure context

**For feature requests:**
- Describe use case
- Expected vs actual behavior
- Impact on workflow

## Resources Referenced

- Red Hat SSG Title Guidelines
- IBM Style Guide (procedure/concept/reference formats)
- JTBD Consistency Guidelines
- Red Hat Modular Documentation template
- OpenShift Builds topicmap structure

## Recent Updates

### v3.0 (July 2024) - jtbd-implement-csv

- ✨ **NEW**: Refactored to follow project conventions
- ✨ **NEW**: Python script for CSV parsing (PEP 723)
- ✨ **NEW**: Structured JSON interface
- ✨ **NEW**: Staged confirmations for xref and topicmap updates
- ✨ **NEW**: Review mode (preview changes before applying)
- ✨ **NEW**: Title format validation with suggestions
- ✨ **NEW**: Batch processing for multiple categories
- ✨ **NEW**: Missing file detection and creation
- 🐛 **FIX**: No inline conditionals in SKILL.md
- 🐛 **FIX**: Separation of procedural logic (script) and orchestration (skill)

### v2.0 (July 2024) - create-jobs (deprecated)

- Automatic topicmap validation and registration
- Prevents PR build failures from missing topicmap entries

### v1.0 (Initial Release) - create-jobs (deprecated)

- L1/L2/L3 file creation from JTBD CSV

## Author

Created by Shivani Sathe for Red Hat documentation workflows

## License

MIT
