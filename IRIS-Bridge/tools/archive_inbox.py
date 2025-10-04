#!/usr/bin/env python3
"""
IRIS-Bridge Inbox Archival Tool
Manages inbox JSONL files by archiving old messages while keeping recent ones active
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

# Configuration
KEEP_RECENT_N = 100  # Keep last 100 messages active
ARCHIVE_DIR_NAME = "archives"

def archive_inbox(inbox_file: Path, keep_recent: int = KEEP_RECENT_N):
    """
    Archive old messages from inbox JSONL file
    
    Args:
        inbox_file: Path to the inbox JSONL file
        keep_recent: Number of recent messages to keep active
    """
    if not inbox_file.exists():
        print(f"✅ No inbox file found at {inbox_file}, nothing to archive")
        return
    
    # Read all messages
    messages = []
    with open(inbox_file, 'r') as f:
        for line in f:
            if line.strip():
                messages.append(json.loads(line))
    
    print(f"📊 Found {len(messages)} total messages in {inbox_file.name}")
    
    if len(messages) <= keep_recent:
        print(f"✅ Message count ({len(messages)}) is within limit ({keep_recent}), no archival needed")
        return
    
    # Split into keep vs archive
    messages_to_keep = messages[-keep_recent:]
    messages_to_archive = messages[:-keep_recent]
    
    print(f"📦 Archiving {len(messages_to_archive)} old messages, keeping {len(messages_to_keep)} recent")
    
    # Create archive directory
    archive_dir = inbox_file.parent.parent / ARCHIVE_DIR_NAME
    archive_dir.mkdir(exist_ok=True)
    
    # Create archive file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    archive_file = archive_dir / f"{inbox_file.stem}_archive_{timestamp}.jsonl"
    
    # Write archived messages
    with open(archive_file, 'w') as f:
        for msg in messages_to_archive:
            f.write(json.dumps(msg) + '\n')
    
    print(f"💾 Archived messages saved to: {archive_file}")
    
    # Write remaining messages back to inbox
    with open(inbox_file, 'w') as f:
        for msg in messages_to_keep:
            f.write(json.dumps(msg) + '\n')
    
    print(f"✨ Active inbox now contains {len(messages_to_keep)} messages")
    print(f"🎯 Freed up {len(messages_to_archive)} messages from active processing")

def main():
    """Main archival process"""
    bridge_root = Path(__file__).parent.parent
    inbox_dir = bridge_root / "dialogue" / "inbox"
    
    if not inbox_dir.exists():
        print(f"❌ Inbox directory not found: {inbox_dir}")
        return
    
    # Find all inbox JSONL files
    inbox_files = list(inbox_dir.glob("*.jsonl"))
    
    # Filter out already archived files
    inbox_files = [f for f in inbox_files if "archive" not in f.name]
    
    if not inbox_files:
        print("✅ No active inbox files found, nothing to archive")
        return
    
    print("🌉 IRIS-Bridge Inbox Archival")
    print("=" * 50)
    print()
    
    for inbox_file in inbox_files:
        print(f"\n📁 Processing: {inbox_file.name}")
        print("-" * 50)
        archive_inbox(inbox_file)
    
    print("\n" + "=" * 50)
    print("✅ Archival complete!")
    
    # Show summary
    archive_dir = inbox_dir.parent / ARCHIVE_DIR_NAME
    if archive_dir.exists():
        archive_count = len(list(archive_dir.glob("*.jsonl")))
        print(f"📚 Total archive files: {archive_count}")

if __name__ == "__main__":
    main()
