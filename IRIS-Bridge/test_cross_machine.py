#!/usr/bin/env python3
"""
Test cross-machine IRIS-Bridge connectivity via Tailscale
"""
import sys
import httpx
import argparse
from datetime import datetime

def test_remote_health(host: str, port: int, token: str):
    """Test remote machine's API health endpoint"""
    url = f"http://{host}:{port}/health"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🌐 Testing Remote API")
    print(f"URL: {url}")
    print(f"Time: {datetime.utcnow().isoformat()}")
    
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            print(f"✅ REMOTE API HEALTHY")
            print(f"Response: {data}")
            return True
    except httpx.ConnectTimeout:
        print(f"❌ FAILED: Connection timeout (firewall? service not running?)")
        return False
    except httpx.ConnectError:
        print(f"❌ FAILED: Cannot connect to {host}:{port}")
        print("Troubleshooting:")
        print("  - Check if remote service is running")
        print("  - Verify Tailscale connection")
        print("  - Check firewall rules")
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
    parser.add_argument("--host", default="100.72.59.69", help="Remote host (Tailscale IP)")
    parser.add_argument("--port", type=int, default=8787, help="Remote port")
    parser.add_argument("--token", default="iris-bridge-autonomous-sync-2025", help="Auth token")
    args = parser.parse_args()
    
    success = test_remote_health(args.host, args.port, args.token)
    sys.exit(0 if success else 1)
