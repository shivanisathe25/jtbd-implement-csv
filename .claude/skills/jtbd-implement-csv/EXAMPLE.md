# Example Usage: jtbd-implement-csv

This document shows a complete example of using the `jtbd-implement-csv` skill.

## Scenario

You have a JTBD CSV mapping file with updated titles for the "What's new" and "Discover" categories in your OpenShift Builds documentation.

## Step-by-Step Walkthrough

### 1. User starts in a git branch

```bash
$ git checkout -b jtbd-title-updates
$ pwd
/home/user/docs/openshift-builds
```

### 2. User invokes the skill

```
/jtbd-implement-csv
```

### 3. Claude prompts for CSV file

```
Please provide the path to the "Job Mapping for Category template" CSV file.
(If not provided, I'll search in ~/Downloads for matching files)
```

User response: `~/Downloads/Job Mapping for Category template.csv`

### 4. Claude invokes the Python script

```bash
uv run --script ~/.claude/skills/jtbd-implement-csv/scripts/parse_csv.py \
  ~/Downloads/Job\ Mapping\ for\ Category\ template.csv \
  /home/user/docs/openshift-builds \
  all
```

**Script output:**
```json
{
  "categories": ["What's new", "Discover", "Plan", "Install", "Configure"],
  "files": [
    {
      "path": "assemblies/builds-release-notes.adoc",
      "full_path": "/home/user/docs/openshift-builds/assemblies/builds-release-notes.adoc",
      "category": "What's new",
      "current_title": "Builds release notes",
      "csv_title": "Review release updates to plan cluster upgrades",
      "level": "L1",
      "content_type": "ASSEMBLY",
      "needs_update": true,
      "validation": {
        "valid": true,
        "message": "Valid format",
        "suggestion": null
      }
    },
    {
      "path": "modules/proc-setup.adoc",
      "full_path": "/home/user/docs/openshift-builds/modules/proc-setup.adoc",
      "category": "Discover",
      "current_title": "Setting up builds",
      "csv_title": "Setup builds",
      "level": "L3",
      "content_type": "PROCEDURE",
      "needs_update": true,
      "validation": {
        "valid": false,
        "message": "Should start with imperative verb",
        "suggestion": "Consider: \"Set up builds\""
      }
    }
  ],
  "missing_files": [
    {
      "path": "modules/con-security-model.adoc",
      "full_path": "/home/user/docs/openshift-builds/modules/con-security-model.adoc",
      "category": "Discover",
      "csv_title": "Security model overview",
      "level": "L3",
      "content_type": "CONCEPT"
    }
  ]
}
```

### 5. Claude prompts for category selection

```
Which category titles do you want to update?

Available categories from CSV: What's new, Discover, Plan, Install, Configure

Options:
- Enter one category name (e.g., "What's new")
- Enter multiple categories separated by commas (e.g., "What's new, Discover")
- Type "all" or "batch" to process all categories
```

User response: `What's new, Discover`

### 6. Claude re-invokes script with filter

```bash
uv run --script ~/.claude/skills/jtbd-implement-csv/scripts/parse_csv.py \
  ~/Downloads/Job\ Mapping\ for\ Category\ template.csv \
  /home/user/docs/openshift-builds \
  "What's new,Discover"
```

(Output filtered to only "What's new" and "Discover" categories)

### 7. Claude displays comparison table

```
Files found for categories: What's new, Discover

✓ Files to update: 2
❌ Missing files: 1

Title comparison from CSV:

| File | Current Title | CSV Title | Level | Content Type | Validation | Needs Update? |
|------|--------------|-----------|-------|--------------|-----------|---------------|
| assemblies/builds-release-notes.adoc | "Builds release notes" | "Review release updates to plan cluster upgrades" | L1 | ASSEMBLY | ✓ Valid | ✓ YES |
| modules/proc-setup.adoc | "Setting up builds" | "Setup builds" | L3 | PROCEDURE | ⚠️ Should be "Set up builds" | ✓ YES (with suggestion) |
```

### 8. Claude handles validation warning

```
⚠️ Title format issue detected:

File: modules/proc-setup.adoc
Type: PROCEDURE
CSV title: "Setup builds"
Issue: Should start with imperative verb
Suggested correction: "Set up builds"

Options:
1. Apply suggested corrections (recommended)
2. Use CSV titles as-is
3. Skip files with validation warnings

Your choice? (1/2/3)
```

User response: `1`

### 9. Claude prompts for missing files

```
❌ Missing files detected: 1

  - modules/con-security-model.adoc (L3 CONCEPT) - Title: "Security model overview"

Do you want to create these missing files?
1. Yes - create missing files first, then update titles
2. No - skip creating files, only update existing titles
3. Cancel - abort the entire operation

Your choice? (1/2/3)
```

User response: `1`

### 10. Claude spawns docs-writer agent

```
Spawning docs-writer agent to create missing file...

Agent prompt:
Create a CONCEPT module for "Security model overview".

Context:
- Category: Discover
- Content type: CONCEPT
- File path: modules/con-security-model.adoc

Requirements:
- Set :_mod-docs-content-type: CONCEPT
- Use title format: noun phrase (e.g., "Security options")
- Write short description (1-2 sentences)
- Follow Red Hat modular docs template
- Include [role="_abstract"] if needed
- Add {context} variable to id

Format: AsciiDoc
Output: Complete module skeleton
```

### 11. Claude updates file titles

```
Updating titles...

✓ assemblies/builds-release-notes.adoc
  Old: "Builds release notes"
  New: "Review release updates to plan cluster upgrades"

✓ modules/proc-setup.adoc
  Old: "Setting up builds"
  New: "Set up builds" (using suggested correction)

✓ modules/con-security-model.adoc
  Created with title: "Security model overview"
```

### 12. Claude prompts for xref updates (staged)

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

User response: `2` (review first)

### 13. Claude shows xref preview

```
Found 3 cross-references to update:

assemblies/builds-overview.adoc:
  xref:builds-release-notes_{context}[Builds release notes]
  → xref:builds-release-notes_{context}[Review release updates to plan cluster upgrades]

modules/con-getting-started.adoc:
  xref:proc-setup_{context}[Setting up builds]
  → xref:proc-setup_{context}[Set up builds]

modules/ref-installation.adoc:
  xref:proc-setup_{context}[Setting up builds]
  → xref:proc-setup_{context}[Set up builds]

Apply these xref updates? (yes/no)
```

User response: `yes`

### 14. Claude updates xrefs

```
Updating cross-references...

✓ Updated 3 xrefs across 3 files
```

### 15. Claude prompts for topicmap updates (staged)

```
Cross-reference updates complete. Now checking topicmap entries...

Do you want to update _topic_maps/_topic_map.yml with new assembly titles?

Options:
1. Yes - update topicmap entries automatically
2. Review - show me which entries will change first
3. Skip - don't update topicmap

Your choice? (1/2/3)
```

User response: `2` (review first)

### 16. Claude shows topicmap preview

```
Found 1 topicmap entry to update:

_topic_maps/_topic_map.yml:
  Topics:
  - Name: Builds release notes
    File: builds-release-notes
  →
  Topics:
  - Name: Review release updates to plan cluster upgrades
    File: builds-release-notes

Apply this topicmap update? (yes/no)
```

User response: `yes`

### 17. Claude updates topicmap and validates

```
Updating topicmap...

✓ Updated 1 entry in _topic_maps/_topic_map.yml
✓ YAML validation passed
```

### 18. Final summary

```
✓ Implementation Complete

Titles updated: 2
  - assemblies/builds-release-notes.adoc (L1)
  - modules/proc-setup.adoc (L3)

Cross-references updated: 3
  - 1 xref in assemblies/builds-overview.adoc
  - 1 xref in modules/con-getting-started.adoc
  - 1 xref in modules/ref-installation.adoc

Topicmap entries updated: 1
  - _topic_maps/_topic_map.yml (1 assembly name updated)

Files created: 1
  - modules/con-security-model.adoc (L3 CONCEPT)

Next steps:
1. Review updated files: git diff
2. Test documentation build
3. Commit changes when satisfied
```

## Key Features Demonstrated

1. **Python script orchestration:** All CSV parsing and validation logic in `parse_csv.py`
2. **Staged confirmations:** User prompted before xref updates and topicmap changes
3. **Validation with suggestions:** Invalid procedure title caught and corrected
4. **Missing file creation:** docs-writer agent spawned to create concept module
5. **Review mode:** User can preview xref and topicmap changes before applying
6. **JSON-based workflow:** SKILL.md acts on structured output from Python script
7. **No inline conditionals:** All logic in Python script or simple JSON parsing
