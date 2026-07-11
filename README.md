# Create Jobs from JTBD Mapping - README

## Overview
A Claude Code skill that automates creation and reorganization of L1/L2/L3 job topics and assemblies from JTBD (Jobs-to-be-Done) CSV mapping for Red Hat product documentation. **Now includes automatic topicmap validation and registration** to prevent PR build failures.

## Prerequisites
- Claude Code installed and configured
- JTBD CSV mapping file (format: "Job Mapping for Category template.csv")
- Red Hat product documentation repository cloned locally
- Must be run from within the documentation repository

## Installation

1. Clone the repository:
```bash
git clone https://github.com/shivanisathe25/create-jobs-skill.git
```

2. Copy skill to Claude Code global skills:
```bash
mkdir -p ~/.claude/skills/create-jobs
cp create-jobs-skill/.claude/skills/create-jobs/SKILL.md ~/.claude/skills/create-jobs/
```

3. Verify installation:
```bash
ls ~/.claude/skills/create-jobs/SKILL.md
```

## Usage

Navigate to your documentation repository first, then run:
```bash
cd /path/to/your/docs-repo
/create-jobs
```

## Workflow

### 1. Automatic Branch Creation
Creates branch based on category (e.g., `builds-configure-l2-topics`)

### 2. Interactive Prompts
- CSV file path (auto-searches ~/Downloads)
- Category selection from 15+ available categories
- File verification and creation confirmation

### 3. File Operations
- Creates missing L1 (assemblies), L2 (reference sections), L3 (topic modules)
- Uses docs-writer agent for professional content
- Reorganizes existing topics per CSV structure
- Updates assembly include directives

### 4. **Topicmap Validation & Registration** (New!)

**Critical step that prevents PR build failures:**

After creating files, the skill automatically:
- ✅ Validates all new assemblies are registered in `_topic_maps/_topic_map.yml`
- ✅ Detects missing categories
- ✅ Inserts new categories in the correct order (before Troubleshooting)
- ✅ Prompts for confirmation before updating topicmap
- ✅ Validates YAML syntax

**Example validation output:**
```
Topicmap Validation:

✓ Category "Configure" found in _topic_map.yml
✓ Assembly "builds-configure" already registered

❌ Category "Reference" NOT found in _topic_map.yml
   Need to add:
   ---
   Name: Reference
   Dir: reference
   Distros: openshift-builds
   Topics:
   - Name: API specifications and examples
     File: reference-openshift-builds

Would you like me to update _topic_map.yml? (yes/no)
```

**Topicmap entry format:**
```yaml
---
Name: Reference                      # Display name
Dir: reference                       # Filesystem directory
Distros: openshift-builds           # Product distro
Topics:
- Name: API specifications and examples  # From assembly heading
  File: reference-openshift-builds      # From assembly [id="..."]
```

### 5. Review Process
Displays created/reorganized files and waits for user review before committing

## File Structure

**L1 Assemblies**: Top-level job collections with outcome-based titles

**L2 Reference Sections**: Major groupings within assemblies

**L3 Topic Modules**: Individual concept/procedure/reference modules

All files include proper AsciiDoc structure, metadata, and JTBD-compliant titles.

## Key Features
- ✅ Never overwrites existing files without confirmation
- ✅ Follows JTBD guidelines for titles and structure
- ✅ Uses docs-writer agent for quality content generation
- ✅ Preserves content when reorganizing topics
- ✅ **Automatically validates and updates topicmap** (prevents build failures)
- ✅ **Inserts categories in correct order** (Reference before Troubleshooting)
- ✅ **Validates YAML syntax** before committing

## Common Issues & Solutions

### ❌ PR Build Failure: "Assembly not found in _topic_map.yml"

**Symptom**: GitHub PR fails with:
```
Build failed: Assembly 'reference-openshift-builds' not found in _topic_map.yml
```

**Cause**: New assembly created but topicmap wasn't updated.

**Solution**: The skill now **automatically detects and fixes this** in Step 4. If you encounter this error:
1. Run `/create-jobs` again
2. When prompted, confirm topicmap update
3. The skill will add the missing entry in the correct location

**Example from PR #115155**:
- Created: `reference/reference-openshift-builds.adoc`
- Missing: Entry in `_topic_maps/_topic_map.yml`
- Fix: Skill now automatically adds the Reference category before Troubleshooting

### Manual Verification Commands

After running the skill, you can verify topicmap updates:

```bash
# Check topicmap registration
grep -A10 "^Name: Reference" _topic_maps/_topic_map.yml

# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load_all(open('_topic_maps/_topic_map.yml'))"

# Check created assemblies
ls assemblies/builds-*.adoc

# Verify CSV mapping matches structure
grep -r "include::modules" assemblies/
```

## Category Placement Order

The skill inserts new categories in the standard Red Hat documentation order:

```
1. Release notes
2. About {Product}
3. Install
4. Configure
5. Work with {X}
6. Authentication
7. Observability
8. Reference          ← New categories inserted here
9. Troubleshooting
10. Uninstall
```

## Resources Referenced
- Product Documentation Categories definitions
- JTBD Consistency Guidelines
- Red Hat Ansible Automation Platform documentation examples
- OpenShift Builds topicmap structure

## Recent Updates

### v2.0 (July 2024)
- ✨ **NEW**: Automatic topicmap validation and registration
- ✨ **NEW**: Prevents PR build failures from missing topicmap entries
- ✨ **NEW**: Correct category placement (Reference before Troubleshooting)
- ✨ **NEW**: YAML syntax validation
- 🐛 **FIX**: Addresses issue from PR #115155 (missing topicmap entries)

### v1.0 (Initial Release)
- L1/L2/L3 file creation from JTBD CSV
- docs-writer agent integration
- Topic reorganization

## Author
Created by Shivani Sathe for Red Hat documentation workflows

## Contributing
Issues and pull requests welcome at: https://github.com/shivanisathe25/create-jobs-skill

## License
MIT
