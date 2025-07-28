# Open Deep Research - Quick Reference

## 🚀 Quick Commands

```bash
# First time setup
./install.sh

# Start the application
./ui/start.sh

# Start in production mode
./ui/start-production.sh

# View chat history
cd ui/backend && python view_chats.py
```

## 🔧 Configuration Examples

### Ollama (Local)
```env
SUMMARIZATION_MODEL_NAME=llama3.2:latest
SUMMARIZATION_MODEL_BASE_URL=http://localhost:11434/v1
SUMMARIZATION_MODEL_API_KEY=ollama
SUMMARIZATION_MODEL_MAX_TOKENS=4096
```

### OpenAI
```env
RESEARCH_MODEL_NAME=gpt-4o
RESEARCH_MODEL_BASE_URL=https://api.openai.com/v1
RESEARCH_MODEL_API_KEY=sk-...
RESEARCH_MODEL_MAX_TOKENS=8192
```

## 🐛 Common Fixes

### Port in use
```bash
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

### Reinstall dependencies
```bash
uv sync
cd ui/frontend && npm install
```

### Check Ollama
```bash
ollama list
ollama serve
```

## 📁 Important Files

- `.env` - Your configuration
- `ui/backend/research_chats.db` - Chat history database
- `ui/backend/research_reports/` - Saved reports
- `ui/backend/view_chats.py` - View chat history

## 🌐 URLs

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 💡 Tips

1. Use different models for different tasks to optimize cost/performance
2. Reports are automatically saved in markdown format
3. All conversations are persistent - click any chat in the sidebar
4. WebSocket provides real-time research progress
5. You can download reports directly from the UI