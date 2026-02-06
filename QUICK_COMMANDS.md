# Executive Mind Matrix - Quick Command Reference

## 🚀 Starting the Server

### Development Mode (Recommended)
```bash
cd /home/rippere/Projects/executive-mind-matrix
venv/bin/uvicorn main:app --reload
```
- Shows logs directly in terminal
- Auto-reloads on code changes
- Press **Ctrl+C** to stop

### Background Mode
```bash
cd /home/rippere/Projects/executive-mind-matrix
venv/bin/uvicorn main:app --reload &
```
- Runs in background
- Use `pkill -f "uvicorn main:app"` to stop

---

## 🔍 Monitoring & Logs

### Watch Live Logs
```bash
tail -f logs/app.log
```

### Check Last 50 Lines
```bash
tail -50 logs/app.log
```

### Search Logs for Errors
```bash
grep ERROR logs/app.log | tail -20
```

---

## 🧪 Testing

### Run All Tests
```bash
cd /home/rippere/Projects/executive-mind-matrix
venv/bin/pytest tests/ -v
```

### Run Specific Test File
```bash
venv/bin/pytest tests/test_workflow_integration.py -v
```

### Run with Coverage
```bash
venv/bin/pytest tests/ -v --cov=app --cov=main
```

---

## 🌐 API Access

### API Documentation (Interactive)
```
http://127.0.0.1:8000/docs
```
- Swagger UI
- Try endpoints directly

### Alternative Docs
```
http://127.0.0.1:8000/redoc
```
- ReDoc style

### Health Check
```bash
curl http://127.0.0.1:8000/health
```

### Trigger Manual Poll
```bash
curl -X POST http://127.0.0.1:8000/trigger-poll
```

### Run Dialectic Analysis
```bash
curl -X POST http://127.0.0.1:8000/dialectic/{intent_id}
```

### Approve an Action
```bash
curl -X POST http://127.0.0.1:8000/action/{action_id}/approve
```

---

## 🛠️ Environment & Dependencies

### Activate Virtual Environment
```bash
cd /home/rippere/Projects/executive-mind-matrix
source venv/bin/activate
```

### Install/Update Dependencies
```bash
venv/bin/pip install -r requirements.txt
```

### Recreate Virtual Environment (if broken)
```bash
rm -rf venv
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

---

## 🔧 Process Management

### Check if Server is Running
```bash
ps aux | grep uvicorn | grep -v grep
```

### Kill All Uvicorn Processes
```bash
pkill -f "uvicorn main:app"
```

### Check Port 8000 Usage
```bash
lsof -i :8000
```

---

## 📝 Git Commands

### Check Status
```bash
git status
```

### View Recent Commits
```bash
git log --oneline -10
```

### Create Commit
```bash
git add -A
git commit -m "Your commit message"
```

### View Changes
```bash
git diff
```

---

## 🐛 Debugging

### Validate Python Syntax
```bash
python3 -m py_compile main.py
python3 -m py_compile app/*.py
```

### Check Environment Variables
```bash
cat .env | grep -v "^#" | grep -v "^$"
```

### Test Notion Connection
```bash
venv/bin/python scripts/test-connections.py
```

### Check Installed Packages
```bash
venv/bin/pip list
```

---

## 📊 Useful Searches

### Find Property References
```bash
grep -r "Property_Name" app/ --include="*.py"
```

### Find Function Definitions
```bash
grep -r "def function_name" app/
```

### Count Lines of Code
```bash
find app/ -name "*.py" | xargs wc -l
```

---

## 🔄 Common Workflows

### Full Restart (Clean)
```bash
# 1. Stop server
pkill -f "uvicorn main:app"

# 2. Check for errors in code
python3 -m py_compile main.py

# 3. Run tests
venv/bin/pytest tests/ -v

# 4. Start server
venv/bin/uvicorn main:app --reload
```

### Deploy Code Changes
```bash
# 1. Make changes
# 2. Test locally
venv/bin/pytest tests/ -v

# 3. Commit
git add -A
git commit -m "Description of changes"

# 4. Server auto-reloads (if using --reload)
```

### Debug a Failing Test
```bash
# Run with verbose traceback
venv/bin/pytest tests/test_name.py::test_function -vv --tb=short

# Run with print statements shown
venv/bin/pytest tests/test_name.py::test_function -s
```

---

## 📁 Important File Locations

| Item | Location |
|------|----------|
| Main Application | `main.py` |
| Workflow Integration | `app/workflow_integration.py` |
| Agent Router | `app/agent_router.py` |
| Tests | `tests/` |
| Logs | `logs/app.log` |
| Environment Variables | `.env` |
| Requirements | `requirements.txt` |
| Database Property Map | `DATABASE_PROPERTY_MAP.md` |
| This Reference | `QUICK_COMMANDS.md` |

---

## 🆘 Emergency Fixes

### Server Won't Start (Port in Use)
```bash
pkill -f "uvicorn main:app"
sleep 2
venv/bin/uvicorn main:app --reload
```

### Dependencies Broken
```bash
rm -rf venv
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

### Tests Failing After Changes
```bash
# Revert changes
git diff  # See what changed
git checkout -- file_name.py  # Revert specific file

# Or restore from last commit
git reset --hard HEAD
```

---

## 💡 Pro Tips

1. **Always use venv/bin/python or venv/bin/pip** - Never use system Python for this project
2. **Keep server running with --reload** - Auto-restarts on code changes
3. **Check logs/app.log first** - Most errors are logged there
4. **Use the /docs endpoint** - Interactive API testing
5. **Run tests before committing** - Catch errors early

---

## 📞 Quick Access

**This file**: `/home/rippere/Projects/executive-mind-matrix/QUICK_COMMANDS.md`

**View anytime**:
```bash
cat ~/Projects/executive-mind-matrix/QUICK_COMMANDS.md
# or
less ~/Projects/executive-mind-matrix/QUICK_COMMANDS.md
```

**Create an alias** (add to ~/.bashrc or ~/.zshrc):
```bash
alias emm-help='cat ~/Projects/executive-mind-matrix/QUICK_COMMANDS.md'
alias emm-start='cd ~/Projects/executive-mind-matrix && venv/bin/uvicorn main:app --reload'
alias emm-test='cd ~/Projects/executive-mind-matrix && venv/bin/pytest tests/ -v'
alias emm-logs='tail -f ~/Projects/executive-mind-matrix/logs/app.log'
```

Then use:
- `emm-help` - Show this guide
- `emm-start` - Start server
- `emm-test` - Run tests
- `emm-logs` - Watch logs
