#!/usr/bin/env python3
"""
Test local IRIS-Bridge API health endpoints
"""
import sys
import httpx
import argparse
from datetime import datetime

def test_health(port: int, token: str):
    """Test health endpoint"""
    url = f"http://localhost:{port}/health"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🔍 Testing API on port {port}")
    print(f"URL: {url}")
    print(f"Time: {datetime.utcnow().isoformat()}")
    
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            print(f"✅ API HEALTHY")
            print(f"Response: {data}")
            return True
    except httpx.ConnectError:
        print(f"❌ FAILED: Cannot connect to port {port} (service not running?)")
        return False
    except httpx.HTTPStatusError as e:
        print(f"❌ FAILED: HTTP {e.response.status_code}")
        print(f"Response: {e.response.text}")
        return False
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8788, help="Port to test")
    parser.add_argument("--token", default="iris-bridge-autonomous-sync-2025", help="Auth token")
    args = parser.parse_args()
    
    success = test_health(args.port, args.token)
    sys.exit(0 if success else 1)
