#!/usr/bin/env python3
"""AG-UI Backend Server for Open Deep Research"""

import os
import sys
import json
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, asdict
import sqlite3
import aiofiles

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse

# AG-UI imports
from ag_ui.core import (
    TextMessageStartEvent,
    TextMessageContentEvent,
    TextMessageEndEvent,
    CustomEvent,
    EventType,
    AssistantMessage,
    UserMessage,
    BaseMessage
)
from ag_ui.encoder import EventEncoder

from langchain_core.messages import HumanMessage, AIMessage
from open_deep_research.deep_researcher import deep_researcher
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DB_PATH = "research_chats.db"
REPORTS_DIR = Path("research_reports")
REPORTS_DIR.mkdir(exist_ok=True)

def init_db():
    """Initialize SQLite database for chat history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create chats table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL
        )
    """)
    
    # Create messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            chat_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            report_path TEXT,
            FOREIGN KEY (chat_id) REFERENCES chats (id)
        )
    """)
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

@dataclass
class ChatSession:
    id: str
    title: str
    created_at: str
    updated_at: str

@dataclass
class ChatMessage:
    id: str
    chat_id: str
    role: str
    content: str
    timestamp: str
    report_path: Optional[str] = None

# Session state management - store per WebSocket connection
class SessionState:
    def __init__(self):
        self.current_query: str = ""
        self.is_researching: bool = False
        self.research_status: str = ""
        self.chat_id: Optional[str] = None
        self.notes: List[str] = []
        self.final_report: str = ""

# Store active sessions
active_sessions: Dict[WebSocket, SessionState] = {}

# Event encoder
encoder = EventEncoder()

# Database helper functions
def save_chat(chat_id: str, title: str):
    """Save a new chat session"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO chats (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (chat_id, title, now, now)
    )
    
    conn.commit()
    conn.close()

def save_message(chat_id: str, role: str, content: str, report_path: Optional[str] = None) -> str:
    """Save a message to the database and return the message ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    message_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    cursor.execute(
        "INSERT INTO messages (id, chat_id, role, content, timestamp, report_path) VALUES (?, ?, ?, ?, ?, ?)",
        (message_id, chat_id, role, content, now, report_path)
    )
    
    # Update chat updated_at
    cursor.execute(
        "UPDATE chats SET updated_at = ? WHERE id = ?",
        (now, chat_id)
    )
    
    conn.commit()
    conn.close()
    
    return message_id

def get_chats() -> List[ChatSession]:
    """Get all chat sessions"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, title, created_at, updated_at FROM chats ORDER BY updated_at DESC")
    rows = cursor.fetchall()
    
    conn.close()
    
    return [ChatSession(*row) for row in rows]

def get_messages(chat_id: str) -> List[ChatMessage]:
    """Get messages for a chat"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, chat_id, role, content, timestamp, report_path FROM messages WHERE chat_id = ? ORDER BY timestamp",
        (chat_id,)
    )
    rows = cursor.fetchall()
    
    conn.close()
    
    return [ChatMessage(*row) for row in rows]

def update_chat_title(chat_id: str, title: str):
    """Update chat title"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE chats SET title = ?, updated_at = ? WHERE id = ?",
        (title, datetime.now().isoformat(), chat_id)
    )
    
    conn.commit()
    conn.close()

async def save_report(query: str, report: str, chat_id: str) -> str:
    """Save report to disk and return the path"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{chat_id}_{timestamp}.md"
    filepath = REPORTS_DIR / filename
    
    async with aiofiles.open(filepath, "w", encoding="utf-8") as f:
        await f.write(f"# Research Report\n\n")
        await f.write(f"**Query**: {query}\n\n")
        await f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        await f.write(f"**Chat ID**: {chat_id}\n\n")
        await f.write("---\n\n")
        await f.write(report)
    
    return str(filepath)

async def handle_research_message(websocket: WebSocket, query: str, session: SessionState):
    """Handle a research query"""
    
    # Update session state
    session.current_query = query
    session.is_researching = True
    session.research_status = "Starting research..."
    
    # Create or get chat ID
    if not session.chat_id:
        session.chat_id = str(uuid.uuid4())
        # Save new chat with query as title
        save_chat(session.chat_id, query[:50] + "..." if len(query) > 50 else query)
    
    # Save user message
    save_message(session.chat_id, "user", query)
    
    # Send chat_id to frontend
    await websocket.send_json({
        "type": "state",
        "data": {
            "chat_id": session.chat_id,
            "is_researching": True,
            "research_status": "Starting research..."
        }
    })
    
    # Send research started event
    await websocket.send_json({
        "type": "event",
        "event": "research_started",
        "data": {"query": query}
    })
    
    # Send and save initial message
    initial_msg = "🔎 Starting research on your query..."
    await websocket.send_json({
        "type": "message",
        "sender": "assistant",
        "text": initial_msg
    })
    save_message(session.chat_id, "assistant", initial_msg)
    
    try:
        # Update progress - gathering information
        await websocket.send_json({
            "type": "event",
            "event": "research_progress",
            "data": {
                "status": "Gathering information from various sources...",
                "progress": 0.2
            }
        })
        
        gathering_msg = "📚 Gathering information from various sources..."
        await websocket.send_json({
            "type": "message",
            "sender": "assistant",
            "text": gathering_msg
        })
        save_message(session.chat_id, "assistant", gathering_msg)
        
        # Update progress - conducting research
        await websocket.send_json({
            "type": "event",
            "event": "research_progress",
            "data": {
                "status": "Conducting deep research...",
                "progress": 0.5
            }
        })
        
        # Run the deep researcher
        result = await deep_researcher.ainvoke({
            "messages": [HumanMessage(content=query)]
        })
        
        # Extract report and notes
        final_report = result.get("final_report", "No report generated")
        notes = result.get("notes", [])
        
        # Update session state
        session.final_report = final_report
        session.notes = notes
        session.is_researching = False
        session.research_status = "Research complete!"
        
        # Save the report
        report_path = await save_report(query, final_report, session.chat_id)
        
        # Save final report as assistant response
        save_message(
            session.chat_id, 
            "assistant", 
            final_report,
            report_path=report_path
        )
        
        # Send completion event
        await websocket.send_json({
            "type": "event",
            "event": "research_completed",
            "data": {
                "report": final_report,
                "report_path": report_path
            }
        })
        
        # Send final report
        report_message = f"## Research Complete! 🎉\n\n{final_report}"
        if report_path:
            report_message += f"\n\n📄 *Report saved to: {report_path}*"
        
        await websocket.send_json({
            "type": "message",
            "sender": "assistant",
            "text": report_message
        })
        
        # Send updated state
        await websocket.send_json({
            "type": "state",
            "data": {
                "current_query": session.current_query,
                "is_researching": session.is_researching,
                "research_status": session.research_status,
                "chat_id": session.chat_id,
                "notes": session.notes,
                "final_report": session.final_report
            }
        })
        
    except Exception as e:
        session.is_researching = False
        session.research_status = f"Error: {str(e)}"
        
        error_msg = f"❌ An error occurred during research: {str(e)}"
        await websocket.send_json({
            "type": "message",
            "sender": "assistant",
            "text": error_msg
        })
        save_message(session.chat_id, "assistant", error_msg)

# REST API endpoints
@app.get("/api/chats")
async def list_chats():
    """Get all chat sessions"""
    chats = get_chats()
    return [asdict(chat) for chat in chats]

@app.get("/api/chats/{chat_id}/messages")
async def get_chat_messages(chat_id: str):
    """Get messages for a specific chat"""
    messages = get_messages(chat_id)
    return [asdict(msg) for msg in messages]

@app.delete("/api/chats/{chat_id}")
async def delete_chat(chat_id: str):
    """Delete a chat and its messages"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
    cursor.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
    
    conn.commit()
    conn.close()
    
    return {"status": "deleted"}

@app.post("/api/chats")
async def create_chat(data: dict = {"title": "New Research"}):
    """Create a new chat session"""
    chat_id = str(uuid.uuid4())
    title = data.get("title", "New Research")
    save_chat(chat_id, title)
    return {"id": chat_id, "title": title}

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections for AG-UI protocol"""
    await websocket.accept()
    
    # Create session state for this connection
    session = SessionState()
    active_sessions[websocket] = session
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            if data.get("type") == "select_chat":
                # Handle chat selection
                chat_id = data.get("chat_id")
                if chat_id:
                    session.chat_id = chat_id
                    # Send state update
                    await websocket.send_json({
                        "type": "state",
                        "data": {
                            "chat_id": chat_id,
                            "is_researching": False,
                            "research_status": ""
                        }
                    })
            
            elif data.get("type") == "message" and data.get("sender") == "user":
                query = data.get("text", "").strip()
                
                # Check if a specific chat_id is provided
                if "chat_id" in data and data["chat_id"]:
                    session.chat_id = data["chat_id"]
                
                if not query:
                    await websocket.send_json({
                        "type": "message",
                        "sender": "assistant",
                        "text": "Please provide a research query."
                    })
                else:
                    # Handle the research query
                    await handle_research_message(websocket, query, session)
            
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()
    finally:
        # Clean up session
        if websocket in active_sessions:
            del active_sessions[websocket]

# Serve reports
@app.get("/api/reports/{filename}")
async def get_report(filename: str):
    """Download a report file"""
    filepath = REPORTS_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(filepath, media_type="text/markdown", filename=filename)

# Serve frontend files
frontend_path = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)