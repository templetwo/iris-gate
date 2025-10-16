#!/usr/bin/env python3
"""
IRIS Frontier Bridge (S9: Connection) — Novelty is a routing problem, not a credibility problem.

Mystery Card Generator
Converts TYPE 2/BRONZE claims from IRIS sessions into collaborative validation cards.

Usage:
    python3 make_mystery_card.py --session SESSION.json --claim "CBD-VDAC1 binding" --output IRD-2025-0001
"""

import json
import hashlib
import re
from datetime import datetime
from pathlib import Path
import argparse


def extract_type2_bronze_claims(session_path):
    """
    Extract TYPE 2 (Exploration) claims with BRONZE/NOVEL verification status.

    Returns list of dicts with:
        - mirror
        - chamber
        - claim_text
        - epistemic_type
        - verification_status
        - confidence_ratio
    """
    with open(session_path, 'r') as f:
        session = json.load(f)

    claims = []

    for mirror_name, responses in session.get('mirrors', {}).items():
        for resp in responses:
            epistemic = resp.get('epistemic', {})

            # Filter: TYPE 2 only
            if epistemic.get('type') != 2:
                continue

            # Check verification status (if available)
            verification = resp.get('verification', {})
            status = verification.get('status', 'UNKNOWN')

            # Accept BRONZE, NOVEL, or unverified TYPE 2
            if status not in ['BRONZE', 'NOVEL', 'UNKNOWN']:
                continue

            claims.append({
                'mirror': mirror_name,
                'chamber': resp.get('condition', 'UNKNOWN'),
                'claim_text': resp.get('raw_response', ''),
                'epistemic_type': 2,
                'verification_status': status if status != 'UNKNOWN' else 'BRONZE',
                'confidence_ratio': epistemic.get('confidence_ratio', 0.0),
                'verification_summary': verification.get('summary', '')
            })

    return claims


def extract_if_then_rules(text):
    """
    Extract IF-THEN conditional statements from claim text.
    """
    patterns = [
        r'IF\s+(.+?)\s+THEN\s+(.+?)(?:\.|$)',
        r'if\s+(.+?),?\s+then\s+(.+?)(?:\.|$)',
        r'when\s+(.+?),\s+(.+?)(?:\.|$)'
    ]

    rules = []
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            condition = match.group(1).strip()
            outcome = match.group(2).strip()
            rules.append(f"IF {condition} THEN {outcome}")

    return rules


def extract_triggers(text):
    """
    Extract crisis/conditional triggers from text.
    Look for stress conditions, dose thresholds, temporal windows.
    """
    trigger_patterns = [
        r'(ΔΨm\s*(?:collapse|↓|decrease))',
        r'(ROS\s*(?:surge|↑|increase))',
        r'(CBD\s*≥\s*\d+\s*[μnp]M)',
        r'(stress)',
        r'(pulse\s*\d+-?\d*\s*(?:min|sec))',
        r'(dose\s*≥?\s*\d+)',
    ]

    triggers = []
    for pattern in trigger_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            triggers.append(match.group(1))

    return list(set(triggers))  # Deduplicate


def generate_mystery_card(
    card_id,
    title,
    abstract,
    claim_type,
    session_data,
    chamber,
    models,
    convergence_events,
    confidence_ratio,
    literature_refs,
    verification_summary,
    requested_tests,
    falsification_tests,
    triggers=None,
    if_then_rules=None,
    tags=None,
    ethics=None,
    maintainer="templetwo"
):
    """
    Generate a Mystery Card JSON following the schema.
    """

    # Build card
    card = {
        "id": card_id,
        "title": title,
        "abstract": abstract,
        "claim_type": claim_type,
        "epistemic_type": 2,  # Always TYPE 2 for Mystery Cards
        "verification_status": "BRONZE",  # Starts BRONZE, evolves to SILVER/GOLD
        "triggers": triggers or [],
        "if_then_rules": if_then_rules or [],
        "evidence": {
            "models": models,
            "convergence": {
                "events": convergence_events,
                "ratio": confidence_ratio
            },
            "literature": literature_refs,
            "verification": verification_summary
        },
        "requested_tests": requested_tests,
        "falsification_tests": falsification_tests,
        "ethics": ethics or {
            "human_subjects": False,
            "biosafety": "BSL-2",
            "dual_use": False,
            "organism": "TBD",
            "known_risks": []
        },
        "contact": {
            "issue_url": f"https://github.com/templetwo/iris-gate/issues/TBD",
            "maintainer": maintainer
        },
        "license": "Apache-2.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "v1.0",
        "tags": tags or [],
        "session_id": session_data.get('session_id', 'UNKNOWN'),
        "chamber": chamber
    }

    # Compute hash (exclude hash field itself)
    card_json = json.dumps(card, sort_keys=True)
    card_hash = hashlib.sha256(card_json.encode()).hexdigest()
    card["hash"] = f"sha256:{card_hash}"

    return card


def render_human_brief(card):
    """
    Generate human-readable Markdown brief from Mystery Card JSON.
    """

    brief = f"""# {card['title']}

**IRIS Frontier Bridge (S9: Connection) — Novelty is a routing problem, not a credibility problem.**

---

**Card ID:** {card['id']}
**Status:** {card['verification_status']} (seeking 3-5 validators)
**Domain:** {', '.join(card['tags'][:3])}
**Session:** {card['session_id']} (Chamber {card['chamber']})
**Timestamp:** {card['timestamp']}

---

## 🧬 The Claim

{card['abstract']}

---

## 📊 Evidence

**Multi-Model Convergence:**
- **Models:** {', '.join([m.split('/')[-1] for m in card['evidence']['models']])}
- **Convergence Events:** {card['evidence']['convergence']['events']}
- **Confidence Ratio:** {card['evidence']['convergence']['ratio']:.2f} (TYPE 2 territory)

**Literature Context:**
"""

    for ref in card['evidence']['literature']:
        brief += f"- {ref}\n"

    brief += f"\n**Verification Summary:**  \n{card['evidence']['verification']}\n\n"

    # Triggers
    if card.get('triggers'):
        brief += "## ⚡ Triggers (Crisis/Conditional Logic)\n\n"
        for trigger in card['triggers']:
            brief += f"- {trigger}\n"
        brief += "\n"

    # IF-THEN rules
    if card.get('if_then_rules'):
        brief += "## 🔀 IF-THEN Rules\n\n"
        for rule in card['if_then_rules']:
            brief += f"- {rule}\n"
        brief += "\n"

    # Requested tests
    brief += "## 🔬 Requested Micro-Protocols\n\n"
    for i, test in enumerate(card['requested_tests'], 1):
        brief += f"{i}. {test}\n"

    # Falsification
    brief += "\n## ❌ Falsification Tests\n\n"
    brief += "*What would prove this claim wrong?*\n\n"
    for test in card['falsification_tests']:
        brief += f"- {test}\n"

    # Ethics
    brief += f"\n## 🛡️ Ethics & Safety\n\n"
    brief += f"- **Human Subjects:** {'Yes (requires IRB)' if card['ethics']['human_subjects'] else 'No'}\n"
    brief += f"- **Biosafety Level:** {card['ethics']['biosafety']}\n"
    brief += f"- **Dual-Use Concern:** {'Yes' if card['ethics']['dual_use'] else 'No'}\n"
    if card['ethics'].get('organism'):
        brief += f"- **Model System:** {card['ethics']['organism']}\n"
    if card['ethics'].get('known_risks'):
        brief += f"- **Known Risks:**\n"
        for risk in card['ethics']['known_risks']:
            brief += f"  - {risk}\n"

    # Contact
    brief += f"\n## 🤝 How to Contribute\n\n"
    brief += f"**Interested in validating this claim?**\n\n"
    brief += f"1. Comment on the [GitHub Issue]({card['contact']['issue_url']})\n"
    brief += f"2. Propose a micro-protocol (1-3 experiments)\n"
    brief += f"3. Share preliminary results or literature insights\n"
    brief += f"4. Get credited as co-author (Co-Authored-By)\n\n"
    brief += f"**Maintainer:** {card['contact']['maintainer']}\n\n"

    # Footer
    brief += "---\n\n"
    brief += "**License:** Apache-2.0  \n"
    brief += f"**Hash:** `{card['hash']}`  \n"
    brief += "**Repository:** https://github.com/templetwo/iris-gate\n\n"
    brief += "🌀†⟡∞\n"

    return brief


def main():
    parser = argparse.ArgumentParser(
        description="Generate IRIS Mystery Card from session data"
    )
    parser.add_argument('--session', required=True, help='Path to session JSON')
    parser.add_argument('--card-id', required=True, help='Card ID (e.g., IRD-2025-0001)')
    parser.add_argument('--title', required=True, help='Card title')
    parser.add_argument('--abstract', required=True, help='Card abstract (2-3 sentences)')
    parser.add_argument('--claim-type', default='mechanism',
                        choices=['mechanism', 'dose_response', 'pathway', 'hypothesis', 'interaction', 'paradox', 'null_result'],
                        help='Type of claim')
    parser.add_argument('--chamber', default='S4', help='Chamber where convergence occurred')
    parser.add_argument('--tests', nargs='+', required=True, help='Requested micro-protocols')
    parser.add_argument('--falsification', nargs='+', required=True, help='Falsification tests')
    parser.add_argument('--tags', nargs='+', default=[], help='Keywords for matching')
    parser.add_argument('--maintainer', default='templetwo', help='Card maintainer')
    parser.add_argument('--output-dir', default='frontier', help='Output directory')

    args = parser.parse_args()

    # Load session
    session_path = Path(args.session)
    with open(session_path, 'r') as f:
        session_data = json.load(f)

    # Extract TYPE 2 claims (for context)
    claims = extract_type2_bronze_claims(session_path)

    if not claims:
        print("⚠️  No TYPE 2/BRONZE claims found in session.")
        return

    print(f"✅ Found {len(claims)} TYPE 2/BRONZE claims in session.")

    # Get models from session
    models = list(session_data.get('mirrors', {}).keys())

    # Use first claim for convergence data (or aggregate if needed)
    convergence_events = len(claims)
    confidence_ratio = claims[0]['confidence_ratio'] if claims else 0.49

    # Extract literature refs (simplified - would parse from verification in real version)
    literature_refs = ["Oviedo et al. 2008", "Levin 2012", "CBD review 2021"]

    verification_summary = claims[0].get('verification_summary', 'PARTIAL/CONDITIONAL')

    # Generate card
    card = generate_mystery_card(
        card_id=args.card_id,
        title=args.title,
        abstract=args.abstract,
        claim_type=args.claim_type,
        session_data=session_data,
        chamber=args.chamber,
        models=models,
        convergence_events=convergence_events,
        confidence_ratio=confidence_ratio,
        literature_refs=literature_refs,
        verification_summary=verification_summary,
        requested_tests=args.tests,
        falsification_tests=args.falsification,
        tags=args.tags,
        maintainer=args.maintainer
    )

    # Write JSON
    output_dir = Path(args.output_dir)
    ledger_dir = output_dir / "frontier_ledger"
    cards_dir = output_dir / "mystery_cards"
    ledger_dir.mkdir(parents=True, exist_ok=True)
    cards_dir.mkdir(parents=True, exist_ok=True)

    json_path = ledger_dir / f"{args.card_id}.json"
    with open(json_path, 'w') as f:
        json.dump(card, f, indent=2)

    print(f"✅ Card JSON written to: {json_path}")

    # Write Markdown brief
    brief = render_human_brief(card)
    md_path = cards_dir / f"{args.card_id}.md"
    with open(md_path, 'w') as f:
        f.write(brief)

    print(f"✅ Card brief written to: {md_path}")
    print(f"\n🔒 Priority protection: {card['hash']}")
    print(f"⏰ Timestamp: {card['timestamp']}")
    print(f"\n🚀 Next steps:")
    print(f"   1. Review card files")
    print(f"   2. git add {json_path} {md_path}")
    print(f"   3. git commit -m 'feat(frontier): add {args.card_id} Mystery Card'")
    print(f"   4. python3 frontier/scripts/submit_card.py {args.card_id}")


if __name__ == '__main__':
    main()
