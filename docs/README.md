# Executive Mind Matrix - Documentation Hub

Complete documentation for deploying, using, and understanding the Executive Mind Matrix decision intelligence system.

---

## Quick Navigation

### New Users Start Here

1. **[Executive Overview](README-EXECUTIVE.md)** - What is this system and why use it?
   - High-level architecture
   - Key benefits
   - Real-world use cases
   - FAQ

2. **[Quick Start Guide](QUICKSTART.md)** - Get started in 5 minutes
   - Daily workflow cheat sheet
   - Common commands
   - Keyboard shortcuts
   - Troubleshooting quick fixes

### Setup & Deployment

3. **[Deployment Guide](DEPLOYMENT-GUIDE.md)** - Step-by-step deployment instructions
   - Notion database setup
   - API key configuration
   - Local testing
   - Railway deployment
   - Environment variables
   - Security best practices

### Daily Usage

4. **[User Guide](USER-GUIDE.md)** - Comprehensive daily usage guide
   - Submitting intents
   - Understanding classifications
   - Reading agent analysis
   - Running dialectic analysis
   - Approving actions
   - Tracking tasks
   - Performance dashboard

### Technical Deep Dive

5. **[Architecture Guide](ARCHITECTURE.md)** - System architecture and implementation
   - System overview
   - Database schema
   - Agent architecture
   - Workflow diagrams
   - API endpoints
   - Data models
   - Security architecture

---

## Documentation Structure

```
docs/
├── README.md                    # This file - documentation hub
├── README-EXECUTIVE.md          # Executive overview & high-level concepts
├── QUICKSTART.md               # 5-minute quick start & cheat sheets
├── USER-GUIDE.md               # Comprehensive daily usage guide
├── DEPLOYMENT-GUIDE.md         # Step-by-step deployment instructions
└── ARCHITECTURE.md             # Technical architecture & deep dive
```

---

## Document Summaries

### README-EXECUTIVE.md
**Who**: Executives, decision-makers, non-technical users
**What**: High-level overview of what the system does and why it's valuable
**Key Topics**:
- Elevator pitch
- Problem statement
- System architecture (simplified)
- Decision flow examples
- Real-world use cases
- Benefits and ROI
- FAQ

**Read this if**: You want to understand what the system does at a business level

---

### QUICKSTART.md
**Who**: All users
**What**: Fast reference guide for common tasks
**Key Topics**:
- 5-minute first-time setup
- Daily workflow checklist
- Common commands
- Database quick reference
- Troubleshooting quick fixes
- Keyboard shortcuts
- Example workflows

**Read this if**: You need a quick answer or reminder

---

### USER-GUIDE.md
**Who**: Daily users
**What**: Comprehensive guide for using the system effectively
**Key Topics**:
- Submitting intents (Strategic/Operational/Reference)
- Understanding AI classifications
- Reading agent analysis
- Running dialectic analysis
- Approving actions and spawning tasks
- Using the performance dashboard
- Best practices
- Advanced features
- Troubleshooting

**Read this if**: You want to master daily usage

---

### DEPLOYMENT-GUIDE.md
**Who**: Technical users, DevOps, system administrators
**What**: Complete deployment instructions from scratch
**Key Topics**:
- Prerequisites and requirements
- Notion integration setup (all 10 databases)
- API key acquisition (Notion + Anthropic)
- Local testing and validation
- Railway deployment step-by-step
- Environment configuration
- Security best practices
- Monitoring and maintenance
- Cost breakdown

**Read this if**: You're setting up a new instance or troubleshooting deployment issues

---

### ARCHITECTURE.md
**Who**: Developers, technical architects
**What**: Deep technical dive into system implementation
**Key Topics**:
- System architecture diagrams
- Database schema and relationships
- Agent architecture (Entrepreneur, Quant, Auditor)
- Workflow diagrams (Mermaid + text)
- API endpoint reference
- Data models (Pydantic schemas)
- Background jobs and polling
- Security architecture
- Performance optimization
- Extending the system

**Read this if**: You're modifying the code or need to understand implementation details

---

## User Journeys

### Journey 1: First-Time Setup (Technical User)

1. Read [Executive Overview](README-EXECUTIVE.md) - Understand the system (10 min)
2. Read [Deployment Guide](DEPLOYMENT-GUIDE.md) - Follow step-by-step (1-2 hours)
3. Skim [User Guide](USER-GUIDE.md) - Learn daily usage (20 min)
4. Bookmark [Quick Start](QUICKSTART.md) - Keep handy for reference

**Total time**: 2-3 hours first time, then 10 min/day

---

### Journey 2: Daily User (Non-Technical)

1. Read [Executive Overview](README-EXECUTIVE.md) - Understand benefits (10 min)
2. Read [User Guide](USER-GUIDE.md) sections 1-6 - Learn core features (30 min)
3. Use [Quick Start](QUICKSTART.md) - Daily cheat sheet (bookmark this)

**Total time**: 40 min onboarding, then 5 min/day

---

### Journey 3: Developer/Contributor

1. Skim [Executive Overview](README-EXECUTIVE.md) - Context (5 min)
2. Read [Architecture Guide](ARCHITECTURE.md) - Understand implementation (1 hour)
3. Reference [Deployment Guide](DEPLOYMENT-GUIDE.md) - Setup local dev (30 min)
4. Skim [User Guide](USER-GUIDE.md) - Understand user perspective (15 min)

**Total time**: 2 hours, then reference as needed

---

## Key Concepts Index

### Decision Types

| Concept | Defined In | Page |
|---------|-----------|------|
| Strategic Intents | [User Guide](USER-GUIDE.md) | Section 3 |
| Operational Tasks | [User Guide](USER-GUIDE.md) | Section 3 |
| Reference Knowledge | [User Guide](USER-GUIDE.md) | Section 3 |

### Agent Personas

| Concept | Defined In | Page |
|---------|-----------|------|
| The Entrepreneur | [Architecture](ARCHITECTURE.md) | Agent Architecture |
| The Quant | [Architecture](ARCHITECTURE.md) | Agent Architecture |
| The Auditor | [Architecture](ARCHITECTURE.md) | Agent Architecture |
| Smart Router | [Architecture](ARCHITECTURE.md) | Agent Architecture |

### Workflows

| Concept | Defined In | Page |
|---------|-----------|------|
| Intent Processing Flow | [Architecture](ARCHITECTURE.md) | Workflow Diagrams |
| Dialectic Analysis | [User Guide](USER-GUIDE.md) | Section 5 |
| Task Spawning | [User Guide](USER-GUIDE.md) | Section 7 |
| Settlement Diff Logging | [Architecture](ARCHITECTURE.md) | Training Data Flow |

### Databases

| Concept | Defined In | Page |
|---------|-----------|------|
| Notion Setup | [Deployment Guide](DEPLOYMENT-GUIDE.md) | Section 2 |
| Database Schema | [Architecture](ARCHITECTURE.md) | Database Schema |
| Property Validation | [Architecture](ARCHITECTURE.md) | Database Schema |

---

## Feature Matrix

| Feature | User Guide | Deployment | Architecture |
|---------|-----------|------------|--------------|
| Submitting Intents | ✅ Section 2 | - | ✅ Workflows |
| Agent Analysis | ✅ Section 4 | - | ✅ Agent Architecture |
| Dialectic Flow | ✅ Section 5 | - | ✅ Workflows |
| Task Spawning | ✅ Section 7 | - | ✅ Workflows |
| Performance Metrics | ✅ Section 8 | - | ✅ API Endpoints |
| Notion Setup | - | ✅ Section 2 | ✅ Schema |
| Railway Deployment | - | ✅ Section 5 | ✅ Deployment |
| Security | ✅ Best Practices | ✅ Section 9 | ✅ Security |
| API Endpoints | ✅ Advanced | - | ✅ API Reference |

---

## Common Questions

### "How do I add my first intent?"

See: [Quick Start](QUICKSTART.md) → 5-Minute Setup

---

### "How does the AI classify my intents?"

See: [User Guide](USER-GUIDE.md) → Section 3: Understanding Classifications

---

### "What's the difference between The Entrepreneur and The Quant?"

See: [Architecture](ARCHITECTURE.md) → Agent Architecture

---

### "How do I deploy this to my team?"

See: [Deployment Guide](DEPLOYMENT-GUIDE.md) → Complete walkthrough

---

### "What does a dialectic analysis look like?"

See: [User Guide](USER-GUIDE.md) → Section 5: Running Dialectic Analysis

---

### "How do I customize the AI agents?"

See: [Architecture](ARCHITECTURE.md) → Extending the System → Adding Custom Agents

---

### "My intent isn't processing - what do I do?"

See: [Quick Start](QUICKSTART.md) → Troubleshooting Quick Fixes

---

### "How much does this cost to run?"

See: [Deployment Guide](DEPLOYMENT-GUIDE.md) → Cost Breakdown

---

### "Can I run this locally?"

See: [Deployment Guide](DEPLOYMENT-GUIDE.md) → Section 4: Local Testing

---

### "How do I see agent performance metrics?"

See: [User Guide](USER-GUIDE.md) → Section 8: Using the Performance Dashboard

---

## Glossary

**Action Pipe**: A decision that's been analyzed and approved, ready for execution

**Agent Persona**: AI personality with specific focus (Entrepreneur/Quant/Auditor)

**Acceptance Rate**: % of AI recommendations kept as-is (measures AI accuracy)

**Dialectic Flow**: Multi-agent analysis with Growth vs. Risk perspectives

**Executive Intent**: Strategic decision requiring analysis and approval

**Knowledge Node**: Concept or framework extracted from reference content

**Polling Cycle**: Background check for new intents (every 2 minutes)

**Settlement Diff**: Difference between AI suggestion and human final decision

**Smart Router**: Auto-assigns best agent based on keywords and metadata

**System Inbox**: Primary input queue for all requests

**Task Spawning**: Auto-creating tasks from approved action templates

**Triage Destination**: Where intent was routed (Strategic/Operational/Reference)

---

## Version History

### v1.0.0 (Current)
- Initial public release
- 10 Notion databases fully integrated
- 3 AI agent personas
- Dialectic analysis
- Training data capture
- Task spawning
- Smart router
- Performance dashboard

### Roadmap (P3 Features)
- Multi-user support
- Slack/Discord notifications
- Custom agent builder UI
- Workflow templates
- Fine-tuned models
- Mobile app

---

## Support & Contributing

### Getting Help

1. **Documentation**: Start here (this file)
2. **Logs**: `railway logs` or `logs/app.log`
3. **Health Check**: `curl https://your-app.up.railway.app/health`
4. **Execution Log**: Check DB_Execution_Log in Notion for audit trail

### Reporting Issues

When reporting issues, include:
- System status from `/health` endpoint
- Recent logs from Railway or `logs/app.log`
- Steps to reproduce
- Expected vs. actual behavior

### Contributing

Contributions welcome! Areas of interest:
- Custom agent personas
- New workflow integrations
- Performance optimizations
- Documentation improvements
- Test coverage

---

## License

MIT License - See LICENSE file for details

---

## Acknowledgments

Built with:
- **Notion API** - Database platform
- **Anthropic Claude** - AI analysis engine
- **FastAPI** - Python web framework
- **Railway** - Deployment platform

---

**Start your journey**:
- New to the system? → [Executive Overview](README-EXECUTIVE.md)
- Ready to use? → [Quick Start](QUICKSTART.md)
- Need to deploy? → [Deployment Guide](DEPLOYMENT-GUIDE.md)
- Want to understand deeply? → [Architecture](ARCHITECTURE.md)

**Every great decision starts with great analysis. Let's begin.**
