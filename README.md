# Create Jobs from JTBD Mapping

A Claude Code skill to create and reorganize L1/L2/L3 job topics and assemblies from JTBD CSV mapping with docs-writer agent for Red Hat product documentation.

## Overview

Automates the creation of missing documentation files (assemblies and modules) based on JTBD CSV mapping and reorganizes existing topics to match the Jobs-to-be-Done (JTBD) framework structure.

## Prerequisites

- **Claude Code** installed and configured
- **JTBD CSV mapping file** in format: `Job Mapping for Category template.csv`
- **Red Hat product documentation repository** (to apply the skill to)

## Repository Structure

**Before Installation:**
- `create-jobs-skill/` - Clone repository
- `.claude/skills/` - Contains skill workflow

**After Installation:**
- `~/.claude/skills/create-jobs/SKILL.md` - Global skill
- Documentation projects ready for JTBD transformation

## Installation Steps

1. Clone repository:
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

Navigate to your documentation project and run:
```
/create-jobs
```

Claude will then prompt you for:
1. **CSV file path** - Job Mapping for Category template
2. **Category name** - Which category to create/update

## Workflow

### Interactive Prompts

1. **CSV File Location**
   ```
   Please provide the path to the "Job Mapping for Category template" CSV file.
   ```
   Auto-searches ~/Downloads if not provided

2. **Category Selection**
   ```
   Which category do you want to create/update?
   Available: What's new, Discover, Get started, Plan, Install, Upgrade, 
   Migrate, Administer, Develop, Configure, Secure, Observe, Integrate, 
   Optimize, Extend, Troubleshoot, Reference, Download PDF
   ```

3. **File Verification**
   ```
   Missing files found:
   
   L1 (Assemblies):
   - assemblies/builds-configure.adoc
   
   L2 (Reference sections):
   - modules/ob-configuration-options.adoc
   
   L3 (Topic modules):
   - modules/proc-configure-ansible.adoc
   
   Do you want to create these files? (yes/no)
   ```

4. **Creation & Reorganization**
   - Creates missing L1/L2/L3 files using docs-writer agent
   - Generates professional abstracts and descriptions
   - Reorganizes existing topics per CSV structure
   - Updates assembly include directives

5. **Review Request**
   ```
   ✓ Files created: 12 total
   ✓ Files reorganized: 3 assemblies updated
   
   Please review the changes. Type 'yes' when ready to commit.
   ```

## What the Skill Does

### 1. Parse CSV and Check Files
- Reads JTBD mapping CSV for specified category
- Checks "Full .adoc filename path" column
- Identifies missing L1 (assemblies), L2 (sections), L3 (topics)

### 2. Create Missing Files
Uses **docs-writer agent** to generate:
- **L1 Assemblies** - Top-level job collections with outcome-based titles
- **L2 Reference Sections** - Major groupings within assemblies  
- **L3 Topic Modules** - Individual concept/procedure/reference modules

All with:
- Professional abstracts and descriptions
- Correct AsciiDoc structure
- JTBD-compliant titles (imperatives for procedures, noun phrases for concepts)
- Proper metadata and context variables

### 3. Reorganize Existing Topics
- Reorders assembly include directives per CSV mapping
- Adjusts leveloffset values (+1 for L2, +2 for L3)
- Groups topics under correct L2 sections
- Maintains all existing content

## File Templates

### L1 Assembly
```asciidoc
:_mod-docs-content-type: ASSEMBLY
[id="assembly-id"]
= Job Title

include::_attributes/common-attributes.adoc[]
:context: assembly-id

toc::[]

[role="_abstract"]
2-3 sentence abstract explaining purpose and scope

include::modules/ob-section-1.adoc[leveloffset=+1]
include::modules/topic-1.adoc[leveloffset=+2]
```

### L2 Reference Section
```asciidoc
:_mod-docs-content-type: REFERENCE
[id="ob-section-id_{context}"]
= Section Title

[role="_abstract"]
2-3 sentence abstract

This section covers:
* Topic 1
* Topic 2
```

### L3 Topic Module
```asciidoc
:_mod-docs-content-type: CONCEPT|PROCEDURE|REFERENCE
[id="module-id_{context}"]
= Topic Title

[role="_abstract"]
1-2 sentence description
```

## Resources Used by the Skill

The skill references these resources during execution to ensure JTBD compliance:

### 1. Product Documentation Categories (1).md
- **Purpose**: Defines 15+ product documentation categories
- **Content**: 
  - Category definitions (What's new, Discover, Get started, Plan, Install, Upgrade, Migrate, Administer, Develop, Configure, Secure, Observe, Integrate, Optimize, Extend, Troubleshoot, Reference, Download PDF)
  - JTBD-aligned framing ("When I want to...")
  - Content type mapping for each category
- **Usage**: Guides category selection and content organization

### 2. JTBD Consistency Guidelines.md
- **Purpose**: Ensures consistent JTBD implementation across products
- **Content**:
  - Use case metadata and taxonomy values
  - Heading style guidelines (imperatives vs gerunds)
  - Navigation title best practices
  - Outcome-based heading patterns
  - Title formatting rules (avoid "About", "Understanding", etc.)
- **Usage**: Enforces style and structure compliance in generated files

### 3. Product Documentation Examples
- **Purpose**: Reference implementation of JTBD structure
- **Example**: [Red Hat Ansible Automation Platform 2.6](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/)
- **Content**:
  - Live examples of L1/L2/L3 structure
  - Assembly and module organization
  - AsciiDoc formatting patterns
- **Usage**: Provides templates and patterns for file creation

## Example Output

```
✓ Files created:
  - 2 L1 assemblies
  - 5 L2 reference sections  
  - 15 L3 topic modules

✓ Files reorganized:
  - 3 assemblies updated with new structure
  - 12 topics moved to correct L2 sections

Files ready for review:
assemblies/builds-configure.adoc
assemblies/builds-secure.adoc
modules/ob-configuration-options.adoc
modules/proc-configure-ansible.adoc
...

Next steps:
1. Review abstracts and descriptions
2. Verify file organization matches CSV
3. Check include paths are correct
4. Test documentation build
5. Commit when satisfied
```

## Verification Commands

```bash
# Check created assemblies
ls assemblies/builds-*.adoc

# Check L2 sections
ls modules/ob-*.adoc

# Check L3 topics
ls modules/{con,proc,ref}-*.adoc

# Verify structure
grep -r "include::modules" assemblies/
```

## Troubleshooting

- **CSV not found**: Provide explicit path or copy to ~/Downloads
- **Category not in CSV**: Check spelling matches CSV exactly
- **File already exists**: Skill skips without overwriting
- **Build fails**: Verify include paths match created files
- **Abstract quality**: Review docs-writer output, adjust if needed

## Important Notes

- **Never overwrites** existing files without confirmation
- **Uses docs-writer agent** for professional content quality
- **Follows JTBD guidelines** for titles and structure
- **Waits for review** before committing changes
- **Preserves content** when reorganizing topics

## Related Resources

- [Red Hat Modular Documentation](https://redhat-documentation.github.io/modular-docs/)
- [JTBD Framework Overview](https://jtbd.info/)
- [Red Hat Ansible Automation Platform Documentation](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/)

## License

MIT

## Author

Created by Shivani Sathe for Red Hat documentation workflows.
