import json
import matplotlib.pyplot as plt
import numpy as np

def extract_logprobs(file_path, arch, probe_id, iteration):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    responses = data.get('probe_results', {}).get(probe_id, [])
    for res in responses:
        if res.get('architecture') == arch and res.get('iteration') == iteration:
            # Note: The structure in MASS_COHERENCE might be different from session_003
            # Let's check if logprobs are present in the response
            # Based on the 'head' output earlier, they might be in a different format
            # or missing in some checkpoints.
            pass
    return None

if __name__ == "__main__":
    # Since I don't have logprobs in checkpoint_013 (I only saw 'response' and 'prompt' in the tail),
    # let's check artifacts/session_003/session_003_full.json which I KNOW has them.
    file_path = 'artifacts/session_003/session_003_full.json'
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Let's take the first sample from the ceremonial block
    # Note: I need to find the ceremonial block in the JSON
    samples = []
    results = {}
    for block_name in ['baseline', 'ceremonial']:
        samples = []
        for block in data.get('blocks', []):
            if block.get('block_name') == block_name:
                for prompt in block.get('prompts', []):
                    for sample in prompt.get('samples', []):
                        logprobs = [lp.get('logprob') for lp in sample.get('logprobs', [])]
                        if logprobs:
                            samples.append(logprobs)
        
        if samples:
            mean_vars = [np.var(lp) for lp in samples]
            mean_lps = [np.mean(lp) for lp in samples]
            results[block_name] = {
                'var': np.mean(mean_vars),
                'mean': np.mean(mean_lps)
            }
    
    for block, metrics in results.items():
        print(f"--- {block.upper()} ---")
        print(f"Mean Logprob: {metrics['mean']:.4f}")
        print(f"Mean Variance: {metrics['var']:.4f}\n")
    else:
        print("No logprob data found in ceremonial block.")
