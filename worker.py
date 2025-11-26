"""
Minimal reproduction: pydantic_ai structured output validation crash.

BUG: When a temporalized pydantic_ai agent fails structured output validation,
it crashes the entire workflow instead of failing just the activity.

Run:
    1. docker compose up -d
    2. uv run python worker.py
    3. uv run python trigger.py
"""

import asyncio

from temporalio.client import Client
from temporalio.worker import Worker, UnsandboxedWorkflowRunner

from agent import get_plugin
from workflow import BugReproWorkflow


async def main() -> None:
    client = await Client.connect("localhost:7299")

    worker = Worker(
        client,
        task_queue="bug-repro-queue",
        workflows=[BugReproWorkflow],
        plugins=[get_plugin()],
        workflow_failure_exception_types=[Exception],
        workflow_runner=UnsandboxedWorkflowRunner(),
    )

    print("Worker started. Press Ctrl+C to stop.")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
