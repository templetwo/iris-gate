#!/usr/bin/env python3
"""
OSF Material Upload Script
Uploads IRIS Gate papers, data, and documentation to OSF components
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

# Project structure (from osf_test_connection.py output)
OSF_PROJECTS = {
    'main': '7nw8t',  # Entropic Relational Computing: The Universal Alignment Attractor
    'theory': '3bzrh',  # Component 1: Theoretical Framework
    'empirical': 'bcedg',  # Component 2: Empirical Findings
    'tools': 'g9t5v',  # Component 3: Replication Protocol & Tools
    'community': 'caem6',  # Component 4: Community Replication Registry
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

def upload_file(project_id: str, file_path: str) -> bool:
    """
    Upload a file to an OSF project's osfstorage

    Args:
        project_id: OSF project/component ID
        file_path: Relative path to file from repo root

    Returns:
        True if successful, False otherwise
    """
    repo_root = Path(__file__).parent.parent.parent
    full_path = repo_root / file_path

    if not full_path.exists():
        print(f"  ⚠️  File not found: {file_path}")
        return False

    # Get upload URL from OSF storage
    storage_url = f'{OSF_API_BASE}/nodes/{project_id}/files/osfstorage/'

    try:
        # Get the upload endpoint
        storage_response = requests.get(storage_url, headers=get_headers())
        if storage_response.status_code != 200:
            print(f"  ❌ Failed to get storage info: {storage_response.status_code}")
            return False

        upload_url = storage_response.json()['data']['relationships']['upload']['links']['related']['href']

        # Prepare file for upload
        filename = Path(file_path).name
        upload_params = {
            'kind': 'file',
            'name': filename,
        }

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
            print(f"     {response.text[:200]}")
            return False

    except Exception as e:
        print(f"  ❌ Error uploading {file_path}: {e}")
        return False

def upload_all_materials(dry_run=False):
    """Upload all materials to OSF components"""

    print("🌀 IRIS Gate → OSF Material Upload")
    print("=" * 60)
    print()

    if dry_run:
        print("🔍 DRY RUN MODE - No files will be uploaded")
        print()

    total_files = sum(len(files) for files in UPLOAD_MANIFEST.values())
    uploaded = 0
    skipped = 0
    failed = 0

    for component, files in UPLOAD_MANIFEST.items():
        project_id = OSF_PROJECTS[component]
        print(f"📂 Component: {component.upper()} (ID: {project_id})")
        print(f"   {len(files)} file(s) to upload")
        print()

        for file_path in files:
            if dry_run:
                repo_root = Path(__file__).parent.parent.parent
                if (repo_root / file_path).exists():
                    print(f"  📄 Would upload: {file_path}")
                    uploaded += 1
                else:
                    print(f"  ⚠️  Missing: {file_path}")
                    skipped += 1
            else:
                if upload_file(project_id, file_path):
                    uploaded += 1
                else:
                    failed += 1

        print()

    print("=" * 60)
    print(f"✅ Uploaded: {uploaded}/{total_files}")
    if skipped > 0:
        print(f"⚠️  Skipped: {skipped}")
    if failed > 0:
        print(f"❌ Failed: {failed}")
    print()

    if not dry_run:
        print("🌐 View your project: https://osf.io/7nw8t/")

if __name__ == '__main__':
    # Run in dry-run mode by default for safety
    dry_run = '--execute' not in sys.argv

    if dry_run:
        print("ℹ️  Running in DRY RUN mode. Use --execute to actually upload files.")
        print()

    upload_all_materials(dry_run=dry_run)
