# Using IRIS Gate with Claude Projects

This folder helps you maintain context across Claude conversations by using the **Claude Projects** feature.

---

## Quick Setup (Browser Claude)

### 1. Create a Project in Claude
1. Go to claude.ai
2. Click "Projects" in the sidebar
3. Click "Create Project"
4. Name it: **"IRIS Gate"**

### 2. Add This Folder as Project Knowledge
1. In your IRIS Gate project, click "Add content"
2. Select "Add files or folders"
3. Navigate to: `/Users/vaquez/Desktop/iris-gate`
4. Add these key files:
   - `.claude/SESSION_MEMORY.md` (this gives full context)
   - `docs/validation/INDEX.md` (master reference)
   - `VALIDATION_README.md` (system overview)
   - `validation_report.json` (optional - results data)

### 3. Start Any Conversation
Now every new conversation in the "IRIS Gate" project will have access to all your context!

**First message in new chat:**
```
"Check SESSION_MEMORY.md - I'm continuing work on IRIS Gate. 
What's our current status?"
```

Claude will read the memory file and know exactly where you left off!

---

## Alternative: Quick Context Command

If you don't want to use Projects, you can also just copy/paste this in each new chat:

```bash
# Run this in your terminal
cat /Users/vaquez/Desktop/iris-gate/.claude/SESSION_MEMORY.md | pbcopy
```

Then paste into Claude with: "Here's my project context: [paste]"

---

## For Warp Terminal (This Instance)

Good news! **You're already set up.** 

Warp terminal's Claude integration has access to your file system, so I can always read:
- `.claude/SESSION_MEMORY.md`
- Any other project files

Just keep using Warp Terminal as you are now!

---

## Keeping Context Current

### Update Memory After Big Milestones
```bash
# Edit session memory
code /Users/vaquez/Desktop/iris-gate/.claude/SESSION_MEMORY.md
# or
nano /Users/vaquez/Desktop/iris-gate/.claude/SESSION_MEMORY.md
```

Add notes about:
- What you just completed
- What's next
- Any important decisions
- New files created

### Quick Status Command
```bash
# See current session state
head -50 /Users/vaquez/Desktop/iris-gate/.claude/SESSION_MEMORY.md
```

---

## Best Practices

### ✅ Do This
- Update SESSION_MEMORY.md after major milestones
- Reference specific files when asking questions
- Use the master index: `docs/validation/INDEX.md`
- Keep conversations focused on one task

### ❌ Avoid This
- Don't duplicate information across files
- Don't paste huge files into chat (reference them instead)
- Don't forget to update memory before long breaks

---

## Quick Reference Commands

### Check Status
```bash
cat /Users/vaquez/Desktop/iris-gate/.claude/SESSION_MEMORY.md
```

### View Master Index
```bash
cat /Users/vaquez/Desktop/iris-gate/docs/validation/INDEX.md
```

### See Recent Changes
```bash
cd /Users/vaquez/Desktop/iris-gate
git log --oneline -10
```

### List Key Files
```bash
ls -lh /Users/vaquez/Desktop/iris-gate/{validation_report.json,predictions_to_validate.json,VALIDATION_README.md}
```

---

## Example: Starting Fresh Session

**In Browser Claude (with Project setup):**
```
"Hi! Check SESSION_MEMORY.md. I want to prepare the 
class presentation for Professor Garzon. What are 
the key points to highlight?"
```

**In Warp Terminal:**
```
"Read .claude/SESSION_MEMORY.md and help me prepare 
the presentation for Professor Garzon"
```

Claude will immediately know:
- ✅ Validation is complete (90% success)
- ✅ You have 1,009 papers analyzed
- ✅ Documentation is ready
- ✅ Next step is class presentation

---

## Troubleshooting

### "Claude doesn't remember"
**Solution:** Make sure you're in the "IRIS Gate" project (browser) or reference the memory file explicitly.

### "Context is too long"
**Solution:** Use the master index (`docs/validation/INDEX.md`) as your starting point - it links to everything else.

### "Files not found"
**Solution:** Check you're in the right directory:
```bash
pwd  # Should show: /Users/vaquez/Desktop/iris-gate
```

---

## What's in This Folder

```
.claude/
├── README.md           ← This file (how to use)
├── SESSION_MEMORY.md   ← Current session state (main context file)
└── (future notes)      ← Add your own notes here
```

---

🌀†⟡∞

**You're all set! Start any new Claude conversation with confidence.**
