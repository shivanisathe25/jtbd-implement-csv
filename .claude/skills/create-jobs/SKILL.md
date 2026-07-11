---
name: create-jobs
description: Create and reorganize L1/L2/L3 job topics and assemblies from JTBD CSV mapping with docs-writer agent
triggers: []
---

# Create Jobs from JTBD Mapping

A skill to create missing L1/L2/L3 documentation files from JTBD CSV mapping and reorganize existing topics to match the JTBD structure for Red Hat product documentation.

## Prerequisites

- **Claude Code** installed and configured
- **JTBD CSV mapping file** in format: `Job Mapping for Category template.csv`
- **Product documentation categories (1).md** - Category definitions and JTBD alignment
- **JTBD consistency guidelines.md** - Style and structure guidelines
- **Product documentation** (e.g., [Red Hat Ansible Automation Platform 2.6](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.6/))

## Resource Files

The following resources guide the job creation and organization process:

1. **Product documentation categories (1).md**
   - Defines 15+ product documentation categories (What's new, Discover, Get started, Plan, Install, etc.)
   - Provides JTBD-aligned framing ("When I want to...")
   - Maps content types to each category

2. **JTBD consistency guidelines.md**
   - Use case metadata and taxonomy values
   - Heading style guidelines (imperatives vs gerunds)
   - Navigation title best practices
   - Outcome-based heading patterns
   - Content organization rules

3. **Product Documentation**
   - Reference documentation structure (e.g., Ansible Automation Platform)
   - Existing module files and assemblies
   - Current content organization

## Repository Structure

**Before Running:**
- JTBD CSV file with complete job mapping
- Existing product documentation repository
- Reference resources in accessible location

**After Running:**
- New L1/L2/L3 AsciiDoc files created
- Existing topics reorganized per CSV structure
- Assembly files updated with correct includes
- Ready for review and commit

## Usage

Navigate to your documentation project and run:
```
/create-jobs
```

Claude will then prompt you for:
1. CSV file path (Job Mapping for Category template)
2. Category name to create/update

## Workflow

### 1. Prompt for CSV File

Ask the user:
```
Please provide the path to the "Job Mapping for Category template" CSV file.
(If not provided, I'll search in ~/Downloads for matching files)
```

If no path provided, search:
```bash
find ~/Downloads -name "*Job Mapping*" -o -name "*Category template*.csv" 2>/dev/null | head -5
```

### 2. Prompt for Category

Ask the user:
```
Which category do you want to create/update?
Available categories: What's new, Discover, Get started, Plan, Install, Upgrade, 
Migrate, Administer, Develop, Configure, Secure, Observe, Integrate, Optimize, 
Extend, Troubleshoot, Reference, Download PDF
```

### 3. Parse CSV and Check Existing Files

Read the CSV for the specified category and extract:
- **L1 jobs** (assembly-level parent topics)
- **L2 sections** (major groupings within assemblies)
- **L3 topics** (individual concept/procedure/reference modules)
- **Full .adoc filename path** column

For each file path in the CSV, check if the file exists:
```bash
test -f "modules/ob-{filename}.adoc" && echo "EXISTS" || echo "MISSING"
test -f "assemblies/{filename}.adoc" && echo "EXISTS" || echo "MISSING"
```

### 4. List Missing Files and Confirm

Display to user:
```
Missing files found:

L1 (Assemblies):
- assemblies/builds-configure.adoc
- assemblies/builds-secure.adoc

L2 (Reference sections):
- modules/ob-configuration-options.adoc
- modules/ob-security-features.adoc

L3 (Topic modules):
- modules/proc-configure-ansible.adoc
- modules/con-security-model.adoc
- modules/ref-api-endpoints.adoc

Do you want to create these files? (yes/no)
```

### 5. Create Missing Files with docs-writer Agent

If user confirms, for each missing file:

#### For L1 Assembly Files

Call docs-writer agent:
```
Create an ASSEMBLY file for "{L1 job title}".

Context:
- Category: {category name}
- JTBD framing: {from Product documentation categories.md}
- This assembly covers {number} L2 sections: {comma-separated L2 titles}

Requirements:
- Follow Red Hat modular documentation structure
- Use outcome-based title (imperative form, not gerund)
- Write 2-3 sentence abstract explaining purpose and scope
- Include toc::[] directive
- Set up :context: attribute
- Add include directives for all L2 and L3 files per CSV structure
- Follow JTBD consistency guidelines

Format: AsciiDoc
Output: Complete assembly file content
```

#### For L2 Reference Section Files

Call docs-writer agent:
```
Create a REFERENCE module for "{L2 section title}".

Context:
- Parent assembly: {L1 assembly title}
- Category: {category name}
- Topics covered: {comma-separated L3 topic list}

Requirements:
- Set :_mod-docs-content-type: REFERENCE
- Use outcome-based section title
- Write 2-3 sentence abstract explaining what this section helps users accomplish
- List all covered topics as bullet points
- Include [role="_abstract"] for abstract
- Add {context} variable to id

Format: AsciiDoc
Output: Complete reference module content
```

#### For L3 Topic Modules

Call docs-writer agent:
```
Create a {CONCEPT/PROCEDURE/REFERENCE} module for "{L3 topic title}".

Context:
- Parent section: {L2 section title}
- Parent assembly: {L1 assembly title}
- Category: {category name}
- Content type: {CONCEPT/PROCEDURE/REFERENCE}

Requirements:
- Set :_mod-docs-content-type: {type}
- Use appropriate title format:
  - PROCEDURE: imperative (e.g., "Configure authentication")
  - CONCEPT: noun phrase (e.g., "Security options")
  - REFERENCE: descriptive (e.g., "API endpoint reference")
- Write short description (1-2 sentences)
- Follow Red Hat modular docs template for content type
- Include [role="_abstract"] if needed
- Add {context} variable to id

Format: AsciiDoc
Output: Complete module skeleton with description
```

### 6. Reorganize Existing Topics

After creating missing files:

1. **Read existing assembly structure** from the documentation
2. **Compare with CSV mapping** for the category
3. **Identify topics that need to be moved or reordered**
4. **Update assembly include directives** to match CSV structure:
   - Reorder includes per CSV row order
   - Adjust leveloffset values (+1 for L2, +2 for L3)
   - Group topics under correct L2 sections

Example reorganization:
```asciidoc
// Before (old structure)
include::modules/topic-a.adoc[leveloffset=+1]
include::modules/topic-b.adoc[leveloffset=+1]
include::modules/topic-c.adoc[leveloffset=+1]

// After (JTBD structure per CSV)
include::modules/ob-configuration.adoc[leveloffset=+1]

include::modules/topic-a.adoc[leveloffset=+2]
include::modules/topic-c.adoc[leveloffset=+2]

include::modules/ob-security.adoc[leveloffset=+1]

include::modules/topic-b.adoc[leveloffset=+2]
```

### 7. Report Results and Request Review

Display summary:
```
✓ Files created:
  - {count} L1 assemblies
  - {count} L2 reference sections  
  - {count} L3 topic modules

✓ Files reorganized:
  - {count} assemblies updated with new structure
  - {count} topics moved to correct L2 sections

Files ready for review:
{list all created and modified files with paths}

Next steps:
1. Review all abstracts and descriptions for accuracy
2. Verify file organization matches CSV structure
3. Check that all include paths are correct
4. Test documentation build
5. Commit changes when satisfied

Please review the changes. Type 'yes' when you're ready to proceed with commit, 
or let me know if you need any adjustments.
```

Wait for user confirmation before proceeding to commit.

## File Templates

### L1 Assembly Template
```asciidoc
:_mod-docs-content-type: ASSEMBLY
[id="{assembly-id}"]
= {L1 Job Title}

include::_attributes/common-attributes.adoc[]
:context: {assembly-id}

toc::[]

[role="_abstract"]
{2-3 sentence abstract explaining overall purpose and scope}

include::modules/ob-{l2-section-1-id}.adoc[leveloffset=+1]

include::modules/{l3-topic-1}.adoc[leveloffset=+2]

include::modules/{l3-topic-2}.adoc[leveloffset=+2]

include::modules/ob-{l2-section-2-id}.adoc[leveloffset=+1]

include::modules/{l3-topic-3}.adoc[leveloffset=+2]

// [role="_additional-resources"]
// == Additional resources
```

### L2 Reference Section Template
```asciidoc
// This module is included in the following assembly:
//
// * {assembly-path}

:_mod-docs-content-type: REFERENCE
[id="ob-{section-id}_{context}"]
= {L2 Section Title}

[role="_abstract"]
{2-3 sentence abstract explaining what this section helps users accomplish}

This section covers the following topics:

* {Topic 1 navtitle}
* {Topic 2 navtitle}
* {Topic 3 navtitle}
```

### L3 Topic Module Template
```asciidoc
// This module is included in the following assembly:
//
// * {assembly-path}

:_mod-docs-content-type: {CONCEPT|PROCEDURE|REFERENCE}
[id="{module-id}_{context}"]
= {Topic Title}

[role="_abstract"]
{1-2 sentence description}

{Module content based on type}
```

## Important Notes

- **Auto-detect CSV**: Search ~/Downloads if path not provided
- **Verify before creating**: Always confirm file list with user
- **Use docs-writer agent**: For all abstracts and descriptions (professional quality)
- **Follow JTBD guidelines**: Imperatives for procedures, noun phrases for concepts
- **Check existing files**: Never overwrite without explicit user confirmation
- **Reorganize carefully**: Maintain all existing content, just reorder per CSV
- **Wait for review**: Always ask user to review before committing

## Verification Commands

After running, verify:
```bash
# Check created assemblies
ls assemblies/builds-*.adoc

# Check created L2 sections
ls modules/ob-*.adoc

# Check created L3 topics
ls modules/{con,proc,ref}-*.adoc

# Verify CSV mapping matches structure
grep -r "include::modules" assemblies/
```

## Troubleshooting

- **CSV not found**: Provide explicit path or copy to ~/Downloads
- **Category not in CSV**: Check category spelling matches CSV exactly
- **File already exists**: Skill will skip and report, not overwrite
- **Build fails**: Check include paths and file references match created files
- **Abstract quality**: docs-writer agent creates professional descriptions; review and adjust if needed
