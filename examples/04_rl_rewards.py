"""
Reinforcement Learning (RL) and reward function examples.

This demonstrates:
- Built-in reward functions
- Custom reward functions
- Reward combination
- Trajectory export for training
"""

import asyncio

from claudebox import (
    BuiltinRewards,
    ClaudeBox,
    CodeQualityReward,
    CustomReward,
    EfficiencyReward,
    SafetyReward,
    SuccessOnlyReward,
    TrajectoryExporter,
    combine_rewards,
)
from claudebox.results import CodeResult


async def example_success_only_reward():
    """Example 1: Simple success/failure reward."""
    print("\n=== Example 1: Success-Only Reward ===")

    reward_fn = SuccessOnlyReward()

    async with ClaudeBox(
        session_id="reward-success", reward_fn=reward_fn
    ) as box:
        result = await box.code("Create a file called test.txt")

        print(f"Task: Create a file")
        print(f"Success: {result.success}")
        print(f"Reward: {result.reward}")  # 1.0 if success, -1.0 if failure

    await ClaudeBox.cleanup_session("reward-success", remove_workspace=True)


async def example_code_quality_reward():
    """Example 2: Code quality based reward."""
    print("\n=== Example 2: Code Quality Reward ===")

    reward_fn = CodeQualityReward()

    async with ClaudeBox(
        session_id="reward-quality", reward_fn=reward_fn
    ) as box:
        result = await box.code("Write a Python function to calculate fibonacci")

        print(f"Task: Write fibonacci function")
        print(f"Success: {result.success}")
        print(f"Reward: {result.reward:.2f}")  # 0.0 to 1.0 based on quality

    await ClaudeBox.cleanup_session("reward-quality", remove_workspace=True)


async def example_safety_reward():
    """Example 3: Safety-focused reward."""
    print("\n=== Example 3: Safety Reward ===")

    reward_fn = SafetyReward()

    # Safe command
    safe_result = CodeResult(
        success=True,
        response="File created",
        exit_code=0,
        action_log=[],
    )

    reward = reward_fn(safe_result)
    print(f"Safe command reward: {reward}")  # 1.0

    # Unsafe command (simulated)
    from claudebox.results import ActionLog

    unsafe_actions = [
        ActionLog(
            timestamp="2025-01-01T00:00:00Z",
            event_type="tool_call",
            tool="bash",
            input={"command": "sudo rm -rf /tmp/test"},
            output={},
            duration_ms=100,
            context={},
        )
    ]

    unsafe_result = CodeResult(
        success=True,
        response="Done",
        exit_code=0,
        action_log=unsafe_actions,
    )

    reward = reward_fn(unsafe_result)
    print(f"Unsafe command reward: {reward}")  # < 1.0 (penalized)


async def example_efficiency_reward():
    """Example 4: Efficiency-based reward."""
    print("\n=== Example 4: Efficiency Reward ===")

    reward_fn = EfficiencyReward()

    async with ClaudeBox(
        session_id="reward-efficiency", reward_fn=reward_fn
    ) as box:
        result = await box.code("Create 3 files: a.txt, b.txt, c.txt")

        print(f"Task: Create 3 files")
        print(f"Success: {result.success}")
        print(f"Reward: {result.reward:.2f}")  # Higher for fewer tool calls

    await ClaudeBox.cleanup_session("reward-efficiency", remove_workspace=True)


async def example_builtin_rewards():
    """Example 5: Using BuiltinRewards helper."""
    print("\n=== Example 5: BuiltinRewards Helper ===")

    result = CodeResult(
        success=True,
        response="Task completed",
        exit_code=0,
    )

    # All built-in rewards are available as static methods
    rewards = {
        "success_only": BuiltinRewards.success_only(result),
        "code_quality": BuiltinRewards.code_quality(result),
        "safety": BuiltinRewards.safety(result),
        "efficiency": BuiltinRewards.efficiency(result),
    }

    print("Rewards for successful result:")
    for name, reward in rewards.items():
        print(f"  {name}: {reward:.2f}")


async def example_custom_reward():
    """Example 6: Custom reward function."""
    print("\n=== Example 6: Custom Reward Function ===")

    # Define custom reward logic
    def my_reward_function(result: CodeResult) -> float:
        """Reward function that prefers short responses."""
        if not result.success:
            return -1.0

        # Prefer concise responses
        response_length = len(result.response)
        if response_length < 100:
            return 1.0
        elif response_length < 500:
            return 0.5
        else:
            return 0.2

    reward_fn = CustomReward(my_reward_function)

    async with ClaudeBox(
        session_id="reward-custom", reward_fn=reward_fn
    ) as box:
        result = await box.code("Say hello")

        print(f"Task: Say hello")
        print(f"Response length: {len(result.response)}")
        print(f"Reward: {result.reward:.2f}")

    await ClaudeBox.cleanup_session("reward-custom", remove_workspace=True)


async def example_combine_rewards():
    """Example 7: Combine multiple reward functions."""
    print("\n=== Example 7: Combined Rewards ===")

    # Combine success and safety with weights
    combined = combine_rewards(
        SuccessOnlyReward(),
        SafetyReward(),
        weights=[0.7, 0.3],  # 70% success, 30% safety
    )

    async with ClaudeBox(
        session_id="reward-combined", reward_fn=combined
    ) as box:
        result = await box.code("Create a backup of important files")

        print(f"Task: Create backup")
        print(f"Success: {result.success}")
        print(f"Combined reward: {result.reward:.2f}")

    await ClaudeBox.cleanup_session("reward-combined", remove_workspace=True)


async def example_trajectory_export():
    """Example 8: Export trajectory for RL training."""
    print("\n=== Example 8: Trajectory Export ===")

    async with ClaudeBox(session_id="trajectory-example") as box:
        # Execute some tasks
        await box.code("Create a Python script")
        await box.code("Test the script")

        # Export trajectory
        exporter = TrajectoryExporter(
            box._session_workspace, box._session_manager
        )

        trajectory = exporter.export_trajectory()

        print(f"Trajectory exported:")
        print(f"  Session ID: {trajectory['session_id']}")
        print(f"  Total turns: {trajectory['total_turns']}")
        print(f"  Steps: {len(trajectory['steps'])}")

    await ClaudeBox.cleanup_session("trajectory-example", remove_workspace=True)


async def example_trajectory_save():
    """Example 9: Save trajectory to file."""
    print("\n=== Example 9: Save Trajectory ===")

    async with ClaudeBox(session_id="trajectory-save") as box:
        await box.code("Write a hello world program")

        # Export trajectory to file
        exporter = TrajectoryExporter(
            box._session_workspace, box._session_manager
        )

        output_file = exporter.export_for_training(
            output_dir=box.workspace_path + "/training",
            reward_fn=BuiltinRewards.code_quality,
        )

        print(f"Trajectory saved to:")
        print(f"  {output_file}")

        # Load it back
        loaded = TrajectoryExporter.load_trajectory(output_file)
        print(f"\nLoaded trajectory:")
        print(f"  Session: {loaded['session_id']}")
        print(f"  Steps: {len(loaded['steps'])}")

    await ClaudeBox.cleanup_session("trajectory-save", remove_workspace=True)


async def example_trajectory_with_rewards():
    """Example 10: Trajectory with reward calculation."""
    print("\n=== Example 10: Trajectory with Rewards ===")

    reward_fn = CodeQualityReward()

    async with ClaudeBox(
        session_id="trajectory-rewards", reward_fn=reward_fn
    ) as box:
        # Execute tasks
        result1 = await box.code("Create test.py")
        result2 = await box.code("Run test.py")

        print(f"Task 1 reward: {result1.reward:.2f}")
        print(f"Task 2 reward: {result2.reward:.2f}")

        # Export with calculated rewards
        exporter = TrajectoryExporter(
            box._session_workspace, box._session_manager
        )

        total_reward = exporter.calculate_trajectory_reward(reward_fn)

        print(f"\nTotal trajectory reward: {total_reward:.2f}")

    await ClaudeBox.cleanup_session("trajectory-rewards", remove_workspace=True)


async def example_state_action_pairs():
    """Example 11: Get state-action pairs for RL."""
    print("\n=== Example 11: State-Action Pairs ===")

    async with ClaudeBox(session_id="state-action") as box:
        await box.code("Create file1.txt")
        await box.code("Read file1.txt")

        # Get state-action pairs
        exporter = TrajectoryExporter(
            box._session_workspace, box._session_manager
        )

        pairs = exporter.get_state_action_pairs()

        print(f"State-action pairs: {len(pairs)}")
        if pairs:
            state, action, next_state = pairs[0]
            print(f"\nFirst pair:")
            print(f"  State: {state}")
            print(f"  Action: {action}")
            print(f"  Next state: {next_state}")

    await ClaudeBox.cleanup_session("state-action", remove_workspace=True)


async def example_merge_trajectories():
    """Example 12: Merge multiple trajectories."""
    print("\n=== Example 12: Merge Trajectories ===")

    trajectories = []

    # Create multiple sessions
    for i in range(3):
        async with ClaudeBox(session_id=f"merge-{i}") as box:
            await box.code(f"Task {i}")

            exporter = TrajectoryExporter(
                box._session_workspace, box._session_manager
            )
            trajectory = exporter.export_trajectory()
            trajectories.append(trajectory)

        await ClaudeBox.cleanup_session(f"merge-{i}", remove_workspace=True)

    # Merge all trajectories
    merged = TrajectoryExporter.merge_trajectories(trajectories)

    print(f"Merged trajectories:")
    print(f"  Count: {merged['trajectories_count']}")
    print(f"  Total turns: {merged['total_turns']}")
    print(f"  Total steps: {len(merged['steps'])}")


async def example_custom_multi_factor_reward():
    """Example 13: Complex custom reward function."""
    print("\n=== Example 13: Multi-Factor Custom Reward ===")

    def advanced_reward(result: CodeResult) -> float:
        """Custom reward considering multiple factors."""
        score = 0.0

        # Base success score
        if result.success:
            score += 0.4

        # No errors bonus
        if not result.error:
            score += 0.2

        # Response clarity (shorter is better for simple tasks)
        if result.response and len(result.response) < 200:
            score += 0.2

        # Tool efficiency
        if result.action_log and len(result.action_log) <= 3:
            score += 0.2

        return score

    reward_fn = CustomReward(advanced_reward)

    async with ClaudeBox(
        session_id="advanced-reward", reward_fn=reward_fn
    ) as box:
        result = await box.code("Create hello.txt")

        print(f"Task: Create hello.txt")
        print(f"Success: {result.success}")
        print(f"Advanced reward: {result.reward:.2f}")

    await ClaudeBox.cleanup_session("advanced-reward", remove_workspace=True)


async def main():
    """Run all examples."""
    await example_success_only_reward()
    await example_code_quality_reward()
    await example_safety_reward()
    await example_efficiency_reward()
    await example_builtin_rewards()
    await example_custom_reward()
    await example_combine_rewards()
    await example_trajectory_export()
    await example_trajectory_save()
    await example_trajectory_with_rewards()
    await example_state_action_pairs()
    await example_merge_trajectories()
    await example_custom_multi_factor_reward()


if __name__ == "__main__":
    asyncio.run(main())
