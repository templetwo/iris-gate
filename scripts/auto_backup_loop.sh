#!/bin/bash
# IRIS Gate v0.3 - Automatic Checkpoint Backup Loop
# Backs up every 5 iterations while convergence is running

SESSION_DIR="iris_vault/sessions"
BACKUP_DIR="iris_vault/backups"
DESKTOP_BACKUP="$HOME/Desktop/iris_backups"

# Find active session
ACTIVE_SESSION=$(ls -t $SESSION_DIR | grep "MASS_COHERENCE" | head -1)

if [ -z "$ACTIVE_SESSION" ]; then
    echo "No active session found"
    exit 0
fi

echo "🔄 Auto-backup loop started for: $ACTIVE_SESSION"
echo "   Backup interval: Every 5 iterations"
echo "   Press Ctrl+C to stop"

LAST_BACKUP_COUNT=0

while true; do
    # Count current checkpoints
    CHECKPOINT_COUNT=$(ls "$SESSION_DIR/$ACTIVE_SESSION"/checkpoint_*.json 2>/dev/null | wc -l | tr -d ' ')

    # Backup every 5 iterations
    if [ $CHECKPOINT_COUNT -gt 0 ] && [ $(($CHECKPOINT_COUNT % 5)) -eq 0 ] && [ $CHECKPOINT_COUNT -ne $LAST_BACKUP_COUNT ]; then
        TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
        BACKUP_FILE="$BACKUP_DIR/${ACTIVE_SESSION}_iter_$(printf "%03d" $CHECKPOINT_COUNT)_${TIMESTAMP}.tar.gz"

        echo ""
        echo "📦 Iteration $CHECKPOINT_COUNT reached - Creating backup..."
        tar -czf "$BACKUP_FILE" -C "$SESSION_DIR" "$ACTIVE_SESSION"

        BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        echo "   ✓ Backup: $BACKUP_FILE ($BACKUP_SIZE)"

        # Copy to desktop
        cp "$BACKUP_FILE" "$DESKTOP_BACKUP/" 2>/dev/null
        echo "   ✓ Desktop backup: $DESKTOP_BACKUP/"

        LAST_BACKUP_COUNT=$CHECKPOINT_COUNT

        # Clean old backups (keep last 20)
        ls -t "$BACKUP_DIR/${ACTIVE_SESSION}_"*.tar.gz 2>/dev/null | tail -n +21 | xargs rm -f 2>/dev/null
    fi

    # Check every 2 minutes
    sleep 120
done
