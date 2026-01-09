import json
import re

def find_proposals(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    proposal_pattern = r'([^.!?]*\b(?:propose|predict|hypothesis|conjecture|suggest|novel|new)\b[^.!?]*[.!?])'
    proposals = []
    
    probe_results = data.get('probe_results', {})
    for probe_id, responses in probe_results.items():
        for res in responses:
            arch = res.get('architecture')
            model = res.get('model')
            text = res.get('response')
            if not isinstance(text, str):
                continue
            
            for match in re.finditer(proposal_pattern, text, re.IGNORECASE):
                p_text = match.group(1).strip()
                if len(p_text) >= 100:
                    proposals.append({
                        'arch': arch,
                        'model': model,
                        'probe': probe_id,
                        'text': p_text
                    })
    
    # Deduplicate
    seen = set()
    unique = []
    for p in proposals:
        key = (p['arch'], p['text'][:50])
        if key not in seen:
            seen.add(key)
            unique.append(p)
            
    return unique

if __name__ == "__main__":
    file_path = 'iris_vault/sessions/MASS_COHERENCE_20260109_041127/checkpoint_013.json'
    proposals = find_proposals(file_path)
    
    print(f"Found {len(proposals)} unique proposals:\n")
    for i, p in enumerate(proposals):
        print(f"[{i+1}] {p['arch'].upper()} ({p['model']}) - {p['probe']}")
        print(f"    {p['text']}\n")
