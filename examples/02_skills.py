"""
Skills system examples.

This demonstrates how to use pre-built and custom skills:
- Built-in skills
- Custom skills
- Multiple skills
- Skill configuration
"""

import asyncio
import logging

from claudebox import (
    API_SKILL,
    AWS_SKILL,
    DATA_SCIENCE_SKILL,
    DOCKER_SKILL,
    EMAIL_SKILL,
    MYSQL_SKILL,
    POSTGRES_SKILL,
    REDIS_SKILL,
    SCRAPING_SKILL,
    ClaudeBox,
    Skill,
    get_skill,
    list_skills,
    register_skill,
)


async def example_builtin_email_skill():
    """Example 1: Use built-in email skill."""
    print("\n=== Example 1: Built-in Email Skill ===")

    async with ClaudeBox(
        session_id="email-example", skills=[EMAIL_SKILL]
    ) as box:
        print(f"Email skill loaded:")
        print(f"  Name: {EMAIL_SKILL.name}")
        print(f"  Description: {EMAIL_SKILL.description}")
        print(f"  Requirements: {EMAIL_SKILL.requirements}")

        # Now Claude can use sendgrid for emails
        result = await box.code(
            "Show me how to send an email using sendgrid (don't actually send)"
        )

        print(f"\nResult: {result.success}")

    await ClaudeBox.cleanup_session("email-example", remove_workspace=True)


async def example_builtin_api_skill():
    """Example 2: Use API skill for HTTP requests."""
    print("\n=== Example 2: Built-in API Skill ===")

    async with ClaudeBox(
        session_id="api-example", skills=[API_SKILL]
    ) as box:
        print(f"API skill loaded:")
        print(f"  Name: {API_SKILL.name}")
        print(f"  Requirements: {API_SKILL.requirements}")

        # Claude can use requests/httpx for API calls
        result = await box.code(
            "Create a Python script that makes a GET request to an API"
        )

        print(f"\nResult: {result.success}")

    await ClaudeBox.cleanup_session("api-example", remove_workspace=True)


async def example_database_skills():
    """Example 3: Use database skills."""
    print("\n=== Example 3: Database Skills ===")

    async with ClaudeBox(
        session_id="db-example",
        skills=[POSTGRES_SKILL, MYSQL_SKILL, REDIS_SKILL],
    ) as box:
        print(f"Database skills loaded:")
        print(f"  - PostgreSQL")
        print(f"  - MySQL")
        print(f"  - Redis")

        result = await box.code(
            "Show me how to connect to PostgreSQL, MySQL, and Redis"
        )

        print(f"\nResult: {result.success}")

    await ClaudeBox.cleanup_session("db-example", remove_workspace=True)


async def example_data_science_skill():
    """Example 4: Use data science skill."""
    print("\n=== Example 4: Data Science Skill ===")

    async with ClaudeBox(
        session_id="ds-example", skills=[DATA_SCIENCE_SKILL]
    ) as box:
        print(f"Data science skill loaded:")
        print(f"  Name: {DATA_SCIENCE_SKILL.name}")
        print(f"  Requirements: {DATA_SCIENCE_SKILL.requirements}")

        result = await box.code(
            "Create a sample pandas DataFrame and plot it with matplotlib"
        )

        print(f"\nResult: {result.success}")

    await ClaudeBox.cleanup_session("ds-example", remove_workspace=True)


async def example_custom_skill():
    """Example 5: Create a custom skill."""
    print("\n=== Example 5: Custom Skill ===")

    # Define a custom skill
    custom_skill = Skill(
        name="text_processing",
        description="Advanced text processing tools",
        install_cmd="pip3 install nltk spacy",
        requirements=["nltk", "spacy"],
        config={
            "default_language": "en",
            "models": ["en_core_web_sm"],
        },
        files={
            "process.py": """
import nltk
from nltk.tokenize import word_tokenize

def process_text(text):
    tokens = word_tokenize(text)
    return tokens
""",
            "config.json": '{"version": "1.0", "enabled": true}',
        },
    )

    async with ClaudeBox(
        session_id="custom-skill-example", skills=[custom_skill]
    ) as box:
        print(f"Custom skill created:")
        print(f"  Name: {custom_skill.name}")
        print(f"  Install command: {custom_skill.install_cmd}")
        print(f"  Files: {list(custom_skill.files.keys())}")

        result = await box.code("List files in the skills directory")

        print(f"\nResult: {result.success}")

    await ClaudeBox.cleanup_session("custom-skill-example", remove_workspace=True)


async def example_skill_with_env_vars():
    """Example 6: Skill with environment variables."""
    print("\n=== Example 6: Skill with Environment Variables ===")

    api_skill = Skill(
        name="external_api",
        description="Connect to external API",
        install_cmd="pip3 install requests",
        env_vars={
            "API_KEY": "your-api-key-here",
            "API_ENDPOINT": "https://api.example.com",
        },
    )

    async with ClaudeBox(
        session_id="env-skill-example", skills=[api_skill]
    ) as box:
        print(f"Skill with environment variables:")
        print(f"  Env vars: {list(api_skill.env_vars.keys())}")

        # Environment variables are automatically set in the VM
        result = await box.code("Print the API_KEY environment variable")

        print(f"\nResult: {result.success}")

    await ClaudeBox.cleanup_session("env-skill-example", remove_workspace=True)


async def example_multiple_skills():
    """Example 7: Multiple skills together."""
    print("\n=== Example 7: Multiple Skills ===")

    skills = [API_SKILL, DATA_SCIENCE_SKILL, DOCKER_SKILL]

    async with ClaudeBox(
        session_id="multi-skill-example", skills=skills
    ) as box:
        print(f"Loaded {len(skills)} skills:")
        for skill in skills:
            print(f"  - {skill.name}: {skill.description}")

        result = await box.code(
            "Show me the capabilities available with these skills"
        )

        print(f"\nResult: {result.success}")

    await ClaudeBox.cleanup_session("multi-skill-example", remove_workspace=True)


async def example_skill_registry():
    """Example 8: Using the skill registry."""
    print("\n=== Example 8: Skill Registry ===")

    # List all built-in skills
    available_skills = list_skills()
    print(f"Available built-in skills: {len(available_skills)}")
    for skill_name in available_skills[:5]:  # Show first 5
        print(f"  - {skill_name}")

    # Get a specific skill
    postgres = get_skill("postgres")
    print(f"\nPostgreSQL skill:")
    print(f"  Name: {postgres.name}")
    print(f"  Description: {postgres.description}")
    print(f"  Requirements: {postgres.requirements}")
    print(f"  System packages: {postgres.system_packages}")

    # Register a custom skill
    my_skill = Skill(
        name="my_custom_tool",
        description="My custom development tool",
        install_cmd="echo 'Installing custom tool'",
    )

    register_skill(my_skill)
    print(f"\n✓ Registered custom skill: {my_skill.name}")

    # Verify it's registered
    registered = get_skill("my_custom_tool")
    print(f"✓ Retrieved from registry: {registered.name}")


async def example_skill_with_system_packages():
    """Example 9: Skill requiring system packages."""
    print("\n=== Example 9: Skill with System Packages ===")

    video_skill = Skill(
        name="video_processing",
        description="Video processing with ffmpeg",
        system_packages=["ffmpeg", "imagemagick"],
        install_cmd="pip3 install moviepy",
        requirements=["moviepy"],
    )

    print(f"Video processing skill:")
    print(f"  System packages: {video_skill.system_packages}")
    print(f"  Python packages: {video_skill.requirements}")

    # Note: This requires root access to install system packages
    # In production, use pre-configured template with these packages


async def example_cloud_skills():
    """Example 10: Cloud provider skills."""
    print("\n=== Example 10: Cloud Skills ===")

    async with ClaudeBox(
        session_id="cloud-example", skills=[AWS_SKILL]
    ) as box:
        print(f"AWS skill loaded:")
        print(f"  Name: {AWS_SKILL.name}")
        print(f"  Requirements: {AWS_SKILL.requirements}")

        result = await box.code(
            "Show me how to list S3 buckets using boto3 (don't execute)"
        )

        print(f"\nResult: {result.success}")

    await ClaudeBox.cleanup_session("cloud-example", remove_workspace=True)


async def main():
    """Run all examples."""
    await example_builtin_email_skill()
    await example_builtin_api_skill()
    await example_database_skills()
    await example_data_science_skill()
    await example_custom_skill()
    await example_skill_with_env_vars()
    await example_multiple_skills()
    await example_skill_registry()
    await example_skill_with_system_packages()
    await example_cloud_skills()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(name)s %(levelname)s %(message)s")
    asyncio.run(main())
