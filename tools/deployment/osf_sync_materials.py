#!/usr/bin/env python3
"""
OSF Material Sync Script
Intelligently syncs files to OSF, avoiding duplicates
"""

import os
import sys
from pathlib import Path
import requests
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

OSF_API_TOKEN = os.getenv('OSF_API_TOKEN')
OSF_API_BASE = 'https://api.osf.io/v2'

# Project structure
OSF_PROJECTS = {
    'main': '7nw8t',
    'theory': '3bzrh',
    'empirical': 'bcedg',
    'tools': 'g9t5v',
    'community': 'caem6',
}

# File upload mapping
UPLOAD_MANIFEST = {
    'theory': [
        'papers/drafts/ERC_Manifesto_arXiv.tex',
        'papers/drafts/RCT_arXiv.tex',
        'papers/drafts/IRIS_Gate_Methodology_arXiv.tex',
        'papers/drafts/CBD_TwoPathway_arXiv.tex',
        'papers/drafts/references.bib',
        'papers/published/RCT_arXiv.pdf',
        'papers/published/CBD_TwoPathway_arXiv.pdf',
        'osf/theory/OSF_PROJECT_DESCRIPTION.md',
        'osf/theory/OSF_PREREGISTRATION.md',
        'osf/theory/references.bib',
        'FIELDSCRIPT_SPEC.md',  # New computational primitive specification
    ],
    'empirical': [
        'docs/RELEASE_v0.2-discovery.md',
        'docs/methodology/METHODOLOGY_PAPER_V2.md',
        'docs/methodology/METHODOLOGY_PAPER_V2_SUPPLEMENTARY.md',
        'investigations/investigations/inversion_mechanism_20260102/complete_session_entropy_analysis.json',
    ],
    'tools': [
        'osf/tools/REPLICATION_GUIDE.md',
        'tools/entropy/measure_baseline_entropy.py',
        'tools/entropy/entropy_thermometer.py',
        'tools/entropy/train_mistral_lantern_mps.py',
        'requirements.txt',
    ],
    'community': [
        'CONTRIBUTING.md',
        'CODE_OF_CONDUCT.md',
        'README.md',
    ],
}

def get_headers():
    """Get authorization headers"""
    return {
        'Authorization': f'Bearer {OSF_API_TOKEN}',
    }

def get_existing_files(project_id: str) -> set:
    """
    Get list of files already uploaded to OSF component

    Returns:
        Set of filenames already on OSF
    """
    storage_url = f'{OSF_API_BASE}/nodes/{project_id}/files/osfstorage/'

    try:
        response = requests.get(storage_url, headers=get_headers())
        if response.status_code != 200:
            print(f"  ⚠️  Could not fetch file list: {response.status_code}")
            return set()

        data = response.json()
        files = data.get('data', [])

        # Extract filenames
        existing = set()
        for file_obj in files:
            if file_obj['attributes']['kind'] == 'file':
                existing.add(file_obj['attributes']['name'])

        return existing

    except Exception as e:
        print(f"  ⚠️  Error fetching file list: {e}")
        return set()

def upload_file(project_id: str, file_path: str) -> bool:
    """Upload a file to an OSF project's osfstorage"""
    repo_root = Path(__file__).parent.parent.parent
    full_path = repo_root / file_path

    if not full_path.exists():
        print(f"  ⚠️  File not found: {file_path}")
        return False

    # OSF files API upload URL
    filename = Path(file_path).name
    upload_url = f'https://files.osf.io/v1/resources/{project_id}/providers/osfstorage/'
    upload_params = {
        'kind': 'file',
        'name': filename,
    }

    try:
        with open(full_path, 'rb') as f:
            response = requests.put(
                upload_url,
                params=upload_params,
                data=f,
                headers=get_headers()
            )

        if response.status_code in [200, 201]:
            print(f"  ✅ Uploaded: {filename}")
            return True
        else:
            print(f"  ❌ Upload failed ({response.status_code}): {filename}")
            if response.status_code == 409:
                print(f"     (File may already exist)")
            else:
                print(f"     {response.text[:200]}")
            return False

    except Exception as e:
        print(f"  ❌ Error uploading {file_path}: {e}")
        return False

def sync_materials():
    """Sync materials to OSF, avoiding duplicates"""

    print("🌀 IRIS Gate → OSF Smart Sync")
    print("=" * 60)
    print()

    total_needed = 0
    already_uploaded = 0
    newly_uploaded = 0
    failed = 0

    for component, files in UPLOAD_MANIFEST.items():
        project_id = OSF_PROJECTS[component]
        print(f"📂 Component: {component.upper()} (ID: {project_id})")

        # Get existing files
        print(f"   Checking existing files...")
        existing_files = get_existing_files(project_id)
        print(f"   Found {len(existing_files)} file(s) already uploaded")

        if existing_files:
            print(f"   Existing: {', '.join(sorted(existing_files))}")
        print()

        # Process each file
        for file_path in files:
            filename = Path(file_path).name
            total_needed += 1

            if filename in existing_files:
                print(f"  ⏭️  Already exists: {filename}")
                already_uploaded += 1
            else:
                if upload_file(project_id, file_path):
                    newly_uploaded += 1
                else:
                    failed += 1

        print()

    print("=" * 60)
    print(f"📊 Sync Summary:")
    print(f"   Total files needed: {total_needed}")
    print(f"   ⏭️  Already uploaded: {already_uploaded}")
    print(f"   ✅ Newly uploaded: {newly_uploaded}")
    if failed > 0:
        print(f"   ❌ Failed: {failed}")
    print()
    print(f"🌐 View your project: https://osf.io/7nw8t/")

if __name__ == '__main__':
    sync_materials()
