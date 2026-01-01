"""
Sandbox template examples.

This demonstrates how to use pre-configured sandbox templates:
- Template selection
- Template features
- Custom images
"""

import asyncio

from claudebox import (
    ClaudeBox,
    SandboxTemplate,
    get_template_description,
    get_template_image,
    list_templates,
)


async def example_default_template():
    """Example 1: Default template (base runtime)."""
    print("\n=== Example 1: Default Template ===")

    async with ClaudeBox() as box:
        print(f"Using default template:")
        print(f"  Image: {SandboxTemplate.DEFAULT}")

        result = await box.code("Check which tools are available")

        print(f"\nResult: {result.success}")


async def example_web_dev_template():
    """Example 2: Web development template."""
    print("\n=== Example 2: Web Development Template ===")

    async with ClaudeBox(
        session_id="webdev-example", template=SandboxTemplate.WEB_DEV
    ) as box:
        desc = get_template_description(SandboxTemplate.WEB_DEV)
        print(f"Web Dev template:")
        print(f"  Description: {desc}")

        result = await box.code(
            "Create a simple Express.js server with TypeScript"
        )

        print(f"\nResult: {result.success}")

    await ClaudeBox.cleanup_session("webdev-example", remove_workspace=True)


async def example_data_science_template():
    """Example 3: Data science template."""
    print("\n=== Example 3: Data Science Template ===")

    async with ClaudeBox(
        session_id="ds-template-example",
        template=SandboxTemplate.DATA_SCIENCE,
    ) as box:
        desc = get_template_description(SandboxTemplate.DATA_SCIENCE)
        print(f"Data Science template:")
        print(f"  Description: {desc}")

        result = await box.code(
            "Create a pandas DataFrame and generate a matplotlib plot"
        )

        print(f"\nResult: {result.success}")

    await ClaudeBox.cleanup_session("ds-template-example", remove_workspace=True)


async def example_security_template():
    """Example 4: Security research template."""
    print("\n=== Example 4: Security Template ===")

    # Security template includes tools like nmap, wireshark (for authorized use only)
    desc = get_template_description(SandboxTemplate.SECURITY)
    print(f"Security template:")
    print(f"  Description: {desc}")
    print(f"  ⚠️  Use only for authorized security testing!")

    # Example usage (not executed for safety)
    print("\nExample usage:")
    print("  async with ClaudeBox(template=SandboxTemplate.SECURITY) as box:")
    print("      await box.code('Scan localhost for open ports')")


async def example_devops_template():
    """Example 5: DevOps template."""
    print("\n=== Example 5: DevOps Template ===")

    async with ClaudeBox(
        session_id="devops-example", template=SandboxTemplate.DEVOPS
    ) as box:
        desc = get_template_description(SandboxTemplate.DEVOPS)
        print(f"DevOps template:")
        print(f"  Description: {desc}")

        result = await box.code("Show Docker and Kubernetes CLI versions")

        print(f"\nResult: {result.success}")

    await ClaudeBox.cleanup_session("devops-example", remove_workspace=True)


async def example_mobile_template():
    """Example 6: Mobile development template."""
    print("\n=== Example 6: Mobile Template ===")

    desc = get_template_description(SandboxTemplate.MOBILE)
    print(f"Mobile template:")
    print(f"  Description: {desc}")

    # Would include Android SDK, iOS tools, etc.
    print("\nIdeal for mobile app development workflows")


async def example_template_enum_usage():
    """Example 7: Using template enum values."""
    print("\n=== Example 7: Template Enum Values ===")

    templates = [
        SandboxTemplate.DEFAULT,
        SandboxTemplate.WEB_DEV,
        SandboxTemplate.DATA_SCIENCE,
    ]

    print("Available templates:")
    for template in templates:
        image = str(template)
        desc = get_template_description(template)
        print(f"\n  {template.name}:")
        print(f"    Image: {image}")
        print(f"    Description: {desc}")


async def example_template_string():
    """Example 8: Using template as string."""
    print("\n=== Example 8: Template as String ===")

    # You can use template string directly
    async with ClaudeBox(
        session_id="string-template",
        template="ghcr.io/boxlite-labs/claudebox-runtime:latest",
    ) as box:
        print(f"Using template string directly")
        print(f"  Box ID: {box.id}")

    await ClaudeBox.cleanup_session("string-template", remove_workspace=True)


async def example_custom_image():
    """Example 9: Custom Docker image."""
    print("\n=== Example 9: Custom Docker Image ===")

    # Use a completely custom image
    custom_image = "ghcr.io/boxlite-labs/claudebox-runtime:latest"

    async with ClaudeBox(
        session_id="custom-image", image=custom_image
    ) as box:
        print(f"Using custom image:")
        print(f"  Image: {custom_image}")
        print(f"  Box ID: {box.id}")

    await ClaudeBox.cleanup_session("custom-image", remove_workspace=True)


async def example_image_overrides_template():
    """Example 10: Explicit image overrides template."""
    print("\n=== Example 10: Image Overrides Template ===")

    # When both are specified, image takes priority
    async with ClaudeBox(
        session_id="override-example",
        template=SandboxTemplate.WEB_DEV,  # This is ignored
        image="ghcr.io/boxlite-labs/claudebox-runtime:latest",  # This is used
    ) as box:
        print(f"Image parameter takes priority over template")
        print(f"  Box ID: {box.id}")

    await ClaudeBox.cleanup_session("override-example", remove_workspace=True)


async def example_list_all_templates():
    """Example 11: List all available templates."""
    print("\n=== Example 11: List All Templates ===")

    templates = list_templates()

    print(f"Found {len(templates)} templates:")
    for name, description in templates.items():
        print(f"\n  {name}:")
        print(f"    {description}")


async def example_get_template_image():
    """Example 12: Get template image URL."""
    print("\n=== Example 12: Get Template Image ===")

    # Get image URL from template
    web_dev_image = get_template_image(SandboxTemplate.WEB_DEV)
    print(f"Web Dev image URL:")
    print(f"  {web_dev_image}")

    # Works with string too
    ds_image = get_template_image("ghcr.io/boxlite-labs/claudebox-runtime:data-science")
    print(f"\nData Science image URL:")
    print(f"  {ds_image}")


async def example_template_for_use_case():
    """Example 13: Choose template based on use case."""
    print("\n=== Example 13: Template Selection by Use Case ===")

    use_cases = {
        "Web API development": SandboxTemplate.WEB_DEV,
        "Machine learning": SandboxTemplate.DATA_SCIENCE,
        "Infrastructure automation": SandboxTemplate.DEVOPS,
        "Pentesting (authorized)": SandboxTemplate.SECURITY,
        "React Native app": SandboxTemplate.MOBILE,
    }

    print("Recommended templates by use case:")
    for use_case, template in use_cases.items():
        desc = get_template_description(template)
        print(f"\n  {use_case}:")
        print(f"    Template: {template.name}")
        print(f"    {desc}")


async def main():
    """Run all examples."""
    await example_default_template()
    await example_web_dev_template()
    await example_data_science_template()
    await example_security_template()
    await example_devops_template()
    await example_mobile_template()
    await example_template_enum_usage()
    await example_template_string()
    await example_custom_image()
    await example_image_overrides_template()
    await example_list_all_templates()
    await example_get_template_image()
    await example_template_for_use_case()


if __name__ == "__main__":
    asyncio.run(main())
