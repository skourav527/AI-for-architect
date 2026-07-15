# Foundation Week 4 - MCP Production Practice

## 📁 Folder Structure
```
Foundation-Week-4/
├── Document/
│   ├── WEEK4_4DAY_MCP_PRACTICE_PLAN.md          # Main 4-day plan
│   └── WEEK4_PRODUCTION_PATTERNS_QUICK_REF.md   # Quick reference cheatsheet
├── templates/
│   ├── api_connector_template.py                # Day 1: REST API starter
│   ├── database_connector_template.py           # Day 2: Database starter
│   ├── file_connector_template.py               # Day 3: File/RAG starter
│   └── test_mcp_server_template.py              # Day 4: Testing starter
└── Project-1/  # Your Day 1 implementation
└── Project-2/  # Your Day 2 implementation
└── Project-3/  # Your Day 3 implementation
```

## 🎯 Week 4 Goal
Build 3 production-grade MCP servers with HTTP transport, security, validation, and testing.

## 🚀 Quick Start

### Day 1: REST API MCP
```bash
cd Foundation-Week-4/Project-1
cp ../templates/api_connector_template.py mcp_server.py
# Edit to connect to your work API (ADO/SonarQube/GitHub)
uv run mcp_server.py
```

### Day 2: Database MCP
```bash
cd Foundation-Week-4/Project-2
cp ../templates/database_connector_template.py mcp_server.py
# Configure database connection in .env
uv run mcp_server.py
```

### Day 3: File/RAG MCP
```bash
cd Foundation-Week-4/Project-3
cp ../templates/file_connector_template.py mcp_server.py
# Set allowed roots in .env
uv run mcp_server.py
```

### Day 4: Testing
```bash
cd Foundation-Week-4/Project-1  # Or any project
cp ../templates/test_mcp_server_template.py test_mcp_server.py
pytest test_mcp_server.py -v
```

## 📝 What You'll Learn

### Production Patterns
- ✅ Stateless vs Streamable HTTP transport
- ✅ Input validation (schema + business + security)
- ✅ Error taxonomy with JSON-RPC codes
- ✅ Secrets management with environment variables
- ✅ SQL injection prevention
- ✅ Path traversal prevention
- ✅ Connection pooling
- ✅ Structured logging with correlation IDs
- ✅ Health checks and metrics
- ✅ Comprehensive testing

### Week 4 Completion Checklist
- [ ] Server 1 (API): HTTP transport + error handling
- [ ] Server 2 (Database): Parameterized queries + validation
- [ ] Server 3 (File): Stateless design + path security
- [ ] All servers tested (>70% coverage)
- [ ] Production deployment docs created
- [ ] Can build production MCP in <2 hours

## 📚 Key Documents

1. **WEEK4_4DAY_MCP_PRACTICE_PLAN.md** - Full day-by-day schedule
2. **WEEK4_PRODUCTION_PATTERNS_QUICK_REF.md** - Quick reference for patterns
3. **Templates** - Production-ready starter code for each server type

## 🔗 Prerequisites
- Completed Week 3 (MCP fundamentals)
- Python 3.10+
- uv or pip
- Basic understanding of HTTP, SQL, and file systems

## 💡 Tips
- Start with templates, customize for your use case
- Focus on security validation patterns
- Test both success and failure paths
- Document deployment steps as you go
- Use Copilot prompts from the plan document

## 📖 Next Steps After Week 4
- Upgrade existing ADO/SonarQube MCP servers
- Build MCP servers for new work projects
- Move to Week 5 (Flex week / advanced topics)

---

**Remember**: Week 4 is about production readiness, not just "working code". Every server should be deployable, secure, and tested.
