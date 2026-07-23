# jtbd-implement-csv

## Overview

A Claude Code skill that updates existing JTBD (Jobs-to-be-Done) titles in Red Hat product documentation from CSV mapping files. Handles batch processing, title validation, cross-reference updates, and topicmap synchronization with staged user confirmations.

## What It Does

**Title Updates:**
- Updates L1/L2/L3 titles in existing AsciiDoc files from CSV
- Validates title formats (CONCEPT, PROCEDURE, REFERENCE)
- Suggests corrections for invalid formats
- Batch processes multiple categories at once

**Cross-Reference Updates:**
- Updates xref display text to match new titles
- Preserves anchor IDs (keeps `[id="..."]` unchanged)
- Skips custom display text
- Staged confirmation with review mode

**Topicmap Synchronization:**
- Auto-updates `_topic_maps/_topic_map.yml` with new assembly titles
- Validates YAML syntax
- Staged confirmation with review mode

**Missing File Creation:**
- Detects files referenced in CSV but missing from repo
- Creates them via docs-writer agent
- Prompts for user confirmation

## What It Does NOT Do

Change filenames  
Change anchor IDs  
Update external references outside the repo  
Overwrite content (only updates titles and structure)

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

