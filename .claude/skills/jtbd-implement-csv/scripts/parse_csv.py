#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Parse JTBD CSV mapping file and generate structured update plan.

Outputs JSON with:
- categories: list of available categories
- files: list of file update operations with current vs CSV titles
- missing_files: list of files that need to be created
"""

import csv
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional


def read_csv_mapping(csv_path: str) -> List[Dict]:
    """Read CSV and extract job mappings.

    Supports two column name formats:
    Format 1: L1 Job Title, L2 Section Title, L3 Topic Title, Content Type
    Format 2: Level 1 (Jobs), Level 2 (Jobs), Level 3 (Jobs or Topics), Topic (H2)

    Handles CSVs with instruction/header rows by finding the row with 'Category' column.
    """
    mappings = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        # Read all lines to find the actual header row
        lines = list(csv.reader(f))

        # Find the row that contains 'Category' (the actual header)
        header_idx = None
        for idx, line in enumerate(lines):
            if line and 'Category' in line:
                header_idx = idx
                break

        if header_idx is None:
            return mappings  # No valid header found

        # Use the found header row
        headers = lines[header_idx]
        data_rows = lines[header_idx + 1:]

        # Create a DictReader-like structure
        for row_data in data_rows:
            if len(row_data) < len(headers):
                # Pad short rows with empty strings
                row_data.extend([''] * (len(headers) - len(row_data)))
            row = dict(zip(headers, row_data))

            # Skip empty rows
            if not any(row.values()):
                continue

            # Support both column name formats
            category = row.get('Category', '').strip()

            # L1 - try both formats
            l1_job = row.get('L1 Job Title', '').strip()
            if not l1_job:
                l1_job = row.get('Level 1 (Jobs)', '').strip()

            # L2 - try both formats
            l2_section = row.get('L2 Section Title', '').strip()
            if not l2_section:
                l2_section = row.get('Level 2 (Jobs)', '').strip()

            # L3 - try both formats
            l3_topic = row.get('L3 Topic Title', '').strip()
            if not l3_topic:
                l3_topic = row.get('Level 3 (Jobs or Topics)', '').strip()
            if not l3_topic:
                l3_topic = row.get('Topic (H2)', '').strip()

            # File path
            file_path = row.get('Full .adoc filename path', '').strip()

            # Content Type - try both formats
            content_type = row.get('Content Type', '').strip().upper()
            if not content_type:
                # Infer from file path if not provided
                if file_path.startswith('assemblies/'):
                    content_type = 'ASSEMBLY'
                elif 'proc-' in file_path or 'procedure' in file_path.lower():
                    content_type = 'PROCEDURE'
                elif 'con-' in file_path or 'concept' in file_path.lower():
                    content_type = 'CONCEPT'
                elif 'ref-' in file_path or 'reference' in file_path.lower():
                    content_type = 'REFERENCE'
                else:
                    content_type = 'CONCEPT'  # default

            mappings.append({
                'category': category,
                'l1_job': l1_job,
                'l2_section': l2_section,
                'l3_topic': l3_topic,
                'file_path': file_path,
                'content_type': content_type,
            })

    return mappings


def extract_title_from_file(file_path: str) -> Optional[str]:
    """Extract the title line (starting with =) from an AsciiDoc file."""
    if not os.path.exists(file_path):
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('= '):
                    return line[2:].strip()
    except Exception:
        return None

    return None


def extract_content_type_from_file(file_path: str) -> Optional[str]:
    """Extract content type from :_mod-docs-content-type: attribute."""
    if not os.path.exists(file_path):
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if ':_mod-docs-content-type:' in line:
                    parts = line.split(':_mod-docs-content-type:')
                    if len(parts) > 1:
                        return parts[1].strip().upper()
    except Exception:
        return None

    return None


def validate_title_format(title: str, content_type: str) -> Dict:
    """
    Validate title matches the expected format for content type.

    Returns:
        dict with 'valid' (bool), 'message' (str), 'suggestion' (str or None)
    """
    if not title:
        return {'valid': False, 'message': 'Empty title', 'suggestion': None}

    # Basic validation rules
    if content_type == 'PROCEDURE':
        # Should start with imperative verb
        imperative_verbs = ['configure', 'install', 'create', 'set', 'deploy', 'enable',
                           'disable', 'update', 'add', 'remove', 'delete', 'manage',
                           'monitor', 'view', 'edit', 'customize', 'optimize']

        first_word = title.lower().split()[0] if title.split() else ''
        if first_word not in imperative_verbs:
            return {
                'valid': False,
                'message': 'Should start with imperative verb',
                'suggestion': f'Consider: "Configure {title.lower()}" or "Set up {title.lower()}"'
            }

    elif content_type == 'CONCEPT':
        # Should be noun phrase (not starting with imperative verb)
        imperative_starters = ['configure', 'install', 'create', 'set', 'deploy',
                              'configuring', 'installing', 'creating', 'setting']
        first_word = title.lower().split()[0] if title.split() else ''
        if first_word in imperative_starters:
            return {
                'valid': False,
                'message': 'Should be noun phrase, not imperative verb',
                'suggestion': f'Consider: "{title.replace("Configuring", "Configuration").replace("Installing", "Installation")}"'
            }

    return {'valid': True, 'message': 'Valid format', 'suggestion': None}


def check_file_status(mappings: List[Dict], categories: List[str], repo_root: str) -> Dict:
    """
    Check which files exist, compare titles, and identify missing files.

    Args:
        mappings: List of CSV row dicts
        categories: List of category names to process (or ['all'] for all)
        repo_root: Root directory of the documentation repo

    Returns:
        dict with 'categories', 'files', 'missing_files'
    """
    result = {
        'categories': [],
        'files': [],
        'missing_files': []
    }

    # Get unique categories from CSV
    all_categories = sorted(set(m['category'] for m in mappings if m['category']))
    result['categories'] = all_categories

    # Filter mappings by requested categories
    if 'all' in [c.lower() for c in categories]:
        filtered_mappings = mappings
    else:
        filtered_mappings = [m for m in mappings if m['category'] in categories]

    for mapping in filtered_mappings:
        file_path = mapping['file_path']
        if not file_path:
            continue

        # Construct full path
        full_path = os.path.join(repo_root, file_path)

        # Determine which title from CSV to use (L1, L2, or L3)
        csv_title = None
        level = None

        if mapping['l3_topic']:
            csv_title = mapping['l3_topic']
            level = 'L3'
        elif mapping['l2_section']:
            csv_title = mapping['l2_section']
            level = 'L2'
        elif mapping['l1_job']:
            csv_title = mapping['l1_job']
            level = 'L1'

        if not csv_title:
            continue

        # Check if file exists
        if os.path.exists(full_path):
            current_title = extract_title_from_file(full_path)
            content_type = extract_content_type_from_file(full_path)

            # Validate title format
            validation = validate_title_format(csv_title, content_type or mapping['content_type'])

            needs_update = current_title != csv_title

            result['files'].append({
                'path': file_path,
                'full_path': full_path,
                'category': mapping['category'],
                'current_title': current_title or '(not found)',
                'csv_title': csv_title,
                'level': level,
                'content_type': content_type or mapping['content_type'],
                'needs_update': needs_update,
                'validation': validation
            })
        else:
            # File is missing
            result['missing_files'].append({
                'path': file_path,
                'full_path': full_path,
                'category': mapping['category'],
                'csv_title': csv_title,
                'level': level,
                'content_type': mapping['content_type']
            })

    return result


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print(json.dumps({
            'error': 'Usage: parse_csv.py <csv_path> <repo_root> [category1,category2,...]'
        }))
        sys.exit(1)

    csv_path = sys.argv[1]
    repo_root = sys.argv[2]
    categories = sys.argv[3].split(',') if len(sys.argv) > 3 else ['all']

    # Validate inputs
    if not os.path.exists(csv_path):
        print(json.dumps({
            'error': f'CSV file not found: {csv_path}'
        }))
        sys.exit(1)

    if not os.path.isdir(repo_root):
        print(json.dumps({
            'error': f'Repository root not found: {repo_root}'
        }))
        sys.exit(1)

    # Parse CSV
    try:
        mappings = read_csv_mapping(csv_path)
    except Exception as e:
        print(json.dumps({
            'error': f'Failed to parse CSV: {str(e)}'
        }))
        sys.exit(1)

    # Check file status
    result = check_file_status(mappings, categories, repo_root)

    # Output JSON
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
