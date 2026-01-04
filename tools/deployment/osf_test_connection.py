#!/usr/bin/env python3
"""
OSF API Connection Test
Tests authentication and retrieves user profile information
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

def test_connection():
    """Test OSF API connection and authentication"""

    if not OSF_API_TOKEN:
        print("❌ ERROR: OSF_API_TOKEN not found in .env file")
        return False

    print("🔑 OSF API Token found")
    print(f"   Token: {OSF_API_TOKEN[:10]}...{OSF_API_TOKEN[-6:]}")
    print()

    # Test authentication by fetching user profile
    headers = {
        'Authorization': f'Bearer {OSF_API_TOKEN}',
        'Content-Type': 'application/vnd.api+json'
    }

    try:
        print("🌐 Testing connection to OSF API...")
        response = requests.get(f'{OSF_API_BASE}/users/me/', headers=headers)

        if response.status_code == 200:
            user_data = response.json()['data']
            attributes = user_data['attributes']

            print("✅ Authentication successful!")
            print()
            print("User Profile:")
            print(f"  Name: {attributes.get('full_name', 'N/A')}")
            print(f"  OSF ID: {user_data['id']}")
            print(f"  Timezone: {attributes.get('timezone', 'N/A')}")
            print(f"  Locale: {attributes.get('locale', 'N/A')}")
            print()

            # List user's projects
            print("📁 Fetching your OSF projects...")
            projects_response = requests.get(f'{OSF_API_BASE}/users/me/nodes/', headers=headers)

            if projects_response.status_code == 200:
                projects = projects_response.json()['data']
                print(f"   Found {len(projects)} project(s)")

                if projects:
                    print()
                    print("Existing projects:")
                    for project in projects[:5]:  # Show first 5
                        proj_attrs = project['attributes']
                        print(f"  • {proj_attrs['title']}")
                        print(f"    ID: {project['id']}")
                        print(f"    Created: {proj_attrs['date_created'][:10]}")
                        print(f"    Public: {proj_attrs['public']}")
                        print()

            return True

        elif response.status_code == 401:
            print("❌ Authentication failed: Invalid token")
            print("   Please verify your OSF_API_TOKEN in .env")
            return False
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)
