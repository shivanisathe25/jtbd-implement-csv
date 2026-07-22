# Quick Start: jtbd-implement-csv

## What It Does

Batch update JTBD job titles from a CSV mapping file:
- ✅ Updates L1/L2/L3 titles in AsciiDoc files
- ✅ Updates cross-reference display text
- ✅ Updates topicmap entries
- ✅ Creates missing files with docs-writer
- ✅ Validates title formats with suggestions

## Prerequisites

1. Git branch created
2. JTBD CSV file (format: "Job Mapping for Category template.csv")
3. Documentation repo with assemblies/modules

## Usage

```bash
/jtbd-implement-csv
```

Follow prompts:
1. **CSV path** (or auto-detect from ~/Downloads)
2. **Categories** (single, multiple, or "all")
3. **Review** comparison table
4. **Create missing files?** (yes/no/cancel)
5. **Update xrefs?** (yes/review/skip)
6. **Update topicmap?** (yes/review/skip)

## Example

```
User: /jtbd-implement-csv

Claude: Please provide the path to the CSV file.
User: ~/Downloads/Job Mapping.csv

Claude: Which categories? (or "all")
User: What's new, Discover

Claude: [Shows comparison table]
        Missing files detected: 1
        Create them? (1/2/3)
User: 1

Claude: [Creates files, updates titles]
        Update xrefs? (1/2/3)
User: 2

Claude: [Shows xref preview]
        Apply? (yes/no)
User: yes

Claude: [Updates xrefs]
        Update topicmap? (1/2/3)
User: 1

Claude: ✓ Complete
        - 5 titles updated
        - 12 xrefs updated
        - 2 topicmap entries updated
        - 1 file created
```

## CSV Format

Required columns:
- `Category`: JTBD category name
- `L1 Job Title`: Assembly title
- `L2 Section Title`: Section heading
- `L3 Topic Title`: Module title
- `Full .adoc filename path`: e.g., `modules/proc-setup.adoc`
- `Content Type`: CONCEPT, PROCEDURE, or REFERENCE

## Title Validation

| Type | Format | ✅ Valid | ❌ Invalid |
|------|--------|---------|-----------|
| CONCEPT | Noun phrase | "Security overview" | "Configuring security" |
| PROCEDURE | Imperative | "Configure auth" | "Configuration of auth" |
| REFERENCE | Noun form | "API reference" | "Referencing API" |

## What Gets Updated

✅ **Always:**
- Module/assembly title lines (starting with `=`)

✅ **Staged (with confirmation):**
- Cross-reference display text `[...]`
- Topicmap `Name:` fields

❌ **Never:**
- Filenames
- Anchor IDs `[id="..."]`
- Any other metadata

## After Running

```bash
# Review changes
git diff

# Test build
./build.sh  # or your build command

# Commit when satisfied
git add -A
git commit -m "Update JTBD titles from CSV mapping"
```

## Troubleshooting

**CSV not found**
→ Copy to ~/Downloads or provide full path

**Category not in CSV**
→ Check spelling matches CSV exactly

**Title validation warning**
→ Choose option 1 to apply suggested correction

**YAML syntax error**
→ Script validates topicmap, check indentation

**Xref not updated**
→ Custom display text is intentionally skipped

## Technical Details

- **Python script:** `scripts/parse_csv.py` (PEP 723)
- **JSON interface:** Structured stdin/stdout
- **No dependencies:** Uses Python stdlib only
- **Invocation:** `uv run --script`

For full documentation, see `SKILL.md` and `EXAMPLE.md`.
