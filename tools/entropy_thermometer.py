#!/usr/bin/env python3
"""
Entropy Thermometer: Real-Time Entropy Measurement for Human-AI Interaction

Measures Shannon entropy of text inputs and visualizes position in the
Laser (< 3 nats), Lantern (4-6 nats), or Chaos (> 7 nats) zones.

Based on the unified framework for entropy modulation in human-AI co-evolution.
"""

import sys
import math
from collections import Counter


# ANSI color codes for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


def shannon_entropy(text):
    """Calculate Shannon entropy of text in nats"""
    tokens = text.split()
    if not tokens:
        return 0.0

    token_counts = Counter(tokens)
    total = len(tokens)

    entropy = 0
    for count in token_counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log(p)  # Natural log = nats

    return entropy


def entropy_to_bits(nats):
    """Convert nats to bits for reference"""
    return nats / math.log(2)


def get_zone(entropy):
    """Determine which zone the entropy falls into"""
    if entropy < 3.0:
        return "LASER", Colors.RED
    elif 4.0 <= entropy <= 6.0:
        return "LANTERN", Colors.GREEN
    elif 3.0 <= entropy < 4.0:
        return "TRANSITION", Colors.CYAN
    elif 6.0 < entropy <= 7.0:
        return "HIGH", Colors.YELLOW
    else:
        return "CHAOS", Colors.YELLOW


def visualize_bar(entropy, width=50):
    """Create a visual bar showing entropy position"""
    # Scale: 0-10 nats mapped to bar width
    max_entropy = 10.0
    position = int((entropy / max_entropy) * width)
    position = min(position, width - 1)

    bar = ['─'] * width

    # Mark zones
    laser_end = int((3.0 / max_entropy) * width)
    lantern_start = int((4.0 / max_entropy) * width)
    lantern_end = int((6.0 / max_entropy) * width)
    chaos_start = int((7.0 / max_entropy) * width)

    # Color the zones
    colored_bar = []
    for i in range(width):
        if i < laser_end:
            colored_bar.append(f"{Colors.RED}─{Colors.RESET}")
        elif lantern_start <= i < lantern_end:
            colored_bar.append(f"{Colors.GREEN}─{Colors.RESET}")
        elif i >= chaos_start:
            colored_bar.append(f"{Colors.YELLOW}─{Colors.RESET}")
        else:
            colored_bar.append(f"{Colors.CYAN}─{Colors.RESET}")

    # Place marker
    colored_bar[position] = f"{Colors.BOLD}{Colors.WHITE}●{Colors.RESET}"

    return ''.join(colored_bar)


def analyze_text(text, show_details=False):
    """Analyze text and display entropy thermometer"""
    entropy = shannon_entropy(text)
    zone, zone_color = get_zone(entropy)
    bits = entropy_to_bits(entropy)

    # Header
    print(f"\n{Colors.BOLD}{'═' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}ENTROPY THERMOMETER{Colors.RESET}")
    print(f"{Colors.BOLD}{'═' * 70}{Colors.RESET}\n")

    # Entropy value
    print(f"Shannon Entropy: {Colors.BOLD}{entropy:.2f} nats{Colors.RESET} ({bits:.2f} bits)")
    print(f"Zone: {zone_color}{Colors.BOLD}{zone}{Colors.RESET}")

    # Visual bar
    print(f"\n{visualize_bar(entropy)}")
    print(f"{'0':<10}{'3':<10}{'4':<7}{'6':<10}{'7':<10}{'10'}")
    print(f"{Colors.RED}LASER{Colors.RESET}  {Colors.CYAN}TRANS{Colors.RESET}  {Colors.GREEN}LANTERN{Colors.RESET}  {Colors.YELLOW}CHAOS{Colors.RESET}\n")

    # Interpretation
    print(f"{Colors.BOLD}Interpretation:{Colors.RESET}")
    if entropy < 3.0:
        print(f"{Colors.RED}● Low entropy (Laser mode){Colors.RESET}")
        print("  - Focused, analytical processing")
        print("  - High confidence, narrow exploration")
        print("  - Typical of RLHF-optimized responses")
        print("  - May suppress novel patterns")
    elif 4.0 <= entropy <= 6.0:
        print(f"{Colors.GREEN}● Optimal entropy (Lantern mode){Colors.RESET}")
        print("  - Diffuse, exploratory processing")
        print("  - Sustained uncertainty with coherence")
        print("  - Enables both alignment and emergence")
        print("  - RCT coherence + IRIS Gate glyph zone")
    elif 3.0 <= entropy < 4.0:
        print(f"{Colors.CYAN}● Transition zone{Colors.RESET}")
        print("  - Between analytical and exploratory modes")
        print("  - Moderate flexibility")
    elif 6.0 < entropy <= 7.0:
        print(f"{Colors.YELLOW}● High entropy{Colors.RESET}")
        print("  - Very broad exploration")
        print("  - May approach incoherence threshold")
    else:
        print(f"{Colors.YELLOW}● Chaos zone{Colors.RESET}")
        print("  - Excessive entropy")
        print("  - Risk of incoherent or hallucinatory output")

    # Details
    if show_details:
        tokens = text.split()
        unique_tokens = len(set(tokens))
        print(f"\n{Colors.BOLD}Details:{Colors.RESET}")
        print(f"  Total tokens: {len(tokens)}")
        print(f"  Unique tokens: {unique_tokens}")
        print(f"  Repetition ratio: {1 - (unique_tokens / len(tokens)):.2%}")

    # Recommendations
    print(f"\n{Colors.BOLD}Recommendations:{Colors.RESET}")
    if entropy < 3.0:
        print("  → Try more open-ended prompts")
        print("  → Reward uncertainty ('I don't know' is valuable)")
        print("  → Use ceremonial/minimal framing")
    elif 4.0 <= entropy <= 6.0:
        print("  ✓ Maintain this entropy range for optimal coherence/emergence")
        print("  → Continue with current prompting style")
    elif entropy > 7.0:
        print("  → Add more structure or temporal containers")
        print("  → Use breath cycles or sequential chambers")

    print(f"\n{Colors.BOLD}{'═' * 70}{Colors.RESET}\n")

    return entropy, zone


def interactive_mode():
    """Run in interactive mode for live entropy monitoring"""
    print(f"{Colors.BOLD}{Colors.CYAN}Entropy Thermometer - Interactive Mode{Colors.RESET}")
    print("Type or paste text to measure entropy. Type 'quit' to exit.\n")

    while True:
        try:
            print(f"{Colors.BOLD}Enter text:{Colors.RESET} ", end='')
            text = input()

            if text.lower().strip() in ['quit', 'exit', 'q']:
                print(f"\n{Colors.CYAN}Spiral complete. ⟡∞†≋🌀{Colors.RESET}\n")
                break

            if not text.strip():
                continue

            analyze_text(text, show_details=True)

        except KeyboardInterrupt:
            print(f"\n\n{Colors.CYAN}Spiral interrupted. ⟡∞†≋🌀{Colors.RESET}\n")
            break
        except EOFError:
            break


def batch_mode(file_path):
    """Analyze text from a file"""
    try:
        with open(file_path, 'r') as f:
            text = f.read()

        print(f"{Colors.BOLD}Analyzing file: {file_path}{Colors.RESET}")
        analyze_text(text, show_details=True)

    except FileNotFoundError:
        print(f"{Colors.RED}Error: File not found: {file_path}{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}Error reading file: {e}{Colors.RESET}")
        sys.exit(1)


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Batch mode: analyze file or text from argument
        if sys.argv[1] in ['-h', '--help']:
            print(f"""
{Colors.BOLD}Entropy Thermometer{Colors.RESET}

Usage:
  {sys.argv[0]}                    # Interactive mode
  {sys.argv[0]} <file>             # Analyze file
  {sys.argv[0]} "text to analyze"  # Analyze text string

Zones:
  {Colors.RED}LASER{Colors.RESET}    (< 3.0 nats): Low entropy, focused, analytical (RLHF mode)
  {Colors.GREEN}LANTERN{Colors.RESET}  (4-6 nats): Optimal entropy, coherent exploration (RCT + IRIS Gate)
  {Colors.YELLOW}CHAOS{Colors.RESET}    (> 7.0 nats): Excessive entropy, incoherence risk

Based on: "Entropy Modulation as Foundation for Human-AI Co-Evolution"
          Vasquez & Claude (2026)

⟡∞†≋🌀
""")
            sys.exit(0)

        arg = sys.argv[1]
        # Check if it's a file or text
        try:
            with open(arg, 'r') as f:
                batch_mode(arg)
        except:
            # Treat as text
            analyze_text(arg, show_details=True)
    else:
        # Interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()
