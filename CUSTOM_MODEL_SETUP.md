# Custom Model Configuration for Open Deep Research

This fork of Open Deep Research has been modified to support multiple custom model endpoints using the ChatOpenAI wrapper. You can configure different OpenAI-compatible models for each task type: summarization, research, compression, and final report generation.

## Configuration

### Environment Variables

Configure each model type in your `.env` file:

```bash
# Summarization Model - Used for summarizing web search results
SUMMARIZATION_MODEL_NAME=your-fast-model
SUMMARIZATION_MODEL_BASE_URL=https://api.example.com/v1
SUMMARIZATION_MODEL_API_KEY=your-api-key
SUMMARIZATION_MODEL_MAX_TOKENS=4096

# Research Model - Used for conducting research and asking questions
RESEARCH_MODEL_NAME=your-smart-model
RESEARCH_MODEL_BASE_URL=https://api.example.com/v1
RESEARCH_MODEL_API_KEY=your-api-key
RESEARCH_MODEL_MAX_TOKENS=8192

# Compression Model - Used for compressing research findings
COMPRESSION_MODEL_NAME=your-efficient-model
COMPRESSION_MODEL_BASE_URL=https://api.example.com/v1
COMPRESSION_MODEL_API_KEY=your-api-key
COMPRESSION_MODEL_MAX_TOKENS=4096

# Final Report Model - Used for writing comprehensive reports
FINAL_REPORT_MODEL_NAME=your-creative-model
FINAL_REPORT_MODEL_BASE_URL=https://api.example.com/v1
FINAL_REPORT_MODEL_API_KEY=your-api-key
FINAL_REPORT_MODEL_MAX_TOKENS=16384

# Search API Configuration (required)
TAVILY_API_KEY=your-tavily-api-key
```

### Example Configurations

#### Optimized for Cost and Performance
Use cheaper/faster models for simple tasks and powerful models for complex tasks:

```bash
# Fast, cheap model for summarization
SUMMARIZATION_MODEL_NAME=gpt-3.5-turbo
SUMMARIZATION_MODEL_BASE_URL=https://api.openai.com/v1
SUMMARIZATION_MODEL_API_KEY=sk-...
SUMMARIZATION_MODEL_MAX_TOKENS=4096

# Powerful model for research
RESEARCH_MODEL_NAME=gpt-4
RESEARCH_MODEL_BASE_URL=https://api.openai.com/v1
RESEARCH_MODEL_API_KEY=sk-...
RESEARCH_MODEL_MAX_TOKENS=8192

# Efficient model for compression
COMPRESSION_MODEL_NAME=gpt-3.5-turbo
COMPRESSION_MODEL_BASE_URL=https://api.openai.com/v1
COMPRESSION_MODEL_API_KEY=sk-...
COMPRESSION_MODEL_MAX_TOKENS=4096

# Best model for final reports
FINAL_REPORT_MODEL_NAME=gpt-4
FINAL_REPORT_MODEL_BASE_URL=https://api.openai.com/v1
FINAL_REPORT_MODEL_API_KEY=sk-...
FINAL_REPORT_MODEL_MAX_TOKENS=16384
```

#### All Local Models (Ollama)
```bash
# Small, fast model for summarization
SUMMARIZATION_MODEL_NAME=qwen3:1.7b
SUMMARIZATION_MODEL_BASE_URL=http://localhost:11434/v1
SUMMARIZATION_MODEL_API_KEY=ollama
SUMMARIZATION_MODEL_MAX_TOKENS=4096

# Larger model for research
RESEARCH_MODEL_NAME=gemma3:4b
RESEARCH_MODEL_BASE_URL=http://localhost:11434/v1
RESEARCH_MODEL_API_KEY=ollama
RESEARCH_MODEL_MAX_TOKENS=8192

# Small model for compression
COMPRESSION_MODEL_NAME=qwen3:1.7b
COMPRESSION_MODEL_BASE_URL=http://localhost:11434/v1
COMPRESSION_MODEL_API_KEY=ollama
COMPRESSION_MODEL_MAX_TOKENS=4096

# Larger model for reports
FINAL_REPORT_MODEL_NAME=gemma3:4b
FINAL_REPORT_MODEL_BASE_URL=http://localhost:11434/v1
FINAL_REPORT_MODEL_API_KEY=ollama
FINAL_REPORT_MODEL_MAX_TOKENS=16384
```

## Usage

1. Clone the repository and set up the virtual environment:
```bash
git clone <your-fork-url>
cd open_deep_research
uv venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
uv sync
```

3. Configure your `.env` file with your custom model settings

4. Launch the application:
```bash
uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.11 langgraph dev --allow-blocking
```

## Model Selection Guide

### Summarization Model
- **Purpose**: Summarizes web search results from Tavily
- **Recommended**: Fast, efficient models (e.g., GPT-3.5-turbo, Qwen 1.7B)
- **Requirements**: Structured output support

### Research Model
- **Purpose**: Conducts research, asks clarifying questions, manages sub-agents
- **Recommended**: Powerful, reasoning-capable models (e.g., GPT-4, Claude 3, Gemma 4B+)
- **Requirements**: Tool calling, structured outputs, good reasoning

### Compression Model
- **Purpose**: Compresses and synthesizes research findings
- **Recommended**: Balanced models (e.g., GPT-3.5-turbo, Qwen 1.7B)
- **Requirements**: Good summarization capabilities

### Final Report Model
- **Purpose**: Writes the final comprehensive research report
- **Recommended**: Creative, high-quality models (e.g., GPT-4, Claude 3 Opus)
- **Requirements**: Large context window, excellent writing capabilities

## Important Notes

- All endpoints must be OpenAI-compatible (support the same API format)
- Each model type can use different endpoints and API keys
- Models must support:
  - Structured outputs (for summarization and research planning)
  - Tool calling (for research model)
  - The token limits you specify

## Differences from Original

- Added support for multiple custom model configurations
- Each task type can use a different model and endpoint
- Removed built-in support for specific providers (OpenAI, Anthropic, Google)
- Focused on OpenAI-compatible endpoints only
- Search functionality limited to Tavily