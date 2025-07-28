# Troubleshooting Guide

## Common Issues and Solutions

### Node.js Issues

#### ERR_INVALID_PACKAGE_CONFIG
**Problem**: Error when running npm install with newer Node.js versions (v24+)

**Solution**: 
1. Make sure you have the latest package.json with proper configuration
2. Clear npm cache and reinstall:
```bash
cd ui/frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

3. If still having issues, try using Node.js v20 LTS:
```bash
# Using nvm
nvm install 20
nvm use 20
```

#### PostCSS Module Warning
**Problem**: Warning about module type for postcss.config.js

**Solution**: This is just a warning and can be ignored. The app will still work correctly.

### Remote Model Server Issues

#### Connection Refused to Model Endpoint
**Problem**: Cannot connect to model at configured URL

**Solution**:
1. Verify the model server is running and accessible:
```bash
curl -X GET http://your-server:port/v1/models
```

2. Check firewall rules allow connection to the model server port

3. If using a remote Linux server, ensure it's configured to accept external connections

4. Update your .env with the correct URL:
```env
RESEARCH_MODEL_BASE_URL=http://your-server-ip:port/v1
```

#### Model Not Found
**Problem**: 404 error when trying to use a model

**Solution**:
1. List available models on your server
2. Update .env with the exact model name as shown on the server
3. Ensure the model is loaded and ready

### Python/Backend Issues

#### Module Import Errors
**Problem**: ImportError when starting the backend

**Solution**:
```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### AG-UI Import Error
**Problem**: Cannot import ag_ui or ag_ui_protocol

**Solution**:
```bash
pip install ag-ui-protocol==0.1.8
```

### Database Issues

#### SQLite Database Locked
**Problem**: Database is locked error

**Solution**:
1. Stop all running instances of the backend
2. Delete the lock file if it exists:
```bash
cd ui/backend
rm research_chats.db-journal
```

### WebSocket Issues

#### WebSocket Connection Failed
**Problem**: Frontend cannot connect to backend WebSocket

**Solution**:
1. Ensure backend is running on the correct port (8000)
2. Check no proxy is interfering with WebSocket connections
3. If using WSL or remote server, ensure proper port forwarding

### Environment Configuration

#### Missing API Keys
**Problem**: Tavily or model API errors

**Solution**:
1. Copy .env.example to .env if not done
2. Add your Tavily API key from https://tavily.com
3. Configure all four model types in .env

#### Test Your Configuration
Run the test script to verify everything is set up correctly:
```bash
python test_config.py
```

### Port Conflicts

#### Port 8000 or 3000 Already in Use
**Solution**:
```bash
# Linux/Mac
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Installation Issues

#### UV Not Found
**Problem**: UV package manager not installed

**Solution**: The install script will fall back to pip automatically. Or install UV:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Getting Help

If you're still having issues:

1. Check you have all prerequisites:
   - Python 3.10+
   - Node.js 18+ (recommend v20 LTS)
   - Git

2. Try the manual installation steps in README.md

3. Run the test configuration:
   ```bash
   python test_config.py
   ```

4. Check the backend logs for detailed error messages

5. Open an issue on GitHub with:
   - Your OS and versions (Python, Node.js)
   - Error messages
   - Your .env configuration (without API keys)
   - Output of `python test_config.py`