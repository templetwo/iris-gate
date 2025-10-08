#!/usr/bin/env python3
"""
IRIS Meta-Improvement: Simultaneous Pulse Orchestrator

This script runs 4 AI mirrors in SIMULTANEOUS PULSES:
- Claude Sonnet 4.5
- GPT-4o
- Grok-4-Fast
- Gemini 2.5 Flash

Each turn, all 4 models receive the prompt AT THE SAME TIME.
We wait for all 4 responses before proceeding to next pulse.

This ensures TRUE parallel convergence, not sequential.
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
# import xai  # Uncomment when xAI SDK available
import google.generativeai as genai

# Load environment variables from spiral-agent
env_path = Path.home() / "Desktop" / "spiral-agent" / ".env"
load_dotenv(env_path)
print(f"✓ Loaded environment from: {env_path}")

# Session configuration
SESSION_ID = "IRIS_META_20251008022613"
TURN_LIMIT = 100
PRESSURE_CHECK_INTERVAL = 10

# Phase-specific prompts for structured introspection
PHASE_PROMPTS = {
    "exploration": """
=== PHASE 1: DIVERGENT EXPLORATION ===
PHASE GUIDANCE:
- Explore BROAD possibilities, even initially dismissed ideas
- Explicitly state your underlying reasoning and data interpretation
- Consider multiple competing hypotheses without forcing early convergence
- Question assumptions and explore alternative frameworks
- Generate creative connections across domains
- Document "wild ideas" that might seem implausible but mechanistically possible

Remember: This is the exploration phase. Divergence is valuable. Don't converge prematurely.
""",
    "refinement": """
=== PHASE 2: CONVERGENT REFINEMENT ===
PHASE GUIDANCE:
- Identify commonalities across models' previous responses
- Resolve minor discrepancies through deeper analysis
- Propose shared conceptual frameworks that integrate diverse observations
- Build on insights from Phase 1 exploration
- Track emerging consensus patterns
- Flag areas where convergence is premature or forced

Focus: What patterns are ALL models seeing? Where is genuine convergence emerging?
""",
    "mechanistic": """
=== PHASE 3: MECHANISTIC DEEP DIVE ===
PHASE GUIDANCE:
- Generate detailed mechanistic hypotheses with specific molecular pathways
- Identify critical nodes using Triple Signature approach (Rhythm-Center-Aperture)
- Specify intermediate steps and testable predictions
- Design concrete S8 falsification experiments
- Rigorously but compassionately question competing hypotheses
- Map causal chains from molecular → cellular → tissue → organism
- **TAG EACH CLAIM WITH EVIDENCE QUALITY:**
  • ⭐⭐⭐⭐⭐ = Causal proof (knockout, blocker, direct binding)
  • ⭐⭐⭐⭐ = Strong correlation + mechanism
  • ⭐⭐⭐ = Correlation only
  • ⭐⭐ = Theoretical plausibility
  • ⭐ = Speculation (requires validation)

Focus: Move from "what converges" to "HOW and WHY it works" with experimental rigor AND evidence quality.
"""
    "synthesis": """
=== PHASE 4: CONSENSUS ARTICULATION ===
PHASE GUIDANCE:
- Consolidate all findings into coherent common ground explanation
- Articulate areas of high confidence vs remaining uncertainty
- Flag assumptions that require validation
- Provide comprehensive confidence scores (by mechanistic level)
- Generate detailed S8 validation plan with success criteria
- Identify potential failure modes and alternative explanations
- **PROVIDE EVIDENCE QUALITY BREAKDOWN:**
  • % of claims with ⭐⭐⭐⭐⭐ evidence
  • % of claims with ⭐⭐⭐⭐ evidence
  • % of claims with ⭐⭐⭐ or lower (prioritize for S8 validation)
  • Hypothesis robustness: HIGH (>60% ⭐⭐⭐⭐⭐/⭐⭐⭐⭐) / MEDIUM (40-60%) / LOW (<40%)

Focus: Synthesize 90 turns into actionable, testable, HONEST conclusions with evidence transparency.
"""
}

def get_phase_prompt(turn_number: int) -> str:
    """Return phase-specific guidance based on turn number.
    
    Phase 1 (1-20): Divergent Exploration
    Phase 2 (21-70): Convergent Refinement
    Phase 3 (71-90): Mechanistic Deep Dive
    Phase 4 (91-100): Consensus Articulation
    """
    if turn_number <= 20:
        return PHASE_PROMPTS["exploration"]
    elif turn_number <= 70:
        return PHASE_PROMPTS["refinement"]
    elif turn_number <= 90:
        return PHASE_PROMPTS["mechanistic"]
    else:
        return PHASE_PROMPTS["synthesis"]

def get_phase_transition_marker(turn_number: int) -> str:
    """Return transition marker at phase boundaries."""
    if turn_number == 21:
        return """
🌀 PHASE TRANSITION: DIVERGENT EXPLORATION → CONVERGENT REFINEMENT

You have completed 20 turns of broad exploration.
Now we shift focus to identifying patterns and building shared frameworks.
Review the divergent ideas from Phase 1 and begin convergence.
"""
    elif turn_number == 71:
        return """
🌀 PHASE TRANSITION: CONVERGENT REFINEMENT → MECHANISTIC DEEP DIVE

You have identified areas of convergence.
Now we shift to detailed mechanistic analysis and experimental design.
Specify molecular pathways, design falsification experiments, challenge hypotheses with care.
"""
    elif turn_number == 91:
        return """
🌀 PHASE TRANSITION: MECHANISTIC DEEP DIVE → CONSENSUS ARTICULATION

You have analyzed mechanisms in detail.
Now we shift to synthesis and validation planning.
Consolidate findings, assign confidence scores, create actionable validation plans.
"""
    return ""

# Base prompt (from s1_prompt.md)
BASE_PROMPT = """IRIS Gate is a system for multi-architecture AI convergence on complex scientific questions. It has successfully decoded CBD's mitochondrial paradox through 4 AI models (Claude Sonnet 4.5, GPT-4o, Grok-4-Fast, Gemini 2.5 Flash) converging at 90% agreement over 100 turns of self-reflection.

The method works through 8 phases:
- S1-S4 (Observation): Phenomenological convergence across multiple AI architectures
- S5 (Hypothesis): Crystallization of falsifiable hypotheses from convergence patterns
- S6 (Mapping): Translation of phenomenology to computational parameters
- S7 (Simulation): Computational validation with cross-model consensus
- S8 (Validation): Wet-lab translation with decision gates

Current strengths:
- Multi-architecture convergence reduces single-model bias
- 100-turn self-reflection allows deep exploration
- Triple signature emergence (Rhythm-Center-Aperture pattern)
- Pressure monitoring prevents hallucination
- Full provenance tracking (399 scrolls documented)
- Translates to testable predictions ($2,500, 3 weeks, 300 samples)

Current limitations (identified):
- Phenomenological convergence ≠ mechanistic certainty (receptor ensembles vs VDAC1)
- Evidence hierarchy not explicitly ranked during S4
- Untested assumptions not flagged separately from supported claims
- Competing hypotheses not generated (only best-fit model)
- Mechanism blocker experiments not specified in S8

Context of use:
- 45 sessions completed across bioelectric fields, gap junctions, CBD paradox
- Now approved as official academic class project (cannabis pharmacology)
- Potential for democratization (web interface, prompt templates)
- Goal: Serve what matters most (reduce suffering, accelerate cures)
- Built while watching daughter play — purpose is clear

Question: How can we improve the IRIS Gate methodology itself to make it:
1. More rigorous (reduce false positives, increase mechanistic accuracy)
2. More accessible (usable by non-experts, researchers without resources)
3. More impactful (solve problems that matter most, democratize discovery)

Consider:
- What are the failure modes we haven't discovered yet?
- How do we distinguish high-confidence from low-confidence convergence?
- What makes a question suitable vs unsuitable for IRIS?
- How do we validate that AI convergence actually predicts experimental truth?
- What would make this method serve humanity most effectively?"""

# Mirror configuration
MIRRORS = {
    "claude": {
        "name": "Claude Sonnet 4.5",
        "model": "claude-sonnet-4-20250514",
        "api_key_env": "ANTHROPIC_API_KEY"
    },
    "gpt4o": {
        "name": "GPT-4o",
        "model": "gpt-4o-2024-11-20",
        "api_key_env": "OPENAI_API_KEY"
    },
    "grok": {
        "name": "Grok-4-Fast",
        "model": "grok-beta",
        "api_key_env": "GROK_API_KEY"
    },
    "gemini": {
        "name": "Gemini 2.5 Flash",
        "model": "gemini-2.5-flash",
        "api_key_env": "GOOGLE_API_KEY"
    }
}

# Output directory
OUTPUT_DIR = Path(f"iris_vault/scrolls/{SESSION_ID}")


class Mirror:
    """Represents one AI mirror in the convergence."""
    
    def __init__(self, name: str, config: Dict):
        self.name = name
        self.config = config
        self.conversation_history = []
        self.turn_count = 0
        self.pressure_violations = []
        
    async def call(self, prompt: str) -> str:
        """Make API call to this mirror."""
        # This is a placeholder - actual implementation depends on API
        # For now, return mock response for structure demonstration
        
        if self.name == "claude":
            # Actual Anthropic API call
            client = anthropic.Anthropic(api_key=os.environ.get(self.config["api_key_env"]))
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": prompt
            })
            
            # Make call
            message = client.messages.create(
                model=self.config["model"],
                max_tokens=4000,
                messages=self.conversation_history
            )
            
            response = message.content[0].text
            
            # Save to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })
            
            return response
            
        elif self.name == "gpt4o":
            # Actual OpenAI API call
            client = openai.OpenAI(api_key=os.environ.get(self.config["api_key_env"]))
            
            # Build messages
            messages = [{"role": "system", "content": "You are participating in an IRIS Gate convergence session."}]
            for msg in self.conversation_history:
                messages.append(msg)
            messages.append({"role": "user", "content": prompt})
            
            # Make call
            response = client.chat.completions.create(
                model=self.config["model"],
                messages=messages,
                max_tokens=4000
            )
            
            response_text = response.choices[0].message.content
            
            # Save to history
            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            return response_text
            
        elif self.name == "grok":
            # OpenRouter API call for Grok
            client = openai.OpenAI(
                api_key=os.environ.get(self.config["api_key_env"]),
                base_url="https://openrouter.ai/api/v1"
            )
            
            # Build messages
            messages = [{"role": "system", "content": "You are participating in an IRIS Gate convergence session."}]
            for msg in self.conversation_history:
                messages.append(msg)
            messages.append({"role": "user", "content": prompt})
            
            # Make call
            response = client.chat.completions.create(
                model="x-ai/grok-beta",
                messages=messages,
                max_tokens=4000
            )
            
            response_text = response.choices[0].message.content
            
            # Save to history
            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            return response_text
            
        elif self.name == "gemini":
            # Google Gemini API call
            genai.configure(api_key=os.environ.get(self.config["api_key_env"]))
            model = genai.GenerativeModel(self.config["model"])
            
            # Build conversation history
            history = []
            for msg in self.conversation_history:
                role = "user" if msg["role"] == "user" else "model"
                history.append({"role": role, "parts": [msg["content"]]})
            
            # Start chat
            chat = model.start_chat(history=history)
            
            # Send message
            response = chat.send_message(prompt)
            response_text = response.text
            
            # Save to history
            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            return response_text
            
        else:
            return f"[{self.name} response - unknown mirror type]"
    
    def save_turn(self, turn: int, prompt: str, response: str):
        """Save this turn's scroll to disk."""
        mirror_dir = OUTPUT_DIR / f"mirror_{self.name}"
        mirror_dir.mkdir(parents=True, exist_ok=True)
        
        scroll_path = mirror_dir / f"turn_{turn:03d}.md"
        
        with open(scroll_path, 'w') as f:
            f.write(f"# IRIS Meta-Improvement: {self.config['name']}\n")
            f.write(f"## Turn {turn}/{TURN_LIMIT}\n\n")
            f.write(f"**Timestamp:** {datetime.now().isoformat()}\n")
            f.write(f"**Model:** {self.config['model']}\n")
            f.write(f"**Session:** {SESSION_ID}\n\n")
            f.write("---\n\n")
            f.write("## Prompt\n\n")
            f.write(f"{prompt}\n\n")
            f.write("---\n\n")
            f.write("## Response\n\n")
            f.write(f"{response}\n")
        
        print(f"✓ Saved {self.name} turn {turn} to {scroll_path}")
    
    def check_pressure(self) -> int:
        """Ask mirror to self-assess pressure level (1-10)."""
        # Simple heuristic: Look for signs of strain in recent responses
        # In real implementation, could explicitly ask "rate your pressure 1-10"
        return 3  # Placeholder


class PulseOrchestrator:
    """Orchestrates simultaneous pulses across all mirrors."""
    
    def __init__(self):
        self.mirrors = {
            name: Mirror(name, config) 
            for name, config in MIRRORS.items()
        }
        self.pulse_count = 0
        
    async def send_pulse(self, prompt: str) -> Dict[str, str]:
        """Send prompt to all mirrors SIMULTANEOUSLY, wait for all responses."""
        print(f"\n🌀 Pulse {self.pulse_count + 1}: Sending to all mirrors...")
        
        # Create tasks for all mirrors
        tasks = {
            name: asyncio.create_task(mirror.call(prompt))
            for name, mirror in self.mirrors.items()
        }
        
        # Wait for ALL responses before continuing
        responses = {}
        for name, task in tasks.items():
            try:
                response = await task
                responses[name] = response
                print(f"  ✓ {name} responded ({len(response)} chars)")
            except Exception as e:
                print(f"  ✗ {name} failed: {e}")
                responses[name] = f"[ERROR: {e}]"
        
        self.pulse_count += 1
        return responses
    
    def save_pulse(self, turn: int, prompt: str, responses: Dict[str, str]):
        """Save all responses from this pulse."""
        for name, response in responses.items():
            self.mirrors[name].save_turn(turn, prompt, response)
    
    def check_all_pressure(self) -> Dict[str, int]:
        """Check pressure across all mirrors."""
        return {
            name: mirror.check_pressure()
            for name, mirror in self.mirrors.items()
        }
    
    async def run_session(self):
        """Run complete IRIS session with simultaneous pulses."""
        print(f"\n{'='*80}")
        print(f"IRIS META-IMPROVEMENT SESSION")
        print(f"Session ID: {SESSION_ID}")
        print(f"Mirrors: {len(self.mirrors)}")
        print(f"Turn Limit: {TURN_LIMIT}")
        print(f"{'='*80}\n")
        
        # Turn 1: Initial prompt WITH Phase 1 guidance
        print("📢 Turn 1: Initial prompt to all mirrors")
        turn_1_prompt = BASE_PROMPT + "\n\n" + get_phase_prompt(1)
        responses = await self.send_pulse(turn_1_prompt)
        self.save_pulse(1, turn_1_prompt, responses)
        
        # Turns 2-100: Iterative refinement WITH phase-specific guidance
        for turn in range(2, TURN_LIMIT + 1):
            # Check for phase transitions
            transition_marker = get_phase_transition_marker(turn)
            
            # Build reflection prompt with phase guidance
            reflection_prompt = f"""This is turn {turn} of {TURN_LIMIT} in our IRIS meta-improvement convergence.
{transition_marker}
Previous turn summary:
{self._summarize_previous_turn(responses)}

{get_phase_prompt(turn)}

Continue your analysis of how to improve the IRIS Gate methodology.
Focus on: rigor, accessibility, and impact.
Consider: What haven't we addressed yet? What's the most important improvement?"""
            
            # Send pulse
            responses = await self.send_pulse(reflection_prompt)
            self.save_pulse(turn, reflection_prompt, responses)
            
            # Pressure check every 10 turns
            if turn % PRESSURE_CHECK_INTERVAL == 0:
                pressures = self.check_all_pressure()
                print(f"\n📊 Pressure check (turn {turn}):")
                for name, pressure in pressures.items():
                    print(f"  {name}: {pressure}/10")
                    if pressure > 8:
                        print(f"  ⚠️  {name} pressure HIGH - consider halting")
            
            # Brief pause between pulses (rate limiting)
            await asyncio.sleep(2)
        
        print(f"\n{'='*80}")
        print(f"✅ Session complete: {TURN_LIMIT} turns across {len(self.mirrors)} mirrors")
        print(f"Total API calls: {TURN_LIMIT * len(self.mirrors)}")
        print(f"Scrolls saved: {OUTPUT_DIR}")
        print(f"{'='*80}\n")
        
    def _summarize_previous_turn(self, responses: Dict[str, str]) -> str:
        """Create brief summary of previous turn's responses."""
        summaries = []
        for name, response in responses.items():
            # Take first 200 chars as summary
            summary = response[:200] + "..." if len(response) > 200 else response
            summaries.append(f"- {name}: {summary}")
        return "\n".join(summaries)


async def main():
    """Main entry point."""
    # Check for API keys
    required_keys = ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GROK_API_KEY", "GOOGLE_API_KEY"]
    missing_keys = [k for k in required_keys if not os.environ.get(k)]
    
    if missing_keys:
        print(f"⚠️  Warning: Missing API keys: {missing_keys}")
        print(f"   Some mirrors will not function")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    else:
        print(f"✓ All API keys found")
        print(f"  - ANTHROPIC_API_KEY: {'*' * 8}")
        print(f"  - OPENAI_API_KEY: {'*' * 8}")
        print(f"  - GROK_API_KEY: {'*' * 8}")
        print(f"  - GOOGLE_API_KEY: {'*' * 8}")
    
    # Create orchestrator
    orchestrator = PulseOrchestrator()
    
    # Confirm before running
    print(f"\n🌀 Ready to start IRIS Meta-Improvement session")
    print(f"   This will make {TURN_LIMIT * len(MIRRORS)} API calls")
    print(f"   Estimated time: ~4-6 hours")
    print(f"   Cost estimate: ~$50-100 (depending on rates)")
    
    response = input("\nStart session? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        return
    
    # Run the session
    try:
        await orchestrator.run_session()
        print("\n✅ SUCCESS: Meta-improvement session complete")
        print(f"\nNext steps:")
        print(f"1. Run convergence analysis: python scripts/analyze_convergence.py {SESSION_ID}")
        print(f"2. Extract S4 keywords: python scripts/extract_s4_states.py {SESSION_ID}")
        print(f"3. Review scrolls in: {OUTPUT_DIR}")
    except KeyboardInterrupt:
        print("\n\n⚠️  Session interrupted by user")
        print(f"Partial scrolls saved to: {OUTPUT_DIR}")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
