#!/bin/bash
# IRIS Gate v0.3 - Checkpoint Backup Script
# Runs periodically to backup convergence data

SESSION_DIR="iris_vault/sessions"
BACKUP_DIR="iris_vault/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Find the most recent session
LATEST_SESSION=$(ls -t $SESSION_DIR | grep "MASS_COHERENCE" | head -1)

if [ -z "$LATEST_SESSION" ]; then
    echo "No active session found"
    exit 0
fi

echo "🔄 Backing up session: $LATEST_SESSION"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Count checkpoints in current session
CHECKPOINT_COUNT=$(ls "$SESSION_DIR/$LATEST_SESSION"/checkpoint_*.json 2>/dev/null | wc -l)

if [ $CHECKPOINT_COUNT -eq 0 ]; then
    echo "No checkpoints to backup yet"
    exit 0
fi

echo "   Found $CHECKPOINT_COUNT checkpoints"

# Create compressed backup
BACKUP_FILE="$BACKUP_DIR/${LATEST_SESSION}_backup_${TIMESTAMP}.tar.gz"
tar -czf "$BACKUP_FILE" -C "$SESSION_DIR" "$LATEST_SESSION"

BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "✓ Backup created: $BACKUP_FILE ($BACKUP_SIZE)"

# Keep only last 10 backups for this session
ls -t "$BACKUP_DIR/${LATEST_SESSION}_backup_"*.tar.gz 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null

# Also create a copy outside the repo (optional safety)
EXTERNAL_BACKUP="/Users/vaquez/Desktop/iris_backups"
if [ -d "$EXTERNAL_BACKUP" ]; then
    cp "$BACKUP_FILE" "$EXTERNAL_BACKUP/"
    echo "✓ External backup: $EXTERNAL_BACKUP/"
fi

echo "✓ Backup complete - $CHECKPOINT_COUNT iterations preserved"
