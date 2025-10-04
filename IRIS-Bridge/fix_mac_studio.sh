#!/bin/bash
# Fix Mac Studio IRIS-Bridge service with correct token

echo "🔧 Fixing Mac Studio IRIS-Bridge..."

# Kill existing service
ssh tony_studio@anthonys-mac-studio.tail99990f.ts.net "kill 72480 2>/dev/null; sleep 2"

# Create startup script on Mac Studio
ssh tony_studio@anthonys-mac-studio.tail99990f.ts.net "cat > /Users/tony_studio/Desktop/IRIS-Bridge/start_api.sh << 'EOF'
#!/bin/bash
export DIALOGUE_AUTH_TOKEN=\"iris-bridge-autonomous-sync-2025\"
export PEER_BASE_URL=\"http://100.93.122.63:8788\"
cd /Users/tony_studio/Desktop/IRIS-Bridge
python3 -m uvicorn services.dialogue_api:app --host 0.0.0.0 --port 8787
EOF"

# Make it executable
ssh tony_studio@anthonys-mac-studio.tail99990f.ts.net "chmod +x /Users/tony_studio/Desktop/IRIS-Bridge/start_api.sh"

# Start service
echo "🚀 Starting Mac Studio service with correct token..."
ssh tony_studio@anthonys-mac-studio.tail99990f.ts.net "cd /Users/tony_studio/Desktop/IRIS-Bridge && nohup ./start_api.sh > api.log 2>&1 & echo \$!"

sleep 3

# Test
echo "🧪 Testing connection..."
curl -sS -H "Authorization: Bearer iris-bridge-autonomous-sync-2025" http://100.72.59.69:8787/health

echo ""
echo "✅ Done! Mac Studio should now accept the correct token."
