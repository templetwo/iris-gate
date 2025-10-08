#!/bin/bash
# Quick context copier for browser Claude
# Usage: ./.claude/copy-context.sh

echo "🌀 IRIS Gate Context Copier"
echo ""
echo "Copying session memory to clipboard..."

# Check if file exists
if [ ! -f ".claude/SESSION_MEMORY.md" ]; then
    echo "❌ Error: SESSION_MEMORY.md not found"
    echo "   Make sure you're in the iris-gate directory"
    exit 1
fi

# Copy to clipboard
cat .claude/SESSION_MEMORY.md | pbcopy

echo "✅ Context copied to clipboard!"
echo ""
echo "Now in browser Claude, paste and say:"
echo "   'Here's my project context: [paste]'"
echo ""
echo "Or better yet, set up a Claude Project:"
echo "   Read .claude/README.md for instructions"
echo ""
echo "🌀†⟡∞"
