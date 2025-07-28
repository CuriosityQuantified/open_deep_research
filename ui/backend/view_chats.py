#!/usr/bin/env python3
"""View chat history from the database"""

import sqlite3
from datetime import datetime
import json

def view_chats():
    conn = sqlite3.connect("research_chats.db")
    cursor = conn.cursor()
    
    # Get all chats
    cursor.execute("SELECT id, title, created_at, updated_at FROM chats ORDER BY updated_at DESC")
    chats = cursor.fetchall()
    
    print("\n=== CHAT SESSIONS ===")
    for chat in chats:
        chat_id, title, created_at, updated_at = chat
        print(f"\nChat ID: {chat_id}")
        print(f"Title: {title}")
        print(f"Created: {created_at}")
        print(f"Updated: {updated_at}")
        
        # Get messages for this chat
        cursor.execute(
            "SELECT role, content, timestamp, report_path FROM messages WHERE chat_id = ? ORDER BY timestamp",
            (chat_id,)
        )
        messages = cursor.fetchall()
        
        print(f"\nMessages ({len(messages)} total):")
        for role, content, timestamp, report_path in messages:
            print(f"\n[{timestamp}] {role.upper()}:")
            # Truncate long content
            if len(content) > 200:
                print(f"{content[:200]}...")
            else:
                print(content)
            if report_path:
                print(f"Report saved to: {report_path}")
        
        print("\n" + "-" * 80)
    
    conn.close()

if __name__ == "__main__":
    view_chats()