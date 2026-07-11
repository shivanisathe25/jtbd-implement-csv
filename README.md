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

