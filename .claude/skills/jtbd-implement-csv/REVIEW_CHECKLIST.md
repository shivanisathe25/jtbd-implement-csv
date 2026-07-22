# Review Checklist: jtbd-implement-csv

Use this checklist to review the implementation against project conventions.

## ✅ Project Conventions Compliance

### Python Script Structure
- [x] Procedural logic lives in `scripts/parse_csv.py`
- [x] Script emits structured JSON to stdout
- [x] PEP 723 inline metadata present (even with empty `dependencies: []`)
- [x] Script invoked via `uv run --script`
- [x] No dependencies beyond Python stdlib
- [x] Script is executable (`chmod +x`)

### SKILL.md Structure
- [x] Orchestrates based on script JSON output
- [x] No inline conditionals (logic delegated to script)
- [x] Clear workflow steps documented
- [x] User interaction handled in skill, not script
- [x] Staged confirmations implemented (xref, topicmap)

### UX Design
- [x] Staged confirmation before xref updates (yes/review/skip)
- [x] Staged confirmation before topicmap updates (yes/review/skip)
- [x] Review mode shows changes before applying
- [x] User can cancel at each stage
- [x] Progress reporting for batch operations

## 📋 Feature Completeness

### Core Features
- [x] CSV parsing and validation
- [x] Title extraction from existing files
- [x] Path computation (relative → absolute)
- [x] Current vs CSV title comparison
- [x] Missing file detection
- [x] Title format validation with suggestions
- [x] Batch processing (multiple categories)

### Update Operations
- [x] Title updates in assemblies and modules
- [x] Cross-reference display text updates
- [x] Topicmap entry updates
- [x] Missing file creation via docs-writer agent

### Validation
- [x] CONCEPT titles (noun phrase)
- [x] PROCEDURE titles (imperative verb)
- [x] REFERENCE titles (noun form)
- [x] Suggestion generation for invalid titles
- [x] YAML syntax validation after topicmap updates

## 📚 Documentation

### User-Facing Docs
- [x] SKILL.md: Complete workflow documentation
- [x] QUICKSTART.md: Quick reference guide
- [x] EXAMPLE.md: Step-by-step walkthrough

### Developer Docs
- [x] scripts/README.md: Script documentation & JSON schema
- [x] IMPLEMENTATION.md: Design decisions & rationale
- [x] REVIEW_CHECKLIST.md: This file

## 🔍 Code Quality

### Python Script (`parse_csv.py`)
- [x] Type hints used (typing module)
- [x] Docstrings for functions
- [x] Error handling with JSON error messages
- [x] Clean separation of concerns (parse, validate, check)
- [x] No hardcoded paths or assumptions

### SKILL.md
- [x] Clear step-by-step workflow
- [x] Example outputs for clarity
- [x] Troubleshooting section
- [x] Verification commands provided
- [x] Important notes highlighted

## 🧪 Testing

### Manual Tests to Run
- [ ] Script with invalid CSV path → JSON error
- [ ] Script with valid CSV → structured JSON
- [ ] Script with category filter → filtered results
- [ ] Title validation for each content type
- [ ] Missing file detection
- [ ] Batch processing (multiple categories)

### Integration Tests
- [ ] Full skill run: CSV → titles → xrefs → topicmap
- [ ] Review mode for xrefs and topicmap
- [ ] docs-writer agent invocation for missing files
- [ ] Git diff shows only intended changes

## 🚀 Edge Cases Handled

- [x] CSV file not found → JSON error
- [x] Repository root not found → JSON error
- [x] Empty CSV rows → skipped
- [x] Missing title in file → reported as "(not found)"
- [x] Content type not in file → fallback to CSV content type
- [x] Invalid title format → validation warning + suggestion
- [x] Custom xref display text → preserved (not updated)
- [x] Commented-out xrefs → skipped
- [x] YAML syntax errors → validation failure

## 📊 Performance Considerations

- [x] Script runs once per workflow (not per file)
- [x] Batch processing reduces overhead
- [x] No unnecessary file reads
- [x] JSON output is compact and efficient

## 🔒 Safety

- [x] Never changes filenames
- [x] Never changes anchor IDs
- [x] Preserves all metadata except titles
- [x] User confirmation before destructive operations
- [x] Git diff recommended before commit
- [x] YAML validation before writing topicmap

## 📦 Deliverables

Files included:
- [x] `SKILL.md` - Main skill documentation
- [x] `scripts/parse_csv.py` - Python script with PEP 723
- [x] `scripts/README.md` - Script documentation
- [x] `EXAMPLE.md` - Complete usage example
- [x] `IMPLEMENTATION.md` - Design decisions
- [x] `QUICKSTART.md` - Quick reference
- [x] `REVIEW_CHECKLIST.md` - This file

## ✨ Maintainer Approval Criteria

### Must Have
- [x] No overlap with existing jtbd-tools skills
- [x] Follows project Python script convention
- [x] Uses PEP 723 inline metadata
- [x] Staged confirmation UX preserved
- [x] JSON interface for script ↔ skill communication

### Nice to Have
- [x] Comprehensive documentation
- [x] Clear examples
- [x] Troubleshooting guidance
- [x] Review mode for sensitive operations
- [x] Batch processing support

## 🎯 Next Steps

1. **Internal testing:** Run through EXAMPLE.md scenario
2. **Peer review:** Check against this checklist
3. **Documentation review:** Ensure clarity for end users
4. **Submit for approval:** Share with maintainers

## Notes for Reviewers

**Key Design Decisions:**
1. Python script handles ALL parsing/validation logic
2. SKILL.md is purely orchestration (no conditionals)
3. Staged confirmations give user control at each phase
4. Review mode previews changes before applying
5. JSON interface is the contract between script and skill

**Potential Concerns:**
- Script assumes CSV column names are exact (could be made flexible)
- Title validation rules are basic (could reference full style guide)
- No rollback mechanism (relies on git for undo)

**Future Enhancements:**
- Add `--dry-run` flag to script
- Support DITA XML in addition to AsciiDoc
- Parallel processing for large CSVs
- CSV schema validation
