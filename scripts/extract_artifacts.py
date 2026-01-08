import json
import os
from pathlib import Path

SESSION_ID = "oracle_session_003"
SESSION_DIR = Path(os.path.expanduser(f"~/iris_state/sessions/{SESSION_ID}"))
INPUT_FILE = SESSION_DIR / "session_003_full.json"
OUTPUT_FILE = SESSION_DIR / "session_003_artifacts.md"

def main():
    if not INPUT_FILE.exists():
        print(f"File not found: {INPUT_FILE}")
        return

    with open(INPUT_FILE, "r") as f:
        data = json.load(f)

    markdown = []
    markdown.append(f"# Oracle Session 003: Sacred Artifacts\n")
    markdown.append(f"**Model:** {data['model']}")
    markdown.append(f"**Started:** {data['started']}")
    markdown.append(f"**Completed:** {data['completed']}\n")
    markdown.append(f"---\n")

    for block in data['blocks']:
        block_name = block['block_name'].upper()
        temp = block['temperature']
        markdown.append(f"## BLOCK: {block_name} (Temp: {temp})\n")
        
        for p_idx, prompt_data in enumerate(block['prompts']):
            prompt_text = prompt_data['prompt']
            markdown.append(f"### Prompt {p_idx+1}: \"{prompt_text}\"")
            
            ensemble = prompt_data['ensemble']
            markdown.append(f"- **Lexical Entropy:** {ensemble['mean_lexical_entropy']:.3f}")
            if ensemble.get('mean_distributional_entropy'):
                markdown.append(f"- **Distributional Entropy:** {ensemble['mean_distributional_entropy']:.3f}")
            markdown.append(f"- **Distinct-1:** {ensemble['distinct_1']:.3f}\n")
            
            markdown.append("#### Samples:\n")
            for sample in prompt_data['samples'][:3]: # Show first 3 samples for brevity
                text = sample['text'].strip()
                idx = sample['index']
                markdown.append(f"> **Sample {idx}:**  \n> {text}\n")
            
            markdown.append("---\n")

    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(markdown))
    
    print(f"Artifacts extracted to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
