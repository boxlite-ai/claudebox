# Sandbox Templates Guide

Use pre-configured environments tailored for web development, data science, security research, and more.

---

## What Are Sandbox Templates?

**Sandbox templates** are pre-configured Docker images that provide specialized development environments for ClaudeBox. Each template comes with tools, frameworks, and dependencies for specific use cases.

**Benefits:**
- ⚡ **Fast Setup** - Skip manual installation of tools
- 🎯 **Purpose-Built** - Optimized for specific workflows
- 📦 **Batteries Included** - Common dependencies pre-installed
- 🔄 **Reproducible** - Consistent environments across machines

---

## Available Templates

ClaudeBox provides **6 built-in templates**:

| Template | Use Case | Key Tools |
|----------|----------|-----------|
| `DEFAULT` | General purpose | Claude Code CLI, Python, basic tools |
| `WEB_DEV` | Web development | Node.js, TypeScript, Docker, PostgreSQL |
| `DATA_SCIENCE` | Data analysis & ML | Jupyter, pandas, numpy, scikit-learn |
| `SECURITY` | Security research* | nmap, wireshark, tcpdump |
| `DEVOPS` | Infrastructure & ops | Docker, Kubernetes, Terraform |
| `MOBILE` | Mobile development | Android SDK, iOS tools |

*For authorized security testing, CTF competitions, and educational use only*

---

## Template Reference

### 1. DEFAULT Template

**Purpose:** Base runtime with Claude Code CLI and essential tools

**Pre-installed:**
- Claude Code CLI
- Python 3.10+ (supports 3.10-3.14)
- pip, git
- Basic Unix utilities

**Docker Image:**
```
ghcr.io/boxlite-ai/claudebox-runtime:latest
```

**When to use:**
- General-purpose tasks
- Learning ClaudeBox
- Tasks not fitting other templates

**Example:**
```python
from claudebox import ClaudeBox, SandboxTemplate

async def default_example():
    async with ClaudeBox(template=SandboxTemplate.DEFAULT) as box:
        await box.code("Create a Python script to calculate Fibonacci numbers")
```

---

### 2. WEB_DEV Template

**Purpose:** Modern web development with full-stack tools

**Pre-installed:**
- **Languages:** Node.js 18+, TypeScript, Python 3.10+
- **Frameworks:** Express, React tooling
- **Databases:** PostgreSQL client, Redis client
- **Tools:** Docker CLI, npm, yarn, git
- **Dev Tools:** ESLint, Prettier

**Docker Image:**
```
ghcr.io/boxlite-ai/claudebox-runtime:web-dev
```

**When to use:**
- Building web applications (frontend/backend)
- API development (REST, GraphQL)
- Full-stack projects
- TypeScript/JavaScript development

**Example:**
```python
from claudebox import ClaudeBox, SandboxTemplate

async def web_dev_example():
    async with ClaudeBox(template=SandboxTemplate.WEB_DEV) as box:
        await box.code(
            "Create an Express.js API with TypeScript:\n"
            "- GET /users endpoint\n"
            "- PostgreSQL connection\n"
            "- Redis caching\n"
            "- Proper TypeScript types"
        )
```

**Common Tasks:**
```python
# React app
await box.code("Create a React app with TypeScript using Vite")

# Express API
await box.code("Build a REST API with Express and PostgreSQL")

# Full-stack
await box.code("Create a full-stack app: React frontend + Express backend")
```

---

### 3. DATA_SCIENCE Template

**Purpose:** Data analysis, machine learning, and scientific computing

**Pre-installed:**
- **Core:** Jupyter Notebook, JupyterLab
- **Data:** pandas, numpy
- **ML:** scikit-learn, scipy
- **Viz:** matplotlib, seaborn, plotly
- **Tools:** R, Julia (optional)

**Docker Image:**
```
ghcr.io/boxlite-ai/claudebox-runtime:data-science
```

**When to use:**
- Data analysis and exploration
- Machine learning experiments
- Statistical computing
- Data visualization
- Jupyter notebooks

**Example:**
```python
from claudebox import ClaudeBox, SandboxTemplate

async def data_science_example():
    async with ClaudeBox(template=SandboxTemplate.DATA_SCIENCE) as box:
        await box.code(
            "Analyze dataset.csv:\n"
            "1. Load data with pandas\n"
            "2. Calculate descriptive statistics\n"
            "3. Create correlation heatmap\n"
            "4. Train linear regression model\n"
            "5. Save plots as PNG files"
        )
```

**Common Tasks:**
```python
# Data exploration
await box.code("Load sales.csv and create summary statistics")

# ML training
await box.code("Train a random forest classifier on iris dataset")

# Visualization
await box.code("Create interactive dashboard with plotly")

# Jupyter notebook
await box.code("Create Jupyter notebook for exploratory analysis")
```

---

### 4. SECURITY Template

**Purpose:** Security research, penetration testing, network analysis

**⚠️ IMPORTANT:** For authorized use only. This includes:
- Authorized penetration testing engagements
- CTF (Capture The Flag) competitions
- Security education and research
- Defensive security analysis

**Pre-installed:**
- **Network:** nmap, wireshark, tcpdump, netcat
- **Analysis:** binwalk, foremost, exiftool
- **Scripting:** Python, Bash
- **Crypto:** OpenSSL, hashcat (CPU)

**Docker Image:**
```
ghcr.io/boxlite-ai/claudebox-runtime:security
```

**When to use:**
- Authorized security assessments
- CTF competitions
- Learning security concepts
- Network traffic analysis
- Malware analysis (in isolated environment)

**Example:**
```python
from claudebox import ClaudeBox, SandboxTemplate, RESTRICTED_POLICY

async def security_example():
    # Use restricted policy for safety
    async with ClaudeBox(
        template=SandboxTemplate.SECURITY,
        security_policy=RESTRICTED_POLICY
    ) as box:
        await box.code(
            "Scan localhost for open ports using nmap "
            "(authorized security testing only)"
        )
```

**Common Tasks (Authorized Use):**
```python
# Network scanning
await box.code("Scan localhost network for open ports")

# Packet analysis
await box.code("Analyze pcap file for suspicious traffic")

# CTF challenges
await box.code("Decode base64-encoded flag from file")
```

**Security Note:** Always use with appropriate security policies. Never use for unauthorized testing.

---

### 5. DEVOPS Template

**Purpose:** Infrastructure automation, deployment, orchestration

**Pre-installed:**
- **Containers:** Docker, Docker Compose
- **Orchestration:** Kubernetes CLI (kubectl), Helm
- **IaC:** Terraform, Ansible
- **Cloud:** AWS CLI, Azure CLI, gcloud
- **CI/CD:** GitHub Actions tools, GitLab Runner

**Docker Image:**
```
ghcr.io/boxlite-ai/claudebox-runtime:devops
```

**When to use:**
- Infrastructure as Code (IaC)
- Container orchestration
- CI/CD pipeline development
- Cloud deployments
- System automation

**Example:**
```python
from claudebox import ClaudeBox, SandboxTemplate

async def devops_example():
    async with ClaudeBox(template=SandboxTemplate.DEVOPS) as box:
        await box.code(
            "Create Kubernetes deployment YAML for nginx:\n"
            "- 3 replicas\n"
            "- LoadBalancer service\n"
            "- Health checks\n"
            "- Resource limits"
        )
```

**Common Tasks:**
```python
# Terraform
await box.code("Write Terraform config for AWS EC2 instance")

# Kubernetes
await box.code("Create Helm chart for microservices deployment")

# Docker
await box.code("Build multi-stage Dockerfile for Node.js app")

# Ansible
await box.code("Create Ansible playbook to configure web servers")
```

---

### 6. MOBILE Template

**Purpose:** Mobile application development (Android/iOS)

**Pre-installed:**
- **Android:** Android SDK, Android Studio CLI tools
- **iOS:** Xcode command-line tools (macOS only)
- **Cross-platform:** React Native, Flutter
- **Tools:** Fastlane, Gradle, CocoaPods

**Docker Image:**
```
ghcr.io/boxlite-ai/claudebox-runtime:mobile
```

**When to use:**
- Android app development
- iOS app development (macOS only)
- Cross-platform mobile apps
- Mobile app automation
- App build pipelines

**Example:**
```python
from claudebox import ClaudeBox, SandboxTemplate

async def mobile_example():
    async with ClaudeBox(template=SandboxTemplate.MOBILE) as box:
        await box.code(
            "Create a React Native app with:\n"
            "- Login screen\n"
            "- API integration\n"
            "- Local storage"
        )
```

**Common Tasks:**
```python
# React Native
await box.code("Initialize React Native project")

# Flutter
await box.code("Create Flutter app with navigation")

# Android
await box.code("Build Android APK with Gradle")
```

---

## Using Templates

### Basic Usage

```python
from claudebox import ClaudeBox, SandboxTemplate

async def main():
    # Use template enum
    async with ClaudeBox(template=SandboxTemplate.DATA_SCIENCE) as box:
        await box.code("Analyze dataset.csv")
```

### Template as String

```python
async def main():
    # Use template name as string
    async with ClaudeBox(template="DATA_SCIENCE") as box:
        await box.code("Train ML model")
```

### Custom Docker Image

```python
async def main():
    # Use custom Docker image
    async with ClaudeBox(
        template="ghcr.io/myorg/custom-runtime:v1.0"
    ) as box:
        await box.code("Use custom environment")
```

### Template + Skills Combination

```python
from claudebox import ClaudeBox, SandboxTemplate, AWS_SKILL, POSTGRES_SKILL

async def main():
    # Combine template with skills
    async with ClaudeBox(
        template=SandboxTemplate.WEB_DEV,
        skills=[AWS_SKILL, POSTGRES_SKILL]
    ) as box:
        await box.code(
            "Build web API, deploy to AWS, use PostgreSQL database"
        )
```

---

## Template Selection Guide

### By Use Case

**Building Web Applications:**
- ✅ `WEB_DEV` - Full-stack development
- ✅ Combine with `POSTGRES_SKILL`, `REDIS_SKILL`

**Data Analysis:**
- ✅ `DATA_SCIENCE` - Jupyter, pandas, ML tools
- ✅ Combine with `AWS_SKILL` for S3 data

**DevOps & Infrastructure:**
- ✅ `DEVOPS` - Kubernetes, Terraform, Ansible
- ✅ Combine with `AWS_SKILL` for cloud deployments

**Security Research:**
- ✅ `SECURITY` - Network tools, analysis utilities
- ⚠️ Authorized use only, use security policies

**Mobile Development:**
- ✅ `MOBILE` - React Native, Flutter, Android/iOS
- ✅ Combine with `API_SKILL` for backend integration

**General Purpose:**
- ✅ `DEFAULT` - Basic tools, flexible

### By Language/Framework

| Language/Framework | Recommended Template |
|-------------------|---------------------|
| JavaScript/TypeScript | `WEB_DEV` |
| Python (Data Science) | `DATA_SCIENCE` |
| Python (Web) | `WEB_DEV` |
| React/Vue/Angular | `WEB_DEV` |
| Node.js/Express | `WEB_DEV` |
| Terraform/Ansible | `DEVOPS` |
| React Native/Flutter | `MOBILE` |
| Jupyter Notebooks | `DATA_SCIENCE` |

---

## Custom Templates

### Creating Custom Docker Images

**1. Create Dockerfile:**
```dockerfile
# Start from ClaudeBox base
FROM ghcr.io/boxlite-ai/claudebox-runtime:latest

# Install custom tools
RUN apt-get update && apt-get install -y \
    custom-tool-1 \
    custom-tool-2 \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install \
    custom-package-1 \
    custom-package-2

# Add custom scripts
COPY scripts/ /usr/local/bin/

# Set environment variables
ENV CUSTOM_VAR=value
```

**2. Build and Push:**
```bash
# Build image
docker build -t ghcr.io/myorg/custom-claudebox:v1.0 .

# Push to registry
docker push ghcr.io/myorg/custom-claudebox:v1.0
```

**3. Use in ClaudeBox:**
```python
async def main():
    async with ClaudeBox(
        template="ghcr.io/myorg/custom-claudebox:v1.0"
    ) as box:
        await box.code("Use custom environment")
```

### Example: Custom ML Research Template

```dockerfile
FROM ghcr.io/boxlite-ai/claudebox-runtime:data-science

# Additional ML frameworks
RUN pip3 install \
    torch==2.0.0 \
    tensorflow==2.13.0 \
    transformers==4.30.0 \
    accelerate==0.20.0

# GPU support (if needed)
RUN apt-get update && apt-get install -y \
    nvidia-cuda-toolkit \
    && rm -rf /var/lib/apt/lists/*

# Custom research tools
COPY research_utils/ /opt/research_utils/
ENV PYTHONPATH="/opt/research_utils:$PYTHONPATH"
```

---

## Advanced Patterns

### Pattern 1: Template Selection by Environment

```python
import os
from claudebox import ClaudeBox, SandboxTemplate

async def environment_based_template():
    """Choose template based on environment."""
    env = os.environ.get("ENV", "development")

    if env == "production":
        template = SandboxTemplate.DEVOPS
    elif env == "data-analysis":
        template = SandboxTemplate.DATA_SCIENCE
    else:
        template = SandboxTemplate.WEB_DEV

    async with ClaudeBox(template=template) as box:
        await box.code("Run environment-specific tasks")
```

### Pattern 2: Template + Skills Matrix

```python
from claudebox import ClaudeBox, SandboxTemplate, *

# Define combinations
COMBINATIONS = {
    "web-api": {
        "template": SandboxTemplate.WEB_DEV,
        "skills": [POSTGRES_SKILL, REDIS_SKILL, API_SKILL]
    },
    "data-pipeline": {
        "template": SandboxTemplate.DATA_SCIENCE,
        "skills": [AWS_SKILL, POSTGRES_SKILL]
    },
    "cloud-infra": {
        "template": SandboxTemplate.DEVOPS,
        "skills": [AWS_SKILL, DOCKER_SKILL]
    }
}

async def use_combination(combo_name: str):
    combo = COMBINATIONS[combo_name]
    async with ClaudeBox(
        template=combo["template"],
        skills=combo["skills"]
    ) as box:
        await box.code(f"Execute {combo_name} workflow")
```

### Pattern 3: Progressive Template Migration

```python
async def migrate_to_specialized_template():
    """Start with DEFAULT, migrate to specialized template."""
    # Phase 1: Prototype with DEFAULT
    async with ClaudeBox(template=SandboxTemplate.DEFAULT) as box:
        await box.code("Prototype feature")

    # Phase 2: Move to specialized template
    async with ClaudeBox(template=SandboxTemplate.WEB_DEV) as box:
        await box.code("Implement full feature with web dev tools")
```

---

## Best Practices

### 1. Choose Minimal Template

```python
# ✅ Good: Use specialized template
async with ClaudeBox(template=SandboxTemplate.DATA_SCIENCE) as box:
    await box.code("Analyze data")

# ❌ Bad: Use template with unnecessary tools
async with ClaudeBox(template=SandboxTemplate.DEVOPS) as box:
    await box.code("Analyze data")  # Don't need Kubernetes for this
```

### 2. Combine Templates with Skills

```python
# ✅ Good: Template + relevant skills
async with ClaudeBox(
    template=SandboxTemplate.WEB_DEV,
    skills=[POSTGRES_SKILL, AWS_SKILL]
) as box:
    ...

# ❌ Bad: Skills that duplicate template tools
async with ClaudeBox(
    template=SandboxTemplate.DATA_SCIENCE,  # Already has pandas
    skills=[DATA_SCIENCE_SKILL]  # Redundant
) as box:
    ...
```

### 3. Version Pin Custom Images

```python
# ✅ Good: Pinned version
template = "ghcr.io/myorg/custom:v1.2.3"

# ❌ Bad: Floating tag
template = "ghcr.io/myorg/custom:latest"
```

### 4. Document Template Requirements

```python
async def documented_template_usage():
    """
    Uses DATA_SCIENCE template for ML training.

    Requirements:
    - Minimum 8GB RAM
    - Minimum 20GB disk space
    - GPU optional but recommended

    Template includes:
    - Jupyter, pandas, scikit-learn
    - Pre-configured Python 3.10+
    """
    async with ClaudeBox(
        template=SandboxTemplate.DATA_SCIENCE,
        memory_mib=8192,
        disk_size_gb=20
    ) as box:
        ...
```

---

## Listing Available Templates

```python
from claudebox.templates import list_templates, get_template_description

# List all templates
templates = list_templates()
for name, description in templates.items():
    print(f"{name}: {description}")

# Output:
# DEFAULT: Base runtime with Claude Code CLI
# WEB_DEV: Web development: Node.js, TypeScript, Docker, PostgreSQL, Redis
# DATA_SCIENCE: Data science: Jupyter, pandas, numpy, scikit-learn, matplotlib
# SECURITY: Security research: nmap, wireshark, tcpdump (authorized use only)
# DEVOPS: DevOps: Docker, Kubernetes, Terraform, Ansible
# MOBILE: Mobile development: Android SDK, iOS tools
```

---

## Troubleshooting

### Issue: Template Image Not Found

**Error:**
```
Error pulling image 'ghcr.io/boxlite-ai/claudebox-runtime:web-dev'
```

**Solution:**
```bash
# Pull image manually
docker pull ghcr.io/boxlite-ai/claudebox-runtime:web-dev

# Verify image exists
docker images | grep claudebox
```

### Issue: Out of Disk Space

**Error:**
```
OSError: No space left on device
```

**Solution:**
```bash
# Remove unused images
docker image prune -a

# Increase disk_size_gb
async with ClaudeBox(
    template=SandboxTemplate.DATA_SCIENCE,
    disk_size_gb=20  # Increase from default 8GB
) as box:
    ...
```

### Issue: Template Lacks Required Tool

**Problem:** Template missing a specific tool

**Solution:** Combine with skills or use custom image
```python
# Option 1: Add skill
async with ClaudeBox(
    template=SandboxTemplate.WEB_DEV,
    skills=[MISSING_TOOL_SKILL]
) as box:
    ...

# Option 2: Use custom image with tool pre-installed
async with ClaudeBox(
    template="ghcr.io/myorg/custom-with-tool:v1.0"
) as box:
    ...
```

---

## Next Steps

- **[Skills Guide](skills.md)** - Combine skills with templates
- **[Security Guide](security.md)** - Secure template usage
- **[Examples](../../examples/03_templates.py)** - 13 template examples

---

**Choose the right template, work faster!**
