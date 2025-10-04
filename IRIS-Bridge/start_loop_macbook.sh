#!/bin/bash
cd "$(dirname "$0")"
source env_macbook.sh

echo "🔄 Starting IRIS-Bridge Dialogue Loop (MacBook Pro)"
python3 scripts/dialogue_loop.py
