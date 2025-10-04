#!/bin/bash
cd "$(dirname "$0")"
source env_studio.sh

echo "🔄 Starting IRIS-Bridge Dialogue Loop (Mac Studio)"
python3 scripts/dialogue_loop.py
