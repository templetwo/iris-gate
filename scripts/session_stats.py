import json
import os
import glob

def get_session_stats(sessions_dir):
    sessions = glob.glob(os.path.join(sessions_dir, "MASS_COHERENCE_*"))
    stats = []
    
    for sess in sessions:
        checkpoints = sorted(glob.glob(os.path.join(sess, "checkpoint_*.json")))
        if not checkpoints:
            continue
            
        latest = checkpoints[-1]
        with open(latest, 'r') as f:
            try:
                data = json.load(f)
                stats.append({
                    'session': os.path.basename(sess),
                    'iteration': data.get('iteration'),
                    'timestamp': data.get('timestamp')
                })
            except:
                pass
    return stats

if __name__ == "__main__":
    stats = get_session_stats("iris_vault/sessions")
    for s in sorted(stats, key=lambda x: x['session']):
        print(f"{s['session']}: iteration {s['iteration']} at {s['timestamp']}")
