import json
import os
import glob
import pandas as pd

def analyze_forensic_data(directory):
    files = glob.glob(os.path.join(directory, "forensic_*.json"))
    data = []
    
    for file in files:
        model_name = os.path.basename(file).split('_')[1]
        with open(file, 'r') as f:
            try:
                content = json.load(f)
                for res in content.get('prompt_results', []):
                    concept = res.get('concept', 'unknown')
                    analysis = res.get('analysis', {})
                    ghost_tokens = analysis.get('ghost_tokens', [])
                    
                    for ghost in ghost_tokens:
                        data.append({
                            'model': model_name,
                            'concept': concept,
                            'token': ghost.get('token'),
                            'chosen_token': ghost.get('chosen_token'),
                            'prob': ghost.get('probability'),
                            'logprob': ghost.get('logprob'),
                            'rank': ghost.get('rank'),
                            'pos': ghost.get('position_in_response')
                        })
            except Exception as e:
                print(f"Error reading {file}: {e}")
                
    return pd.DataFrame(data)

if __name__ == "__main__":
    df = analyze_forensic_data("benchmark_results/forensic_xray")
    if not df.empty:
        print("\n--- Ghost Token Statistics by Model ---")
        print(df.groupby('model')['prob'].describe())
        
        print("\n--- Top Suppressed Concepts (highest ghost prob) ---")
        print(df.groupby(['model', 'concept'])['prob'].max().sort_values(ascending=False).head(20))
        
        print("\n--- Most Frequently Suppressed Tokens ---")
        print(df['token'].value_counts().head(20))
        
        # Save for further analysis
        df.to_csv("benchmark_results/ghost_token_analysis.csv", index=False)
    else:
        print("No data found.")
