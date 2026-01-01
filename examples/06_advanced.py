"""
Advanced ClaudeBox examples.

This demonstrates advanced usage patterns:
- Combining skills, templates, and security
- Multi-session workflows
- RL training pipelines
- Production patterns
"""

import asyncio

from claudebox import (
    API_SKILL,
    DATA_SCIENCE_SKILL,
    RESEARCH_POLICY,
    RESTRICTED_POLICY,
    BuiltinRewards,
    ClaudeBox,
    CodeQualityReward,
    SandboxTemplate,
    Skill,
    TrajectoryExporter,
    combine_rewards,
)


async def example_full_featured_session():
    """Example 1: Session with all features enabled."""
    print("\n=== Example 1: Full-Featured Session ===")

    # Custom skill
    custom_skill = Skill(
        name="ml_tools",
        description="Machine learning utilities",
        install_cmd="pip3 install scikit-learn tensorflow",
        requirements=["scikit-learn", "tensorflow"],
    )

    # Combined reward function
    reward_fn = combine_rewards(
        CodeQualityReward(),
        weights=[1.0],
    )

    async with ClaudeBox(
        session_id="full-featured",
        template=SandboxTemplate.DATA_SCIENCE,
        skills=[DATA_SCIENCE_SKILL, custom_skill],
        security_policy=RESEARCH_POLICY,
        reward_fn=reward_fn,
        cpus=4,
        memory_mib=8192,
        enable_logging=True,
    ) as box:
        print(f"Full-featured session:")
        print(f"  Template: DATA_SCIENCE")
        print(f"  Skills: {len([DATA_SCIENCE_SKILL, custom_skill])}")
        print(f"  Security: RESEARCH_POLICY")
        print(f"  Reward: CodeQuality")
        print(f"  Resources: 4 CPUs, 8GB RAM")

        result = await box.code("Analyze a sample dataset with pandas")

        print(f"\nResult:")
        print(f"  Success: {result.success}")
        print(f"  Reward: {result.reward:.2f}")

    await ClaudeBox.cleanup_session("full-featured", remove_workspace=True)


async def example_multi_session_workflow():
    """Example 2: Multi-session workflow."""
    print("\n=== Example 2: Multi-Session Workflow ===")

    # Session 1: Data preparation
    async with ClaudeBox(
        session_id="data-prep",
        template=SandboxTemplate.DATA_SCIENCE,
        skills=[DATA_SCIENCE_SKILL],
    ) as box:
        print("Session 1: Data preparation")
        result = await box.code("Create a sample dataset and save to data.csv")
        print(f"  ✓ Data prepared: {result.success}")

    # Session 2: Model training
    async with ClaudeBox(
        session_id="model-train",
        template=SandboxTemplate.DATA_SCIENCE,
        skills=[DATA_SCIENCE_SKILL],
    ) as box:
        print("\nSession 2: Model training")
        result = await box.code("Train a simple ML model")
        print(f"  ✓ Model trained: {result.success}")

    # Session 3: API deployment
    async with ClaudeBox(
        session_id="api-deploy",
        template=SandboxTemplate.WEB_DEV,
        skills=[API_SKILL],
    ) as box:
        print("\nSession 3: API deployment")
        result = await box.code("Create a REST API endpoint")
        print(f"  ✓ API created: {result.success}")

    # Cleanup all sessions
    for session_id in ["data-prep", "model-train", "api-deploy"]:
        await ClaudeBox.cleanup_session(session_id, remove_workspace=True)

    print("\n✓ Multi-session workflow completed")


async def example_rl_training_pipeline():
    """Example 3: RL training data collection pipeline."""
    print("\n=== Example 3: RL Training Pipeline ===")

    reward_fn = CodeQualityReward()
    trajectories = []

    # Collect training data from multiple sessions
    tasks = [
        "Create a Python function to sort a list",
        "Write a function to calculate factorial",
        "Implement a binary search algorithm",
    ]

    for i, task in enumerate(tasks):
        async with ClaudeBox(
            session_id=f"rl-train-{i}",
            reward_fn=reward_fn,
            enable_logging=True,
        ) as box:
            result = await box.code(task)

            # Export trajectory
            exporter = TrajectoryExporter(
                box._session_workspace, box._session_manager
            )
            trajectory = exporter.export_trajectory()
            trajectories.append(trajectory)

            print(f"Task {i+1}: {task[:40]}...")
            print(f"  Reward: {result.reward:.2f}")

        await ClaudeBox.cleanup_session(f"rl-train-{i}", remove_workspace=True)

    # Merge trajectories for training
    merged = TrajectoryExporter.merge_trajectories(trajectories)

    print(f"\n✓ RL training data collected:")
    print(f"  Trajectories: {merged['trajectories_count']}")
    print(f"  Total steps: {len(merged['steps'])}")


async def example_secure_research_environment():
    """Example 4: Secure research environment."""
    print("\n=== Example 4: Secure Research Environment ===")

    async with ClaudeBox(
        session_id="secure-research",
        template=SandboxTemplate.DATA_SCIENCE,
        security_policy=RESEARCH_POLICY,
        skills=[DATA_SCIENCE_SKILL],
        max_disk_usage_gb=10,
    ) as box:
        print(f"Secure research environment:")
        print(f"  Template: DATA_SCIENCE")
        print(f"  Policy: RESEARCH (network restricted)")
        print(f"  Max disk: 10 GB")
        print(f"  Allowed domains: {RESEARCH_POLICY.allowed_domains[:2]}...")

        result = await box.code(
            "Download data from GitHub and analyze it"
        )

        print(f"\nResult: {result.success}")

    await ClaudeBox.cleanup_session("secure-research", remove_workspace=True)


async def example_session_persistence_pattern():
    """Example 5: Long-running project pattern."""
    print("\n=== Example 5: Long-Running Project ===")

    project_id = "long-running-project"

    # Day 1: Initialize project
    async with ClaudeBox(
        session_id=project_id,
        template=SandboxTemplate.WEB_DEV,
    ) as box:
        print("Day 1: Initialize project")
        result = await box.code("Create a Node.js project with Express")
        print(f"  ✓ Project initialized: {result.success}")

    # Day 2: Add features (reconnect)
    box = await ClaudeBox.reconnect(project_id)
    async with box:
        print("\nDay 2: Add features")
        result = await box.code("Add authentication endpoints")
        print(f"  ✓ Features added: {result.success}")

    # Day 3: Testing (reconnect again)
    box = await ClaudeBox.reconnect(project_id)
    async with box:
        print("\nDay 3: Testing")
        result = await box.code("Write unit tests")
        print(f"  ✓ Tests written: {result.success}")

    # Project complete, cleanup
    await ClaudeBox.cleanup_session(project_id, remove_workspace=True)
    print("\n✓ Project completed and cleaned up")


async def example_template_skill_combination():
    """Example 6: Template + Skill combination."""
    print("\n=== Example 6: Template + Skill Combo ===")

    # Web dev template + API skill for enhanced capabilities
    async with ClaudeBox(
        session_id="enhanced-webdev",
        template=SandboxTemplate.WEB_DEV,
        skills=[API_SKILL],  # Add extra capabilities
    ) as box:
        print(f"Enhanced web development environment:")
        print(f"  Base: WEB_DEV template (Node.js, Docker, PostgreSQL)")
        print(f"  Extra: API_SKILL (requests, httpx)")

        result = await box.code(
            "Create a microservice that calls external APIs"
        )

        print(f"\nResult: {result.success}")

    await ClaudeBox.cleanup_session("enhanced-webdev", remove_workspace=True)


async def example_progressive_security():
    """Example 7: Progressive security levels."""
    print("\n=== Example 7: Progressive Security ===")

    # Development: Unrestricted
    from claudebox import UNRESTRICTED_POLICY

    async with ClaudeBox(
        session_id="dev-env",
        security_policy=UNRESTRICTED_POLICY,
    ) as box:
        print("Development environment: UNRESTRICTED")
        await box.code("Develop and test freely")

    await ClaudeBox.cleanup_session("dev-env", remove_workspace=True)

    # Testing: Standard
    from claudebox import STANDARD_POLICY

    async with ClaudeBox(
        session_id="test-env",
        security_policy=STANDARD_POLICY,
    ) as box:
        print("\nTesting environment: STANDARD")
        await box.code("Run tests with basic restrictions")

    await ClaudeBox.cleanup_session("test-env", remove_workspace=True)

    # Production: Restricted
    async with ClaudeBox(
        session_id="prod-env",
        security_policy=RESTRICTED_POLICY,
    ) as box:
        print("\nProduction environment: RESTRICTED")
        await box.code("Execute with strict security")

    await ClaudeBox.cleanup_session("prod-env", remove_workspace=True)

    print("\n✓ Progressive security pattern demonstrated")


async def example_observability_pattern():
    """Example 8: Observability and metrics."""
    print("\n=== Example 8: Observability Pattern ===")

    async with ClaudeBox(
        session_id="observable",
        enable_logging=True,
    ) as box:
        # Execute tasks
        await box.code("Create file1.txt")
        await box.code("Create file2.txt")
        await box.code("Create file3.txt")

        # Get metrics
        metrics = await box.get_metrics()
        print(f"Current metrics:")
        print(f"  CPU: {metrics.cpu_percent}%")
        print(f"  Memory: {metrics.memory_mb} MB")
        print(f"  Commands: {metrics.commands_executed}")

        # Get history
        history = await box.get_history_metrics()
        print(f"\nHistory: {len(history)} metric snapshots")

    await ClaudeBox.cleanup_session("observable", remove_workspace=True)


async def example_batch_processing():
    """Example 9: Batch processing pattern."""
    print("\n=== Example 9: Batch Processing ===")

    tasks = [
        "Process dataset A",
        "Process dataset B",
        "Process dataset C",
    ]

    results = []

    for i, task in enumerate(tasks):
        async with ClaudeBox(
            session_id=f"batch-{i}",
            template=SandboxTemplate.DATA_SCIENCE,
        ) as box:
            result = await box.code(task)
            results.append(result)

            print(f"Task {i+1}: {result.success}")

        await ClaudeBox.cleanup_session(f"batch-{i}", remove_workspace=True)

    success_rate = sum(1 for r in results if r.success) / len(results)
    print(f"\n✓ Batch complete: {success_rate*100:.0f}% success rate")


async def example_workspace_sharing():
    """Example 10: Workspace data sharing between sessions."""
    print("\n=== Example 10: Workspace Sharing ===")

    from pathlib import Path

    # Session 1: Generate data
    async with ClaudeBox(session_id="generator") as box:
        workspace = Path(box.workspace_path)

        # Create shared data file
        shared_file = workspace / "shared_data.json"
        shared_file.write_text('{"data": [1, 2, 3]}')

        print(f"Session 1: Created shared data")
        print(f"  File: {shared_file.name}")

    # Session 2: Process shared data
    box = await ClaudeBox.reconnect("generator")
    async with box:
        result = await box.code("Read and process shared_data.json")

        print(f"\nSession 2: Processed shared data")
        print(f"  Success: {result.success}")

    await ClaudeBox.cleanup_session("generator", remove_workspace=True)


async def example_error_recovery_pattern():
    """Example 11: Error recovery pattern."""
    print("\n=== Example 11: Error Recovery ===")

    async with ClaudeBox(session_id="error-recovery") as box:
        # Attempt task
        result = await box.code("Complex task that might fail")

        if not result.success:
            print("Task failed, attempting recovery...")

            # Retry with simpler approach
            result = await box.code("Simplified version of the task")

            if result.success:
                print("✓ Recovery successful")
            else:
                print("✗ Recovery failed")
        else:
            print("✓ Task succeeded on first try")

    await ClaudeBox.cleanup_session("error-recovery", remove_workspace=True)


async def example_custom_workflow_orchestration():
    """Example 12: Custom workflow orchestration."""
    print("\n=== Example 12: Workflow Orchestration ===")

    workflow = [
        ("setup", "Initialize project structure"),
        ("install", "Install dependencies"),
        ("build", "Build the project"),
        ("test", "Run tests"),
        ("deploy", "Deploy to staging"),
    ]

    async with ClaudeBox(
        session_id="workflow",
        template=SandboxTemplate.DEVOPS,
    ) as box:
        for step, description in workflow:
            print(f"\nStep: {step}")
            result = await box.code(description)

            if not result.success:
                print(f"  ✗ Failed at step: {step}")
                break

            print(f"  ✓ Completed: {step}")
        else:
            print("\n✓ Workflow completed successfully")

    await ClaudeBox.cleanup_session("workflow", remove_workspace=True)


async def main():
    """Run all examples."""
    await example_full_featured_session()
    await example_multi_session_workflow()
    await example_rl_training_pipeline()
    await example_secure_research_environment()
    await example_session_persistence_pattern()
    await example_template_skill_combination()
    await example_progressive_security()
    await example_observability_pattern()
    await example_batch_processing()
    await example_workspace_sharing()
    await example_error_recovery_pattern()
    await example_custom_workflow_orchestration()


if __name__ == "__main__":
    asyncio.run(main())
