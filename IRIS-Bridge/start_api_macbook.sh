#!/bin/bash
cd "$(dirname "$0")"
source env_macbook.sh

echo "🚀 Starting IRIS-Bridge API Service (MacBook Pro)"
python3 -m uvicorn services.dialogue_api:app --host 0.0.0.0 --port 8788
