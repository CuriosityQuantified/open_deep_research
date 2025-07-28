# Open Deep Research - Custom Model Fork

A powerful AI research assistant that conducts deep, multi-step research with reflection and iteration. This fork supports multiple custom OpenAI-compatible API endpoints and includes a modern web UI with chat history.

## 🌟 Features

- **🤖 Multi-Model Support**: Configure different models for different tasks (summarization, research, compression, final reports)
- **🔍 Deep Research**: Multi-step research with web search integration via Tavily
- **💬 Modern Web UI**: ChatGPT-like interface with conversation history
- **💾 Persistent Storage**: All research sessions and reports are automatically saved
- **📝 Structured Reports**: Generates comprehensive, well-formatted research reports
- **🔌 OpenAI-Compatible**: Works with any OpenAI-compatible API (OpenAI, Anthropic via proxy, Ollama, etc.)

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.10+** installed
- **Node.js 18+** and npm installed
- **Git** installed
- A **Tavily API key** for web search (get one at [tavily.com](https://tavily.com))
- At least one **OpenAI-compatible API endpoint** (OpenAI, Ollama, etc.)

## 🚀 Quick Start

### Automatic Installation (Recommended)

Run the installation script which will check prerequisites and set up everything:

```bash
git clone https://github.com/CuriosityQuantified/open_deep_research.git
cd open_deep_research
./install.sh
```

Then edit `.env` with your API keys and test your configuration:

```bash
# Test your configuration
python test_config.py

# Start the application
./ui/start.sh
```

### Manual Installation

<details>
<summary>Click to expand manual installation steps</summary>

#### 1. Clone the Repository

```bash
git clone https://github.com/CuriosityQuantified/open_deep_research.git
cd open_deep_research
```

#### 2. Install UV (Python Package Manager)

UV is a fast Python package manager that we use for dependency management:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

#### 3. Set Up Python Environment

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python dependencies
uv sync

# Or with pip (alternative)
pip install -r requirements.txt
```

#### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```bash
# Tavily API Key (required for web search)
TAVILY_API_KEY=your-tavily-api-key

# Model Configuration Examples:

# Example 1: Using Ollama for all models
SUMMARIZATION_MODEL_NAME=llama3.2:latest
SUMMARIZATION_MODEL_BASE_URL=http://localhost:11434/v1
SUMMARIZATION_MODEL_API_KEY=ollama
SUMMARIZATION_MODEL_MAX_TOKENS=4096

RESEARCH_MODEL_NAME=llama3.2:latest
RESEARCH_MODEL_BASE_URL=http://localhost:11434/v1
RESEARCH_MODEL_API_KEY=ollama
RESEARCH_MODEL_MAX_TOKENS=8192

COMPRESSION_MODEL_NAME=llama3.2:latest
COMPRESSION_MODEL_BASE_URL=http://localhost:11434/v1
COMPRESSION_MODEL_API_KEY=ollama
COMPRESSION_MODEL_MAX_TOKENS=4096

FINAL_REPORT_MODEL_NAME=llama3.2:latest
FINAL_REPORT_MODEL_BASE_URL=http://localhost:11434/v1
FINAL_REPORT_MODEL_API_KEY=ollama
FINAL_REPORT_MODEL_MAX_TOKENS=16384

# Example 2: Using OpenAI
# SUMMARIZATION_MODEL_NAME=gpt-4o-mini
# SUMMARIZATION_MODEL_BASE_URL=https://api.openai.com/v1
# SUMMARIZATION_MODEL_API_KEY=sk-...
# SUMMARIZATION_MODEL_MAX_TOKENS=4096
```

#### 5. Install Frontend Dependencies

```bash
cd ui/frontend
npm install
cd ../..
```

#### 6. Start the Application

The easiest way is to use the provided start script:

```bash
./ui/start.sh
```

This will:
- Start the backend API server on http://localhost:8000
- Start the frontend development server on http://localhost:3000
- Open http://localhost:3000 in your browser

</details>

## 🔧 Configuration Guide

### Model Configuration

You can use different models for different parts of the research process:

1. **Summarization Model**: Used for summarizing web search results
2. **Research Model**: Main model for conducting research
3. **Compression Model**: Used for compressing/synthesizing findings
4. **Final Report Model**: Used for writing the final report

### Example Configurations

#### All Ollama (Local)
```bash
# Install Ollama first: https://ollama.ai
# Pull a model: ollama pull llama3.2

SUMMARIZATION_MODEL_NAME=llama3.2:latest
SUMMARIZATION_MODEL_BASE_URL=http://localhost:11434/v1
SUMMARIZATION_MODEL_API_KEY=ollama
SUMMARIZATION_MODEL_MAX_TOKENS=4096

# Repeat for other models...
```

#### OpenAI
```bash
SUMMARIZATION_MODEL_NAME=gpt-4o-mini
SUMMARIZATION_MODEL_BASE_URL=https://api.openai.com/v1
SUMMARIZATION_MODEL_API_KEY=sk-your-api-key
SUMMARIZATION_MODEL_MAX_TOKENS=4096

RESEARCH_MODEL_NAME=gpt-4o
RESEARCH_MODEL_BASE_URL=https://api.openai.com/v1
RESEARCH_MODEL_API_KEY=sk-your-api-key
RESEARCH_MODEL_MAX_TOKENS=8192
```

#### Mixed Setup (Recommended)
```bash
# Fast local model for summarization
SUMMARIZATION_MODEL_NAME=llama3.2:latest
SUMMARIZATION_MODEL_BASE_URL=http://localhost:11434/v1
SUMMARIZATION_MODEL_API_KEY=ollama

# Powerful cloud model for research
RESEARCH_MODEL_NAME=gpt-4o
RESEARCH_MODEL_BASE_URL=https://api.openai.com/v1
RESEARCH_MODEL_API_KEY=sk-your-api-key
```

## 📁 Project Structure

```
open_deep_research/
├── src/                    # Source code
│   └── open_deep_research/ # Main package
├── ui/                     # Web UI
│   ├── frontend/          # React frontend
│   ├── backend/           # FastAPI backend
│   ├── start.sh          # Development startup script
│   └── start-production.sh # Production startup script
├── .env                   # Environment configuration
├── pyproject.toml        # Python project configuration
└── README.md             # This file
```

## 🖥️ Using the Web UI

1. **Start a New Research**: Type your research query in the input box
2. **View Progress**: Watch real-time updates as the research progresses
3. **Access History**: Click on previous chats in the sidebar
4. **Download Reports**: Each research generates a downloadable markdown report

### Features:
- 💬 ChatGPT-like interface
- 📚 Persistent chat history
- 💾 Automatic report saving
- 🔄 Real-time research progress
- 📥 Download research reports

## 🛠️ Advanced Usage

### Running Servers Separately

#### Backend Only
```bash
cd ui/backend
source ../../.venv/bin/activate
python server.py
```

#### Frontend Only
```bash
cd ui/frontend
npm run dev
```

### Production Mode

For production deployment with a single server:

```bash
./ui/start-production.sh
```

This builds the frontend and serves everything from port 8000.

### Using LangGraph Studio (Alternative)

If you prefer the LangGraph Studio interface:

```bash
uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.11 langgraph dev
```

Then open: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

## 🐛 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Kill processes on ports
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

#### 2. Ollama Connection Error
- Ensure Ollama is running: `ollama serve`
- Check if model is pulled: `ollama list`
- Verify URL is correct: `http://localhost:11434/v1`

#### 3. Module Import Errors
```bash
# Reinstall dependencies
uv sync
```

#### 4. Frontend Build Issues
```bash
cd ui/frontend
rm -rf node_modules package-lock.json
npm install
```

### Viewing Chat History

To debug or view stored conversations:

```bash
cd ui/backend
python view_chats.py
```

## 📊 How It Works

1. **Query Processing**: Your research query is processed and planned
2. **Web Search**: Tavily API searches for relevant information
3. **Multi-Model Pipeline**:
   - Summarization model processes search results
   - Research model conducts deep analysis
   - Compression model synthesizes findings
   - Final report model generates comprehensive report
4. **Storage**: All conversations and reports are saved automatically

## 🔐 Security Notes

- API keys are stored in `.env` and never committed to git
- All data is stored locally in SQLite and markdown files
- WebSocket connections are used for real-time updates
- CORS is configured for local development

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

Based on the original [Open Deep Research](https://github.com/langchain-ai/open_deep_research) by LangChain.

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review your `.env` configuration
3. Ensure all prerequisites are installed
4. Open an issue on GitHub with:
   - Your configuration (without API keys)
   - Error messages
   - Steps to reproduce