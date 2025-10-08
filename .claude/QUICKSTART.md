# 🚀 Quick Start: Using IRIS Gate with Claude

**Problem:** Browser Claude has short conversation limits  
**Solution:** Use Claude Projects with this folder as knowledge base

---

## Option 1: Claude Projects (RECOMMENDED) 🎯

### Step 1: Create Project
```
1. Go to claude.ai
2. Click "Projects" → "Create Project"
3. Name: "IRIS Gate"
```

### Step 2: Add Knowledge
```
In project settings, add these files:
✅ .claude/SESSION_MEMORY.md       (main context)
✅ docs/validation/INDEX.md        (master index)
✅ VALIDATION_README.md            (overview)
```

### Step 3: Start Chatting
```
Every new chat in "IRIS Gate" project automatically 
has your context. Just ask questions!

Example first message:
"What's our current validation status?"
```

**That's it!** ✨

---

## Option 2: Quick Copy/Paste 📋

### When Starting New Browser Chat:
```bash
# In terminal:
cd /Users/vaquez/Desktop/iris-gate
./.claude/copy-context.sh

# Then in browser Claude, paste and say:
"Here's my project context: [paste]"
```

---

## Option 3: Warp Terminal (What You're Using Now) ⚡

**You're already set!** 

Warp's Claude can read your files directly. Just say:
```
"Read .claude/SESSION_MEMORY.md and [your request]"
```

---

## What You Get

### 🎯 Full Context Every Time
- Your 90% validation success
- All 1,009 papers analyzed
- Complete project history
- Next steps and priorities

### 📚 All Documentation
- Executive summary for professor
- Quick reference tables
- Full technical details
- Commands and examples

### 🔄 Always Up-to-Date
- Update SESSION_MEMORY.md after milestones
- Claude always reads latest version
- No re-explaining needed

---

## Quick Commands

### Copy context to clipboard
```bash
cd /Users/vaquez/Desktop/iris-gate
./.claude/copy-context.sh
```

### View current status
```bash
cat .claude/SESSION_MEMORY.md
```

### Check validation results
```bash
cat validation_report.json | head -50
```

---

## File Structure

```
iris-gate/
├── .claude/
│   ├── QUICKSTART.md         ← You are here
│   ├── README.md             ← Full instructions
│   ├── SESSION_MEMORY.md     ← Current context
│   └── copy-context.sh       ← Helper script
│
├── docs/validation/
│   └── INDEX.md              ← Master reference
│
├── presentations/
│   ├── IRIS_VALIDATION_EXECUTIVE_SUMMARY.md
│   └── VALIDATION_RESULTS_TABLE.md
│
├── validation_report.json    ← Full results
└── predictions_to_validate.json
```

---

## Example Usage

### Starting Fresh in Browser Claude:

**Without Projects:**
```
1. Run: ./.claude/copy-context.sh
2. Paste in Claude
3. Ask: "Help me prepare the class presentation"
```

**With Projects:**
```
1. Open "IRIS Gate" project
2. Ask: "Help me prepare the class presentation"
   (Context loaded automatically!)
```

### Continuing in Warp Terminal:
```
"Read SESSION_MEMORY.md. Let's work on the 
class presentation for Professor Garzon."
```

---

## Tips

✅ **Update memory regularly** - After big milestones  
✅ **Use Projects** - Best long-term solution  
✅ **Reference files** - "Check INDEX.md" not copy/paste  
✅ **Stay organized** - One task per conversation

❌ **Don't repeat context** - It's all saved  
❌ **Don't paste huge files** - Reference them  
❌ **Don't forget updates** - Keep memory current

---

## Need Help?

**Read detailed guide:**
```bash
cat .claude/README.md
```

**Check master index:**
```bash
cat docs/validation/INDEX.md
```

**View all files:**
```bash
ls -lh .claude/
```

---

## You're Ready! 🎉

**Current Status:**
- ✅ Literature validation: 90% success
- ✅ 1,009 papers analyzed
- ✅ Documentation complete
- ✅ Context preservation: active

**Next Step:**
- Choose Option 1 (Projects) or Option 2 (Copy/paste)
- Start using browser Claude with full context
- Never lose your place again!

🌀†⟡∞

**Go forth and conquer those conversation limits!**
