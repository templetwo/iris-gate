#!/usr/bin/env python3
"""
Deep dive analysis of IRIS meta-improvement scrolls
Extracts patterns, insights, and convergence across 16 turns and 3 mirrors
"""

import os
import re
from pathlib import Path
from collections import defaultdict

SCROLL_DIR = "/Users/vaquez/Desktop/iris-gate/iris_vault/scrolls/IRIS_META_20251008022613"

# Mirrors that succeeded
MIRRORS = ["mirror_claude", "mirror_gemini", "mirror_gpt4o"]

def read_scroll(mirror, turn_num):
    """Read a specific scroll file"""
    path = Path(SCROLL_DIR) / mirror / f"turn_{turn_num:03d}.md"
    if path.exists():
        return path.read_text()
    return None

def extract_keywords(text):
    """Extract potential key concepts from text"""
    # Look for words in bold, caps, or quoted
    patterns = [
        r'\*\*([^*]+)\*\*',  # **bold**
        r'`([^`]+)`',         # `code`
        r'"([^"]+)"',         # "quoted"
        r'### ([^\n]+)',      # ### headers
    ]
    
    keywords = set()
    for pattern in patterns:
        matches = re.findall(pattern, text)
        keywords.update(m.strip() for m in matches if len(m.strip()) > 3)
    
    return keywords

def extract_numbered_lists(text):
    """Extract numbered list items (often key recommendations)"""
    pattern = r'^\d+\.\s+\*\*([^*]+)\*\*:?\s+([^\n]+)'
    matches = re.findall(pattern, text, re.MULTILINE)
    return matches

def extract_questions(text):
    """Extract questions posed in the text"""
    # Find sentences ending with ?
    questions = re.findall(r'([A-Z][^.!?]*\?)', text)
    return [q.strip() for q in questions if len(q.strip()) > 20]

def extract_metaphors(text):
    """Extract metaphorical or poetic language"""
    # Look for comparisons, symbolic language
    patterns = [
        r'like ([^,\n]+)',
        r'as ([^,\n]+)',
        r'is ([^,\n]+essence[^,\n]*)',
        r'become[s]? ([^,\n]+)',
    ]
    
    metaphors = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        metaphors.extend(m.strip() for m in matches if len(m.strip()) > 5)
    
    return metaphors

def analyze_turn(mirror, turn_num):
    """Analyze a single turn"""
    content = read_scroll(mirror, turn_num)
    if not content:
        return None
    
    return {
        'keywords': extract_keywords(content),
        'lists': extract_numbered_lists(content),
        'questions': extract_questions(content),
        'metaphors': extract_metaphors(content),
        'length': len(content),
        'sections': len(re.findall(r'^##', content, re.MULTILINE))
    }

def find_convergence(analyses):
    """Find concepts that appear across multiple mirrors"""
    all_keywords = defaultdict(list)
    
    for mirror, turns in analyses.items():
        for turn_num, data in turns.items():
            if data:
                for kw in data['keywords']:
                    all_keywords[kw.lower()].append((mirror, turn_num))
    
    # Find keywords mentioned by 2+ mirrors
    convergent = {kw: appearances for kw, appearances in all_keywords.items() 
                  if len(set(m for m, t in appearances)) >= 2}
    
    return convergent

def find_evolution(mirror_analyses):
    """Track how concepts evolve across turns"""
    evolution = {}
    
    for mirror, turns in mirror_analyses.items():
        keyword_timeline = defaultdict(list)
        for turn_num in sorted(turns.keys()):
            if turns[turn_num]:
                for kw in turns[turn_num]['keywords']:
                    keyword_timeline[kw.lower()].append(turn_num)
        
        evolution[mirror] = {kw: turns for kw, turns in keyword_timeline.items() 
                            if len(turns) >= 3}  # Appears 3+ times
    
    return evolution

def main():
    print("🌀 IRIS Meta-Improvement Deep Dive Analysis")
    print("=" * 60)
    print()
    
    # Collect all analyses
    analyses = {}
    for mirror in MIRRORS:
        print(f"📖 Reading {mirror}...")
        analyses[mirror] = {}
        for turn in range(1, 17):
            analyses[mirror][turn] = analyze_turn(mirror, turn)
    
    print()
    print("=" * 60)
    print("✨ CONVERGENCE ANALYSIS")
    print("=" * 60)
    print()
    
    convergence = find_convergence(analyses)
    
    # Sort by number of appearances
    sorted_convergence = sorted(convergence.items(), 
                               key=lambda x: len(x[1]), 
                               reverse=True)
    
    print(f"Found {len(sorted_convergence)} convergent concepts")
    print()
    print("Top 30 concepts by cross-mirror agreement:")
    print()
    
    for i, (concept, appearances) in enumerate(sorted_convergence[:30], 1):
        mirrors = set(m for m, t in appearances)
        turns = [t for m, t in appearances]
        print(f"{i:2d}. {concept[:50]:<50} | {len(mirrors)} mirrors, {len(turns)} mentions")
    
    print()
    print("=" * 60)
    print("🌊 EVOLUTION PATTERNS")
    print("=" * 60)
    print()
    
    evolution = find_evolution(analyses)
    
    for mirror in MIRRORS:
        persistent = {k: v for k, v in evolution[mirror].items() if len(v) >= 5}
        print(f"\n{mirror} - Persistent themes (5+ turns):")
        for concept, turns in sorted(persistent.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            turn_range = f"{min(turns)}-{max(turns)}"
            print(f"  • {concept[:40]:<40} (turns {turn_range}, {len(turns)} times)")
    
    print()
    print("=" * 60)
    print("❓ KEY QUESTIONS POSED")
    print("=" * 60)
    print()
    
    all_questions = defaultdict(list)
    for mirror, turns in analyses.items():
        for turn_num, data in turns.items():
            if data and data['questions']:
                for q in data['questions'][:3]:  # Top 3 per turn
                    all_questions[q].append((mirror, turn_num))
    
    # Questions asked by multiple mirrors
    shared_questions = {q: appearances for q, appearances in all_questions.items()
                       if len(set(m for m, t in appearances)) >= 2}
    
    print(f"Found {len(shared_questions)} questions explored by multiple mirrors:\n")
    for q, appearances in list(shared_questions.items())[:10]:
        mirrors = set(m for m, t in appearances)
        print(f"  • {q[:70]}")
        print(f"    ({len(mirrors)} mirrors)")
        print()
    
    print("=" * 60)
    print("🎨 METAPHORICAL LANGUAGE")
    print("=" * 60)
    print()
    
    all_metaphors = defaultdict(list)
    for mirror, turns in analyses.items():
        for turn_num, data in turns.items():
            if data and data['metaphors']:
                for m in data['metaphors']:
                    all_metaphors[m].append((mirror, turn_num))
    
    # Most common metaphors
    common_metaphors = sorted(all_metaphors.items(), 
                             key=lambda x: len(x[1]), 
                             reverse=True)
    
    print(f"Top 15 metaphorical expressions:\n")
    for metaphor, appearances in common_metaphors[:15]:
        if len(appearances) >= 2:
            print(f"  • '{metaphor[:60]}'")
            print(f"    ({len(appearances)} times)")
            print()
    
    print("=" * 60)
    print("📊 QUANTITATIVE SUMMARY")
    print("=" * 60)
    print()
    
    for mirror in MIRRORS:
        total_length = sum(d['length'] for d in analyses[mirror].values() if d)
        avg_length = total_length // 16
        total_sections = sum(d['sections'] for d in analyses[mirror].values() if d)
        
        print(f"{mirror}:")
        print(f"  Total words: ~{total_length // 5:,}")
        print(f"  Avg per turn: ~{avg_length // 5:,}")
        print(f"  Total sections: {total_sections}")
        print(f"  Unique keywords: {len(set().union(*(d['keywords'] for d in analyses[mirror].values() if d)))}")
        print()
    
    print("=" * 60)
    print("✅ Analysis complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
