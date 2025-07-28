# Open Deep Research - Web UI

A modern web interface for Open Deep Research with chat history and automatic report saving.

## Features

- 🤖 **ChatGPT-like Interface**: Clean, intuitive chat interface
- 💬 **Previous Chat Sidebar**: Access all your research conversations
- 💾 **Automatic Report Saving**: All research reports are automatically saved
- 🔄 **Real-time Updates**: WebSocket-based real-time communication
- 📊 **Multiple Model Support**: Use different models for different tasks

## Quick Start

### Development Mode (Two Servers)

Run both frontend and backend servers for development:

```bash
./ui/start.sh
```

This will:
- Start backend on http://localhost:8000
- Start frontend dev server on http://localhost:3000 (with hot reload)

### Production Mode (Single Server)

Run a single server that serves both API and frontend:

```bash
./ui/start-production.sh
```

This will:
- Build the frontend for production
- Serve everything from http://localhost:8000

## Manual Setup

If you prefer to run servers manually:

### Backend Server

```bash
cd ui/backend
source ../../.venv/bin/activate
python server.py
```

### Frontend Development

```bash
cd ui/frontend
npm install  # First time only
npm run dev
```

### Frontend Build

```bash
cd ui/frontend
npm run build
```

## Architecture

- **Backend**: FastAPI + WebSocket + SQLite
- **Frontend**: React + TypeScript + Tailwind CSS
- **Communication**: WebSocket with JSON messages
- **Database**: SQLite for chat history
- **Reports**: Saved as markdown files in `research_reports/`

## API Endpoints

- `GET /api/chats` - List all chats
- `GET /api/chats/{chat_id}/messages` - Get messages for a chat
- `POST /api/chats` - Create new chat
- `DELETE /api/chats/{chat_id}` - Delete a chat
- `GET /api/reports/{filename}` - Download report
- `WS /ws` - WebSocket for real-time chat

## Configuration

The UI uses the same `.env` configuration as the main project. Make sure you have configured your custom models in the `.env` file.

## Troubleshooting

### Port Already in Use

If you get a "port already in use" error:

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### WebSocket Connection Failed

Ensure:
1. Backend server is running
2. No firewall blocking WebSocket connections
3. Correct WebSocket URL in frontend (ws://localhost:8000/ws)

### Build Issues

If frontend build fails:

```bash
cd ui/frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```