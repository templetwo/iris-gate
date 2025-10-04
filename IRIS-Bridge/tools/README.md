# 🛠️ IRIS-Bridge Tools

**Utility scripts for monitoring, maintenance, and analysis**

---

## 📊 monitor.py

**Real-time dialogue monitoring dashboard**

### Features:
- Live system status for both machines
- Inbox message counts
- Recent message feed with timestamps
- Message statistics (total, AI, user)
- Auto-refresh every 3 seconds

### Usage:
```bash
python3 tools/monitor.py
```

### Requirements:
- Services must be running on both machines
- `httpx` library installed
- Network access to Mac Studio

### Keyboard:
- `Ctrl+C` to exit

---

## 🗄️ archive_inbox.py

**Inbox archival and maintenance tool**

### Features:
- Archives old messages to keep inboxes fast
- Keeps last 100 messages active (configurable)
- Creates timestamped archive files
- Safe operation with full backup

### Usage:
```bash
# Archive all inboxes
python3 tools/archive_inbox.py

# Archives saved to: dialogue/archives/
```

### Configuration:
Edit `KEEP_RECENT_N` in the file to change retention count (default: 100)

### When to Use:
- When inbox files exceed 200 messages
- Weekly maintenance schedule recommended
- Before deploying to production

---

## 🔬 compare_sessions.py

**IRIS session comparison and analysis**

### Features:
- Compares two IRIS sessions side-by-side
- Extracts attractor patterns from S4 scrolls
- Calculates convergence scores
- Finds pattern overlap and unique elements
- Saves detailed comparison reports

### Usage:
```bash
# Compare two most recent sessions
python3 tools/compare_sessions.py

# Output saved to: dialogue/comparisons/
```

### Requirements:
- At least 2 session files in `iris_vault/`
- Sessions must have S4 attractor data

### Output:
- Console: Formatted comparison report
- File: JSON with full analysis data

---

## 🔧 Quick Reference

### Check System Health:
```bash
# View real-time status
python3 tools/monitor.py
```

### Weekly Maintenance:
```bash
# Clean up old messages
python3 tools/archive_inbox.py

# Analyze session patterns
python3 tools/compare_sessions.py
```

### Debugging:
```bash
# Check if services are running
ps aux | grep -E "(dialogue_loop|dialogue_api)"

# View recent logs
tail -f ../logs_api.txt
tail -f ../loop_new.log
```

---

## 📝 Notes

### Tool Dependencies:
- All tools use Python 3.10+
- `httpx` required for monitor.py
- Standard library otherwise

### File Locations:
- **Inboxes:** `../dialogue/inbox/`
- **Archives:** `../dialogue/archives/`
- **Comparisons:** `../dialogue/comparisons/`
- **Sessions:** `../../iris_vault/`

### Best Practices:
1. Run monitor in a separate terminal
2. Archive inboxes weekly or at 200+ messages
3. Compare sessions after each IRIS run
4. Keep archives for historical analysis

---

**Created:** 2025-10-04  
**Version:** 1.0  
**Status:** Production Ready ✨
