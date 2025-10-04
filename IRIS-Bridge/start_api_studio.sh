#!/bin/bash
cd "$(dirname "$0")"
source env_studio.sh

echo "🚀 Starting IRIS-Bridge API Service (Mac Studio)"
python3 -m uvicorn services.dialogue_api:app --host 0.0.0.0 --port 8787
