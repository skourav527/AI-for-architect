# Week 1: Python Foundations + LLM API Integration

**Learn by building, not by watching!**

This is your complete, hands-on learning path to master Python for Gen AI development in 5-7 days.

## 📁 What's Inside

```
week1-python-llm/
├── 📖 WEEK1_LEARNING_ROADMAP.md    ← Start here! Complete strategy
├── 🚀 QUICK_START.md                ← 5-minute setup guide
├── ⚙️  setup.ps1                     ← Automated setup script
├── 📦 requirements.txt               ← All dependencies
├── 🔐 .env.template                  ← API keys template
│
├── quick-references/                ← Cheat sheets (type these!)
│   ├── python-essentials.py         ← Core Python patterns
│   ├── async-patterns.py            ← Async/await mastery
│   └── decorators-context-managers.md
│
├── project1-llm-client/             ← Build async LLM client
│   ├── stage1_sync_client.py        ← Start here (2-3 hours)
│   ├── stage2_async_client.py       ← Add async (3-4 hours)
│   └── stage3_production_ready.py   ← Full features (coming soon)
│
├── project2-multi-provider-cli/     ← Multi-provider chat CLI
│   ├── chat_cli.py                  ← Main CLI (4-6 hours)
│   └── README.md                    ← Project guide
│
└── project3-token-tracker/          ← Track API usage & costs
    ├── token_tracker.py             ← Token tracking (4-6 hours)
    └── README.md                    ← Project guide
```

## 🎯 Learning Objectives

By the end of Week 1, you will:

✅ **Master Advanced Python**
- List comprehensions, decorators, context managers
- Type hints with Pydantic
- Python idioms and best practices

✅ **Async Programming**
- async/await fundamentals
- Concurrent API calls with asyncio
- Async context managers

✅ **LLM API Integration**
- OpenAI and Anthropic SDKs
- Error handling and retry logic
- Token usage optimization

✅ **Production Patterns**
- Logging, configuration management
- Rate limiting and backoff strategies
- CLI tools with Click and Rich

## 🚀 Quick Start

### ⚡ **NEW LEARNERS: Start with [START_HERE.md](START_HERE.md)**
*Get from zero to your first API call in 30 minutes!*

### Option 1: Automated Setup
```powershell
cd "c:\Users\skourav\My Python\week1-python-llm"
.\setup.ps1
```

### Option 2: Manual Setup
```powershell
# 1. Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up API keys
copy .env.template .env
# Edit .env and add your keys

# 4. Test
python quick-references/python-essentials.py
```

## 📚 Your Learning Path

### **Day 1-2: Foundations + Sync Client** (6-8h)
1. Read `WEEK1_LEARNING_ROADMAP.md`
2. Type and run `quick-references/python-essentials.py`
3. Build `project1-llm-client/stage1_sync_client.py`
4. Make your first successful API call! 🎉

### **Day 3: Async Mastery** (6-8h)
1. Run `quick-references/async-patterns.py`
2. Convert to async: `stage2_async_client.py`
3. Experience the speed: 10 requests in 1 second!

### **Day 4: Multi-Provider CLI** (6-8h)
1. Build `project2-multi-provider-cli/chat_cli.py`
2. Switch between OpenAI and Claude
3. Add streaming responses

### **Day 5: Token Tracking** (6-8h)
1. Build `project3-token-tracker/token_tracker.py`
2. Track costs and usage
3. Set budget alerts

### **Day 6-7: Integration** (4-6h)
1. Combine all projects
2. Add token tracking to CLI
3. Polish and document

## 🎓 Learning Principles

### 1. **Learn-By-Needing, Not Learn-By-Reading**
❌ Don't spend 2 hours reading about decorators  
✅ Learn decorators when you need retry logic

### 2. **Type, Don't Copy-Paste**
Muscle memory matters. Type every example.

### 3. **Break It, Then Fix It**
- Got code working?
- Change something to break it
- Fix it yourself
- Now you REALLY understand it

### 4. **20-Minute Rule**
- Stuck? Try for 20 minutes
- Still stuck? Ask for help
- Don't waste hours in frustration

### 5. **Build Real Things**
- No toy examples
- Projects you'll actually use
- Production-ready patterns

## 💡 What Makes This Different?

### Traditional Learning (❌)
- Watch 50 hours of lectures
- Memorize syntax
- Build toy examples
- Never use it in production
- Forget everything in a week

### This Approach (✅)
- Build real projects immediately
- Learn concepts when needed
- Production-ready code
- Muscle memory from typing
- Skills you'll use daily

## 🛠️ Projects You'll Build

### 1. **Advanced LLM Client**
- Async API calls
- Automatic retry logic
- Error handling
- Logging and monitoring

**Real-world use**: Every Gen AI app needs this!

### 2. **Multi-Provider Chat CLI**
- Works with OpenAI, Claude, local models
- Abstract provider interface
- Beautiful terminal UI
- Streaming responses

**Real-world use**: Switch providers without code changes!

### 3. **Token Usage Tracker**
- Track costs across providers
- SQLite persistence
- Usage analytics
- Budget alerts

**Real-world use**: Don't blow your API budget!

## 📊 Success Metrics

You're ready for Week 2 when you can:

- [ ] Build an LLM client from scratch in 1 hour
- [ ] Explain when to use async (and when not to)
- [ ] Debug API errors without panicking
- [ ] Read and understand async code
- [ ] Track and optimize token usage
- [ ] Switch between LLM providers easily

## 🔧 Tools You'll Master

| Tool | Purpose | Why It Matters |
|------|---------|----------------|
| `async/await` | Concurrent operations | 10x faster API calls |
| `httpx` | Async HTTP | Modern API client |
| `tenacity` | Retry logic | Handle failures gracefully |
| `Pydantic` | Validation | Type-safe APIs |
| `click` | CLI creation | Professional interfaces |
| `rich` | Terminal UI | Beautiful output |
| `dotenv` | Config management | Secure API keys |

## 🚨 Common Mistakes to Avoid

### 1. Tutorial Hell
❌ Watching 10 async tutorials  
✅ Watch ONE, then CODE

### 2. Perfect Code Syndrome
❌ Trying to write perfect code first try  
✅ Make it work, then make it better

### 3. No Error Handling
❌ Assuming everything will work  
✅ Add try/except from Day 1

### 4. Copy-Paste Learning
❌ Copying code without understanding  
✅ Type it out, experiment with changes

### 5. Isolated Learning
❌ Learning concepts in isolation  
✅ Learn while building real projects

## 📖 Reference Materials

### Quick References (In this repo)
- `python-essentials.py` - Core patterns
- `async-patterns.py` - Async mastery
- `decorators-context-managers.md` - Advanced patterns

### External Resources (Use sparingly!)
- Python Docs - When you need specific function
- Real Python - For specific topics (10-min reads)
- Stack Overflow - For specific errors

### AI Tools (Use smartly!)
```
❌ Bad: "Teach me async Python"
✅ Good: "Convert this sync code to async [paste code]"
```

## 🎯 Week 2 Preview

After Week 1, you'll build:
- FastAPI services
- LangChain pipelines
- RAG systems
- Vector databases

Your Week 1 skills (async, error handling, API clients) will be crucial!

## 💬 Support & Help

### Getting Stuck?
1. Read error message (start from bottom)
2. Add print statements
3. Check .env file
4. Google exact error
5. Ask AI with specific context
6. Take 10-minute break
7. Explain to rubber duck 🦆

### Questions?
- Check README files in each project folder
- Review quick-references
- Read QUICK_START.md

## 🌟 Motivation

You're not just learning Python for Gen AI. You're building:

- **Async thinking** → Crucial for modern APIs
- **Production patterns** → Error handling, retry, logging
- **System design** → How to architect robust systems
- **Future-proof skills** → LLM integration is the future

Every line you type makes you better.  
Every error you fix makes you stronger.  
Every project you complete brings you closer to mastery.

## 📝 Credits & Philosophy

This curriculum is designed around:
- **Project-based learning** - Build real things
- **Just-in-time learning** - Learn when needed
- **Deliberate practice** - Type, break, fix, repeat
- **Production-ready** - No toy examples

Influenced by:
- Fast.ai's top-down approach
- The Recurse Center's self-directed learning
- Modern software engineering practices

## 🚀 Ready to Start?

```powershell
# 1. Run setup
.\setup.ps1

# 2. Read the roadmap
# Open WEEK1_LEARNING_ROADMAP.md

# 3. Start Day 1
python quick-references/python-essentials.py

# 4. Build your first client
python project1-llm-client/stage1_sync_client.py
```

**Let's build!** 🎯

---

*Last updated: February 2026*  
*Questions? Check QUICK_START.md for troubleshooting*
