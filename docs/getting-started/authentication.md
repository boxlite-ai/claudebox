# Authentication Setup

Comprehensive guide to authenticating ClaudeBox with Claude Code.

---

## Overview

ClaudeBox supports two authentication methods:

1. **Claude Code OAuth Token** (Recommended)
2. **Anthropic API Key** (Alternative)

Both methods allow you to use Claude Code CLI within isolated micro-VMs.

---

## Method 1: Claude Code OAuth Token (Recommended)

### Step 1: Get Your OAuth Token

1. **Go to Claude.ai Settings**
   - Navigate to https://claude.ai/settings/developer
   - Sign in to your Claude account if not already logged in

2. **Create a New OAuth Token**
   - Click "Create new token" or "Generate OAuth token"
   - Give it a descriptive name (e.g., "ClaudeBox Development")
   - Set expiration (recommended: 90 days or never for development)

3. **Copy the Token**
   - Your token will start with `sk-ant-oat01-...`
   - **Important**: Save it immediately - you won't be able to see it again
   - Example: `sk-ant-oat01-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Step 2: Set Environment Variable

#### macOS / Linux

**Temporary (current session only):**
```bash
export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-YOUR-TOKEN-HERE
```

**Permanent (recommended):**

For **Bash** (`~/.bashrc` or `~/.bash_profile`):
```bash
echo 'export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-YOUR-TOKEN-HERE' >> ~/.bashrc
source ~/.bashrc
```

For **Zsh** (`~/.zshrc`):
```bash
echo 'export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-YOUR-TOKEN-HERE' >> ~/.zshrc
source ~/.zshrc
```

For **Fish** (`~/.config/fish/config.fish`):
```bash
echo 'set -gx CLAUDE_CODE_OAUTH_TOKEN sk-ant-oat01-YOUR-TOKEN-HERE' >> ~/.config/fish/config.fish
source ~/.config/fish/config.fish
```

#### Windows (WSL2)

Follow the same Linux instructions inside your WSL2 terminal.

### Step 3: Verify Authentication

**Create `test_auth.py`:**
```python
import asyncio
import os
from claudebox import ClaudeBox

async def main():
    # Check if token is set
    token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
    if not token:
        print("❌ CLAUDE_CODE_OAUTH_TOKEN not set")
        print("Run: export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-YOUR-TOKEN")
        return

    print(f"✅ Token found: {token[:20]}...")

    # Test authentication with ClaudeBox
    try:
        async with ClaudeBox() as box:
            result = await box.code("echo 'Authentication successful!'")
            if result.success:
                print("✅ Authentication verified!")
                print(f"Response: {result.response}")
            else:
                print("❌ Authentication failed")
                print(f"Error: {result.error}")
    except Exception as e:
        print(f"❌ Error: {e}")

asyncio.run(main())
```

**Run it:**
```bash
python3 test_auth.py
```

**Expected output:**
```
✅ Token found: sk-ant-oat01-xxxxx...
✅ Authentication verified!
Response: Authentication successful!
```

---

## Method 2: Anthropic API Key (Alternative)

### Step 1: Get Your API Key

1. **Go to Anthropic Console**
   - Navigate to https://console.anthropic.com/settings/keys
   - Sign in to your Anthropic account

2. **Create a New API Key**
   - Click "Create Key"
   - Give it a name (e.g., "ClaudeBox")
   - Copy the key (starts with `sk-ant-...`)

3. **Copy the Key**
   - Your key will start with `sk-ant-api...`
   - Example: `sk-ant-apixx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Step 2: Set Environment Variable

**Temporary:**
```bash
export ANTHROPIC_API_KEY=sk-ant-YOUR-API-KEY-HERE
```

**Permanent (recommended):**
```bash
# Bash
echo 'export ANTHROPIC_API_KEY=sk-ant-YOUR-API-KEY-HERE' >> ~/.bashrc
source ~/.bashrc

# Zsh
echo 'export ANTHROPIC_API_KEY=sk-ant-YOUR-API-KEY-HERE' >> ~/.zshrc
source ~/.zshrc
```

### Step 3: Verify Authentication

Same as OAuth token verification - ClaudeBox will automatically use the API key if OAuth token is not found.

---

## Passing Credentials Programmatically

Instead of environment variables, you can pass credentials directly:

### OAuth Token

```python
import asyncio
from claudebox import ClaudeBox

async def main():
    async with ClaudeBox(oauth_token="sk-ant-oat01-YOUR-TOKEN") as box:
        result = await box.code("echo 'Hello'")
        print(result.response)

asyncio.run(main())
```

### API Key

```python
import asyncio
from claudebox import ClaudeBox

async def main():
    async with ClaudeBox(api_key="sk-ant-YOUR-API-KEY") as box:
        result = await box.code("echo 'Hello'")
        print(result.response)

asyncio.run(main())
```

**Security Warning**: Hardcoding credentials is **not recommended** for production. Use environment variables or secret management systems.

---

## Authentication Priority

ClaudeBox checks for credentials in this order:

1. **Explicit parameters** (`oauth_token` or `api_key` in constructor)
2. **Environment variables**:
   - `CLAUDE_CODE_OAUTH_TOKEN` (checked first)
   - `ANTHROPIC_API_KEY` (fallback)

**Example:**
```python
# Priority 1: Explicit parameter (highest)
async with ClaudeBox(oauth_token="sk-ant-oat01-xxx") as box:
    ...

# Priority 2: CLAUDE_CODE_OAUTH_TOKEN env var
export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-xxx
async with ClaudeBox() as box:
    ...

# Priority 3: ANTHROPIC_API_KEY env var (fallback)
export ANTHROPIC_API_KEY=sk-ant-xxx
async with ClaudeBox() as box:
    ...
```

---

## Security Best Practices

### 1. Never Commit Credentials

**Bad:**
```python
# ❌ NEVER DO THIS
oauth_token = "sk-ant-oat01-actual-token-here"
```

**Good:**
```python
# ✅ Use environment variables
import os
oauth_token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
```

### 2. Use `.env` Files for Development

**Install python-dotenv:**
```bash
pip install python-dotenv
```

**Create `.env` file:**
```bash
# .env
CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-YOUR-TOKEN
```

**Add to `.gitignore`:**
```bash
echo ".env" >> .gitignore
```

**Use in code:**
```python
import asyncio
import os
from dotenv import load_dotenv
from claudebox import ClaudeBox

# Load .env file
load_dotenv()

async def main():
    async with ClaudeBox() as box:
        result = await box.code("echo 'Secure authentication'")
        print(result.response)

asyncio.run(main())
```

### 3. Use Secret Management in Production

For production deployments, use proper secret management:

**AWS Secrets Manager:**
```python
import boto3
import json
from claudebox import ClaudeBox

def get_secret():
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId='claudebox/oauth-token')
    return json.loads(response['SecretString'])['CLAUDE_CODE_OAUTH_TOKEN']

async def main():
    token = get_secret()
    async with ClaudeBox(oauth_token=token) as box:
        ...
```

**HashiCorp Vault:**
```python
import hvac
from claudebox import ClaudeBox

def get_secret():
    client = hvac.Client(url='http://vault:8200')
    secret = client.secrets.kv.v2.read_secret_version(path='claudebox')
    return secret['data']['data']['CLAUDE_CODE_OAUTH_TOKEN']

async def main():
    token = get_secret()
    async with ClaudeBox(oauth_token=token) as box:
        ...
```

### 4. Rotate Tokens Regularly

**Recommended rotation schedule:**
- Development: Every 90 days
- Production: Every 30 days
- After team member departure: Immediately

**How to rotate:**
1. Generate new OAuth token at https://claude.ai/settings/developer
2. Update environment variable / secret manager
3. Restart ClaudeBox applications
4. Revoke old token after confirming new one works

### 5. Limit Token Scope

When creating OAuth tokens:
- ✅ Use separate tokens for development and production
- ✅ Set appropriate expiration dates
- ✅ Revoke tokens that are no longer needed
- ❌ Don't share tokens between team members

### 6. Secure Environment Variables

**On shared systems:**
```bash
# Set restrictive permissions on .bashrc/.zshrc
chmod 600 ~/.bashrc

# Or use a secure .env file
chmod 600 .env
```

---

## Troubleshooting

### Issue: Authentication Error

**Error:**
```
AuthenticationError: No authentication token found
```

**Solution:**
```bash
# Check if environment variable is set
echo $CLAUDE_CODE_OAUTH_TOKEN

# If empty, set it
export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-YOUR-TOKEN
```

### Issue: Invalid Token

**Error:**
```
AuthenticationError: Invalid authentication token
```

**Causes & Solutions:**

1. **Expired token**
   - Generate new token at https://claude.ai/settings/developer
   - Update environment variable

2. **Typo in token**
   - Verify token starts with `sk-ant-oat01-`
   - Copy-paste directly from Claude.ai (no manual typing)
   - Check for extra spaces or newlines:
     ```bash
     # Trim whitespace
     export CLAUDE_CODE_OAUTH_TOKEN=$(echo "sk-ant-oat01-..." | tr -d '[:space:]')
     ```

3. **Revoked token**
   - Check https://claude.ai/settings/developer
   - Generate new token if revoked

### Issue: Token Not Found in Environment

**Error:**
```
❌ CLAUDE_CODE_OAUTH_TOKEN not set
```

**Debugging:**
```bash
# Check current shell
echo $SHELL

# Check if variable is set in current session
env | grep CLAUDE

# Reload shell configuration
source ~/.bashrc  # or ~/.zshrc

# Verify it's in the config file
grep CLAUDE_CODE_OAUTH_TOKEN ~/.bashrc
```

### Issue: Permission Denied

**Error:**
```
PermissionError: [Errno 13] Permission denied: '/home/user/.claudebox'
```

**Solution:**
```bash
# Fix permissions
chmod 755 ~/.claudebox
chmod -R 755 ~/.claudebox/sessions/

# Or remove and recreate
rm -rf ~/.claudebox
# Will be recreated on next ClaudeBox run
```

### Issue: Rate Limit Exceeded

**Error:**
```
RateLimitError: Rate limit exceeded for API requests
```

**Solutions:**

1. **Using OAuth Token:**
   - OAuth tokens typically have higher rate limits
   - Switch from API key to OAuth token

2. **Using API Key:**
   - Check your plan at https://console.anthropic.com/settings/plans
   - Upgrade plan for higher limits
   - Implement rate limiting in your application:
     ```python
     import asyncio
     from claudebox import ClaudeBox

     async def rate_limited_call():
         async with ClaudeBox() as box:
             result = await box.code("task")
             await asyncio.sleep(1)  # Wait 1 second between calls
             return result
     ```

---

## OAuth Token vs API Key Comparison

| Feature | OAuth Token | API Key |
|---------|-------------|---------|
| **Best For** | Claude Code CLI integration | General Anthropic API usage |
| **Rate Limits** | Higher (Claude Code optimized) | Standard API limits |
| **Expiration** | Configurable (30-90 days or never) | No expiration |
| **Revocation** | Easy via Claude.ai settings | Via Anthropic Console |
| **Recommended Use** | ✅ ClaudeBox (native support) | ⚠️ Fallback option |

**Recommendation**: Use **OAuth tokens** for ClaudeBox. They're designed for Claude Code CLI and offer better integration.

---

## Environment Variable Naming

ClaudeBox recognizes these environment variables:

| Variable Name | Type | Priority |
|--------------|------|----------|
| `CLAUDE_CODE_OAUTH_TOKEN` | OAuth Token | 1 (highest) |
| `ANTHROPIC_API_KEY` | API Key | 2 (fallback) |

**Why two names?**
- `CLAUDE_CODE_OAUTH_TOKEN` - Specific to Claude Code CLI
- `ANTHROPIC_API_KEY` - Standard Anthropic API key (for compatibility)

---

## Multiple Accounts / Token Management

### Using Different Tokens for Different Projects

```python
import asyncio
from claudebox import ClaudeBox

async def project_a():
    async with ClaudeBox(oauth_token="sk-ant-oat01-PROJECT-A-TOKEN") as box:
        await box.code("work on project A")

async def project_b():
    async with ClaudeBox(oauth_token="sk-ant-oat01-PROJECT-B-TOKEN") as box:
        await box.code("work on project B")

# Run with different credentials
await asyncio.gather(project_a(), project_b())
```

### Environment-Specific Tokens

```python
import os
from claudebox import ClaudeBox

# Development
if os.environ.get("ENV") == "development":
    token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN_DEV")
# Production
elif os.environ.get("ENV") == "production":
    token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN_PROD")

async with ClaudeBox(oauth_token=token) as box:
    ...
```

---

## Testing Authentication

**Complete test script with detailed diagnostics:**

```python
import asyncio
import os
from claudebox import ClaudeBox

async def test_authentication():
    print("=== ClaudeBox Authentication Test ===\n")

    # Check environment variables
    oauth_token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    print("Environment Variables:")
    print(f"  CLAUDE_CODE_OAUTH_TOKEN: {'✅ Set' if oauth_token else '❌ Not set'}")
    if oauth_token:
        print(f"    Value: {oauth_token[:20]}...")
    print(f"  ANTHROPIC_API_KEY: {'✅ Set' if api_key else '❌ Not set'}")
    if api_key:
        print(f"    Value: {api_key[:20]}...")
    print()

    if not oauth_token and not api_key:
        print("❌ No authentication credentials found!")
        print("\nPlease set one of:")
        print("  export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-YOUR-TOKEN")
        print("  export ANTHROPIC_API_KEY=sk-ant-YOUR-KEY")
        return

    # Test authentication
    print("Testing authentication with ClaudeBox...")
    try:
        async with ClaudeBox() as box:
            result = await box.code("echo 'Hello from ClaudeBox'")
            if result.success:
                print("✅ Authentication successful!")
                print(f"   Session ID: {box.session_id}")
                print(f"   Response: {result.response[:100]}")
            else:
                print("❌ Authentication failed")
                print(f"   Error: {result.error}")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Verify token is correct")
        print("  2. Check https://claude.ai/settings/developer for token status")
        print("  3. Ensure Docker is running")
        print("  4. Ensure BoxLite is installed")

asyncio.run(test_authentication())
```

**Save as `test_auth.py` and run:**
```bash
python3 test_auth.py
```

---

## Next Steps

Now that authentication is configured:

- **[Quick Start](quick-start.md)** - 5-minute hands-on tutorial
- **[Your First Session](first-session.md)** - Interactive session tutorial
- **[Session Management Guide](../guides/sessions.md)** - Advanced patterns
- **[Examples](../../examples/)** - 71 comprehensive examples

---

**Authentication configured!** Continue to [Quick Start](quick-start.md) →
