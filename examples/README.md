# ClaudeBox Examples

Comprehensive examples demonstrating all ClaudeBox features. **71 total examples** across 6 files covering everything from basic usage to advanced RL training patterns.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/boxlite-labs/claudebox.git
cd claudebox/examples

# Set your authentication
export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...

# Run any example
python 01_basic_usage.py
```

## Examples by Category

### 🚀 Getting Started
Perfect for beginners - start here!

- [**01_basic_usage.py**](#01_basic_usagepy) - Core concepts and session management

### 🧩 Extending Capabilities
Learn how to add skills and use templates:

- [**02_skills.py**](#02_skillspy) - Modular skills system
- [**03_templates.py**](#03_templatespy) - Specialized sandbox environments

### 🔐 Security & Control
Secure execution with fine-grained policies:

- [**05_security.py**](#05_securitypy) - Security policies and enforcement

### 🎯 Research & Training
For RL researchers and agent developers:

- [**04_rl_rewards.py**](#04_rl_rewardspy) - Reward functions and trajectory export

### ⚙️ Production & Advanced
Complex workflows and production patterns:

- [**06_advanced.py**](#06_advancedpy) - Advanced patterns and orchestration

---

## 01_basic_usage.py

**8 examples** covering fundamental operations

### What You'll Learn
- Ephemeral vs persistent sessions
- Session lifecycle management
- Workspace access from host
- Reconnection to sessions
- Backward compatibility

### Examples in This File

1. **Ephemeral Session (Auto-Cleanup)**
   ```python
   async with ClaudeBox() as box:
       result = await box.code("Create a file")
   # Session automatically cleaned up
   ```

2. **Persistent Session**
   ```python
   async with ClaudeBox(session_id="my-project") as box:
       await box.code("npm install")
   # Workspace persists after exit
   ```

3. **Session Reconnection**
   ```python
   box = await ClaudeBox.reconnect("my-project")
   async with box:
       await box.code("npm test")
   ```

4. **List All Sessions**
   ```python
   sessions = ClaudeBox.list_sessions()
   for session in sessions:
       print(f"{session.session_id}: {session.created_at}")
   ```

5. **Manual Cleanup**
   ```python
   await ClaudeBox.cleanup_session("my-project", remove_workspace=True)
   ```

6. **Custom Configuration**
   ```python
   async with ClaudeBox(
       cpus=4,
       memory_mib=8192,
       enable_logging=True
   ) as box:
       ...
   ```

7. **Workspace Access from Host**
   ```python
   from pathlib import Path
   workspace = Path(box.workspace_path)
   (workspace / "config.json").write_text('{"key": "value"}')
   ```

8. **Backward Compatibility**
   - All existing code still works
   - No breaking changes

**When to use:** Start here if you're new to ClaudeBox

---

## 02_skills.py

**10 examples** demonstrating the modular skills system

### What You'll Learn
- Using all 9 built-in skills
- Creating custom skills
- Environment variables and file injection
- Skill registry management
- System package requirements

### Built-in Skills Covered

- `EMAIL_SKILL` - Send emails via SendGrid
- `API_SKILL` - HTTP requests with requests/httpx
- `POSTGRES_SKILL`, `MYSQL_SKILL`, `REDIS_SKILL` - Database connections
- `DATA_SCIENCE_SKILL` - Pandas, NumPy, Matplotlib
- `AWS_SKILL` - AWS SDK (boto3)
- `DOCKER_SKILL` - Docker CLI
- `SCRAPING_SKILL` - BeautifulSoup, Playwright

### Examples in This File

1. **Built-in Email Skill**
   ```python
   async with ClaudeBox(skills=[EMAIL_SKILL]) as box:
       await box.code("Show me how to send an email")
   ```

2. **Built-in API Skill**
   ```python
   async with ClaudeBox(skills=[API_SKILL]) as box:
       await box.code("Make a GET request to an API")
   ```

3. **Database Skills**
   ```python
   async with ClaudeBox(
       skills=[POSTGRES_SKILL, MYSQL_SKILL, REDIS_SKILL]
   ) as box:
       await box.code("Connect to PostgreSQL")
   ```

4. **Data Science Skill**
   ```python
   async with ClaudeBox(skills=[DATA_SCIENCE_SKILL]) as box:
       await box.code("Create a pandas DataFrame and plot it")
   ```

5. **Custom Skill Creation**
   ```python
   custom_skill = Skill(
       name="text_processing",
       description="Advanced text processing tools",
       install_cmd="pip3 install nltk spacy",
       requirements=["nltk", "spacy"],
       files={
           "process.py": "import nltk\n...",
           "config.json": '{"version": "1.0"}'
       }
   )
   async with ClaudeBox(skills=[custom_skill]) as box:
       ...
   ```

6. **Skills with Environment Variables**
   ```python
   api_skill = Skill(
       name="external_api",
       env_vars={"API_KEY": "your-key", "API_ENDPOINT": "https://..."}
   )
   ```

7. **Multiple Skills Together**
   ```python
   async with ClaudeBox(
       skills=[API_SKILL, DATA_SCIENCE_SKILL, DOCKER_SKILL]
   ) as box:
       ...
   ```

8. **Skill Registry Usage**
   ```python
   available = list_skills()
   postgres = get_skill("postgres")
   register_skill(my_custom_skill)
   ```

9. **Skills with System Packages**
   ```python
   video_skill = Skill(
       name="video_processing",
       system_packages=["ffmpeg", "imagemagick"],
       requirements=["moviepy"]
   )
   ```

10. **Cloud Provider Skills (AWS)**
    ```python
    async with ClaudeBox(skills=[AWS_SKILL]) as box:
        await box.code("List S3 buckets using boto3")
    ```

**When to use:** Learn how to extend ClaudeBox with custom capabilities

---

## 03_templates.py

**13 examples** of specialized sandbox environments

### What You'll Learn
- All 6 built-in templates
- When to use each template
- Custom Docker images
- Template selection strategies
- Template enumeration

### Built-in Templates Covered

- `DEFAULT` - Base runtime environment
- `WEB_DEV` - Node.js, TypeScript, Docker, PostgreSQL, Redis
- `DATA_SCIENCE` - Jupyter, Pandas, NumPy, Scikit-learn
- `SECURITY` - nmap, Wireshark (for authorized use only)
- `DEVOPS` - Docker, Kubernetes CLI, Terraform
- `MOBILE` - Android SDK, iOS tools

### Examples in This File

1. **Default Template**
   ```python
   async with ClaudeBox() as box:
       # Uses default template automatically
       ...
   ```

2. **Web Development Template**
   ```python
   async with ClaudeBox(template=SandboxTemplate.WEB_DEV) as box:
       await box.code("Create a React app with TypeScript")
   ```

3. **Data Science Template**
   ```python
   async with ClaudeBox(template=SandboxTemplate.DATA_SCIENCE) as box:
       await box.code("Create pandas DataFrame and plot")
   ```

4. **Security Research Template**
   ```python
   # For authorized security testing only!
   async with ClaudeBox(template=SandboxTemplate.SECURITY) as box:
       await box.code("Scan localhost for open ports")
   ```

5. **DevOps Template**
   ```python
   async with ClaudeBox(template=SandboxTemplate.DEVOPS) as box:
       await box.code("Show Docker and Kubernetes versions")
   ```

6. **Mobile Development Template**
   - Android SDK, iOS tools for app development

7. **Template Enum Usage**
   ```python
   templates = [
       SandboxTemplate.DEFAULT,
       SandboxTemplate.WEB_DEV,
       SandboxTemplate.DATA_SCIENCE
   ]
   for template in templates:
       print(get_template_description(template))
   ```

8. **Template as String**
   ```python
   async with ClaudeBox(
       template="ghcr.io/boxlite-labs/claudebox-runtime:latest"
   ) as box:
       ...
   ```

9. **Custom Docker Images**
   ```python
   async with ClaudeBox(
       image="ghcr.io/boxlite-labs/claudebox-runtime:custom"
   ) as box:
       ...
   ```

10. **Image Overrides Template**
    ```python
    async with ClaudeBox(
        template=SandboxTemplate.WEB_DEV,  # Ignored
        image="custom-image:latest"         # Used
    ) as box:
        ...
    ```

11. **List All Templates**
    ```python
    templates = list_templates()
    for name, description in templates.items():
        print(f"{name}: {description}")
    ```

12. **Get Template Image URL**
    ```python
    web_dev_image = get_template_image(SandboxTemplate.WEB_DEV)
    ```

13. **Template Selection by Use Case**
    - Web API development → WEB_DEV
    - Machine learning → DATA_SCIENCE
    - Infrastructure automation → DEVOPS
    - Pentesting (authorized) → SECURITY
    - React Native app → MOBILE

**When to use:** Choose specialized environments for your workflow

---

## 04_rl_rewards.py

**13 examples** for reinforcement learning and agent training

### What You'll Learn
- All 5 built-in reward functions
- Custom reward creation
- Reward combination strategies
- Trajectory export for training
- State-action pair extraction
- Multi-session training data collection

### Reward Functions Covered

- `SuccessOnlyReward` - Simple binary reward (success = 1.0, failure = -1.0)
- `CodeQualityReward` - Reward based on code quality metrics
- `SafetyReward` - Penalize unsafe commands (sudo, rm -rf, etc.)
- `EfficiencyReward` - Reward fewer tool calls and faster execution
- `CustomReward` - Define your own reward logic

### Examples in This File

1. **Success-Only Reward**
   ```python
   async with ClaudeBox(reward_fn=SuccessOnlyReward()) as box:
       result = await box.code("Create a file")
       print(f"Reward: {result.reward}")  # 1.0 or -1.0
   ```

2. **Code Quality Reward**
   ```python
   async with ClaudeBox(reward_fn=CodeQualityReward()) as box:
       result = await box.code("Write a fibonacci function")
       print(f"Quality reward: {result.reward:.2f}")  # 0.0 to 1.0
   ```

3. **Safety Reward**
   ```python
   reward_fn = SafetyReward()
   # Penalizes unsafe commands like "sudo rm -rf"
   ```

4. **Efficiency Reward**
   ```python
   async with ClaudeBox(reward_fn=EfficiencyReward()) as box:
       result = await box.code("Create 3 files")
       # Higher reward for fewer tool calls
   ```

5. **Built-in Rewards Helper**
   ```python
   rewards = {
       "success": BuiltinRewards.success_only(result),
       "quality": BuiltinRewards.code_quality(result),
       "safety": BuiltinRewards.safety(result),
       "efficiency": BuiltinRewards.efficiency(result)
   }
   ```

6. **Custom Reward Function**
   ```python
   def my_reward(result: CodeResult) -> float:
       if not result.success:
           return -1.0
       # Prefer concise responses
       return 1.0 if len(result.response) < 100 else 0.5

   async with ClaudeBox(reward_fn=CustomReward(my_reward)) as box:
       ...
   ```

7. **Combined Rewards**
   ```python
   combined = combine_rewards(
       SuccessOnlyReward(),
       SafetyReward(),
       weights=[0.7, 0.3]  # 70% success, 30% safety
   )
   async with ClaudeBox(reward_fn=combined) as box:
       ...
   ```

8. **Trajectory Export**
   ```python
   exporter = TrajectoryExporter(workspace, session_manager)
   trajectory = exporter.export_trajectory()
   # Format: {"session_id": "...", "steps": [...], "total_turns": 3}
   ```

9. **Trajectory Saving**
   ```python
   output_file = exporter.export_for_training(
       output_dir="./training_data",
       reward_fn=BuiltinRewards.code_quality
   )
   loaded = TrajectoryExporter.load_trajectory(output_file)
   ```

10. **Trajectory with Rewards**
    ```python
    total_reward = exporter.calculate_trajectory_reward(reward_fn)
    print(f"Total reward: {total_reward:.2f}")
    ```

11. **State-Action Pairs**
    ```python
    pairs = exporter.get_state_action_pairs()
    for state, action, next_state in pairs:
        # Use for RL training
        ...
    ```

12. **Merge Trajectories**
    ```python
    trajectories = [traj1, traj2, traj3]
    merged = TrajectoryExporter.merge_trajectories(trajectories)
    # Combined dataset for training
    ```

13. **Multi-Factor Custom Reward**
    ```python
    def advanced_reward(result: CodeResult) -> float:
        score = 0.0
        if result.success: score += 0.4
        if not result.error: score += 0.2
        if len(result.response) < 200: score += 0.2
        if len(result.action_log) <= 3: score += 0.2
        return score
    ```

**When to use:** RL research, agent training, collecting training data

---

## 05_security.py

**15 examples** of security policies and enforcement

### What You'll Learn
- All 5 pre-defined security policies
- Custom policy creation
- Command, network, and filesystem enforcement
- Resource limits and isolation
- Layered security approach

### Security Policies Covered

- `UNRESTRICTED_POLICY` - No restrictions (default)
- `STANDARD_POLICY` - Basic restrictions (recommended)
- `RESTRICTED_POLICY` - High security
- `READONLY_POLICY` - Read-only filesystem
- `RESEARCH_POLICY` - Balanced for research (restricted network)

### Examples in This File

1. **Unrestricted Policy**
   ```python
   async with ClaudeBox(security_policy=UNRESTRICTED_POLICY) as box:
       # Full access to network, filesystem, commands
       ...
   ```

2. **Standard Policy (Recommended)**
   ```python
   async with ClaudeBox(security_policy=STANDARD_POLICY) as box:
       # Basic restrictions on dangerous commands
       ...
   ```

3. **Restricted Policy**
   ```python
   async with ClaudeBox(security_policy=RESTRICTED_POLICY) as box:
       # High security: workspace-only filesystem, restricted network
       ...
   ```

4. **Read-Only Policy**
   ```python
   async with ClaudeBox(security_policy=READONLY_POLICY) as box:
       # Can read but not modify files
       ...
   ```

5. **Research Policy**
   ```python
   async with ClaudeBox(security_policy=RESEARCH_POLICY) as box:
       # Restricted network (only GitHub, PyPI, etc.)
       # Workspace-only filesystem
       # Resource limits
       ...
   ```

6. **Custom Security Policy**
   ```python
   custom_policy = SecurityPolicy(
       network_access="restricted",
       file_system="workspace_only",
       allowed_domains=["*.github.com", "*.npmjs.com"],
       blocked_commands=["rm -rf", "sudo", "curl"],
       max_disk_usage_gb=5,
       max_memory_mb=2048,
       allow_sudo=False
   )
   async with ClaudeBox(security_policy=custom_policy) as box:
       ...
   ```

7. **Command Enforcement**
   ```python
   policy = SecurityPolicy(blocked_commands=["rm -rf", "sudo", "dd"])
   enforcer = SecurityPolicyEnforcer(policy)
   allowed, reason = enforcer.check_command("rm -rf /tmp")
   # allowed=False, reason="Blocked command"
   ```

8. **Network Enforcement**
   ```python
   policy = SecurityPolicy(
       network_access="restricted",
       allowed_domains=["*.github.com", "*.pypi.org"],
       blocked_domains=["*.internal", "localhost"]
   )
   enforcer = SecurityPolicyEnforcer(policy)
   allowed, reason = enforcer.check_network_access("api.github.com")
   ```

9. **Filesystem Enforcement**
   ```python
   policy = SecurityPolicy(
       file_system="workspace_only",
       blocked_paths=["/etc/", "/var/", "/sys/"]
   )
   enforcer = SecurityPolicyEnforcer(policy)
   allowed, reason = enforcer.check_file_access("/etc/passwd", write=False)
   ```

10. **Network Isolation**
    ```python
    no_network = SecurityPolicy(
        network_access="none",
        file_system="workspace_only"
    )
    # Completely air-gapped
    ```

11. **Resource Limits**
    ```python
    limited = SecurityPolicy(
        max_disk_usage_gb=2,
        max_memory_mb=1024,
        max_cpu_percent=50,
        max_execution_time_s=300
    )
    ```

12. **Command Whitelist**
    ```python
    whitelist = SecurityPolicy(
        allowed_commands=["python", "pip", "git", "npm"]
    )
    # Only these commands allowed
    ```

13. **Policy Serialization**
    ```python
    policy_dict = policy.to_dict()
    # Save/load policies
    ```

14. **Domain Wildcards**
    ```python
    policy = SecurityPolicy(
        allowed_domains=["*.github.com", "*.npmjs.com"]
    )
    # Matches api.github.com, registry.npmjs.com, etc.
    ```

15. **Layered Security**
    ```python
    secure_policy = SecurityPolicy(
        # Layer 1: Network restriction
        network_access="restricted",
        allowed_domains=["*.github.com", "*.pypi.org"],
        # Layer 2: Filesystem isolation
        file_system="workspace_only",
        # Layer 3: Command blocking
        blocked_commands=["sudo", "rm -rf", "dd", "mkfs"],
        # Layer 4: Resource limits
        max_disk_usage_gb=10,
        max_memory_mb=4096,
        # Layer 5: Privilege restriction
        allow_sudo=False,
        allow_root=False
    )
    ```

**When to use:** Secure execution, production deployments, untrusted code

---

## 06_advanced.py

**12 examples** of advanced patterns and production workflows

### What You'll Learn
- Full-featured sessions (all options combined)
- Multi-session workflows
- RL training pipelines
- Long-running project patterns
- Observability and metrics
- Batch processing
- Workflow orchestration

### Examples in This File

1. **Full-Featured Session**
   ```python
   async with ClaudeBox(
       session_id="full-featured",
       template=SandboxTemplate.DATA_SCIENCE,
       skills=[DATA_SCIENCE_SKILL, custom_skill],
       security_policy=RESEARCH_POLICY,
       reward_fn=CodeQualityReward(),
       cpus=4,
       memory_mib=8192,
       enable_logging=True
   ) as box:
       # Combines all features
       ...
   ```

2. **Multi-Session Workflow**
   ```python
   # Session 1: Data preparation
   async with ClaudeBox(session_id="data-prep", ...) as box:
       await box.code("Create dataset")

   # Session 2: Model training
   async with ClaudeBox(session_id="model-train", ...) as box:
       await box.code("Train model")

   # Session 3: API deployment
   async with ClaudeBox(session_id="api-deploy", ...) as box:
       await box.code("Create REST API")
   ```

3. **RL Training Pipeline**
   ```python
   tasks = ["Task 1", "Task 2", "Task 3"]
   trajectories = []
   for i, task in enumerate(tasks):
       async with ClaudeBox(
           session_id=f"rl-train-{i}",
           reward_fn=CodeQualityReward()
       ) as box:
           result = await box.code(task)
           trajectory = exporter.export_trajectory()
           trajectories.append(trajectory)
   merged = TrajectoryExporter.merge_trajectories(trajectories)
   ```

4. **Secure Research Environment**
   ```python
   async with ClaudeBox(
       template=SandboxTemplate.DATA_SCIENCE,
       security_policy=RESEARCH_POLICY,
       max_disk_usage_gb=10
   ) as box:
       # Restricted network, workspace-only, resource limits
       ...
   ```

5. **Long-Running Project Pattern**
   ```python
   # Day 1: Initialize
   async with ClaudeBox(session_id="project", ...) as box:
       await box.code("Create Node.js project")

   # Day 2: Add features (reconnect)
   box = await ClaudeBox.reconnect("project")
   async with box:
       await box.code("Add authentication")

   # Day 3: Testing (reconnect again)
   box = await ClaudeBox.reconnect("project")
   async with box:
       await box.code("Write unit tests")
   ```

6. **Template + Skill Combination**
   ```python
   async with ClaudeBox(
       template=SandboxTemplate.WEB_DEV,  # Base capabilities
       skills=[API_SKILL]                   # Extra capabilities
   ) as box:
       # Web dev tools + API skills
       ...
   ```

7. **Progressive Security Levels**
   ```python
   # Development: Unrestricted
   async with ClaudeBox(security_policy=UNRESTRICTED_POLICY) as box:
       await box.code("Develop and test freely")

   # Testing: Standard
   async with ClaudeBox(security_policy=STANDARD_POLICY) as box:
       await box.code("Run tests")

   # Production: Restricted
   async with ClaudeBox(security_policy=RESTRICTED_POLICY) as box:
       await box.code("Execute with strict security")
   ```

8. **Observability Pattern**
   ```python
   async with ClaudeBox(enable_logging=True) as box:
       await box.code("Task 1")
       await box.code("Task 2")

       # Get current metrics
       metrics = await box.get_metrics()
       print(f"CPU: {metrics.cpu_percent}%")
       print(f"Memory: {metrics.memory_mb} MB")

       # Get historical metrics
       history = await box.get_history_metrics()
   ```

9. **Batch Processing**
   ```python
   tasks = ["Process dataset A", "Process dataset B", "Process dataset C"]
   results = []
   for i, task in enumerate(tasks):
       async with ClaudeBox(session_id=f"batch-{i}", ...) as box:
           result = await box.code(task)
           results.append(result)
       await ClaudeBox.cleanup_session(f"batch-{i}", remove_workspace=True)
   success_rate = sum(1 for r in results if r.success) / len(results)
   ```

10. **Workspace Sharing**
    ```python
    # Session 1: Generate data
    async with ClaudeBox(session_id="generator") as box:
        workspace = Path(box.workspace_path)
        (workspace / "shared_data.json").write_text('{"data": [1, 2, 3]}')

    # Session 2: Process shared data
    box = await ClaudeBox.reconnect("generator")
    async with box:
        await box.code("Read and process shared_data.json")
    ```

11. **Error Recovery Pattern**
    ```python
    async with ClaudeBox(session_id="error-recovery") as box:
        result = await box.code("Complex task")
        if not result.success:
            # Retry with simpler approach
            result = await box.code("Simplified version")
            if result.success:
                print("✓ Recovery successful")
    ```

12. **Custom Workflow Orchestration**
    ```python
    workflow = [
        ("setup", "Initialize project"),
        ("install", "Install dependencies"),
        ("build", "Build the project"),
        ("test", "Run tests"),
        ("deploy", "Deploy to staging")
    ]
    async with ClaudeBox(session_id="workflow", ...) as box:
        for step, description in workflow:
            result = await box.code(description)
            if not result.success:
                print(f"✗ Failed at step: {step}")
                break
            print(f"✓ Completed: {step}")
    ```

**When to use:** Production deployments, complex workflows, multi-stage pipelines

---

## Tips & Best Practices

### General
- Start with `01_basic_usage.py` to understand core concepts
- Read example descriptions before running
- Set `CLAUDE_CODE_OAUTH_TOKEN` environment variable
- Check example output to understand behavior

### Persistent Sessions
- Use `session_id` for long-running projects
- Clean up sessions manually with `cleanup_session()`
- List sessions regularly to avoid clutter
- Workspace files at `~/.claudebox/sessions/{id}/workspace/`

### Skills
- Combine skills for rich capabilities
- Create custom skills for domain-specific needs
- Use environment variables for API keys
- Check skill requirements before using

### Security
- Use `STANDARD_POLICY` as default
- Escalate to `RESTRICTED_POLICY` for untrusted code
- Define custom policies for specific needs
- Always use `RESEARCH_POLICY` for research

### RL Training
- Use appropriate reward functions for your task
- Export trajectories regularly
- Merge trajectories from multiple sessions
- Monitor reward distributions

## Need Help?

- **Documentation**: See [docs/](../docs/) for guides and API reference
- **Issues**: Report bugs at https://github.com/boxlite-labs/claudebox/issues
- **Discussions**: Ask questions at https://github.com/boxlite-labs/claudebox/discussions
- **Contributing**: See [CONTRIBUTING.md](../CONTRIBUTING.md)

---

Happy coding with ClaudeBox! 🎉
