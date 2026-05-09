# 🚀 TravelAI Booking System - Complete Setup Guide

## Prerequisites

### System Requirements
- Python 3.10 or higher
- PostgreSQL 13 or higher
- Git
- ~500MB disk space

### Accounts & API Keys
1. **Anthropic API Key**
   - Go to https://console.anthropic.com
   - Sign up or log in
   - Create an API key (free $5 credits for new users)
   - Copy and save it

2. **PostgreSQL Database** (Local or Hosted)
   - Option A: Install locally from https://www.postgresql.org/download/
   - Option B: Use Docker (recommended): `docker run --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15`
   - Option C: Use cloud PostgreSQL (Neon, Supabase, Render)

---

## Installation Steps

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/travel-ai-booking.git
cd travel-ai-booking
```

### Step 2: Create Virtual Environment
```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Setup Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your values (use your favorite editor)
# Windows: notepad .env
# macOS/Linux: nano .env
```

Fill in these values in `.env`:
```
# Your Anthropic API Key
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# PostgreSQL Connection
DATABASE_URL=postgresql://postgres:password@localhost:5432/travel_ai

# Other settings (can keep defaults)
HOST=0.0.0.0
PORT=8000
DEBUG=True
FRONTEND_URL=http://localhost:3000
```

### Step 5: Start PostgreSQL

**Option A: Docker (Easiest)**
```bash
docker-compose up -d
# This starts PostgreSQL + Redis in background
```

**Option B: Manual PostgreSQL**
```bash
# macOS with Homebrew
brew services start postgresql

# Ubuntu/Debian
sudo systemctl start postgresql

# Then create database:
createdb travel_ai
```

### Step 6: Initialize Database
```bash
python -m scripts.setup_db
# Output: ✓ Created users table, ✓ Created bookings table, etc.
```

### Step 7: Start the Server
```bash
python -m api.main
# Output: 
# ✓ Database connected
# ✓ System initialized successfully
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

The server is now running!

---

## Verification

### Test 1: Health Check
```bash
curl http://localhost:8000/health
# Output: {"status":"healthy","timestamp":"...","service":"TravelAI Booking System"}
```

### Test 2: API Documentation
Open in browser: http://localhost:8000/docs
(Interactive Swagger documentation)

### Test 3: Create User
```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "email":"test@example.com",
    "name":"Test User"
  }'
# Output: {"user_id":1,"email":"test@example.com",...}
```

### Test 4: Send Chat Message
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id":1,
    "message":"Show me flights from Toronto to New York on April 15"
  }'
# Output: Agent response from search_agent
```

### Test 5: Run Interactive Demo
```bash
python scripts/demo.py
# Follow the interactive prompts
```

---

## Troubleshooting

### Issue: "ANTHROPIC_API_KEY not set"
**Solution:**
```bash
# Verify the key in .env
cat .env | grep ANTHROPIC_API_KEY

# Or set it directly (temporary)
export ANTHROPIC_API_KEY=sk-ant-xxxxxxx
```

### Issue: "DATABASE_URL not set"
**Solution:**
```bash
# Check .env file
cat .env | grep DATABASE_URL

# Common URLs:
# PostgreSQL local: postgresql://postgres:password@localhost:5432/travel_ai
# Neon (cloud): postgresql://user:password@host.neon.tech/dbname
# Supabase: postgresql://postgres:password@db.host.supabase.co:5432/postgres
```

### Issue: "psycopg2: can't adapt type 'dict'" Error
**Solution:** This means PostgreSQL tables need reinitialization
```bash
# Reset database
python -m scripts.setup_db reset

# Reinitialize
python -m scripts.setup_db
```

### Issue: PostgreSQL connection refused (port 5432)
**Solution:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list  # macOS
docker ps  # Docker

# Or start Docker container:
docker-compose up -d
```

### Issue: Port 8000 already in use
**Solution:**
```bash
# Use different port
python -m api.main --port 8001

# Or kill existing process
# Linux/macOS:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue: Agents not responding / Timeout
**Solution:**
```bash
# Increase agent timeout in .env
AGENT_TIMEOUT_SECONDS=120

# Check API rate limits at
# https://console.anthropic.com/account/limits
```

---

## Next Steps

### 1. Try the Interactive Demo
```bash
python scripts/demo.py
```

### 2. Explore the API
Visit: http://localhost:8000/docs

### 3. Test Multi-Agent Workflows
```python
# In Python shell or script:
import asyncio
from src.orchestrator import orchestrator
from src.database import db, init_db

async def test():
    await init_db()
    result = await orchestrator.handle_user_request(
        user_id=1,
        user_message="Find flights from YYC to NYC on April 15"
    )
    print(result)

asyncio.run(test())
```

### 4. Build a Frontend
The API is ready for a web/mobile frontend:
```javascript
// WebSocket connection
const ws = new WebSocket('ws://localhost:8000/ws/chat/1');

ws.onmessage = (event) => {
    const response = JSON.parse(event.data);
    console.log(response); // Agent response
};

ws.send(JSON.stringify({ message: "Find me flights to Paris" }));
```

### 5. Deploy to Production
See README.md for deployment instructions

---

## Project Structure

```
travel-ai-booking/
├── src/                      # Source code
│   ├── agents/              # AI agents
│   ├── tools/               # Tool implementations
│   ├── config.py            # Settings
│   ├── database.py          # PostgreSQL
│   ├── embeddings.py        # Vector DB
│   └── orchestrator.py      # Agent coordinator
├── api/                     # FastAPI server
├── scripts/                 # Utilities
├── requirements.txt         # Dependencies
├── .env.example            # Template
├── docker-compose.yml      # Docker setup
└── README.md               # Full documentation
```

---

## Common Commands

```bash
# Start server
python -m api.main

# Run demo
python scripts/demo.py

# Initialize database
python -m scripts.setup_db

# Reset database
python -m scripts.setup_db reset

# Start Docker services
docker-compose up -d

# Stop Docker services
docker-compose down

# View API docs
# Open http://localhost:8000/docs

# View logs
tail -f logs/app.log

# Run tests
pytest tests/ -v

# Check Python version
python --version

# Deactivate virtual environment
deactivate
```

---

## Configuration Options

All settings in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | - | Your API key (required) |
| `DATABASE_URL` | - | PostgreSQL connection (required) |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `DEBUG` | `True` | Debug mode (False in production) |
| `AGENT_TIMEOUT_SECONDS` | `60` | Tool execution timeout |
| `MAX_TOOL_CALLS_PER_REQUEST` | `10` | Max tool calls per message |
| `CONVERSATION_HISTORY_LIMIT` | `20` | Messages to keep in memory |

---

## Performance Tips

1. **Use connection pooling:** Configured by default in `src/database.py`
2. **Enable caching:** Optional Redis in `docker-compose.yml`
3. **Optimize vector DB:** Chroma uses local SQLite by default
4. **Monitor agent usage:** Check API usage at Anthropic console

---

## Getting Help

- **API Errors?** Check http://localhost:8000/docs
- **Database Issues?** See DATABASE_URL section above
- **Agent Issues?** Run `python scripts/demo.py` for debugging
- **Code Questions?** See README.md & inline code comments
- **API Key Issues?** https://console.anthropic.com/account/limits

---

## Next: Build Your Frontend

The API is production-ready. You can now:
- Build a React/Vue frontend
- Create a mobile app
- Integrate with other systems
- Deploy to production

Good luck! 🚀
