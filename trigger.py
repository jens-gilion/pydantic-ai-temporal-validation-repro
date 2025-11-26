"""Trigger the workflow to reproduce the bug."""

import asyncio
from uuid import uuid4

from temporalio.client import Client


async def main() -> None:
    client = await Client.connect("localhost:7299")

    handle = await client.start_workflow(
        "BugReproWorkflow",
        id=f"bug-repro-{uuid4()}",
        task_queue="bug-repro-queue",
    )

    print(f"Started workflow: {handle.id}")
    print("Check Temporal UI at http://localhost:8299")

    try:
        result = await handle.result()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Workflow failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())

