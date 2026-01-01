# Skills System Guide

Extend ClaudeBox capabilities with modular skills for databases, APIs, cloud platforms, and more.

---

## What Are Skills?

**Skills** are modular capabilities that extend Claude Code's functionality within ClaudeBox sessions. They handle:

- **Package installation** - Python packages, system packages
- **Environment configuration** - API keys, connection strings
- **File injection** - Config files, helper scripts
- **Tool setup** - CLIs, SDKs, frameworks

Think of skills as "batteries included" extensions that make specific capabilities immediately available to Claude Code.

---

## Built-in Skills Overview

ClaudeBox provides **9 built-in skills**:

| Skill | Purpose | Key Packages |
|-------|---------|--------------|
| `EMAIL_SKILL` | Send emails via SMTP | sendgrid |
| `POSTGRES_SKILL` | PostgreSQL databases | psycopg2-binary |
| `MYSQL_SKILL` | MySQL databases | mysql-connector-python |
| `REDIS_SKILL` | Redis cache/data store | redis, redis-tools |
| `API_SKILL` | HTTP API requests | requests, httpx |
| `AWS_SKILL` | AWS SDK and CLI | boto3, awscli |
| `DOCKER_SKILL` | Docker CLI and SDK | docker, docker.io |
| `SCRAPING_SKILL` | Web scraping | beautifulsoup4, selenium |
| `DATA_SCIENCE_SKILL` | Data analysis | pandas, numpy, matplotlib |

---

## Using Built-in Skills

### Basic Usage

```python
import asyncio
from claudebox import ClaudeBox, EMAIL_SKILL

async def main():
    # Pre-load email skill
    async with ClaudeBox(skills=[EMAIL_SKILL]) as box:
        result = await box.code(
            "Send an email to user@example.com with subject 'Test'"
        )
        print(result.response)

asyncio.run(main())
```

### Multiple Skills

```python
from claudebox import ClaudeBox, POSTGRES_SKILL, API_SKILL, AWS_SKILL

async def main():
    # Load multiple skills
    async with ClaudeBox(skills=[POSTGRES_SKILL, API_SKILL, AWS_SKILL]) as box:
        result = await box.code(
            "Fetch data from API, process it, store in PostgreSQL, "
            "then upload summary to S3"
        )

asyncio.run(main())
```

---

## Built-in Skills Reference

### 1. EMAIL_SKILL

**Purpose:** Send emails via SMTP using SendGrid

**Packages:**
- `sendgrid` - SendGrid Python SDK

**Usage:**
```python
from claudebox import ClaudeBox, EMAIL_SKILL

async def send_email_example():
    async with ClaudeBox(skills=[EMAIL_SKILL]) as box:
        await box.code(
            "Send email to john@example.com:\n"
            "Subject: 'ClaudeBox Notification'\n"
            "Body: 'Task completed successfully!'"
        )
```

**Environment Variables:**
```python
# Set SendGrid API key
EMAIL_SKILL.env_vars = {"SENDGRID_API_KEY": "SG.xxxxx"}
```

---

### 2. POSTGRES_SKILL

**Purpose:** Connect to PostgreSQL databases

**Packages:**
- `psycopg2-binary` - PostgreSQL adapter
- `postgresql-client` (system package)

**Usage:**
```python
from claudebox import ClaudeBox, POSTGRES_SKILL

async def postgres_example():
    # Configure connection
    postgres_skill = POSTGRES_SKILL
    postgres_skill.env_vars = {
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DB": "mydb",
        "POSTGRES_USER": "user",
        "POSTGRES_PASSWORD": "password"
    }

    async with ClaudeBox(skills=[postgres_skill]) as box:
        await box.code(
            "Connect to PostgreSQL and create a 'users' table with "
            "columns: id, name, email, created_at"
        )
```

---

### 3. MYSQL_SKILL

**Purpose:** Connect to MySQL databases

**Packages:**
- `mysql-connector-python` - MySQL adapter
- `mysql-client` (system package)

**Usage:**
```python
from claudebox import ClaudeBox, MYSQL_SKILL

async def mysql_example():
    mysql_skill = MYSQL_SKILL
    mysql_skill.env_vars = {
        "MYSQL_HOST": "localhost",
        "MYSQL_PORT": "3306",
        "MYSQL_DB": "mydb",
        "MYSQL_USER": "root",
        "MYSQL_PASSWORD": "password"
    }

    async with ClaudeBox(skills=[mysql_skill]) as box:
        await box.code("Query all records from customers table")
```

---

### 4. REDIS_SKILL

**Purpose:** Connect to Redis for caching and data storage

**Packages:**
- `redis` - Redis Python client
- `redis-tools` (system package)

**Usage:**
```python
from claudebox import ClaudeBox, REDIS_SKILL

async def redis_example():
    redis_skill = REDIS_SKILL
    redis_skill.env_vars = {
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "REDIS_PASSWORD": ""  # Optional
    }

    async with ClaudeBox(skills=[redis_skill]) as box:
        await box.code(
            "Store user session data in Redis with 1-hour TTL"
        )
```

---

### 5. API_SKILL

**Purpose:** Make HTTP API requests with advanced features

**Packages:**
- `requests` - HTTP library
- `httpx` - Modern async HTTP client

**Usage:**
```python
from claudebox import ClaudeBox, API_SKILL

async def api_example():
    async with ClaudeBox(skills=[API_SKILL]) as box:
        await box.code(
            "Fetch data from https://api.github.com/users/octocat "
            "and display the user's public repos count"
        )
```

**With Authentication:**
```python
api_skill = API_SKILL
api_skill.env_vars = {
    "API_BASE_URL": "https://api.example.com",
    "API_TOKEN": "your-api-token"
}

async with ClaudeBox(skills=[api_skill]) as box:
    await box.code("Call /api/users endpoint with authentication")
```

---

### 6. AWS_SKILL

**Purpose:** AWS SDK and CLI tools

**Packages:**
- `boto3` - AWS SDK for Python
- `awscli` - AWS Command Line Interface

**Usage:**
```python
from claudebox import ClaudeBox, AWS_SKILL

async def aws_example():
    aws_skill = AWS_SKILL
    aws_skill.env_vars = {
        "AWS_ACCESS_KEY_ID": "your-access-key",
        "AWS_SECRET_ACCESS_KEY": "your-secret-key",
        "AWS_DEFAULT_REGION": "us-east-1"
    }

    async with ClaudeBox(skills=[aws_skill]) as box:
        await box.code(
            "List all S3 buckets and upload report.pdf to my-bucket"
        )
```

**Common AWS Tasks:**
```python
# S3 operations
await box.code("Upload files to S3 bucket 'my-data'")

# EC2 operations
await box.code("List all running EC2 instances")

# DynamoDB operations
await box.code("Query DynamoDB table 'users' for user_id=123")

# Lambda operations
await box.code("Invoke Lambda function 'process-data'")
```

---

### 7. DOCKER_SKILL

**Purpose:** Docker CLI and SDK

**Packages:**
- `docker` - Docker SDK for Python
- `docker.io` (system package)

**Usage:**
```python
from claudebox import ClaudeBox, DOCKER_SKILL

async def docker_example():
    async with ClaudeBox(skills=[DOCKER_SKILL]) as box:
        await box.code(
            "List all running Docker containers and their status"
        )
```

**Docker Operations:**
```python
# Container management
await box.code("Start nginx container on port 8080")

# Image management
await box.code("Pull postgres:latest image")

# Build images
await box.code("Build Docker image from Dockerfile in current directory")
```

---

### 8. SCRAPING_SKILL

**Purpose:** Web scraping with BeautifulSoup and Selenium

**Packages:**
- `beautifulsoup4` - HTML/XML parser
- `selenium` - Browser automation
- `lxml` - Fast XML/HTML processor

**Usage:**
```python
from claudebox import ClaudeBox, SCRAPING_SKILL

async def scraping_example():
    async with ClaudeBox(skills=[SCRAPING_SKILL]) as box:
        await box.code(
            "Scrape https://news.ycombinator.com/ and extract "
            "top 10 post titles"
        )
```

**Advanced Scraping:**
```python
# JavaScript-heavy sites with Selenium
await box.code(
    "Use Selenium to scrape dynamic content from "
    "https://example.com/dashboard"
)

# Parse HTML with BeautifulSoup
await box.code(
    "Parse HTML file data.html and extract all links"
)
```

---

### 9. DATA_SCIENCE_SKILL

**Purpose:** Data analysis and machine learning

**Packages:**
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `matplotlib` - Plotting
- `seaborn` - Statistical visualization
- `scikit-learn` - Machine learning

**Usage:**
```python
from claudebox import ClaudeBox, DATA_SCIENCE_SKILL

async def data_science_example():
    async with ClaudeBox(skills=[DATA_SCIENCE_SKILL]) as box:
        await box.code(
            "Load dataset.csv, clean data, calculate statistics, "
            "and create visualizations"
        )
```

**Common Tasks:**
```python
# Data analysis
await box.code("Analyze sales_data.csv and find trends")

# Machine learning
await box.code(
    "Train a linear regression model on housing_data.csv "
    "to predict prices"
)

# Visualization
await box.code(
    "Create scatter plot of age vs income from users.csv"
)
```

---

## Creating Custom Skills

### Basic Custom Skill

```python
from claudebox import Skill, ClaudeBox

# Define custom skill
NOTIFICATION_SKILL = Skill(
    name="notification",
    description="Send notifications via Slack and Discord",
    install_cmd="pip3 install slack-sdk discord-webhook",
    requirements=["slack-sdk", "discord-webhook"],
    env_vars={
        "SLACK_TOKEN": "xoxb-your-token",
        "DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/..."
    }
)

# Use it
async def main():
    async with ClaudeBox(skills=[NOTIFICATION_SKILL]) as box:
        await box.code(
            "Send 'Build completed!' notification to #engineering on Slack"
        )
```

### Skill with File Injection

```python
CUSTOM_CONFIG_SKILL = Skill(
    name="custom_config",
    description="Pre-configured application settings",
    files={
        "config.json": '{"api_url": "https://api.example.com", "timeout": 30}',
        "helper.py": """
def process_data(data):
    # Helper function
    return data.upper()
"""
    }
)

async def main():
    async with ClaudeBox(skills=[CUSTOM_CONFIG_SKILL]) as box:
        await box.code("Use config.json settings and helper.py functions")
```

### Skill with System Packages

```python
GRAPHICS_SKILL = Skill(
    name="graphics",
    description="Image processing with system-level tools",
    system_packages=["imagemagick", "ffmpeg"],
    install_cmd="pip3 install Pillow opencv-python",
    requirements=["Pillow", "opencv-python"]
)

async def main():
    async with ClaudeBox(skills=[GRAPHICS_SKILL]) as box:
        await box.code(
            "Convert image.png to image.jpg using ImageMagick"
        )
```

---

## Skill Dataclass Structure

```python
@dataclass
class Skill:
    name: str                               # Unique skill name
    description: str                        # What the skill does
    install_cmd: str | None = None         # Installation command
    config: dict = field(default_factory=dict)  # Configuration
    files: dict[str, str] = field(default_factory=dict)  # filename -> content
    requirements: list[str] = field(default_factory=list)  # Python packages
    env_vars: dict[str, str] = field(default_factory=dict)  # Environment vars
    system_packages: list[str] = field(default_factory=list)  # apt packages
```

**Field Descriptions:**

- **name**: Alphanumeric identifier (can include `-` or `_`)
- **description**: Human-readable description
- **install_cmd**: Shell command to install packages (optional)
- **config**: Arbitrary configuration data
- **files**: Files to inject into workspace (`filename` → `content`)
- **requirements**: Python packages (for `requirements.txt`)
- **env_vars**: Environment variables to set
- **system_packages**: Ubuntu/Debian packages to install

---

## Skill Registry

### Registering Custom Skills

```python
from claudebox import Skill, register_skill, get_skill, list_skills

# Create skill
my_skill = Skill(
    name="my_custom_skill",
    description="My custom functionality"
)

# Register globally
register_skill(my_skill)

# Retrieve later
skill = get_skill("my_custom_skill")

# List all registered skills
all_skills = list_skills()
print(all_skills)  # ['email', 'postgres', ..., 'my_custom_skill']
```

### Using Registry in Applications

```python
from claudebox import ClaudeBox, get_skill

async def use_registered_skill(skill_name: str):
    """Use skill from registry by name."""
    skill = get_skill(skill_name)

    async with ClaudeBox(skills=[skill]) as box:
        await box.code(f"Use {skill.description}")
```

---

## Advanced Skill Patterns

### Pattern 1: Conditional Skills

```python
import os

async def conditional_skills():
    """Load skills based on environment."""
    skills = []

    # Always include API skill
    skills.append(API_SKILL)

    # Add database skill based on config
    if os.environ.get("USE_POSTGRES"):
        skills.append(POSTGRES_SKILL)
    elif os.environ.get("USE_MYSQL"):
        skills.append(MYSQL_SKILL)

    # Add cloud skills if credentials present
    if os.environ.get("AWS_ACCESS_KEY_ID"):
        skills.append(AWS_SKILL)

    async with ClaudeBox(skills=skills) as box:
        await box.code("Process data with available tools")
```

### Pattern 2: Skill Composition

```python
def create_web_scraping_stack():
    """Combine multiple skills for web scraping."""
    return [
        SCRAPING_SKILL,  # BeautifulSoup, Selenium
        API_SKILL,       # HTTP requests
        POSTGRES_SKILL,  # Store scraped data
        DATA_SCIENCE_SKILL  # Analyze results
    ]

async def scrape_and_analyze():
    async with ClaudeBox(skills=create_web_scraping_stack()) as box:
        await box.code(
            "Scrape product data from e-commerce site, "
            "store in PostgreSQL, and analyze pricing trends"
        )
```

### Pattern 3: Skill Inheritance/Extension

```python
from copy import deepcopy

# Extend built-in skill
CUSTOM_AWS_SKILL = deepcopy(AWS_SKILL)
CUSTOM_AWS_SKILL.name = "aws_custom"
CUSTOM_AWS_SKILL.env_vars = {
    "AWS_ACCESS_KEY_ID": "custom-key",
    "AWS_SECRET_ACCESS_KEY": "custom-secret",
    "AWS_DEFAULT_REGION": "us-west-2"
}

async def use_custom_aws():
    async with ClaudeBox(skills=[CUSTOM_AWS_SKILL]) as box:
        await box.code("List S3 buckets in us-west-2")
```

---

## Best Practices

### 1. Minimize Skill Dependencies

```python
# ✅ Good: Specific skills for specific tasks
async with ClaudeBox(skills=[API_SKILL]) as box:
    await box.code("Fetch data from API")

# ❌ Bad: Loading unnecessary skills
async with ClaudeBox(skills=[API_SKILL, AWS_SKILL, DOCKER_SKILL, ...]) as box:
    await box.code("Fetch data from API")  # Only uses API_SKILL
```

### 2. Use Environment Variables for Secrets

```python
import os

# ✅ Good: Environment variables
postgres_skill = POSTGRES_SKILL
postgres_skill.env_vars = {
    "POSTGRES_PASSWORD": os.environ.get("DB_PASSWORD")
}

# ❌ Bad: Hardcoded secrets
postgres_skill.env_vars = {
    "POSTGRES_PASSWORD": "hardcoded-password-123"
}
```

### 3. Document Custom Skills

```python
PAYMENT_SKILL = Skill(
    name="payment",
    description="""
    Payment processing via Stripe API.

    Capabilities:
    - Create payment intents
    - Process refunds
    - Manage subscriptions

    Required env vars:
    - STRIPE_SECRET_KEY: Stripe API secret key
    - STRIPE_PUBLISHABLE_KEY: Stripe publishable key
    """,
    install_cmd="pip3 install stripe",
    requirements=["stripe"]
)
```

### 4. Version Pin Dependencies

```python
# ✅ Good: Pin versions for reproducibility
DATA_SKILL_PINNED = Skill(
    name="data_pinned",
    description="Data analysis with pinned versions",
    requirements=[
        "pandas==2.1.0",
        "numpy==1.25.0",
        "matplotlib==3.7.2"
    ]
)
```

### 5. Test Skills Independently

```python
import asyncio

async def test_skill(skill: Skill):
    """Test a skill in isolation."""
    async with ClaudeBox(skills=[skill]) as box:
        result = await box.code(f"Test {skill.name} functionality")
        assert result.success, f"Skill {skill.name} test failed"
        print(f"✅ {skill.name} test passed")

# Test all skills
async def test_all_skills():
    skills = [
        EMAIL_SKILL, POSTGRES_SKILL, MYSQL_SKILL, REDIS_SKILL,
        API_SKILL, AWS_SKILL, DOCKER_SKILL, SCRAPING_SKILL,
        DATA_SCIENCE_SKILL
    ]

    for skill in skills:
        await test_skill(skill)
```

---

## Complete Example: Custom Notification Skill

```python
import asyncio
from claudebox import Skill, ClaudeBox

# Define skill
NOTIFICATION_SKILL = Skill(
    name="notification",
    description="Multi-channel notifications (Slack, Discord, Email)",
    install_cmd="pip3 install slack-sdk discord-webhook sendgrid",
    requirements=["slack-sdk", "discord-webhook", "sendgrid"],
    env_vars={
        "SLACK_TOKEN": "",  # Set at runtime
        "DISCORD_WEBHOOK_URL": "",
        "SENDGRID_API_KEY": ""
    },
    files={
        "notify.py": """
import os
from slack_sdk import WebClient
from discord_webhook import DiscordWebhook
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_slack(message):
    client = WebClient(token=os.environ['SLACK_TOKEN'])
    client.chat_postMessage(channel='#general', text=message)

def send_discord(message):
    webhook = DiscordWebhook(url=os.environ['DISCORD_WEBHOOK_URL'], content=message)
    webhook.execute()

def send_email(to_email, subject, body):
    message = Mail(
        from_email='noreply@example.com',
        to_emails=to_email,
        subject=subject,
        html_content=body
    )
    sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
    sg.send(message)
"""
    }
)

# Use skill
async def main():
    # Configure with real credentials
    notification_skill = NOTIFICATION_SKILL
    notification_skill.env_vars = {
        "SLACK_TOKEN": "xoxb-your-slack-token",
        "DISCORD_WEBHOOK_URL": "https://discord.com/api/webhooks/...",
        "SENDGRID_API_KEY": "SG.your-sendgrid-key"
    }

    async with ClaudeBox(skills=[notification_skill]) as box:
        # Send notification
        result = await box.code(
            "Use notify.py to send 'Build completed!' to Slack #engineering channel"
        )

        if result.success:
            print("✅ Notification sent!")
        else:
            print(f"❌ Error: {result.error}")

asyncio.run(main())
```

---

## Troubleshooting

### Issue: Skill Installation Fails

**Error:**
```
Error installing skill 'custom_skill': pip install failed
```

**Solutions:**
1. Check `install_cmd` syntax
2. Ensure packages exist in PyPI
3. Add system package dependencies to `system_packages`

### Issue: Environment Variables Not Set

**Error:**
```
KeyError: 'API_TOKEN' not found in environment
```

**Solution:**
```python
skill.env_vars = {"API_TOKEN": "your-token"}
```

### Issue: File Injection Not Working

**Problem:** Files not appearing in workspace

**Solution:**
```python
# Ensure files dict is correct
skill.files = {
    "config.json": '{"key": "value"}',  # filename -> content as string
    "script.py": "print('hello')"
}
```

---

## Next Steps

- **[Templates Guide](templates.md)** - Combine skills with templates
- **[Workspace Guide](workspace.md)** - Where skill files are injected
- **[Examples](../../examples/02_skills.py)** - 10 skill examples

---

**Extend ClaudeBox, unlock unlimited possibilities!**
