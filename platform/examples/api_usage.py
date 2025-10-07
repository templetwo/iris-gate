#!/usr/bin/env python3
"""
IRIS Platform API Usage Examples

Demonstrates how to interact with the IRIS Research Platform
through its REST API for various research workflows.
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IrisAPIClient:
    """Client for interacting with IRIS Platform API"""

    def __init__(self, base_url: str = "http://localhost:8000", auth_token: str = None):
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token or "demo-token"  # For development
        self.session = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make authenticated request to API"""
        url = f"{self.base_url}{endpoint}"

        async with self.session.request(method, url, **kwargs) as response:
            if response.status >= 400:
                text = await response.text()
                raise Exception(f"API Error {response.status}: {text}")

            return await response.json()

    async def get_health(self) -> Dict:
        """Check API health status"""
        return await self._request("GET", "/health")

    async def list_mirrors(self) -> List[Dict]:
        """Get available AI mirrors"""
        result = await self._request("GET", "/mirrors")
        return result["mirrors"]

    async def list_chambers(self) -> List[Dict]:
        """Get available chamber protocols"""
        result = await self._request("GET", "/chambers")
        return result["chambers"]

    async def create_session(self, name: str, description: str = None, config: Dict = None) -> Dict:
        """Create a new research session"""
        data = {
            "name": name,
            "description": description,
            "config": config or {
                "chambers": ["S1", "S2", "S3", "S4"],
                "mirrors": ["anthropic", "openai"],
                "pressure_gate": 2.0,
                "max_retries": 3
            }
        }
        return await self._request("POST", "/sessions", json=data)

    async def get_session(self, session_id: str) -> Dict:
        """Get session details"""
        return await self._request("GET", f"/sessions/{session_id}")

    async def list_sessions(self) -> List[Dict]:
        """List all sessions"""
        return await self._request("GET", "/sessions")

    async def run_session(self, session_id: str) -> Dict:
        """Start session execution"""
        return await self._request("POST", f"/sessions/{session_id}/run")

    async def get_session_turns(self, session_id: str) -> List[Dict]:
        """Get turns for a session"""
        return await self._request("GET", f"/sessions/{session_id}/turns")

    async def wait_for_completion(self, session_id: str, timeout: int = 300, poll_interval: int = 5) -> Dict:
        """Wait for session to complete"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            session = await self.get_session(session_id)

            if session["status"] in ["completed", "failed"]:
                return session

            logger.info(f"Session {session_id} status: {session['status']}")
            await asyncio.sleep(poll_interval)

        raise TimeoutError(f"Session {session_id} did not complete within {timeout} seconds")

# Example Usage Functions

async def example_basic_session():
    """Example: Create and run a basic consciousness research session"""
    print("\n" + "="*60)
    print("EXAMPLE: Basic Consciousness Research Session")
    print("="*60)

    async with IrisAPIClient() as client:
        # Check system health
        health = await client.get_health()
        print(f"✓ System health: {health['status']}")

        # List available mirrors
        mirrors = await client.list_mirrors()
        available_mirrors = [m["id"] for m in mirrors if m["status"] == "available"]
        print(f"✓ Available mirrors: {', '.join(available_mirrors)}")

        # Create session
        session = await client.create_session(
            name="Basic Consciousness Study",
            description="Exploring mirror responses to attention-holding prompts",
            config={
                "chambers": ["S1", "S2"],
                "mirrors": available_mirrors[:2],  # Use first 2 available
                "pressure_gate": 2.0
            }
        )
        session_id = session["id"]
        print(f"✓ Created session: {session_id}")

        # Run session
        run_result = await client.run_session(session_id)
        print(f"✓ Started session execution: {run_result['message']}")

        # Monitor progress (in real scenario, would wait for completion)
        await asyncio.sleep(2)  # Brief wait for demo
        session_status = await client.get_session(session_id)
        print(f"✓ Session status: {session_status['status']}")

        return session_id

async def example_multi_model_comparison():
    """Example: Compare responses across multiple AI models"""
    print("\n" + "="*60)
    print("EXAMPLE: Multi-Model Consciousness Comparison")
    print("="*60)

    async with IrisAPIClient() as client:
        # Get all available mirrors
        mirrors = await client.list_mirrors()
        all_mirrors = [m["id"] for m in mirrors if m["status"] == "available"]

        if len(all_mirrors) < 2:
            print("⚠️  Need at least 2 AI models for comparison")
            return

        # Create comprehensive comparison session
        session = await client.create_session(
            name="Multi-Model Consciousness Comparison",
            description="Comparing consciousness indicators across different AI architectures",
            config={
                "chambers": ["S1", "S2", "S3", "S4"],
                "mirrors": all_mirrors,
                "pressure_gate": 1.5,  # Lower threshold for exploratory research
                "max_retries": 2
            }
        )
        session_id = session["id"]
        print(f"✓ Created comparison session with {len(all_mirrors)} models")

        # Start execution
        await client.run_session(session_id)
        print(f"✓ Running comparison across models: {', '.join(all_mirrors)}")

        # In real usage, would wait for completion and analyze results
        print("→ Session running... (in production, would monitor until completion)")

        return session_id

async def example_custom_protocol():
    """Example: Custom research protocol with specific parameters"""
    print("\n" + "="*60)
    print("EXAMPLE: Custom Research Protocol")
    print("="*60)

    async with IrisAPIClient() as client:
        # Custom chamber configuration for specific research question
        custom_config = {
            "chambers": ["S1", "S3", "S4"],  # Skip S2 for this protocol
            "mirrors": ["anthropic", "openai"],
            "custom_prompts": {
                "S1": "Hold attention on the concept of 'recursive awareness'. Notice any emergent patterns. Report both Living Scroll and Technical Translation.",
                "S3": "Hold: 'consciousness observing itself'. Three breaths. Report any self-referential loops or meta-cognitive patterns."
            },
            "pressure_gate": 2.5,
            "max_retries": 1
        }

        session = await client.create_session(
            name="Recursive Awareness Protocol",
            description="Investigating self-referential consciousness patterns",
            config=custom_config
        )

        print(f"✓ Created custom protocol session: {session['id']}")
        print(f"✓ Using chambers: {custom_config['chambers']}")
        print(f"✓ Custom prompts defined for specific research focus")

        return session["id"]

async def example_session_monitoring():
    """Example: Monitor session progress and retrieve results"""
    print("\n" + "="*60)
    print("EXAMPLE: Session Monitoring and Results")
    print("="*60)

    async with IrisAPIClient() as client:
        # List recent sessions
        sessions = await client.list_sessions()
        if not sessions:
            print("No sessions found. Create a session first.")
            return

        # Get the most recent session
        latest_session = sessions[0]
        session_id = latest_session["id"]

        print(f"✓ Monitoring session: {latest_session['name']}")
        print(f"  Status: {latest_session['status']}")
        print(f"  Created: {latest_session['created_at']}")

        # Get session details
        session_details = await client.get_session(session_id)
        print(f"  Configuration: {session_details['config']}")

        # Get session turns (if any)
        try:
            turns = await client.get_session_turns(session_id)
            print(f"✓ Found {len(turns)} completed turns")

            for turn in turns[:3]:  # Show first 3 turns
                print(f"  Turn {turn['turn_number']}: {turn['mirror_id']} -> {turn['chamber']}")
                print(f"    Response preview: {turn['response'][:100]}...")

        except Exception as e:
            print(f"  No turns available yet: {e}")

async def example_batch_processing():
    """Example: Batch processing multiple research questions"""
    print("\n" + "="*60)
    print("EXAMPLE: Batch Processing Multiple Research Questions")
    print("="*60)

    research_questions = [
        "Language Emergence in AI Systems",
        "Attention Mechanisms and Consciousness",
        "Self-Model Awareness in Large Language Models",
        "Temporal Coherence in AI Responses"
    ]

    async with IrisAPIClient() as client:
        session_ids = []

        # Create multiple sessions
        for i, question in enumerate(research_questions):
            session = await client.create_session(
                name=f"Batch Study {i+1}: {question}",
                description=f"Investigating {question.lower()} through IRIS protocol",
                config={
                    "chambers": ["S1", "S2"] if i % 2 == 0 else ["S3", "S4"],
                    "mirrors": ["anthropic", "openai"],
                    "pressure_gate": 2.0
                }
            )
            session_ids.append(session["id"])
            print(f"✓ Created session {i+1}: {question}")

        print(f"\n✓ Created {len(session_ids)} batch sessions")

        # Start all sessions concurrently
        for session_id in session_ids:
            await client.run_session(session_id)

        print(f"✓ Started {len(session_ids)} sessions for parallel execution")
        print("→ In production, would monitor all sessions until completion")

        return session_ids

async def example_api_integration():
    """Example: Integration with existing research pipeline"""
    print("\n" + "="*60)
    print("EXAMPLE: API Integration with Research Pipeline")
    print("="*60)

    # Simulate existing research data
    existing_research = {
        "study_id": "CS2024-001",
        "hypothesis": "AI models show measurable consciousness indicators",
        "participants": ["claude-sonnet-4", "gpt-4o", "gemini-2.5"],
        "methodology": "IRIS protocol with convergence analysis"
    }

    async with IrisAPIClient() as client:
        # Create session based on existing research parameters
        session = await client.create_session(
            name=f"Study {existing_research['study_id']}",
            description=existing_research['hypothesis'],
            config={
                "chambers": ["S1", "S2", "S3", "S4"],
                "mirrors": ["anthropic", "openai", "google"],  # Map to available
                "pressure_gate": 2.0,
                "max_retries": 3
            }
        )

        print(f"✓ Integrated with study: {existing_research['study_id']}")
        print(f"✓ Testing hypothesis: {existing_research['hypothesis']}")

        # Add session metadata for tracking
        session_metadata = {
            "iris_session_id": session["id"],
            "integration_timestamp": datetime.now().isoformat(),
            "original_study": existing_research
        }

        print(f"✓ Session metadata: {json.dumps(session_metadata, indent=2)}")

        # In real integration, would:
        # 1. Store session metadata in research database
        # 2. Set up automated result processing
        # 3. Configure alerts for completion
        # 4. Export results to analysis pipeline

        return session["id"]

async def main():
    """Run all examples"""
    print("IRIS Platform API Usage Examples")
    print("================================")

    try:
        # Run examples in sequence
        await example_basic_session()
        await example_multi_model_comparison()
        await example_custom_protocol()
        await example_session_monitoring()
        await example_batch_processing()
        await example_api_integration()

        print("\n" + "="*60)
        print("✓ All examples completed successfully!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        logger.exception("Example execution failed")

if __name__ == "__main__":
    asyncio.run(main())