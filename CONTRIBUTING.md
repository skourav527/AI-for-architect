# 🤝 Contributing Guidelines

Thank you for considering contributing to this learning repository! This project aims to help developers learn AI Engineering, LLM integration, and MCP development through practical examples.

## 🎯 How You Can Contribute

### 1. **Improve Existing Code** 💻
- Fix bugs or errors in examples
- Enhance error handling
- Optimize performance
- Add type hints
- Improve code documentation

### 2. **Add New Examples** 🆕
- New LLM provider integrations
- Additional MCP server implementations
- Different architectural patterns
- Production deployment examples

### 3. **Enhance Documentation** 📚
- Fix typos or clarify explanations
- Add code comments
- Create tutorials or guides
- Improve README files
- Add diagrams or visual aids

### 4. **Share Resources** 📖
- Link to helpful articles or videos
- Add learning resources
- Suggest better approaches
- Share debugging tips

### 5. **Report Issues** 🐛
- Bug reports
- Documentation gaps
- Confusing examples
- Security concerns

## 🚀 Getting Started

### Fork and Clone

1. **Fork this repository** to your GitHub account
2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/ai-llm-learning-journey.git
   cd ai-llm-learning-journey
   ```

3. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/ORIGINAL-OWNER/ai-llm-learning-journey.git
   ```

### Set Up Development Environment

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install uv
   # Install project-specific dependencies as needed
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.template .env
   # Add your API keys to .env
   ```

## 📝 Contribution Workflow

### 1. Create a Feature Branch

```bash
# Update your fork
git fetch upstream
git checkout main
git merge upstream/main

# Create a new branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### Branch Naming Convention

- `feature/` - New features or examples
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Adding tests

Examples:
- `feature/add-cohere-integration`
- `fix/streaming-client-error-handling`
- `docs/improve-mcp-setup-guide`

### 2. Make Your Changes

**Code Quality Standards:**

```python
# Use type hints
def process_response(text: str, max_length: int = 100) -> str:
    """Process and truncate response text.
    
    Args:
        text: Input text to process
        max_length: Maximum length of output
        
    Returns:
        Processed text string
    """
    return text[:max_length]

# Add docstrings for functions and classes
# Use meaningful variable names
# Include error handling
# Follow PEP 8 style guidelines
```

**Documentation Standards:**

- Update README files if adding new features
- Add inline comments for complex logic
- Include usage examples
- Document prerequisites and dependencies

### 3. Test Your Changes

```bash
# Test the specific project
cd Foundation-Week-X/project-name
uv run your_script.py

# Verify no sensitive data is included
git diff

# Check for common issues
python -m py_compile your_file.py
```

### 4. Commit Your Changes

**Commit Message Format:**

```
<type>: <short description>

<detailed description (optional)>

<footer (optional)>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**

```bash
git commit -m "feat: add Cohere provider integration to multi-provider CLI"

git commit -m "fix: handle rate limit errors in streaming client

- Add exponential backoff for 429 errors
- Improve error messages
- Add retry configuration"

git commit -m "docs: add MCP server deployment guide"
```

### 5. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name
```

Then:
1. Go to your fork on GitHub
2. Click "Compare & pull request"
3. Fill out the PR template (see below)
4. Submit the pull request

## 📋 Pull Request Guidelines

### PR Title Format

- Use clear, descriptive titles
- Start with a capital letter
- Use imperative mood ("Add feature" not "Added feature")

Examples:
- ✅ "Add streaming support for Claude models"
- ✅ "Fix token counting in multi-turn conversations"
- ✅ "Update MCP server documentation"
- ❌ "Updated stuff"
- ❌ "bug fix"

### PR Description Template

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Performance improvement

## Changes Made
- List key changes
- One per line
- Be specific

## Testing Done
- [ ] Tested locally
- [ ] Verified with both OpenAI and Anthropic (if applicable)
- [ ] Checked for sensitive data in commits
- [ ] Updated documentation

## Screenshots (if applicable)
Add screenshots for UI changes or output examples.

## Related Issues
Closes #123 (if applicable)

## Additional Notes
Any other context or notes for reviewers.
```

## ✅ Code Review Process

1. **Automated checks** will run (if configured)
2. **Maintainer review** - usually within 48-72 hours
3. **Feedback addressed** - make requested changes
4. **Approval and merge** - once approved, changes will be merged

## 🎨 Code Style Guidelines

### Python Style

Follow [PEP 8](https://pep8.org/) guidelines:

```python
# Good
def calculate_token_cost(tokens: int, model: str) -> float:
    """Calculate cost based on tokens and model."""
    rates = {
        "gpt-4": 0.03,
        "gpt-3.5-turbo": 0.002,
    }
    return tokens * rates.get(model, 0)

# Bad
def calc(t,m):
    r={"gpt-4":0.03,"gpt-3.5-turbo":0.002}
    return t*r.get(m,0)
```

### Formatting

- **Indentation**: 4 spaces (no tabs)
- **Line length**: Max 100 characters (120 for special cases)
- **Imports**: Grouped (standard library, third-party, local)
- **Quotes**: Use double quotes for strings
- **Trailing commas**: Use in multi-line lists/dicts

## 🔒 Security Guidelines

**CRITICAL - Before Committing:**

1. ✅ **NO API keys** in code
2. ✅ **NO passwords** or credentials
3. ✅ **NO certificates** or private keys
4. ✅ Use `.env` for all secrets
5. ✅ Check `git diff` before committing

```bash
# Always check before committing
git diff --staged

# Search for potential secrets
git diff --staged | grep -i "api_key\|secret\|password"
```

## 📦 Adding Dependencies

When adding new dependencies:

1. **Document why it's needed**
2. **Pin versions** in requirements.txt
3. **Update setup instructions**
4. **Keep dependencies minimal**

```bash
# Add to requirements.txt
httpx==0.24.1  # Async HTTP client for LLM API calls
```

## 🐛 Reporting Issues

### Bug Reports

Include:
- **Clear title** describing the issue
- **Steps to reproduce** (be specific)
- **Expected behavior**
- **Actual behavior**
- **Environment** (Python version, OS)
- **Code snippet** (if applicable)
- **Error messages** (full traceback)

### Feature Requests

Include:
- **Clear description** of the feature
- **Use case** - why is this valuable?
- **Proposed implementation** (optional)
- **Examples** from other projects (optional)

## 💡 Tips for Good Contributions

1. **Start small** - Begin with documentation or small fixes
2. **Ask questions** - Open an issue to discuss before big changes
3. **One PR per feature** - Keep changes focused
4. **Test thoroughly** - Verify your changes work
5. **Be patient** - Reviews take time
6. **Be receptive** - Consider feedback constructively

## 📞 Communication

- **GitHub Issues** - For bugs and feature requests
- **Pull Request comments** - For code-specific discussions
- **Discussions tab** - For general questions and ideas

## 🏆 Recognition

Contributors will be:
- Listed in the project's contributors section
- Credited in release notes (for significant contributions)
- Appreciated in PR comments and merges

## 📜 License

By contributing, you agree that your contributions will be licensed under the same [MIT License](LICENSE) as the project.

---

## Thank You! 🙏

Your contributions help make this a better learning resource for the entire community. Whether it's a typo fix, a new feature, or just a helpful comment, every contribution matters!

**Happy Contributing! 🎉**
