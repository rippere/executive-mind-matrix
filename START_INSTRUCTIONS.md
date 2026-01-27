# How to Start the Executive Mind Matrix

## Quick Start

### Start the Application

```bash
# Activate virtual environment and start
cd /home/rippere/Projects/executive-mind-matrix
./venv/bin/python main.py
```

The application will:
- Start on http://0.0.0.0:8000
- Begin polling Notion every 2 minutes
- Process intents automatically
- Log to `logs/app.log`

### Verify It's Running

```bash
# Check health
curl http://localhost:8000/health

# Check logs
tail -f logs/app.log

# View API documentation
# Open browser: http://localhost:8000/docs
```

### Run in Background

```bash
# Start in background
nohup ./venv/bin/python main.py > logs/app.log 2>&1 &

# Get process ID
echo $!

# Stop later
kill <process-id>
```

### Using systemd (Recommended for persistent operation)

Create `/etc/systemd/system/executive-mind-matrix.service`:

```ini
[Unit]
Description=Executive Mind Matrix
After=network.target

[Service]
Type=simple
User=rippere
WorkingDirectory=/home/rippere/Projects/executive-mind-matrix
Environment="PATH=/home/rippere/Projects/executive-mind-matrix/venv/bin"
ExecStart=/home/rippere/Projects/executive-mind-matrix/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
# Enable and start service
sudo systemctl enable executive-mind-matrix
sudo systemctl start executive-mind-matrix

# Check status
sudo systemctl status executive-mind-matrix

# View logs
sudo journalctl -u executive-mind-matrix -f

# Stop service
sudo systemctl stop executive-mind-matrix
```

## For Production (Railway)

Follow the deployment guide:
```bash
# See QUICK_DEPLOY.md for 5-minute setup
# Or DEPLOYMENT_GUIDE.md for complete instructions
```

Railway will handle:
- Automatic restarts
- Health checks
- 24/7 operation
- Log management
- Environment variables

## Troubleshooting

### Application won't start
```bash
# Check environment
./venv/bin/python scripts/validate-env.py

# Test connections
./venv/bin/python scripts/test-connections.py

# Check port availability
lsof -i :8000
```

### Application crashes
```bash
# Check logs
tail -100 logs/app.log

# Verify dependencies
./venv/bin/pip install -r requirements.txt

# Check Notion API access
curl -H "Authorization: Bearer $NOTION_API_KEY" https://api.notion.com/v1/users
```

### High memory usage
```bash
# Check process memory
ps aux | grep python | grep main.py

# If using too much memory, consider:
# 1. Deploying to Railway (better resource management)
# 2. Reducing polling frequency in .env (POLLING_INTERVAL_SECONDS=300)
# 3. Using production Dockerfile with limited workers
```

## Current Status

**Last Test Run**: 2026-01-27 12:48:52
**Test Results**: ✅ All systems operational
- Health check: PASSED
- Poller: ACTIVE
- Intent processing: WORKING
- API connections: WORKING

The application was tested and verified working before being stopped.
