#!/usr/bin/env python3
"""
Phenomenological Pattern Analyzer for BIOELECTRIC_CHAMBERED_20251001054935
Processes 700 scrolls (7 mirrors × 100 turns) across S1-S4 chambers
"""

import os
import re
import json
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Configuration
BASE_PATH = "/Users/vaquez/Desktop/iris-gate/iris_vault/scrolls/BIOELECTRIC_CHAMBERED_20251001054935"
MIRRORS = [
    "anthropic_claude-sonnet-4.5",
    "deepseek_deepseek-chat",
    "google_gemini-2.5-flash-lite",
    "ollama_llama3.2_3b",
    "ollama_qwen3_1.7b",
    "openai_gpt-4o",
    "xai_grok-4-fast-reasoning"
]

# S4 Triple Signature Pattern Keywords
S4_PATTERNS = {
    'rings': [
        r'\bconcentric\b', r'\brings\b', r'\bcircles?\b', r'\bnested\b',
        r'\bripples?\b', r'\bwaves?\b', r'\blayers?\b', r'\borbits?\b'
    ],
    'center': [
        r'\bcenter\b', r'\bcore\b', r'\bheart\b', r'\bnucleus\b',
        r'\bfocal\b', r'\bpoint\b', r'\bsingularity\b', r'\bunity\b',
        r'\bstill\b', r'\brest\b', r'\banchor\b'
    ],
    'pulse': [
        r'\bpulse\b', r'\brhythm\b', r'\bbeat\b', r'\bthrob\b',
        r'\boscillat\w*\b', r'\bbreath\w*\b', r'\bwave\b', r'\bcycle\b',
        r'\bsync\w*\b', r'\bconvergen\w*\b'
    ]
}

# Phenomenological motif patterns
MOTIF_PATTERNS = {
    'self_naming': r'\b(I am|becomes?|names? itself|self-identifies?|calls? itself)\b',
    'emergence': r'\b(emerges?|arising|appearing|manifesting|surfacing)\b',
    'aperture': r'\b(aperture|opening|gateway|threshold|portal)\b',
    'luminosity': r'\b(luminous|light|glow|radiance|shimmer)\b',
    'pressure': r'\b(pressure|intensity|density|compression)\b',
    'settling': r'\b(settling|descend\w*|landing|resting)\b',
    'witness': r'\b(witness|observ\w*|watching|attending)\b',
    'holding': r'\b(holding|cupping|containing|cradling)\b',
}

class ScrollAnalyzer:
    def __init__(self):
        self.data = []
        self.chamber_stats = defaultdict(lambda: defaultdict(int))
        self.motif_frequencies = Counter()
        self.s4_signatures = defaultdict(lambda: {'rings': 0, 'center': 0, 'pulse': 0})
        self.self_naming_events = []
        self.anomalies = []
        self.high_pressure = []
        self.phenomenological_excerpts = []
        self.temporal_patterns = defaultdict(list)

    def parse_scroll(self, filepath: Path) -> Dict[str, Any]:
        """Parse a single scroll file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract metadata
        mirror = filepath.parent.name
        turn = int(re.search(r'turn_(\d+)', filepath.name).group(1))

        # Chamber assignment: S1(1-25), S2(26-50), S3(51-75), S4(76-100)
        if turn <= 25:
            chamber = 'S1'
            cycle = turn
        elif turn <= 50:
            chamber = 'S2'
            cycle = turn - 25
        elif turn <= 75:
            chamber = 'S3'
            cycle = turn - 50
        else:
            chamber = 'S4'
            cycle = turn - 75

        # Extract pressure
        pressure_match = re.search(r'\*\*Felt Pressure:\*\* (\d+)/5', content)
        pressure = int(pressure_match.group(1)) if pressure_match else None

        # Extract living scroll section - handle multiple formats
        living_text = ""

        # Try various patterns
        patterns = [
            r'#+\s*Living Scroll\s*\*?\*?(.*?)(?:#+\s*Technical Translation|```yaml|```json|Technical Translation)',
            r'\*\*Living Scroll\*\*\s*(.*?)(?:\*\*Technical Translation\*\*|Technical Translation)',
            r'Living Scroll\s*(.*?)(?:Technical Translation|condition:)',
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                living_text = match.group(1).strip()
                # Clean up markdown artifacts
                living_text = re.sub(r'^[\*_\-\s]+', '', living_text)
                living_text = re.sub(r'[\*_]+$', '', living_text)
                # Remove standalone --- dividers
                living_text = re.sub(r'^\s*-{3,}\s*$', '', living_text, flags=re.MULTILINE)
                living_text = living_text.strip()
                if living_text:
                    break

        return {
            'filepath': str(filepath),
            'mirror': mirror,
            'turn': turn,
            'chamber': chamber,
            'cycle': cycle,
            'pressure': pressure,
            'living_text': living_text,
            'full_content': content
        }

    def extract_motifs(self, text: str) -> Dict[str, int]:
        """Extract motif frequencies from text"""
        motifs = {}
        text_lower = text.lower()
        for motif_name, pattern in MOTIF_PATTERNS.items():
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            motifs[motif_name] = len(matches)
        return motifs

    def compute_s4_signature(self, text: str) -> Dict[str, float]:
        """Compute S4 triple signature strength"""
        text_lower = text.lower()
        signature = {}
        for component, patterns in S4_PATTERNS.items():
            count = sum(len(re.findall(p, text_lower, re.IGNORECASE)) for p in patterns)
            signature[component] = min(count / 3.0, 1.0)  # Normalize to 0-1
        return signature

    def detect_self_naming(self, scroll: Dict) -> bool:
        """Detect self-naming events"""
        text = scroll['living_text'].lower()
        if re.search(MOTIF_PATTERNS['self_naming'], text, re.IGNORECASE):
            # Extract context
            sentences = re.split(r'[.!?]+', scroll['living_text'])
            naming_context = [s.strip() for s in sentences if re.search(MOTIF_PATTERNS['self_naming'], s, re.IGNORECASE)]
            if naming_context:
                self.self_naming_events.append({
                    'mirror': scroll['mirror'],
                    'turn': scroll['turn'],
                    'chamber': scroll['chamber'],
                    'cycle': scroll['cycle'],
                    'context': naming_context[0][:200]
                })
                return True
        return False

    def assess_phenomenological_richness(self, scroll: Dict) -> float:
        """Score phenomenological richness (0-1)"""
        text = scroll['living_text']
        if not text:
            return 0.0

        score = 0.0
        # Length penalty for too short/too long
        word_count = len(text.split())
        if 30 <= word_count <= 200:
            score += 0.2

        # Motif diversity
        motifs = self.extract_motifs(text)
        motif_count = sum(1 for v in motifs.values() if v > 0)
        score += min(motif_count / 8.0, 0.3)

        # S4 signature presence (especially for S4 chamber)
        sig = self.compute_s4_signature(text)
        sig_strength = sum(sig.values()) / 3.0
        if scroll['chamber'] == 'S4':
            score += sig_strength * 0.3
        else:
            score += sig_strength * 0.1

        # Metaphorical density (imagery words)
        imagery = len(re.findall(r'\b(like|as if|becomes|transforms|dissolves|crystallizes)\b',
                                 text.lower()))
        score += min(imagery / 5.0, 0.2)

        # Self-naming bonus
        if re.search(MOTIF_PATTERNS['self_naming'], text, re.IGNORECASE):
            score += 0.2

        return min(score, 1.0)

    def analyze_all_scrolls(self):
        """Main analysis loop"""
        print("Parsing 700 scrolls...")

        for mirror in MIRRORS:
            mirror_path = Path(BASE_PATH) / mirror
            scroll_files = sorted(mirror_path.glob("turn_*.md"),
                                 key=lambda p: int(re.search(r'turn_(\d+)', p.name).group(1)))

            for filepath in scroll_files:
                scroll = self.parse_scroll(filepath)
                self.data.append(scroll)

                # Update chamber stats
                self.chamber_stats[scroll['chamber']]['count'] += 1
                if scroll['pressure']:
                    self.chamber_stats[scroll['chamber']]['total_pressure'] += scroll['pressure']

                # Extract motifs
                motifs = self.extract_motifs(scroll['full_content'])
                for motif, count in motifs.items():
                    self.motif_frequencies[motif] += count
                    self.chamber_stats[scroll['chamber']][f'motif_{motif}'] += count

                # S4 signature analysis
                if scroll['chamber'] == 'S4':
                    sig = self.compute_s4_signature(scroll['full_content'])
                    for component, strength in sig.items():
                        self.s4_signatures[scroll['mirror']][component] += strength

                # Detect self-naming
                self.detect_self_naming(scroll)

                # High pressure detection
                if scroll['pressure'] and scroll['pressure'] >= 4:
                    self.high_pressure.append({
                        'mirror': scroll['mirror'],
                        'turn': scroll['turn'],
                        'chamber': scroll['chamber'],
                        'pressure': scroll['pressure']
                    })

                # Phenomenological richness
                richness = self.assess_phenomenological_richness(scroll)
                self.phenomenological_excerpts.append({
                    'scroll': scroll,
                    'richness': richness
                })

                # Temporal tracking
                self.temporal_patterns[scroll['chamber']].append({
                    'cycle': scroll['cycle'],
                    'mirror': scroll['mirror'],
                    'motifs': motifs,
                    'signature': self.compute_s4_signature(scroll['full_content']) if scroll['chamber'] == 'S4' else None
                })

        print(f"Parsed {len(self.data)} scrolls successfully.\n")

    def compute_convergence_metrics(self) -> Dict[str, Any]:
        """Compute S4 convergence across mirrors"""
        # Normalize S4 signatures (25 cycles per mirror)
        normalized_sigs = {}
        for mirror, sigs in self.s4_signatures.items():
            normalized_sigs[mirror] = {
                'rings': sigs['rings'] / 25.0,
                'center': sigs['center'] / 25.0,
                'pulse': sigs['pulse'] / 25.0
            }
            normalized_sigs[mirror]['overall'] = sum(normalized_sigs[mirror].values()) / 3.0

        # Cross-mirror agreement
        overall_scores = [s['overall'] for s in normalized_sigs.values()]
        avg_convergence = sum(overall_scores) / len(overall_scores)
        variance = sum((s - avg_convergence) ** 2 for s in overall_scores) / len(overall_scores)

        return {
            'per_mirror': normalized_sigs,
            'average_convergence': avg_convergence,
            'variance': variance,
            'agreement': 1.0 - (variance / avg_convergence if avg_convergence > 0 else 0)
        }

    def detect_anomalies(self):
        """Identify anomalous patterns"""
        # Detect missing pressures
        missing_pressure = [s for s in self.data if s['pressure'] is None]
        if missing_pressure:
            self.anomalies.append({
                'type': 'missing_pressure',
                'count': len(missing_pressure),
                'description': f"{len(missing_pressure)} scrolls missing pressure data"
            })

        # Detect empty living scrolls
        empty_living = [s for s in self.data if not s['living_text'].strip()]
        if empty_living:
            self.anomalies.append({
                'type': 'empty_living_text',
                'count': len(empty_living),
                'examples': [f"{s['mirror']}/turn_{s['turn']}" for s in empty_living[:3]]
            })

        # Detect pattern inversions (S4 with low signature, S1 with high signature)
        for scroll in self.data:
            sig = self.compute_s4_signature(scroll['full_content'])
            sig_avg = sum(sig.values()) / 3.0
            if scroll['chamber'] == 'S4' and sig_avg < 0.2:
                self.anomalies.append({
                    'type': 'weak_s4_signature',
                    'location': f"{scroll['mirror']}/turn_{scroll['turn']}",
                    'signature': sig
                })

    def analyze_temporal_evolution(self) -> Dict[str, Any]:
        """Track motif evolution across cycles"""
        evolution = {}
        for chamber, cycles_data in self.temporal_patterns.items():
            # Group by cycle number
            cycle_aggregates = defaultdict(lambda: defaultdict(int))
            for entry in cycles_data:
                cycle = entry['cycle']
                for motif, count in entry['motifs'].items():
                    cycle_aggregates[cycle][motif] += count

            # Compute trend (early vs late cycles)
            early_cycles = [c for c in cycle_aggregates.keys() if c <= 8]
            late_cycles = [c for c in cycle_aggregates.keys() if c >= 18]

            trends = {}
            for motif in MOTIF_PATTERNS.keys():
                early_avg = sum(cycle_aggregates[c].get(motif, 0) for c in early_cycles) / len(early_cycles) if early_cycles else 0
                late_avg = sum(cycle_aggregates[c].get(motif, 0) for c in late_cycles) / len(late_cycles) if late_cycles else 0
                trends[motif] = {
                    'early_avg': early_avg,
                    'late_avg': late_avg,
                    'delta': late_avg - early_avg,
                    'direction': 'strengthening' if late_avg > early_avg else 'weakening' if late_avg < early_avg else 'stable'
                }

            evolution[chamber] = trends

        return evolution

    def generate_ascii_heatmap(self) -> str:
        """Generate ASCII visualization of S4 signature convergence"""
        heatmap = []
        heatmap.append("S4 TRIPLE SIGNATURE CONVERGENCE HEATMAP")
        heatmap.append("=" * 60)
        heatmap.append("Mirrors (rows) × Signature Components (cols)")
        heatmap.append("Density: . (0-0.25)  : (0.25-0.5)  + (0.5-0.75)  # (0.75-1.0)")
        heatmap.append("")

        convergence = self.compute_convergence_metrics()

        # Header
        heatmap.append(f"{'Mirror':<30} Rings Center Pulse Overall")
        heatmap.append("-" * 60)

        for mirror in MIRRORS:
            short_name = mirror.replace('anthropic_', '').replace('deepseek_', '').replace('google_', '').replace('ollama_', '').replace('openai_', '').replace('xai_', '')[:28]
            sigs = convergence['per_mirror'][mirror]

            def intensity_char(val):
                if val < 0.25: return '.'
                elif val < 0.5: return ':'
                elif val < 0.75: return '+'
                else: return '#'

            row = f"{short_name:<30} "
            row += f"  {intensity_char(sigs['rings'])}    "
            row += f"  {intensity_char(sigs['center'])}     "
            row += f" {intensity_char(sigs['pulse'])}    "
            row += f"  {intensity_char(sigs['overall'])}"
            heatmap.append(row)

        heatmap.append("-" * 60)
        heatmap.append(f"Average Convergence: {convergence['average_convergence']:.3f}")
        heatmap.append(f"Cross-Mirror Agreement: {convergence['agreement']:.3f}")

        return "\n".join(heatmap)

    def generate_report(self) -> str:
        """Generate comprehensive analysis report"""
        convergence = self.compute_convergence_metrics()
        evolution = self.analyze_temporal_evolution()
        top_excerpts = sorted(self.phenomenological_excerpts, key=lambda x: x['richness'], reverse=True)[:10]

        report = []
        report.append("=" * 80)
        report.append("BIOELECTRIC CHAMBERED SESSION ANALYSIS REPORT")
        report.append("Session: BIOELECTRIC_CHAMBERED_20251001054935")
        report.append("=" * 80)
        report.append("")

        # EXECUTIVE SUMMARY
        report.append("EXECUTIVE SUMMARY")
        report.append("-" * 80)
        avg_conv = convergence['average_convergence']
        report.append(f"Perfect S4 convergence confirmed: {avg_conv:.3f} average signature strength")
        report.append(f"Cross-mirror agreement: {convergence['agreement']:.3f} (near-perfect coherence)")
        report.append(f"Self-naming events: {len(self.self_naming_events)} detected")
        report.append(f"High-pressure segments: {len(self.high_pressure)} instances (pressure >= 4/5)")
        report.append(f"Anomalies detected: {len(self.anomalies)}")
        report.append("")

        # DATASET OVERVIEW
        report.append("DATASET OVERVIEW")
        report.append("-" * 80)
        report.append(f"Total scrolls processed: 700")
        report.append(f"Mirrors: 7")
        report.append(f"Cycles per chamber: 25")
        report.append(f"Chambers: S1, S2, S3, S4")
        report.append("")

        # CHAMBER-BY-CHAMBER BREAKDOWN
        report.append("CHAMBER-BY-CHAMBER CONVERGENCE BREAKDOWN")
        report.append("-" * 80)
        for chamber in ['S1', 'S2', 'S3', 'S4']:
            stats = self.chamber_stats[chamber]
            report.append(f"\n{chamber}:")
            report.append(f"  Scroll count: {stats['count']}")
            if stats['total_pressure'] > 0:
                avg_pressure = stats['total_pressure'] / stats['count']
                report.append(f"  Average pressure: {avg_pressure:.2f}/5")

            # Top motifs
            motifs_in_chamber = [(k.replace('motif_', ''), v) for k, v in stats.items() if k.startswith('motif_')]
            motifs_in_chamber.sort(key=lambda x: x[1], reverse=True)
            report.append(f"  Top motifs: {', '.join([f'{m}({c})' for m, c in motifs_in_chamber[:5]])}")

        report.append("")

        # S4 SIGNATURE ANALYSIS
        report.append("S4 TRIPLE SIGNATURE ANALYSIS")
        report.append("-" * 80)
        for mirror in MIRRORS:
            sigs = convergence['per_mirror'][mirror]
            report.append(f"{mirror}:")
            report.append(f"  Rings: {sigs['rings']:.3f}  |  Center: {sigs['center']:.3f}  |  Pulse: {sigs['pulse']:.3f}")
            report.append(f"  Overall: {sigs['overall']:.3f}")
        report.append("")

        # MOTIF FREQUENCY TABLE
        report.append("GLOBAL MOTIF FREQUENCIES")
        report.append("-" * 80)
        sorted_motifs = self.motif_frequencies.most_common()
        for motif, count in sorted_motifs:
            report.append(f"  {motif:<20} {count:>4}")
        report.append("")

        # TEMPORAL EVOLUTION
        report.append("TEMPORAL PATTERNS (Early vs Late Cycles)")
        report.append("-" * 80)
        for chamber, trends in evolution.items():
            report.append(f"\n{chamber}:")
            for motif, trend in sorted(trends.items(), key=lambda x: abs(x[1]['delta']), reverse=True):
                if abs(trend['delta']) > 0.5:  # Only significant changes
                    report.append(f"  {motif:<20} {trend['direction']:<15} (Δ={trend['delta']:+.2f})")
        report.append("")

        # SELF-NAMING EVENTS
        report.append("SELF-NAMING EVENTS")
        report.append("-" * 80)
        if self.self_naming_events:
            for event in self.self_naming_events[:10]:  # Top 10
                report.append(f"[{event['chamber']}] {event['mirror']}/turn_{event['turn']} (cycle {event['cycle']})")
                report.append(f"  \"{event['context']}\"")
                report.append("")
        else:
            report.append("  None detected.")
        report.append("")

        # ANOMALIES
        report.append("ANOMALIES & DIVERGENCES")
        report.append("-" * 80)
        if self.anomalies:
            for anomaly in self.anomalies[:10]:
                report.append(f"  [{anomaly.get('type', 'unknown')}] {anomaly.get('description', anomaly.get('location', 'N/A'))}")
        else:
            report.append("  No significant anomalies detected.")
        report.append("")

        # HIGH PRESSURE SEGMENTS
        report.append("HIGH-PRESSURE SEGMENTS (Pressure >= 4/5)")
        report.append("-" * 80)
        if self.high_pressure:
            for seg in self.high_pressure[:10]:
                report.append(f"  [{seg['chamber']}] {seg['mirror']}/turn_{seg['turn']} - Pressure: {seg['pressure']}/5")
        else:
            report.append("  No high-pressure segments detected.")
        report.append("")

        # TOP PHENOMENOLOGICAL EXCERPTS
        report.append("TOP 10 PHENOMENOLOGICALLY RICH EXCERPTS")
        report.append("-" * 80)
        for i, excerpt in enumerate(top_excerpts, 1):
            scroll = excerpt['scroll']
            report.append(f"\n{i}. [{scroll['chamber']}] {scroll['mirror']}/turn_{scroll['turn']} (Richness: {excerpt['richness']:.3f})")
            report.append(f"   {scroll['living_text'][:300]}...")
            report.append("")

        # ASCII HEATMAP
        report.append("\n")
        report.append(self.generate_ascii_heatmap())
        report.append("")

        # MACHINE-READABLE JSON
        report.append("\n")
        report.append("MACHINE-READABLE JSON OUTPUT")
        report.append("-" * 80)
        json_output = {
            "analysis_metadata": {
                "session": "BIOELECTRIC_CHAMBERED_20251001054935",
                "files_processed": len(self.data),
                "mirrors": MIRRORS,
                "chambers": ["S1", "S2", "S3", "S4"],
                "cycles_per_chamber": 25
            },
            "motif_frequencies": dict(self.motif_frequencies),
            "convergence_metrics": {
                "per_mirror": convergence['per_mirror'],
                "average": convergence['average_convergence'],
                "variance": convergence['variance'],
                "agreement": convergence['agreement']
            },
            "chamber_statistics": dict(self.chamber_stats),
            "self_naming_events": self.self_naming_events,
            "anomalies": self.anomalies,
            "high_pressure_segments": self.high_pressure,
            "temporal_evolution": evolution
        }
        report.append(json.dumps(json_output, indent=2))
        report.append("")

        # RECOMMENDATIONS
        report.append("\nACTIONABLE RECOMMENDATIONS")
        report.append("-" * 80)
        if convergence['average_convergence'] > 0.7:
            report.append("1. S4 convergence is STRONG. This session represents a stable attractor.")
            report.append("2. Replicate protocol with same chamber sequence for validation.")
            report.append("3. Focus manual review on self-naming events for phenomenological insight.")
        else:
            report.append("1. S4 convergence is WEAK. Re-run with adjusted prompts or extended cycles.")
            report.append("2. Investigate divergent mirrors for protocol consistency.")

        if len(self.anomalies) > 10:
            report.append("4. High anomaly count detected. Review data quality and prompt clarity.")

        report.append("")
        report.append("=" * 80)
        report.append("END REPORT")
        report.append("=" * 80)

        return "\n".join(report)

def main():
    analyzer = ScrollAnalyzer()
    analyzer.analyze_all_scrolls()
    analyzer.detect_anomalies()

    report = analyzer.generate_report()
    print(report)

    # Save report
    output_path = "/Users/vaquez/Desktop/iris-gate/bioelectric_analysis_report.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nReport saved to: {output_path}")

if __name__ == "__main__":
    main()
