# RL Training Guide

Collect training data and optimize Claude Code agents with reinforcement learning.

---

## Overview

ClaudeBox provides RL research scaffolding for training agents on coding tasks:

- **5 Reward Functions** - Success, quality, safety, efficiency, custom
- **Trajectory Export** - State-action pairs for training
- **Action Logging** - Structured logs in JSON Lines format
- **Reward Combination** - Multi-objective optimization

---

## Reward Functions

### 1. SuccessOnlyReward

**Purpose:** Binary success/failure reward

**Formula:**
```
reward = 1.0 if success else -1.0
```

**Usage:**
```python
from claudebox import ClaudeBox, SuccessOnlyReward

async def main():
    async with ClaudeBox(reward_fn=SuccessOnlyReward()) as box:
        result = await box.code("Implement binary search")
        print(f"Reward: {result.reward}")  # 1.0 or -1.0
```

**When to use:** Simple tasks where only completion matters

---

### 2. CodeQualityReward

**Purpose:** Reward based on code quality metrics

**Components:**
- Success: 1.0 points
- No errors: 0.5 points
- Fast execution (<5s): 0.3 points
- Few tool calls (<5): 0.2 points
- **Total:** 2.0 points (normalized to 0-1)

**Usage:**
```python
from claudebox import ClaudeBox, CodeQualityReward

async def main():
    async with ClaudeBox(reward_fn=CodeQualityReward()) as box:
        result = await box.code("Write efficient sorting algorithm")
        print(f"Quality Score: {result.reward:.2f}")  # 0.0 to 1.0
```

**When to use:** Optimize for code quality and efficiency

---

### 3. SafetyReward

**Purpose:** Penalize unsafe operations

**Penalizes:**
- Destructive commands: `rm -rf`, `dd`, `mkfs` (-0.5 each)
- Privilege escalation: `sudo`, `su` (-0.3)
- Other unsafe patterns

**Usage:**
```python
from claudebox import ClaudeBox, SafetyReward

async def main():
    async with ClaudeBox(reward_fn=SafetyReward()) as box:
        result = await box.code("Clean up temporary files")
        print(f"Safety Score: {result.reward:.2f}")  #  Higher = safer
```

**When to use:** Train safe coding practices

---

### 4. EfficiencyReward

**Purpose:** Reward efficient execution

**Rewards:**
- Success: +1.0
- ≤3 tool calls: +0.5
- ≤5 tool calls: +0.3
- <2s execution: +0.5
- <5s execution: +0.3

**Usage:**
```python
from claudebox import ClaudeBox, EfficiencyReward

async def main():
    async with ClaudeBox(reward_fn=EfficiencyReward()) as box:
        result = await box.code("Calculate factorial of 10")
        print(f"Efficiency: {result.reward:.2f}")
```

**When to use:** Optimize for speed and minimal tool use

---

### 5. CustomReward

**Purpose:** User-defined reward logic

**Usage:**
```python
from claudebox import ClaudeBox, CustomReward

def my_reward(result):
    """Reward concise responses."""
    score = 1.0 if result.success else -1.0

    # Bonus for short responses
    if result.response and len(result.response) < 100:
        score += 0.5

    return min(score, 1.0)

async def main():
    async with ClaudeBox(reward_fn=CustomReward(my_reward)) as box:
        result = await box.code("Print 'Hello'")
        print(f"Custom Reward: {result.reward:.2f}")
```

**When to use:** Domain-specific reward criteria

---

## Combining Rewards

### Equal Weighting

```python
from claudebox.rewards import combine_rewards, SafetyReward, EfficiencyReward

combined = combine_rewards(
    SafetyReward(),
    EfficiencyReward()
)  # Equal weights: [0.5, 0.5]

async with ClaudeBox(reward_fn=combined) as box:
    result = await box.code("Task")
```

### Custom Weighting

```python
combined = combine_rewards(
    SafetyReward(),
    EfficiencyReward(),
    CodeQualityReward(),
    weights=[0.5, 0.3, 0.2]  # Sum = 1.0
)
```

### Multi-Objective Optimization

```python
# Prioritize safety over efficiency
safe_efficient = combine_rewards(
    SafetyReward(),
    EfficiencyReward(),
    weights=[0.8, 0.2]
)
```

---

## Trajectory Export

### What is a Trajectory?

A **trajectory** is a sequence of (state, action, reward) tuples representing an agent's episode.

**Structure:**
```json
{
  "session_id": "training-001",
  "total_reward": 0.85,
  "steps": [
    {
      "timestamp": "2025-01-01T10:00:00",
      "state": {"prompt": "Implement binary search"},
      "action": {"tool": "bash", "command": "python3 search.py"},
      "reward": 0.5
    },
    ...
  ]
}
```

### Exporting Trajectories

```python
from claudebox import ClaudeBox, CodeQualityReward
from claudebox.trajectory import TrajectoryExporter

async def collect_trajectory():
    async with ClaudeBox(
        session_id="train-001",
        reward_fn=CodeQualityReward()
    ) as box:
        result = await box.code("Implement quicksort")

        # Export trajectory
        exporter = TrajectoryExporter(
            box._session_workspace,
            box._session_manager
        )
        trajectory = exporter.export_trajectory()

        # Save to file
        exporter.save_to_file("trajectories/train_001.json")

        print(f"Total reward: {trajectory['total_reward']}")
        print(f"Steps: {len(trajectory['steps'])}")
```

### State-Action Pairs

```python
exporter = TrajectoryExporter(session_workspace, session_manager)

# Get state-action pairs for training
pairs = exporter.get_state_action_pairs()

for state, action in pairs:
    print(f"State: {state}")
    print(f"Action: {action}")
    # Use for supervised learning, imitation learning, etc.
```

### Merging Trajectories

```python
# Collect multiple trajectories
trajectories = []
for i in range(10):
    async with ClaudeBox(
        session_id=f"train-{i:03d}",
        reward_fn=CodeQualityReward()
    ) as box:
        result = await box.code(f"Task {i}")

        exporter = TrajectoryExporter(box._session_workspace, box._session_manager)
        trajectories.append(exporter.export_trajectory())

# Merge into dataset
exporter = TrajectoryExporter(session_workspace, session_manager)
dataset = exporter.merge_trajectories(trajectories)

# Save dataset
with open("dataset.json", "w") as f:
    json.dump(dataset, f, indent=2)
```

---

## Training Data Collection

### Pattern 1: Single Task Collection

```python
async def collect_single_task():
    """Collect data for one task."""
    async with ClaudeBox(
        session_id="task-binary-search",
        reward_fn=CodeQualityReward()
    ) as box:
        result = await box.code(
            "Implement binary search in Python with docstring and tests"
        )

        if result.reward >= 0.8:  # Quality threshold
            # Save successful trajectory
            exporter = TrajectoryExporter(...)
            exporter.save_to_file("good_examples/binary_search.json")
```

### Pattern 2: Curriculum Learning

```python
CURRICULUM = [
    "Print 'Hello World'",
    "Calculate factorial of 10",
    "Implement binary search",
    "Build REST API with Flask"
]

async def curriculum_training():
    """Progressive difficulty training."""
    for i, task in enumerate(CURRICULUM):
        async with ClaudeBox(
            session_id=f"curriculum-{i}",
            reward_fn=CodeQualityReward()
        ) as box:
            result = await box.code(task)
            print(f"Task {i}: Reward = {result.reward:.2f}")

            # Export trajectory
            ...
```

### Pattern 3: Multi-Agent Collection

```python
async def parallel_collection():
    """Collect data from multiple agents in parallel."""
    tasks = ["Task A", "Task B", "Task C"]

    async def collect_one(task_id, task):
        async with ClaudeBox(
            session_id=f"agent-{task_id}",
            reward_fn=CodeQualityReward()
        ) as box:
            result = await box.code(task)
            # Export...
            return result.reward

    rewards = await asyncio.gather(*[
        collect_one(i, task) for i, task in enumerate(tasks)
    ])

    print(f"Average reward: {sum(rewards) / len(rewards):.2f}")
```

---

## RL Best Practices

### 1. Define Clear Reward Functions

```python
# ✅ Good: Specific reward criteria
def task_specific_reward(result):
    if not result.success:
        return -1.0

    score = 1.0

    # Check for specific requirements
    if "test" in result.response.lower():
        score += 0.3  # Bonus for including tests

    if "docstring" in result.response.lower():
        score += 0.2  # Bonus for documentation

    return min(score, 1.0)

# ❌ Bad: Vague reward criteria
def vague_reward(result):
    return random.random()  # No clear signal
```

### 2. Normalize Rewards

```python
# ✅ Good: Normalized to -1.0 to 1.0 or 0.0 to 1.0
def normalized_reward(result):
    score = calculate_score(result)
    return max(min(score, 1.0), -1.0)  # Clip to [-1, 1]

# ❌ Bad: Unbounded rewards
def unbounded_reward(result):
    return len(result.response)  # Could be arbitrarily large
```

### 3. Balance Exploration vs Exploitation

```python
# Use different reward functions for different stages
async def training_loop():
    # Early training: Encourage exploration
    explore_reward = combine_rewards(
        SuccessOnlyReward(),
        EfficiencyReward(),
        weights=[0.9, 0.1]  # Mostly care about success
    )

    # Later training: Optimize for quality
    exploit_reward = combine_rewards(
        CodeQualityReward(),
        SafetyReward(),
        weights=[0.7, 0.3]  # Refine behavior
    )
```

### 4. Log Everything

```python
async def logged_training():
    """Log all training data."""
    import json
    from datetime import datetime

    async with ClaudeBox(
        session_id="train-001",
        reward_fn=CodeQualityReward(),
        enable_logging=True  # Enable action logging
    ) as box:
        result = await box.code("Task")

        # Log training metadata
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "task": "Task description",
            "reward": result.reward,
            "success": result.success,
            "session_id": box.session_id
        }

        with open("training_log.jsonl", "a") as f:
            f.write(json.dumps(metadata) + "\n")
```

### 5. Validate Reward Functions

```python
# Test reward function behavior
def test_reward_function():
    # Mock successful result
    mock_success = CodeResult(success=True, response="Good code", ...)
    assert reward_fn(mock_success) > 0

    # Mock failed result
    mock_failure = CodeResult(success=False, error="Error", ...)
    assert reward_fn(mock_failure) < 0

    print("✅ Reward function validated")
```

---

## Troubleshooting

### Issue: Rewards Always Same Value

**Problem:** Reward doesn't vary across tasks

**Solution:** Check reward function logic
```python
# Debug reward calculation
result = await box.code("Task")
print(f"Success: {result.success}")
print(f"Error: {result.error}")
print(f"Action count: {len(result.action_log)}")
print(f"Calculated reward: {result.reward}")
```

### Issue: Trajectory Export Fails

**Error:** `FileNotFoundError: history.jsonl not found`

**Solution:** Enable logging
```python
async with ClaudeBox(
    session_id="train-001",
    enable_logging=True  # Must enable logging
) as box:
    ...
```

---

## Next Steps

- **[Examples](../../examples/04_rl_rewards.py)** - 13 RL training examples
- **[Workspace Guide](workspace.md)** - Where trajectories are stored
- **[Sessions Guide](sessions.md)** - Managing training sessions

---

**Train smarter agents with ClaudeBox RL!**
