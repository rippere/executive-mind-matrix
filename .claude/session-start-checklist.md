# Session Start Checklist

When continuing work on Executive Mind Matrix, Claude should:

## 1. Read Core Constraints
- [ ] Read `.claude/constraints.md` - Property creation rules

## 2. Check Current State
- [ ] Read `DATABASE_PROPERTY_MAP.md` - See what properties exist
- [ ] Check application status if needed (`/health` endpoint)

## 3. Context Files
- [ ] `PROPERTY_MANAGEMENT.md` - Guidelines for property changes
- [ ] `START_INSTRUCTIONS.md` - How to run the application
- [ ] `DATABASE_PROPERTY_MAP.md` - Complete schema reference

## 4. Before Making Changes

**Database Structure:**
- Must read `DATABASE_PROPERTY_MAP.md` first
- Must check for existing properties
- Must justify any new properties

**Code Changes:**
- Check existing implementations before writing new ones
- Reuse existing patterns and functions
- Avoid redundancy

**User Preferences:**
- Functionality first, aesthetics later
- No unnecessary emojis/icons unless requested
- Practical implementation over theoretical planning

## Quick Reference Commands

```bash
# Check what's running
curl http://localhost:8000/health

# Audit database properties
./venv/bin/python scripts/audit_database_properties.py

# Start application
./venv/bin/python main.py

# View logs
tail -f logs/app.log
```
