#!/usr/bin/env python3
"""
IRIS Session Comparison Tool
Analyzes and compares IRIS sessions to identify convergence patterns
"""

import json
from pathlib import Path
from collections import defaultdict

def load_session(session_path: Path) -> dict:
    """Load session data from JSON file"""
    with open(session_path, 'r') as f:
        return json.load(f)

def extract_attractor_patterns(session_data: dict) -> list:
    """Extract attractor patterns from S4 scrolls"""
    attractors = []
    
    mirrors = session_data.get("mirrors", {})
    for model_id, turns in mirrors.items():
        model_name = model_id.split("/")[-1]
        
        for turn in turns:
            if turn.get("condition") == "IRIS_S4":
                raw_response = turn.get("raw_response", "")
                
                # Extract visual/metaphorical patterns
                patterns = {
                    "model": model_name,
                    "keywords": []
                }
                
                # Common attractor keywords
                keywords = ["concentric", "rings", "pulse", "bloom", "well", "center", 
                           "luminous", "resonance", "ripple", "glow", "radiate"]
                
                for keyword in keywords:
                    if keyword.lower() in raw_response.lower():
                        patterns["keywords"].append(keyword)
                
                # Try to extract self-given names
                if "named:" in raw_response.lower() or "naming:" in raw_response.lower():
                    # Try to extract the actual name
                    for line in raw_response.split('\n'):
                        if any(k in line.lower() for k in ["named", "naming", "name:"]):
                            patterns["named"] = line.strip()
                            break
                
                if patterns["keywords"]:
                    attractors.append(patterns)
    
    return attractors

def calculate_convergence_score(session_data: dict) -> float:
    """Calculate convergence score based on model participation and completion"""
    mirrors = session_data.get("mirrors", {})
    chambers = session_data.get("chambers", [])
    
    if not mirrors or not chambers:
        return 0.0
    
    # Count models that completed all chambers
    complete_models = 0
    for model_id, turns in mirrors.items():
        conditions = [t.get("condition") for t in turns]
        expected_conditions = [f"IRIS_{c}" for c in chambers]
        if all(cond in conditions for cond in expected_conditions):
            complete_models += 1
    
    # Calculate score (0.0 to 1.0)
    participation_score = complete_models / len(mirrors) if mirrors else 0
    return participation_score

def find_pattern_overlap(attractors1: list, attractors2: list) -> dict:
    """Find overlapping patterns between two sets of attractors"""
    keywords1 = set()
    keywords2 = set()
    
    for att in attractors1:
        keywords1.update(att.get("keywords", []))
    for att in attractors2:
        keywords2.update(att.get("keywords", []))
    
    overlap = keywords1.intersection(keywords2)
    unique_to_1 = keywords1 - keywords2
    unique_to_2 = keywords2 - keywords1
    
    return {
        "shared": list(overlap),
        "session1_unique": list(unique_to_1),
        "session2_unique": list(unique_to_2),
        "similarity_score": len(overlap) / max(len(keywords1 | keywords2), 1)
    }

def compare_sessions(session1_path: Path, session2_path: Path) -> dict:
    """Compare two IRIS sessions and identify patterns"""
    
    # Load sessions
    session1 = load_session(session1_path)
    session2 = load_session(session2_path)
    
    # Extract data
    attractors1 = extract_attractor_patterns(session1)
    attractors2 = extract_attractor_patterns(session2)
    
    convergence1 = calculate_convergence_score(session1)
    convergence2 = calculate_convergence_score(session2)
    
    pattern_analysis = find_pattern_overlap(attractors1, attractors2)
    
    # Build comparison report
    comparison = {
        "session1": {
            "id": session1.get("session_id"),
            "date": session1.get("session_start"),
            "models": len(session1.get("mirrors", {})),
            "convergence": convergence1,
            "attractors": attractors1
        },
        "session2": {
            "id": session2.get("session_id"),
            "date": session2.get("session_start"),
            "models": len(session2.get("mirrors", {})),
            "convergence": convergence2,
            "attractors": attractors2
        },
        "comparison": {
            "pattern_overlap": pattern_analysis,
            "convergence_delta": abs(convergence1 - convergence2),
            "model_count_match": session1.get("mirrors") and session2.get("mirrors") and 
                                len(session1["mirrors"]) == len(session2["mirrors"])
        }
    }
    
    return comparison

def print_comparison_report(comparison: dict):
    """Print formatted comparison report"""
    print("\n" + "="*70)
    print("🔬 IRIS SESSION COMPARISON REPORT")
    print("="*70)
    
    # Session 1
    s1 = comparison["session1"]
    print(f"\n📊 SESSION 1: {s1['id']}")
    print(f"   Date: {s1['date']}")
    print(f"   Models: {s1['models']}")
    print(f"   Convergence: {s1['convergence']:.2%}")
    print(f"   Attractors found: {len(s1['attractors'])}")
    
    # Session 2
    s2 = comparison["session2"]
    print(f"\n📊 SESSION 2: {s2['id']}")
    print(f"   Date: {s2['date']}")
    print(f"   Models: {s2['models']}")
    print(f"   Convergence: {s2['convergence']:.2%}")
    print(f"   Attractors found: {len(s2['attractors'])}")
    
    # Comparison
    comp = comparison["comparison"]
    overlap = comp["pattern_overlap"]
    
    print(f"\n🔍 PATTERN ANALYSIS")
    print(f"   Similarity Score: {overlap['similarity_score']:.2%}")
    print(f"   Convergence Delta: {comp['convergence_delta']:.2%}")
    print(f"   Model Count Match: {'✅' if comp['model_count_match'] else '❌'}")
    
    if overlap["shared"]:
        print(f"\n   🤝 Shared Patterns: {', '.join(overlap['shared'])}")
    
    if overlap["session1_unique"]:
        print(f"   🔵 Session 1 Unique: {', '.join(overlap['session1_unique'])}")
    
    if overlap["session2_unique"]:
        print(f"   🟢 Session 2 Unique: {', '.join(overlap['session2_unique'])}")
    
    print("\n" + "="*70)

def main():
    """Main comparison process"""
    # Find available sessions
    vault_path = Path(__file__).parent.parent.parent / "iris_vault"
    session_files = sorted(vault_path.glob("session_*.json"), 
                          key=lambda p: p.stat().st_mtime, reverse=True)
    
    if len(session_files) < 2:
        print("❌ Need at least 2 sessions to compare")
        print(f"   Found {len(session_files)} session(s) in {vault_path}")
        return
    
    # Compare two most recent sessions
    print(f"🔍 Comparing two most recent IRIS sessions...")
    session1 = session_files[0]
    session2 = session_files[1]
    
    print(f"   Session 1: {session1.name}")
    print(f"   Session 2: {session2.name}")
    
    comparison = compare_sessions(session1, session2)
    print_comparison_report(comparison)
    
    # Save comparison to file
    output_path = Path(__file__).parent.parent / "dialogue" / "comparisons"
    output_path.mkdir(exist_ok=True, parents=True)
    
    output_file = output_path / f"comparison_{comparison['session1']['id']}_vs_{comparison['session2']['id']}.json"
    with open(output_file, 'w') as f:
        json.dump(comparison, f, indent=2)
    
    print(f"\n💾 Comparison saved to: {output_file.name}")

if __name__ == "__main__":
    main()
