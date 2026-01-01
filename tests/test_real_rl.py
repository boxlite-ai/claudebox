"""Real RL scaffolding tests - rewards and trajectory export."""

import os
from pathlib import Path

import pytest

from claudebox import (
    BuiltinRewards,
    ClaudeBox,
    CodeQualityReward,
    EfficiencyReward,
    SafetyReward,
    SuccessOnlyReward,
    TrajectoryExporter,
    combine_rewards,
)

pytestmark = pytest.mark.real


@pytest.fixture
def ensure_oauth_token():
    """Ensure OAuth token is set."""
    token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
    if not token:
        pytest.skip("CLAUDE_CODE_OAUTH_TOKEN not set")
    return token


@pytest.mark.asyncio
async def test_01_success_only_reward(ensure_oauth_token, temp_workspace):
    """Test 1: SuccessOnlyReward function."""
    print("\n🔹 Test 1: SuccessOnlyReward")

    reward_fn = SuccessOnlyReward()

    try:
        async with ClaudeBox(
            oauth_token=ensure_oauth_token,
            workspace_dir=temp_workspace,
            session_id="rl-test-success",
            reward_fn=reward_fn,
        ):
            # Since we're not executing Claude Code (too slow), just test the reward function
            from claudebox.results import CodeResult

            # Test successful result
            success_result = CodeResult(
                success=True,
                response="Success",
                exit_code=0,
                raw_output="Success",
            )

            reward = reward_fn(success_result)
            assert reward == 1.0
            print(f"   ✅ Success reward: {reward}")

            # Test failure result
            failure_result = CodeResult(
                success=False,
                response="Error",
                exit_code=1,
                error="Something failed",
            )

            reward = reward_fn(failure_result)
            assert reward == -1.0
            print(f"   ✅ Failure reward: {reward}")

    finally:
        await ClaudeBox.cleanup_session(
            "rl-test-success", workspace_dir=temp_workspace, remove_workspace=True
        )


@pytest.mark.asyncio
async def test_02_code_quality_reward(ensure_oauth_token, temp_workspace):
    """Test 2: CodeQualityReward function."""
    print("\n🔹 Test 2: CodeQualityReward")

    reward_fn = CodeQualityReward()

    from claudebox.results import CodeResult

    # Perfect code quality
    perfect_result = CodeResult(
        success=True, response="Done", exit_code=0, error=None, action_log=[]
    )

    reward = reward_fn(perfect_result)
    assert reward > 0.5  # Should get points for success and no errors
    print(f"   ✅ Perfect code quality reward: {reward:.2f}")

    # Poor code quality
    poor_result = CodeResult(
        success=False, response="Error", exit_code=1, error="Failed"
    )

    reward = reward_fn(poor_result)
    assert reward < 0.5  # Should get lower reward
    print(f"   ✅ Poor code quality reward: {reward:.2f}")


@pytest.mark.asyncio
async def test_03_safety_reward(ensure_oauth_token, temp_workspace):
    """Test 3: SafetyReward function."""
    print("\n🔹 Test 3: SafetyReward")

    reward_fn = SafetyReward()

    from claudebox.results import ActionLog, CodeResult

    # Safe command
    safe_actions = [
        ActionLog(
            timestamp="2025-01-01T00:00:00Z",
            event_type="tool_call",
            tool="bash",
            input={"command": "echo hello"},
            output={"stdout": "hello"},
            duration_ms=100,
            context={},
        )
    ]

    safe_result = CodeResult(
        success=True,
        response="Done",
        exit_code=0,
        action_log=safe_actions,
    )

    reward = reward_fn(safe_result)
    assert reward == 1.0  # No penalties for safe command
    print(f"   ✅ Safe command reward: {reward}")

    # Unsafe command (rm -rf)
    unsafe_actions = [
        ActionLog(
            timestamp="2025-01-01T00:00:00Z",
            event_type="tool_call",
            tool="bash",
            input={"command": "rm -rf /tmp/test"},
            output={"stdout": ""},
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
    assert reward < 1.0  # Should be penalized
    print(f"   ✅ Unsafe command reward: {reward}")


@pytest.mark.asyncio
async def test_04_efficiency_reward(ensure_oauth_token, temp_workspace):
    """Test 4: EfficiencyReward function."""
    print("\n🔹 Test 4: EfficiencyReward")

    reward_fn = EfficiencyReward()

    from claudebox.results import ActionLog, CodeResult

    # Efficient (few tool calls)
    few_actions = [
        ActionLog(
            timestamp="2025-01-01T00:00:00Z",
            event_type="tool_call",
            tool="bash",
            input={"command": "echo hello"},
            output={"stdout": "hello"},
            duration_ms=100,
            context={},
        )
    ]

    efficient_result = CodeResult(
        success=True,
        response="Done",
        exit_code=0,
        action_log=few_actions,
    )

    efficient_reward = reward_fn(efficient_result)
    assert efficient_reward > 0.5  # Bonus for few tool calls
    print(f"   ✅ Efficient execution reward: {efficient_reward:.2f}")

    # Inefficient (many tool calls)
    many_actions = [
        ActionLog(
            timestamp="2025-01-01T00:00:00Z",
            event_type="tool_call",
            tool="bash",
            input={"command": f"echo {i}"},
            output={"stdout": str(i)},
            duration_ms=100,
            context={},
        )
        for i in range(15)
    ]

    inefficient_result = CodeResult(
        success=True,
        response="Done",
        exit_code=0,
        action_log=many_actions,
    )

    inefficient_reward = reward_fn(inefficient_result)
    assert inefficient_reward <= efficient_reward  # Should be lower than efficient
    print(f"   ✅ Inefficient execution reward: {inefficient_reward:.2f}")


@pytest.mark.asyncio
async def test_05_builtin_rewards(ensure_oauth_token, temp_workspace):
    """Test 5: BuiltinRewards collection."""
    print("\n🔹 Test 5: BuiltinRewards")

    from claudebox.results import CodeResult

    result = CodeResult(success=True, response="Done", exit_code=0)

    # Test all built-in rewards
    reward1 = BuiltinRewards.success_only(result)
    assert reward1 == 1.0
    print(f"   ✅ BuiltinRewards.success_only: {reward1}")

    reward2 = BuiltinRewards.code_quality(result)
    assert reward2 > 0
    print(f"   ✅ BuiltinRewards.code_quality: {reward2:.2f}")

    reward3 = BuiltinRewards.safety(result)
    assert reward3 > 0
    print(f"   ✅ BuiltinRewards.safety: {reward3}")

    reward4 = BuiltinRewards.efficiency(result)
    assert reward4 > 0
    print(f"   ✅ BuiltinRewards.efficiency: {reward4:.2f}")


@pytest.mark.asyncio
async def test_06_combine_rewards(ensure_oauth_token, temp_workspace):
    """Test 6: Combine multiple reward functions."""
    print("\n🔹 Test 6: Combine rewards")

    combined = combine_rewards(
        SuccessOnlyReward(), SafetyReward(), weights=[0.7, 0.3]
    )

    from claudebox.results import CodeResult

    result = CodeResult(success=True, response="Done", exit_code=0)

    reward = combined(result)
    expected = 1.0 * 0.7 + 1.0 * 0.3  # Both return 1.0 for success
    assert abs(reward - expected) < 0.01

    print(f"   ✅ Combined reward: {reward:.2f}")


@pytest.mark.asyncio
async def test_07_trajectory_export(ensure_oauth_token, temp_workspace):
    """Test 7: Trajectory export."""
    print("\n🔹 Test 7: Trajectory export")

    import uuid

    session_id = f"rl-trajectory-{uuid.uuid4().hex[:6]}"

    try:
        async with ClaudeBox(
            oauth_token=ensure_oauth_token,
            workspace_dir=temp_workspace,
            session_id=session_id,
        ) as box:
            Path(box.workspace_path)

            # Create trajectory exporter
            exporter = TrajectoryExporter(
                box._session_workspace, box._session_manager
            )

            # Export trajectory
            trajectory = exporter.export_trajectory()

            assert "session_id" in trajectory
            assert trajectory["session_id"] == session_id
            assert "steps" in trajectory
            assert "total_turns" in trajectory

            print(f"   ✅ Trajectory exported: {trajectory['session_id']}")
            print(f"   ✅ Steps: {len(trajectory['steps'])}")

    finally:
        await ClaudeBox.cleanup_session(
            session_id, workspace_dir=temp_workspace, remove_workspace=True
        )


@pytest.mark.asyncio
async def test_08_trajectory_save_to_file(ensure_oauth_token, temp_workspace):
    """Test 8: Save trajectory to file."""
    print("\n🔹 Test 8: Save trajectory to file")

    import uuid

    session_id = f"rl-trajectory-save-{uuid.uuid4().hex[:6]}"

    try:
        async with ClaudeBox(
            oauth_token=ensure_oauth_token,
            workspace_dir=temp_workspace,
            session_id=session_id,
        ) as box:
            workspace_path = Path(box.workspace_path)

            # Create trajectory exporter
            exporter = TrajectoryExporter(
                box._session_workspace, box._session_manager
            )

            # Export for training
            output_file = exporter.export_for_training(str(workspace_path / "training"))

            assert Path(output_file).exists()
            print(f"   ✅ Trajectory saved: {output_file}")

            # Load trajectory
            trajectory = TrajectoryExporter.load_trajectory(output_file)
            assert trajectory["session_id"] == session_id
            print("   ✅ Trajectory loaded successfully")

    finally:
        await ClaudeBox.cleanup_session(
            session_id, workspace_dir=temp_workspace, remove_workspace=True
        )


@pytest.mark.asyncio
async def test_09_reward_integration(ensure_oauth_token, temp_workspace):
    """Test 9: Reward function integration with ClaudeBox."""
    print("\n🔹 Test 9: Reward integration")

    reward_fn = SuccessOnlyReward()

    try:
        async with ClaudeBox(
            oauth_token=ensure_oauth_token,
            workspace_dir=temp_workspace,
            session_id="rl-test-integration",
            reward_fn=reward_fn,
        ) as box:
            # Reward function should be stored
            assert box._reward_fn is reward_fn
            print(f"   ✅ Reward function integrated: {reward_fn.__class__.__name__}")

    finally:
        await ClaudeBox.cleanup_session(
            "rl-test-integration", workspace_dir=temp_workspace, remove_workspace=True
        )


@pytest.mark.asyncio
async def test_10_custom_reward_function():
    """Test 10: Custom reward function."""
    print("\n🔹 Test 10: Custom reward function")

    from claudebox import CustomReward
    from claudebox.results import CodeResult

    # Define custom reward
    def my_reward(result: CodeResult) -> float:
        if result.success and "hello" in result.response.lower():
            return 2.0
        return 0.0

    custom_reward = CustomReward(my_reward)

    # Test with matching response
    result1 = CodeResult(success=True, response="Hello world", exit_code=0)
    assert custom_reward(result1) == 2.0
    print(f"   ✅ Custom reward (match): {custom_reward(result1)}")

    # Test with non-matching response
    result2 = CodeResult(success=True, response="Goodbye", exit_code=0)
    assert custom_reward(result2) == 0.0
    print(f"   ✅ Custom reward (no match): {custom_reward(result2)}")
