#!/usr/bin/env python3
"""
ClaudeBox example - Run Claude Code in isolated micro-VM.

Usage:
    CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-... python examples/computer_use.py
    ANTHROPIC_API_KEY=sk-ant-... python examples/computer_use.py
"""

import asyncio
import logging

from claudebox import ClaudeBox


async def main():
    async with ClaudeBox() as box:
        print(f"ClaudeBox: {box.id}")

        result = await box.code(
            prompt="List files in the current directory and tell me what you see",
            max_turns=5,
        )

        print(f"Success: {result.success}")
        if result.error:
            print(f"Error: {result.error}")
        print(f"\nResponse:\n{result.response}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(name)s %(levelname)s %(message)s")
    asyncio.run(main())
