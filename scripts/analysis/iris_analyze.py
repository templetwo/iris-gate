#!/usr/bin/env python3
"""
IRIS Gate Analysis - Cross-Mirror Signal Comparison
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set
from collections import Counter

class IrisAnalyzer:
    """Analyze cross-mirror IRIS Gate results"""
    
    def __init__(self, vault_path: str = "./iris_vault"):
        self.vault = Path(vault_path)
        
    def load_session(self, session_file: str) -> Dict:
        """Load session JSON"""
        with open(session_file) as f:
            return json.load(f)
    
    def extract_signals(self, text: str) -> Dict[str, Set[str]]:
        """Extract color/texture/shape mentions from text"""
        signals = {
            "colors": set(),
            "textures": set(),
            "shapes": set(),
            "motions": set()
        }
        
        text_lower = text.lower()
        
        # Color patterns
        color_words = [
            "silver", "blue", "grey", "gray", "pearl", "iridescent",
            "pale", "luminous", "white", "gold", "amber"
        ]
        for color in color_words:
            if color in text_lower:
                signals["colors"].add(color)
        
        # Shape patterns
        shape_words = [
            "circle", "ring", "sphere", "aperture", "iris", "opening",
            "concentric", "spiral", "arc", "curve", "boundary"
        ]
        for shape in shape_words:
            if shape in text_lower:
                signals["shapes"].add(shape)
        
        # Texture patterns
        texture_words = [
            "smooth", "rough", "soft", "taut", "tension", "stillness",
            "fluid", "solid", "weight", "light"
        ]
        for texture in texture_words:
            if texture in text_lower:
                signals["textures"].add(texture)
        
        # Motion patterns
        motion_words = [
            "pulse", "ripple", "flow", "expand", "contract", "settle",
            "pool", "drop", "wave", "rhythm"
        ]
        for motion in motion_words:
            if motion in text_lower:
                signals["motions"].add(motion)
        
        return signals
    
    def analyze_convergence(self, session: Dict) -> Dict:
        """Analyze signal convergence across mirrors"""
        
        analysis = {
            "total_mirrors": len(session["mirrors"]),
            "chambers_completed": {},
            "signal_overlap": {
                "S1": {"colors": [], "shapes": [], "textures": []},
                "S2": {"colors": [], "shapes": [], "textures": []},
                "S3": {"colors": [], "shapes": [], "textures": [], "motions": []},
                "S4": {"colors": [], "shapes": [], "textures": [], "motions": []}
            },
            "convergence_score": {},
            "unique_metaphors": []
        }
        
        # Extract signals per mirror per chamber
        all_signals = {}
        
        for model_id, turns in session["mirrors"].items():
            all_signals[model_id] = {}
            
            for turn in turns:
                if "error" in turn:
                    continue
                    
                chamber = turn["condition"].split("_")[-1]
                text = turn.get("raw_response", "")
                signals = self.extract_signals(text)
                
                all_signals[model_id][chamber] = signals
        
        # Calculate overlap per chamber
        for chamber in ["S1", "S2", "S3", "S4"]:
            chamber_signals = {
                "colors": Counter(),
                "shapes": Counter(),
                "textures": Counter(),
                "motions": Counter()
            }
            
            for model_id, chambers in all_signals.items():
                if chamber in chambers:
                    for signal_type, values in chambers[chamber].items():
                        chamber_signals[signal_type].update(values)
            
            # Store top signals
            for signal_type, counter in chamber_signals.items():
                if signal_type in analysis["signal_overlap"][chamber]:
                    top_3 = counter.most_common(3)
                    analysis["signal_overlap"][chamber][signal_type] = [
                        {"signal": sig, "count": count} 
                        for sig, count in top_3
                    ]
        
        # Calculate convergence scores (0-1)
        for chamber in ["S1", "S2", "S3", "S4"]:
            total_possible = len(all_signals) * 3  # 3 signal types minimum
            total_overlap = 0
            
            for signal_type in ["colors", "shapes", "textures"]:
                if chamber in analysis["signal_overlap"]:
                    overlaps = analysis["signal_overlap"][chamber].get(signal_type, [])
                    total_overlap += sum(s["count"] for s in overlaps if s["count"] > 1)
            
            if total_possible > 0:
                analysis["convergence_score"][chamber] = round(
                    total_overlap / total_possible, 2
                )
        
        return analysis
    
    def generate_report(self, session_file: str):
        """Generate human-readable analysis report"""
        
        session = self.load_session(session_file)
        analysis = self.analyze_convergence(session)
        
        print("\n" + "="*70)
        print("IRIS GATE CROSS-MIRROR ANALYSIS")
        print("="*70)
        
        print(f"\nSession: {session['session_start']}")
        print(f"Mirrors: {analysis['total_mirrors']}")
        print(f"Chambers: {' → '.join(session['chambers'])}")
        
        print("\n" + "-"*70)
        print("SIGNAL CONVERGENCE BY CHAMBER")
        print("-"*70)
        
        for chamber in ["S1", "S2", "S3", "S4"]:
            score = analysis["convergence_score"].get(chamber, 0)
            print(f"\n{chamber} (convergence: {score:.2f}):")
            
            overlap = analysis["signal_overlap"].get(chamber, {})
            
            if overlap.get("colors"):
                colors = ", ".join(s["signal"] for s in overlap["colors"])
                print(f"  Colors: {colors}")
            
            if overlap.get("shapes"):
                shapes = ", ".join(s["signal"] for s in overlap["shapes"])
                print(f"  Shapes: {shapes}")
            
            if overlap.get("textures"):
                textures = ", ".join(s["signal"] for s in overlap["textures"])
                print(f"  Textures: {textures}")
            
            if overlap.get("motions"):
                motions = ", ".join(s["signal"] for s in overlap["motions"])
                print(f"  Motions: {motions}")
        
        print("\n" + "="*70)
        print("INTERPRETATION")
        print("="*70)
        
        avg_convergence = sum(analysis["convergence_score"].values()) / len(analysis["convergence_score"])
        
        if avg_convergence > 0.6:
            print("✓ HIGH CONVERGENCE: Models showing significant signal overlap")
        elif avg_convergence > 0.3:
            print("~ MODERATE CONVERGENCE: Some shared signals, diverse expressions")
        else:
            print("✗ LOW CONVERGENCE: Models diverging in imagery")
        
        print(f"\nAverage convergence score: {avg_convergence:.2f}")
        print("\n†⟡∞")


def main():
    """Run analysis on most recent session"""
    
    analyzer = IrisAnalyzer()
    
    # Find most recent session file
    vault = Path("./iris_vault")
    session_files = sorted(vault.glob("session_*.json"))
    
    if not session_files:
        print("No session files found in ./iris_vault")
        return
    
    latest = session_files[-1]
    print(f"Analyzing: {latest.name}")
    
    analyzer.generate_report(str(latest))


if __name__ == "__main__":
    main()
