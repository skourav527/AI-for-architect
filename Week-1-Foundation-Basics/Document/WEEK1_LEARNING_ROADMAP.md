# Week 1: Python + LLM API Integration - Accelerated Learning Path

## 🎯 The 80/20 Learning Strategy

**Goal**: Learn by BUILDING, not watching. Each concept is learned ONLY when you need it for the project.

---

## 📅 Day-by-Day Project-Based Schedule (5-7 Days)

### **Day 1-2: Python Essentials + Project 1 Foundation (6-8 hours)** - Done 
#### Morning: Quick Python Refresher (2 hours)
- **DON'T**: Watch full Python courses
- **DO**: Code these 5 essential patterns:

```python
# 1. List/Dict Comprehensions (you'll use these EVERYWHERE)
# 2. Context Managers (for API connections)
# 3. Decorators (for retry logic)
# 4. Type Hints with Pydantic (for API validation)
# 5. Basic async/await (for concurrent API calls)
```

**Action**: Open `quick-references/python-essentials.py` and TYPE OUT each example (don't copy-paste)

#### Afternoon: Start Project 1 - Advanced LLM Client (4-6 hours) - Done 
**Build Phase 1**: Synchronous OpenAI client
- Set up environment (.env, API keys)
- Create basic client with error handling
- Add logging
- Test with simple prompts

**Learning by Doing**:
- ✅ You'll learn Pydantic when validating API responses
- ✅ You'll learn context managers when managing connections
- ✅ You'll learn decorators when adding retry logic

---

### **Day 3: Async Programming + Project 1 Phase 2 (6-8 hours)** - In progress 

#### Morning: Async Essentials (2 hours)
**Just-In-Time Learning**:
- Run `quick-references/async-patterns.py` examples
- Understand: `async def`, `await`, `asyncio.gather()`
- That's 90% of what you need!

#### Afternoon: Convert Project 1 to Async (4-6 hours)
**Build Phase 2**: Make your client async
- Convert to `aiohttp` or `httpx`
- Add concurrent request handling
- Implement retry with `tenacity`
- Add rate limiting

**Real Learning**: You'll truly understand async when you see 10 API calls complete in 1 second vs 10 seconds

---

### **Day 4: Multi-Provider Integration - Project 2 (6-8 hours)**

**Build**: Multi-Provider Chat CLI
- Abstract common interface for OpenAI/Anthropic
- Use `click` for CLI
- Use `rich` for beautiful output
- Stream responses

**What You'll Learn**:
- Abstract base classes (when creating provider interface)
- Streaming APIs (when implementing real-time output)
- CLI design (when building user interface)

---

### **Day 5: Advanced Features - Project 3 (6-8 hours)**

**Build**: Token Usage Tracker
- Track costs across providers
- Store usage in SQLite/JSON
- Create usage reports
- Add budget alerts

**What You'll Learn**:
- Data persistence patterns
- Aggregation and analysis
- Background tasks

---

### **Day 6-7: Integration + Production Patterns (4-6 hours)**

**Combine All Projects**:
- Integrate token tracker into multi-provider CLI
- Add configuration management (different configs for dev/prod)
- Add comprehensive error handling
- Write a few tests

---

## 🚀 Quick Start: Do This RIGHT NOW

### Step 1: Environment Setup (10 minutes)
```bash
cd "c:\Users\skourav\My Python\week1-python-llm"

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install essentials
pip install openai anthropic aiohttp httpx tenacity pydantic python-dotenv click rich
```

### Step 2: Create .env file
```bash
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Step 3: Start with Project 1, Stage 1
Open `project1-llm-client/stage1_sync_client.py` and start coding!

---

## 💡 Learning Principles for Rapid Mastery

### 1. **Learn-By-Needing, Not Learn-By-Reading**
❌ Don't: "Let me read about decorators for 2 hours"
✅ Do: "I need retry logic. Let me see how `@retry` decorator works"

### 2. **Type, Don't Copy-Paste**
Muscle memory matters. Type every line of starter code to understand it.

### 3. **Break When It Works, Then Fix It**
- Got code working? 
- Change something deliberately to break it
- Fix it yourself
- Now you REALLY understand it

### 4. **Use AI Tools Smart**
```
❌ Bad prompt: "Teach me async Python"
✅ Good prompt: "I have this synchronous API client [paste code]. 
   Convert it to async using httpx and explain only the changes"
```

### 5. **Progressive Enhancement**
Each project has 3 stages:
- **Stage 1**: Basic version (synchronous, simple)
- **Stage 2**: Async + error handling
- **Stage 3**: Production-ready (logging, config, tests)

---

## 📚 Just-In-Time Learning Resources (Use When Needed)

### When You Need Async:
- **5-min read**: Python docs - asyncio basics
- **10-min practice**: Run `quick-references/async-patterns.py`

### When You Need Decorators:
- **5-min read**: Real Python decorators primer
- **Code example**: See `@retry` in your project

### When You Need Pydantic:
- **Action**: Look at Pydantic docs for the exact validation you need
- **Time**: 10 minutes per use case

### When You Need Context Managers:
- **Read**: Python `with` statement (5 min)
- **Use**: Implement one in your client (15 min)

---

## ✅ Knowledge Validation (Not Tests, Real Checks)

After each project, you should be able to:

### After Project 1:
- [ ] Explain why `async` makes API calls faster
- [ ] Add a new retry strategy in 5 minutes
- [ ] Switch between OpenAI models without code changes

### After Project 2:
- [ ] Add a new LLM provider (like Cohere) in 30 minutes
- [ ] Explain streaming vs non-streaming responses
- [ ] Debug connection issues quickly

### After Project 3:
- [ ] Calculate true cost of your LLM usage
- [ ] Set up alerts for budget overruns
- [ ] Optimize token usage based on data

---

## 🎯 Success Metrics (Know You're Ready for Week 2)

✅ You can build a working LLM client from scratch in 1 hour
✅ You understand when to use `async` and when it's overkill
✅ You can debug API errors without panicking
✅ You can read someone else's async code and understand it
✅ You've made 1000+ API calls and handled failures gracefully

---

## 🔥 Pro Tips from Senior Developers

### Tip 1: **Print-Driven Development**
Don't understand what's happening? Add `print()` statements everywhere. See the data flow.

### Tip 2: **Read Error Messages Backwards**
Python tracebacks: start from the BOTTOM (your code) then work up.

### Tip 3: **Use IPython for Exploration**
```bash
pip install ipython
ipython
```
Test snippets interactively. Way faster than running full scripts.

### Tip 4: **Commit Small, Commit Often**
```bash
git init
git add .
git commit -m "Stage 1 working"
```
So you can rollback when you break things (and you will).

### Tip 5: **Ask "What's the Minimal Version?"**
Before adding features, get the simplest possible version working first.

---

## 🚫 Common Traps to Avoid

1. **Tutorial Hell**: Don't watch 10 async tutorials. Watch ONE, then CODE.
2. **Perfect Code Syndrome**: Your first version will be ugly. That's fine.
3. **Feature Creep**: Stick to the project scope. Add extras AFTER it works.
4. **No Error Handling**: Add try/except from Day 1, even if it's just logging.

---

## 📊 Time Allocation Reality Check

| Activity | Ideal | Reality | How to Handle |
|----------|-------|---------|---------------|
| Reading docs | 20% | 40% | Set 10-min timers |
| Writing code | 50% | 30% | Force yourself to type |
| Debugging | 20% | 25% | Expected, use debugger |
| Thinking/Planning | 10% | 5% | Sketch before coding |

---

## 🎬 Start NOW: Your First 30 Minutes

1. **Minute 0-10**: Set up environment (above)
2. **Minute 10-15**: Read `project1-llm-client/stage1_sync_client.py`
3. **Minute 15-30**: Make your first OpenAI API call successfully
4. **Minute 30+**: Add error handling, then logging

By end of Hour 1: You have a working LLM client. Already learning!

---

## 🤝 Week 2 Preparation

Once you complete Week 1 projects:
- Your FastAPI services (Week 2) will use these clients
- Your LangChain work (Week 2) builds on these patterns
- You'll understand async for FastAPI WebSockets

**Week 1 is your foundation. Build it solid by building real things.**

---

## Need Help?

- **Stuck on async?** → See `quick-references/async-debugging.md`
- **API errors?** → Check `quick-references/api-troubleshooting.md`
- **Type hints confusing?** → See `quick-references/type-hints-guide.md`

**Remember**: Confusion is part of learning. Struggle for 20 minutes, then ask for help.

---

Let's build! 🚀
