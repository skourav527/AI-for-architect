# 🚀 Quick Start Guide - Week 1

## Get Started in 5 Minutes

### Step 1: Navigate to the Week 1 folder
```powershell
cd "c:\Users\skourav\My Python\week1-python-llm"
```

### Step 2: Create virtual environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### Step 3: Install dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Set up API keys
```powershell
# Copy template
copy .env.template .env

# Edit .env and add your API keys:
# OPENAI_API_KEY=sk-your-key-here
# ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Step 5: Test your setup
```powershell
# Test Python essentials
python quick-references/python-essentials.py

# Test async patterns
python quick-references/async-patterns.py
```

---

## Your Learning Path (5-7 Days)

### 🎯 Day 1-2: Python Fundamentals + Project 1 Stage 1
**Time: 6-8 hours**

Morning (2-3 hours):
1. Run and understand `quick-references/python-essentials.py`
2. TYPE OUT (don't copy!) the examples
3. Experiment with changes

Afternoon (4-5 hours):
1. Open `project1-llm-client/stage1_sync_client.py`
2. Read through the code
3. Run it (add your API key first)
4. Make your first successful API call! 🎉
5. Modify examples to test different prompts

**Success Metric**: You can explain what Pydantic does and make API calls

---

### 🎯 Day 3: Async Programming + Project 1 Stage 2
**Time: 6-8 hours**

Morning (2 hours):
1. Run `quick-references/async-patterns.py`
2. Understand the timing difference: sync vs async
3. Practice with asyncio.gather()

Afternoon (4-6 hours):
1. Open `project1-llm-client/stage2_async_client.py`
2. Compare with stage1 - what's different?
3. Run async examples
4. See the POWER: 10 requests in ~1 second vs 10 seconds!

**Success Metric**: You understand why async is faster for I/O

---

### 🎯 Day 4: Multi-Provider CLI
**Time: 6-8 hours**

All Day:
1. Open `project2-multi-provider-cli/chat_cli.py`
2. Study the abstract base class pattern
3. Run examples:
   ```powershell
   python chat_cli.py "What is Python?"
   python chat_cli.py --provider anthropic "Write a haiku"
   python chat_cli.py --stream "Tell me a story"
   python chat_cli.py --interactive
   ```
4. Try switching between providers
5. Add a new model variant

**Success Metric**: You can add a new provider in 30 minutes

---

### 🎯 Day 5: Token Tracking
**Time: 6-8 hours**

All Day:
1. Open `project3-token-tracker/token_tracker.py`
2. Understand SQLite operations
3. Run examples
4. See your usage stats!
5. Exercise: Integrate with Project 2

**Success Metric**: You can track and analyze token usage

---

### 🎯 Day 6-7: Integration & Polish
**Time: 4-6 hours**

1. Combine all three projects
2. Add token tracking to your CLI
3. Add error handling improvements
4. Write a few tests
5. Document your learnings

**Success Metric**: Working multi-provider CLI with token tracking

---

## Troubleshooting

### "OPENAI_API_KEY not found"
```powershell
# Option 1: Create .env file
copy .env.template .env
# Edit .env with your keys

# Option 2: Set environment variable
$env:OPENAI_API_KEY="sk-your-key"
```

### "Module not found"
```powershell
# Make sure virtual environment is activated
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "Cannot run script"
```powershell
# If you get execution policy error
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Async errors
- Make sure you're using `await` with async functions
- Use `asyncio.run()` to run async functions from sync code
- Use `async with` for async context managers

---

## Learning Tips

### 1. Type, Don't Copy-Paste
Muscle memory is real. Type the code yourself.

### 2. Break Things
- Code working? Change something and break it
- Then fix it yourself
- Now you REALLY understand it

### 3. Use Print Debugging
```python
print(f"Variable value: {variable}")
print(f"Type: {type(variable)}")
```

### 4. Read Error Messages Backwards
Start from the bottom (your code) and work up.

### 5. Use IPython for Exploration
```powershell
pip install ipython
ipython
```
Test snippets interactively.

### 6. AI Tools - Smart Prompts
❌ Bad: "Teach me async Python"
✅ Good: "I have this sync code [paste]. Convert to async and explain only the changes"

---

## Practice Challenges

### Easy
1. Add temperature control to CLI
2. Add max_tokens limit
3. Display token count after each request

### Medium
4. Add conversation history (multi-turn)
5. Save conversations to file
6. Add system prompt support

### Hard
7. Add a new provider (Cohere, local model)
8. Implement response caching
9. Add budget alerts

---

## Resource Optimization

### When to Watch Videos
- Stuck for 30+ minutes? Watch a 10-min video
- Need visual explanation? Find specific tutorial
- Don't watch 2-hour courses start-to-finish

### When to Read Docs
- Need specific function? Read that section only
- Set 10-minute timer
- Focus on examples, skip theory

### When to Ask AI
- After trying for 20 minutes yourself
- For code conversion (sync → async)
- For debugging specific errors

### When to Experiment
- Always! Try changing values
- "What if I do X?" → Just try it!
- Can't break anything permanently

---

## Daily Checklist

### Start of Day
- [ ] Activate virtual environment
- [ ] Review yesterday's code
- [ ] Set today's goal (be specific!)

### During Coding
- [ ] Read code before running
- [ ] Predict what will happen
- [ ] Run and verify
- [ ] Experiment with changes

### End of Day
- [ ] Commit your changes (`git add .`, `git commit -m "..."`)
- [ ] Write 3 things you learned
- [ ] Write 1 question for tomorrow

---

## You're Ready for Week 2 When...

✅ You can build an LLM client from scratch in 1 hour
✅ You understand when to use async
✅ You can debug API errors without panicking
✅ You can read someone's async code and understand it
✅ You've made 1000+ API calls successfully

---

## Next Steps

### After Week 1
- Week 2: FastAPI + LangChain
- You'll use these same patterns
- Your async knowledge will shine
- Token tracking becomes crucial

### Keep Learning
- Join Python Discord communities
- Read other people's code on GitHub
- Contribute to open source
- Build something you actually need

---

## Important Reminders

1. **Confusion is Normal**: If you're not confused, you're not learning
2. **Struggle First**: Try for 20 minutes before asking for help
3. **Build, Don't Watch**: 1 hour coding > 5 hours watching
4. **Small Wins**: Celebrate each working feature
5. **Take Breaks**: Your brain needs time to process

---

## Support

### Stuck? Try This:
1. Read error message carefully (start from bottom)
2. Print intermediate values
3. Check .env file and API keys
4. Google exact error message
5. Ask AI with specific context
6. Take 10-minute break
7. Explain problem to rubber duck (seriously!)

---

## Final Motivation

You're not just learning Python. You're building:
- **Async thinking**: Crucial for modern APIs
- **Production patterns**: Error handling, retry, logging
- **System design**: How to architect robust systems
- **LLM integration**: The future of software

Every line you type makes you better. Every error you fix makes you stronger.

**Let's build!** 🚀

---

*Questions? Check the README files in each project folder.*
