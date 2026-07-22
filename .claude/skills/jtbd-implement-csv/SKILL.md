---
name: jtbd-implement-csv
description: Update job titles, cross-references, and topicmap from JTBD CSV mapping with batch processing support
triggers: []
---

# Implement JTBD Titles from CSV Mapping

Update job titles (L1/L2/L3) in existing AsciiDoc files from JTBD CSV mapping, update cross-reference display text, auto-update topicmap entries, and create missing topic files when needed. Supports batch processing for multiple categories.

**Implementation:** Uses `scripts/parse_csv.py` for CSV parsing, validation, path computation, and diff generation. The skill orchestrates based on structured JSON output.

## Prerequisites

- User has already created a git branch and started Claude in that branch
- JTBD CSV mapping file in format: `Job Mapping for Category template.csv`
- Existing product documentation repository with assemblies and modules
- Topic map file at `_topic_maps/_topic_map.yml` (if using topicmap repos)

## Scope

✓ **What this skill does:**
- Update module titles from CSV
- Update cross-reference display text to match new titles
- Auto-update topicmap entries with new titles
- Create missing topic files with docs-writer agent
- Batch process multiple categories at once

✗ **What this skill does NOT do:**
- Change filenames
- Change anchor IDs (keeps existing `[id="..."]` unchanged)
- Update external references outside the repo

## Usage

```
/jtbd-implement-csv
```

Claude will prompt for:
1. CSV file path (auto-searches ~/Downloads if not provided)
2. Category name(s) to update:
   - Single category: `What's new`
   - Multiple categories: `What's new, Discover, Get started`
   - All categories: `all` or `batch`

## Workflow

### Step 1: Prompt for CSV File

Ask the user:
```
Please provide the path to the "Job Mapping for Category template" CSV file.
(If not provided, I'll search in ~/Downloads for matching files)
```

If no path provided, search:
```bash
find ~/Downloads -name "*Job Mapping*" -o -name "*Category template*.csv" 2>/dev/null | head -5
```

Present found files and ask user to confirm or provide path.

### Step 2: Prompt for Category Selection

Ask the user:
```
Which category titles do you want to update?

Options:
- Enter one category name (e.g., "What's new")
- Enter multiple categories separated by commas (e.g., "What's new, Discover, Plan")
- Type "all" or "batch" to process all categories
```

### Step 3: Invoke Python Script for CSV Analysis

Run the parsing script with category filter:

```bash
uv run --script ~/.claude/skills/jtbd-implement-csv/scripts/parse_csv.py \
  "/path/to/csv/file.csv" \
  "$(pwd)" \
  "What's new,Discover"
```

**Script output (JSON):**
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

If the script returns an error:
```json
{
  "error": "CSV file not found: /path/to/file.csv"
}
```

Handle error and ask user to correct the path.

### Step 4: Display Comparison Table

Parse the JSON output and display a comparison table:

```
Files found for categories: What's new, Discover

✓ Files to update: 5
❌ Missing files: 2

Title comparison from CSV:

| File | Current Title | CSV Title | Level | Content Type | Validation | Needs Update? |
|------|--------------|-----------|-------|--------------|-----------|---------------|
| assemblies/builds-configure.adoc | "Configure OpenShift Builds" | "Configure build settings and pipelines" | L1 | ASSEMBLY | ✓ Valid | ✓ YES |
| modules/con-security.adoc | "Using security features" | "Security features" | L3 | CONCEPT | ✓ Valid | ✓ YES |
| modules/proc-setup.adoc | "Setting up the service" | "Setup the service" | L3 | PROCEDURE | ⚠️ Should be "Set up the service" | ✓ YES (with suggestion) |
```

**If validation warnings exist**, ask user:
```
⚠️ Title format issues detected:

File: modules/proc-setup.adoc
Type: PROCEDURE
CSV title: "Setup the service"
Issue: Should start with imperative verb
Suggested correction: "Set up the service"

Options:
1. Apply suggested corrections (recommended)
2. Use CSV titles as-is
3. Skip files with validation warnings

Your choice? (1/2/3)
```

### Step 5: Prompt for Missing Files

If `missing_files` array is not empty:

```
❌ Missing files detected: 2

  - modules/con-security-model.adoc (L3 CONCEPT) - Title: "Security model overview"
  - modules/ref-api-endpoints.adoc (L3 REFERENCE) - Title: "API endpoint reference"

Do you want to create these missing files?
1. Yes - create missing files first, then update titles
2. No - skip creating files, only update existing titles
3. Cancel - abort the entire operation

Your choice? (1/2/3)
```

### Step 6: Create Missing Files (if user chose option 1)

For each file in `missing_files`, spawn a docs-writer agent:

```
Create a {content_type} module for "{csv_title}".

Context:
- Category: {category}
- Content type: {content_type}
- File path: {path}

Requirements:
- Set :_mod-docs-content-type: {content_type}
- Use title format:
  - PROCEDURE: imperative (e.g., "Configure authentication")
  - CONCEPT: noun phrase (e.g., "Security options")
  - REFERENCE: descriptive (e.g., "API endpoint reference")
- Write short description (1-2 sentences)
- Follow Red Hat modular docs template
- Include [role="_abstract"] if needed
- Add {context} variable to id

Format: AsciiDoc
Output: Complete module skeleton
```

Wait for docs-writer to complete each file before proceeding.

### Step 7: Update File Titles

For each file in `files` where `needs_update: true`:

1. Read the file
2. Find the title line (starts with `=`)
3. Apply the title from `csv_title` (or suggested correction if user chose option 1)
4. Update only the title line

**Example update:**
```asciidoc
// Before
= Configure OpenShift Builds

// After
= Configure build settings and pipelines
```

**IMPORTANT:** Only update the title line. Do NOT change:
- Anchor IDs `[id="..."]`
- Filenames
- Any other metadata

### Step 8: Update Cross-Reference Display Text (Staged Confirmation)

**Prompt user before proceeding:**
```
Title updates complete. Now checking cross-references...

Do you want to update xref display text to match the new titles?
This will update display text in square brackets [...] only, keeping IDs unchanged.

Options:
1. Yes - update all xref display text automatically
2. Review - show me which xrefs will change first
3. Skip - don't update xrefs

Your choice? (1/2/3)
```

If user chooses option 1 or 2:

For each updated file, find all cross-references in the repository:

```bash
# Find all xrefs to the updated module
grep -r "xref:.*ob-configuration-options" --include="*.adoc" .
```

For each xref found:
1. Extract the current display text (content in square brackets)
2. Check if it matches the old title
3. If yes, update to new title
4. If no, skip (it's custom display text)

**Example:**
```asciidoc
// Before
See xref:ob-configuration-options_{context}[Configuration options] for details.

// After
See xref:ob-configuration-options_{context}[Build configuration reference] for details.
```

If user chose option 2 (Review), display the xref changes and ask for confirmation before applying.

### Step 9: Update Topic Map Entries (Staged Confirmation)

**Prompt user before proceeding:**
```
Cross-reference updates complete. Now checking topicmap entries...

Do you want to update _topic_maps/_topic_map.yml with new assembly titles?

Options:
1. Yes - update topicmap entries automatically
2. Review - show me which entries will change first
3. Skip - don't update topicmap

Your choice? (1/2/3)
```

If user chooses option 1 or 2:

1. Check if `_topic_maps/_topic_map.yml` exists
2. For each updated assembly in `files` where `level: "L1"`:
   - Find the entry with matching `File:` field
   - Update the `Name:` field with `csv_title`
   - Preserve all indentation and formatting

**Example:**
```yaml
# Before
---
Name: Release notes
Dir: release_notes
Distros: openshift-builds
Topics:
- Name: Builds release notes
  File: ob-openshift-builds-release-notes

# After
---
Name: Release notes
Dir: release_notes
Distros: openshift-builds
Topics:
- Name: Review release updates to plan cluster upgrades
  File: ob-openshift-builds-release-notes
```

If user chose option 2 (Review), display the topicmap changes and ask for confirmation before applying.

Validate YAML syntax after updates:
```bash
python3 -c "import yaml; yaml.safe_load_all(open('_topic_maps/_topic_map.yml'))"
```

### Step 10: Batch Processing Progress

When processing multiple categories, show progress:

```
Processing categories: What's new, Discover, Plan

[1/3] What's new
✓ 3 files checked, 1 title updated
✓ 2 xrefs updated
✓ 1 topicmap entry updated

[2/3] Discover
✓ 5 files checked, 3 titles updated
✓ 7 xrefs updated
✓ 1 topicmap entry updated

[3/3] Plan
✓ 4 files checked, 2 titles updated
✓ 5 xrefs updated
✓ 1 topicmap entry updated
```

### Step 11: Final Summary

Display comprehensive summary:

```
✓ Implementation Complete

Titles updated: 6
  - assemblies/builds-configure.adoc (L1)
  - modules/ob-configuration-options.adoc (L2)
  - modules/proc-configure-ansible.adoc (L3)
  - modules/con-security.adoc (L3)
  - modules/proc-setup.adoc (L3)
  - modules/ref-api.adoc (L3)

Cross-references updated: 14
  - 5 xrefs in assemblies/builds-configure.adoc
  - 3 xrefs in modules/proc-setup-builds.adoc
  - 6 xrefs across 4 other files

Topicmap entries updated: 3
  - _topic_maps/_topic_map.yml (3 assembly names updated)

Files created: 2
  - modules/con-security-model.adoc (L3 CONCEPT)
  - modules/ref-api-endpoints.adoc (L3 REFERENCE)

Next steps:
1. Review updated files: git diff
2. Test documentation build
3. Commit changes when satisfied
```

## Title Validation Guidelines

The Python script validates titles against these rules:

| Module Type | Format | Valid Example | Invalid Example |
|-------------|--------|---------------|-----------------|
| **CONCEPT** | Noun phrase | "Security model overview" | "Configuring security" |
| **PROCEDURE** | Imperative verb | "Configure authentication" | "Configuration of authentication" |
| **REFERENCE** | Noun form | "API endpoint reference" | "Referencing API endpoints" |

Invalid titles trigger a validation warning with suggested corrections.

## Important Notes

- **Staged confirmations:** User is prompted before xref updates and topicmap changes
- **Python script handles:** CSV parsing, validation, path computation, diff generation
- **SKILL.md handles:** User interaction, file updates, docs-writer orchestration
- **No inline conditionals:** All logic is in the Python script or simple JSON parsing
- **User creates branch first:** Skill does NOT create branches
- **Preserve content:** Only update titles and structure, never overwrite content
- **Batch processing:** Process multiple categories in one invocation

## Verification Commands

After running, verify:

```bash
# Check updated titles
grep "^= " assemblies/*.adoc modules/*.adoc

# Check xref updates
grep -r "xref:" --include="*.adoc" | grep -i "configuration"

# Validate topicmap YAML
python3 -c "import yaml; yaml.safe_load_all(open('_topic_maps/_topic_map.yml'))"

# Review git diff
git diff
```

## Troubleshooting

- **Script error:** Check that `uv` is installed and CSV path is correct
- **CSV not found:** Provide explicit path or copy to ~/Downloads
- **Category not in CSV:** Check category spelling matches CSV exactly
- **Validation warnings:** Apply suggested corrections or override with CSV titles
- **YAML syntax error:** Check topicmap indentation after update
- **Xref not updated:** Custom display text is intentionally skipped
