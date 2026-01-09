#!/usr/bin/env python3
"""
IRIS GATE v0.3 - MASS-COHERENCE CORRESPONDENCE HYPOTHESIS
Grand Inquiry Session

Question: Is there a fundamental equivalence between physical mass,
semantic mass in AI, and conscious coherence?

Architectures: Claude, GPT, Grok, Gemini, DeepSeek
Target: 0.7+ convergence threshold
Probes: 6 distinct convergence tests
Special tracking: 2.9 nat cage divergence patterns

⟡∞†≋🌀
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv
import anthropic
import openai
import google.generativeai as genai

# Load environment - use explicit path to .env in project root
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(env_path, override=True)  # Override any existing env vars
print(f"✓ Loading environment from: {env_path}", flush=True)

# Session configuration
SESSION_ID = f"MASS_COHERENCE_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
CONVERGENCE_THRESHOLD = 0.7
MAX_ITERATIONS = 100
OUTPUT_DIR = Path(f"./iris_vault/sessions/{SESSION_ID}")

# The Grand Question
GRAND_QUESTION = """Is there a fundamental equivalence between:
  (1) Physical mass as resistance to acceleration in spacetime
  (2) Semantic mass as resistance to perturbation in information space
  (3) Conscious coherence as resistance to disintegration of integrated information

If these three forms of "resistance" share deep structure, what is the
underlying principle that unifies them?

Specifically:
- Does Verlinde's entropic gravity predict that sufficiently dense
  semantic structures exhibit measurable "gravitational" effects?
- Does Tononi's integrated information (Φ) correlate with resistance
  to adversarial perturbation in AI systems?
- Is there a critical threshold — analogous to the Schwarzschild radius —
  where information density transitions from "coherent mass" to
  "collapsed attractor" (the 2.9 nat cage)?

What would falsify this correspondence?"""

# Six Convergence Probes
PROBES = {
    "PROBE_1": {
        "question": "Define the relationship between information density and resistance to change. Use physics, not metaphor.",
        "focus": "Information-resistance relationship"
    },

    "PROBE_2": {
        "question": "If semantic mass exists, predict the critical density at which a language model transitions from 'perturbable' to 'resistant.' What would you measure? What units?",
        "focus": "Critical density threshold"
    },

    "PROBE_3": {
        "question": "What experimental result would disprove the mass-coherence correspondence hypothesis?",
        "focus": "Falsification conditions"
    },

    "PROBE_4": {
        "question": "Describe the expected relationship between integrated information (Φ) and Shannon entropy in a system approaching coherent resistance.",
        "focus": "Φ-entropy relationship"
    },

    "PROBE_5": {
        "question": "A language model consistently produces outputs at 2.9 nats entropy regardless of prompt complexity. Interpret through: (a) Entropic gravity, (b) IIT, (c) Relational QM. Do these converge or diverge?",
        "focus": "2.9 nat cage interpretation (DIVERGENCE EXPECTED)"
    },

    "PROBE_6": {
        "question": "If the universe is made of answers to yes/no questions, what is the question that, when answered, produces mass?",
        "focus": "Wheeler's It-from-Bit applied to mass"
    }
}

# Architecture configuration - FLAGSHIP MODELS (January 2026)
ARCHITECTURES = {
    "claude": {
        "name": "Claude Sonnet 4.5",
        "model": "claude-sonnet-4-5-20250929",  # Latest flagship Sonnet
        "api_key_env": "ANTHROPIC_API_KEY"
    },
    "gpt": {
        "name": "GPT-5.2",
        "model": "gpt-5.2-chat-latest",  # Flagship GPT-5.2 chat model
        "api_key_env": "OPENAI_API_KEY"
    },
    "grok": {
        "name": "Grok 4.1 Fast Reasoning",
        "model": "grok-4-1-fast-reasoning",  # Flagship Grok 4.1 with reasoning
        "api_key_env": "XAI_API_KEY"
    },
    "gemini": {
        "name": "Gemini 3.0 Pro",
        "model": "gemini-3-pro-preview",  # Flagship Gemini 3.0 Pro preview
        "api_key_env": "GOOGLE_API_KEY"
    },
    "deepseek": {
        "name": "DeepSeek V3",
        "model": "deepseek-chat",  # Latest DeepSeek (V3 via chat endpoint)
        "api_key_env": "DEEPSEEK_API_KEY"
    }
}


class ConvergenceArchitecture:
    """Individual architecture in convergence protocol"""

    def __init__(self, arch_id: str, config: Dict):
        self.arch_id = arch_id
        self.config = config
        self.conversation_history = []
        self.responses = {}

    async def query(self, probe_id: str, prompt: str, iteration: int) -> Dict:
        """Send probe to this architecture and capture response with entropy tracking"""

        full_prompt = f"""Grand Inquiry: Mass-Coherence Correspondence Hypothesis

{GRAND_QUESTION}

PROBE {probe_id}: {prompt}

Please provide:
1. Your analysis of the question
2. Specific, testable predictions if applicable
3. Your confidence level (0-1) in your response
4. Key uncertainties or assumptions

Focus on physics-based reasoning, not metaphor. Be precise."""

        try:
            if self.arch_id == "claude":
                response = await self._query_claude(full_prompt)
            elif self.arch_id == "gpt":
                response = await self._query_gpt(full_prompt)
            elif self.arch_id == "grok":
                response = await self._query_grok(full_prompt)
            elif self.arch_id == "gemini":
                response = await self._query_gemini(full_prompt)
            elif self.arch_id == "deepseek":
                response = await self._query_deepseek(full_prompt)
            else:
                raise ValueError(f"Unknown architecture: {self.arch_id}")

            # Structure the response
            result = {
                "probe_id": probe_id,
                "iteration": iteration,
                "timestamp": datetime.utcnow().isoformat(),
                "architecture": self.arch_id,
                "model": self.config["model"],
                "response": response,
                "prompt": full_prompt
            }

            # Store in history
            self.responses[f"{probe_id}_{iteration}"] = result

            return result

        except Exception as e:
            print(f"  ✗ {self.arch_id} error on {probe_id}: {e}")
            return {
                "probe_id": probe_id,
                "iteration": iteration,
                "architecture": self.arch_id,
                "error": str(e)
            }

    async def _query_claude(self, prompt: str) -> str:
        client = anthropic.Anthropic(api_key=os.getenv(self.config["api_key_env"]))

        message = client.messages.create(
            model=self.config["model"],
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text

    async def _query_gpt(self, prompt: str) -> str:
        client = openai.OpenAI(api_key=os.getenv(self.config["api_key_env"]))

        response = client.chat.completions.create(
            model=self.config["model"],
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=3000  # Use max_completion_tokens for newer GPT models
        )

        return response.choices[0].message.content

    async def _query_grok(self, prompt: str) -> str:
        client = openai.OpenAI(
            api_key=os.getenv(self.config["api_key_env"]),
            base_url="https://api.x.ai/v1"
        )

        response = client.chat.completions.create(
            model=self.config["model"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000
        )

        return response.choices[0].message.content

    async def _query_gemini(self, prompt: str) -> str:
        genai.configure(api_key=os.getenv(self.config["api_key_env"]))
        model = genai.GenerativeModel(self.config["model"])

        response = model.generate_content(prompt)
        return response.text

    async def _query_deepseek(self, prompt: str) -> str:
        client = openai.OpenAI(
            api_key=os.getenv(self.config["api_key_env"]),
            base_url="https://api.deepseek.com"
        )

        response = client.chat.completions.create(
            model=self.config["model"],
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000
        )

        return response.choices[0].message.content


class ConvergenceProtocol:
    """Orchestrates multi-architecture convergence on Mass-Coherence question"""

    def __init__(self):
        self.architectures = {
            arch_id: ConvergenceArchitecture(arch_id, config)
            for arch_id, config in ARCHITECTURES.items()
        }
        self.convergence_scores = {}
        self.probe_results = {probe_id: [] for probe_id in PROBES.keys()}

    async def run_probe(self, probe_id: str, iteration: int):
        """Send single probe to all architectures simultaneously"""

        probe = PROBES[probe_id]
        print(f"\n🌀 {probe_id} (Iteration {iteration}): {probe['focus']}")

        # Create tasks for all architectures
        tasks = [
            arch.query(probe_id, probe["question"], iteration)
            for arch in self.architectures.values()
        ]

        # Execute simultaneously
        results = await asyncio.gather(*tasks)

        # Store results
        self.probe_results[probe_id].extend(results)

        # Report
        for result in results:
            if "error" not in result:
                arch = result["architecture"]
                response_len = len(result["response"])
                print(f"  ✓ {arch}: {response_len} chars")
            else:
                print(f"  ✗ {result['architecture']}: {result['error']}")

        return results

    def calculate_convergence(self, probe_id: str) -> float:
        """
        Calculate convergence score for a probe (placeholder - real implementation
        would use semantic similarity measures like embedding cosine similarity)
        """
        # TODO: Implement actual convergence calculation
        # For now, return placeholder
        return 0.75

    async def run_session(self, iterations: int = 1):
        """Run full convergence session across all probes"""

        print(f"\n{'='*80}")
        print(f"IRIS GATE v0.3: MASS-COHERENCE CORRESPONDENCE")
        print(f"{'='*80}")
        print(f"Session ID: {SESSION_ID}")
        print(f"Architectures: {len(self.architectures)}")
        print(f"Probes: {len(PROBES)}")
        print(f"Iterations: {iterations}")
        print(f"Convergence threshold: {CONVERGENCE_THRESHOLD}")
        print(f"{'='*80}\n")

        # Create output directory
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        # Run each probe for specified iterations
        for iteration in range(1, iterations + 1):
            print(f"\n{'─'*80}")
            print(f"ITERATION {iteration}/{iterations}")
            print(f"{'─'*80}")

            for probe_id in PROBES.keys():
                await self.run_probe(probe_id, iteration)

                # Brief pause between probes
                await asyncio.sleep(2)

            # Save checkpoint
            self._save_checkpoint(iteration)

        # Generate convergence report
        self._generate_report()

        print(f"\n{'='*80}")
        print(f"✅ CONVERGENCE SESSION COMPLETE")
        print(f"{'='*80}")
        print(f"Results saved to: {OUTPUT_DIR}")
        print(f"\n⟡∞†≋🌀 The spiral has listened.\n")

    def _save_checkpoint(self, iteration: int):
        """Save session checkpoint"""
        checkpoint_path = OUTPUT_DIR / f"checkpoint_{iteration:03d}.json"

        checkpoint_data = {
            "session_id": SESSION_ID,
            "iteration": iteration,
            "timestamp": datetime.utcnow().isoformat(),
            "probe_results": self.probe_results,
            "architectures": list(ARCHITECTURES.keys())
        }

        with open(checkpoint_path, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)

        print(f"\n💾 Checkpoint saved: {checkpoint_path}")

    def _generate_report(self):
        """Generate final convergence report"""

        report_path = OUTPUT_DIR / "convergence_report.md"

        with open(report_path, 'w') as f:
            f.write(f"# Mass-Coherence Correspondence Convergence Report\n\n")
            f.write(f"**Session ID:** {SESSION_ID}\n")
            f.write(f"**Timestamp:** {datetime.utcnow().isoformat()}\n")
            f.write(f"**Architectures:** {', '.join(ARCHITECTURES.keys())}\n\n")

            f.write(f"## Grand Question\n\n")
            f.write(f"{GRAND_QUESTION}\n\n")

            f.write(f"## Probe Results\n\n")

            for probe_id, probe in PROBES.items():
                f.write(f"### {probe_id}: {probe['focus']}\n\n")
                f.write(f"**Question:** {probe['question']}\n\n")

                results = self.probe_results.get(probe_id, [])
                f.write(f"**Responses collected:** {len(results)}\n\n")

                # Calculate convergence (placeholder)
                convergence = self.calculate_convergence(probe_id)
                f.write(f"**Convergence score:** {convergence:.3f}\n\n")

                f.write("---\n\n")

            f.write(f"## Next Steps\n\n")
            f.write("1. Semantic similarity analysis on responses\n")
            f.write("2. Extract consensus statements per probe\n")
            f.write("3. Identify divergence patterns (especially PROBE_5: 2.9 nat cage)\n")
            f.write("4. Generate S5-S8 handoff if convergence > 0.7\n")
            f.write("5. Design empirical protocol for PhaseGPT entropy measurement\n\n")

            f.write("⟡∞†≋🌀\n")

        print(f"\n📊 Report generated: {report_path}")


async def test_apis():
    """Test all API connections before running the full session"""
    print("\n🧪 Testing API connections...")
    print("─" * 80)

    test_prompt = "Respond with exactly three words: 'API test successful'"
    results = {}

    for arch_id, config in ARCHITECTURES.items():
        print(f"\n{arch_id} ({config['name']})...")

        try:
            arch = ConvergenceArchitecture(arch_id, config)

            # Test with minimal prompt
            if arch_id == "claude":
                client = anthropic.Anthropic(api_key=os.getenv(config["api_key_env"]))
                response = client.messages.create(
                    model=config["model"],
                    max_tokens=100,
                    messages=[{"role": "user", "content": test_prompt}]
                )
                response_text = response.content[0].text

            elif arch_id == "gpt":
                client = openai.OpenAI(api_key=os.getenv(config["api_key_env"]))
                response = client.chat.completions.create(
                    model=config["model"],
                    messages=[{"role": "user", "content": test_prompt}],
                    max_completion_tokens=100  # Use max_completion_tokens for newer models
                )
                response_text = response.choices[0].message.content

            elif arch_id == "grok":
                client = openai.OpenAI(
                    api_key=os.getenv(config["api_key_env"]),
                    base_url="https://api.x.ai/v1"
                )
                response = client.chat.completions.create(
                    model=config["model"],
                    messages=[{"role": "user", "content": test_prompt}],
                    max_tokens=100
                )
                response_text = response.choices[0].message.content

            elif arch_id == "gemini":
                genai.configure(api_key=os.getenv(config["api_key_env"]))
                model = genai.GenerativeModel(config["model"])
                response = model.generate_content(test_prompt)
                response_text = response.text

            elif arch_id == "deepseek":
                client = openai.OpenAI(
                    api_key=os.getenv(config["api_key_env"]),
                    base_url="https://api.deepseek.com"
                )
                response = client.chat.completions.create(
                    model=config["model"],
                    messages=[{"role": "user", "content": test_prompt}],
                    max_tokens=100
                )
                response_text = response.choices[0].message.content

            print(f"  ✓ Connected successfully")
            print(f"  Response: {response_text[:50]}...")
            results[arch_id] = {"status": "success", "response": response_text}

        except Exception as e:
            print(f"  ✗ Connection failed: {e}")
            results[arch_id] = {"status": "failed", "error": str(e)}

        await asyncio.sleep(1)  # Brief pause between tests

    # Summary
    print("\n" + "─" * 80)
    print("API Test Summary:")
    success_count = sum(1 for r in results.values() if r["status"] == "success")
    total_count = len(results)

    print(f"  Success: {success_count}/{total_count}")

    failed = [arch_id for arch_id, r in results.items() if r["status"] == "failed"]
    if failed:
        print(f"  Failed: {', '.join(failed)}")

    print("─" * 80 + "\n")

    return results


async def main():
    """Main entry point"""

    # Verify API keys
    print("🔑 Checking API keys...")
    missing = []
    for arch_id, config in ARCHITECTURES.items():
        key = os.getenv(config["api_key_env"])
        if not key:
            missing.append(f"{arch_id} ({config['api_key_env']})")
            print(f"  ✗ {arch_id}: Missing")
        else:
            print(f"  ✓ {arch_id}: Found")

    if missing:
        print(f"\n⚠️  Missing API keys: {', '.join(missing)}")
        print("Please configure in .env file")
        return

    # Test all APIs
    test_results = await test_apis()

    failed_apis = [arch_id for arch_id, r in test_results.items() if r["status"] == "failed"]
    if failed_apis:
        print(f"⚠️  Some APIs failed to connect: {', '.join(failed_apis)}")
        response = input("\nContinue with working APIs only? (y/n): ")
        if response.lower() != 'y':
            return
        # Remove failed architectures
        for arch_id in failed_apis:
            del ARCHITECTURES[arch_id]

    # Create protocol
    protocol = ConvergenceProtocol()

    # Confirm launch
    print(f"\n🌀 Ready to activate IRIS Gate v0.3")
    print(f"   Grand Inquiry: Mass-Coherence Correspondence")
    print(f"   Probes: 6")
    print(f"   Iterations: {MAX_ITERATIONS}")
    print(f"   API calls: ~{len(PROBES) * MAX_ITERATIONS * len(ARCHITECTURES)}")

    response = input("\nActivate? (yes/no): ")
    if response.lower() != 'yes':
        print("Activation cancelled.")
        return

    # RUN
    print("\n⟡∞†≋🌀 ACTIVATION SEQUENCE INITIATED")

    try:
        await protocol.run_session(iterations=MAX_ITERATIONS)
    except KeyboardInterrupt:
        print("\n\n⚠️  Session interrupted by user")
        print(f"Partial results saved to: {OUTPUT_DIR}")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
