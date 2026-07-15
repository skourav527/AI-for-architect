# 🔒 Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in this repository, please follow responsible disclosure practices:

1. **DO NOT** open a public issue
2. Send details privately to the repository owner via GitHub Security Advisories
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

## Secure Configuration

### API Keys and Secrets

**NEVER commit sensitive data to this repository:**

- ✅ **USE** `.env` files (already in .gitignore)
- ✅ **USE** `.env.template` for sharing configuration structure
- ✅ **USE** environment variables
- ❌ **NEVER** hardcode API keys in source files
- ❌ **NEVER** commit certificate files
- ❌ **NEVER** commit credential files

### Before Pushing Code

Run this pre-commit checklist:

```bash
# Check for accidentally staged sensitive files
git status

# Search for potential secrets in staged files
git diff --staged | grep -i "api_key\|secret\|password\|token"

# Verify .gitignore is working
git check-ignore -v .env certificates/*
```

## Protected Files & Patterns

These are automatically excluded via `.gitignore`:

```
✅ .env, .env.* (except .env.template)
✅ certificates/*, *.pem, *.key, *.crt
✅ appsettings.json, secrets.json
✅ *password*, *credential*, *secret*
✅ Database files (*.db, *.sqlite)
```

## Safe API Key Management

### Setting Up Environment Variables

1. **Copy the template:**
   ```bash
   cp .env.template .env
   ```

2. **Add your keys to `.env`:**
   ```env
   OPENAI_API_KEY=sk-your-real-key-here
   ANTHROPIC_API_KEY=sk-ant-your-real-key-here
   ```

3. **Never commit `.env`:**
   - It's already in `.gitignore`
   - Double-check: `git status` should NOT show `.env`

### Loading Environment Variables in Code

```python
import os
from dotenv import load_dotenv

load_dotenv()  # Loads from .env file

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment")
```

## API Key Rotation

If you accidentally commit an API key:

### Immediate Actions:

1. **Revoke the exposed key immediately:**
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/settings/keys

2. **Generate a new key**

3. **Update your local `.env` file**

4. **Remove from Git history** (if already pushed):
   ```bash
   # Use BFG Repo-Cleaner or git-filter-repo
   # Better: Create a fresh repository if history is not important
   ```

## Dependencies Security

### Regular Updates

```bash
# Check for security advisories
pip list --outdated

# Update dependencies
pip install --upgrade package-name

# For uv projects
uv pip install --upgrade package-name
```

### Audit Dependencies

```bash
# Install safety checker
pip install safety

# Scan for known vulnerabilities
safety check
```

## Production Deployment

For production deployments:

1. **Use managed secret services:**
   - Azure Key Vault
   - AWS Secrets Manager
   - HashiCorp Vault
   - GitHub Secrets (for CI/CD)

2. **Implement rate limiting** to prevent abuse

3. **Add authentication** for exposed endpoints

4. **Use HTTPS only** for API communications

5. **Monitor API usage** for unusual patterns

6. **Implement proper error handling** (don't leak sensitive info in errors)

## Code Security Best Practices

### Input Validation

```python
from pydantic import BaseModel, Field, validator

class UserInput(BaseModel):
    prompt: str = Field(..., max_length=10000)
    
    @validator('prompt')
    def validate_prompt(cls, v):
        # Sanitize input
        return v.strip()
```

### Secure API Calls

```python
import httpx
from tenacity import retry, stop_after_attempt

@retry(stop=stop_after_attempt(3))
async def safe_api_call(prompt: str):
    async with httpx.AsyncClient(
        timeout=30.0,  # Prevent hanging
        limits=httpx.Limits(max_connections=10)
    ) as client:
        # Make API call
        pass
```

## File Permissions

When deploying:

```bash
# Restrict access to sensitive files
chmod 600 .env
chmod 600 certificates/*
chmod 700 certificates/
```

## Monitoring & Logging

### What to Log

- ✅ API request timestamps
- ✅ Response status codes
- ✅ Error types (without details)
- ✅ Usage metrics

### What NOT to Log

- ❌ API keys or tokens
- ❌ User passwords or credentials
- ❌ Full request/response bodies with PII
- ❌ Certificate contents

## Incident Response

If a security incident occurs:

1. **Assess scope** - What was exposed?
2. **Contain** - Revoke compromised credentials
3. **Notify** - Inform affected parties if necessary
4. **Document** - Record what happened and how it was resolved
5. **Prevent** - Update processes to prevent recurrence

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [OpenAI Security Best Practices](https://platform.openai.com/docs/guides/safety-best-practices)
- [GitHub Security Advisories](https://docs.github.com/en/code-security/security-advisories)

## Security Checklist Before Public Release

- [ ] No API keys in code or commits
- [ ] `.env` file is in `.gitignore`
- [ ] Certificates folder is in `.gitignore`
- [ ] Database files are in `.gitignore`
- [ ] All secrets use environment variables
- [ ] `.env.template` has placeholder values only
- [ ] README includes security setup instructions
- [ ] Dependencies are up to date
- [ ] No personal/company-specific data in code
- [ ] License file is present
- [ ] SECURITY.md is present (this file)

---

**Last Updated:** 2026-07-15  
**Security Contact:** [Create a security advisory](../../security/advisories/new)
